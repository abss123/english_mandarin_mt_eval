"""
Shared Google Sheets data layer.
All scripts import load_votes / save_vote / clear_votes from here.

Sheet schema (row 1 = headers):
  key | voter_email | row_idx | en_text | choices | choice_labels | timestamp

'choices' and 'choice_labels' are stored as JSON arrays.
"""

import json
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = ["key", "voter_email", "row_idx", "en_text", "choices", "choice_labels", "timestamp"]


@st.cache_resource
def get_sheet():
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_url(st.secrets["google_sheets"]["sheet_url"]).sheet1
    # Write headers if sheet is empty
    if sheet.row_count == 0 or sheet.row_values(1) != HEADERS:
        sheet.clear()
        sheet.append_row(HEADERS)
    return sheet


@st.cache_data(ttl=10)
def load_votes():
    """Return votes as dict keyed by 'voter_id|row_idx'."""
    sheet = get_sheet()
    rows = sheet.get_all_records()
    votes = {}
    for row in rows:
        key = row.get("key", "")
        if not key:
            continue
        votes[key] = {
            "choices": json.loads(row.get("choices") or "[]"),
            "choice_labels": json.loads(row.get("choice_labels") or "[]"),
            "voter_email": row.get("voter_email", ""),
            "row_idx": int(row.get("row_idx", 0)),
            "en_text": row.get("en_text", ""),
            "timestamp": row.get("timestamp", ""),
        }
    return votes


def save_vote(voted_key, vote_data):
    """Insert or update a single vote row. Clears the load_votes cache after writing."""
    sheet = get_sheet()
    row_values = [
        voted_key,
        vote_data["voter_email"],
        vote_data["row_idx"],
        vote_data["en_text"],
        json.dumps(vote_data["choices"], ensure_ascii=False),
        json.dumps(vote_data["choice_labels"], ensure_ascii=False),
        vote_data["timestamp"],
    ]
    cell = sheet.find(voted_key, in_column=1)
    if cell:
        sheet.update(f"A{cell.row}:G{cell.row}", [row_values])
    else:
        sheet.append_row(row_values)
    load_votes.clear()


def clear_all_votes():
    """Delete all vote rows, keeping the header."""
    sheet = get_sheet()
    sheet.clear()
    sheet.append_row(HEADERS)
    load_votes.clear()
