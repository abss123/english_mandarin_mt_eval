"""
Clear all votes from Google Sheets — run with: python clear_votes.py
Prompts for confirmation before deleting.
"""

import sys

# Streamlit secrets aren't available outside Streamlit, so load them manually
import toml, os
secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
if not os.path.exists(secrets_path):
    print(f"Secrets file not found at {secrets_path}")
    sys.exit(1)

secrets = toml.load(secrets_path)

import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
HEADERS = ["key", "voter_email", "row_idx", "en_text", "choices", "choice_labels", "timestamp"]

creds = Credentials.from_service_account_info(secrets["gcp_service_account"], scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_url(secrets["google_sheets"]["sheet_url"]).sheet1

rows = sheet.get_all_records()
print(f"Found {len(rows)} vote(s) in the sheet.")
confirm = input("Type 'yes' to permanently delete all votes: ").strip().lower()
if confirm == "yes":
    sheet.clear()
    sheet.append_row(HEADERS)
    print("All votes cleared.")
else:
    print("Aborted. No votes were deleted.")
