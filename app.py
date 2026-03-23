"""
Translation Quality Voting Dashboard
=====================================
Teammates can vote on which ZH translation is best for each EN subtitle line.
Translations are shown in randomized order (blind evaluation) to avoid bias.

Deploy: Push to GitHub → connect at share.streamlit.io
"""

import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime

# =============================================================================
# CONFIG  ← edit here to control which translations voters see
# =============================================================================

DATA_FILE = "translations.csv"
VOTES_FILE = "votes.json"

# Add or remove entries to control which translation systems appear for voting.
# Voters never see these names — they only see "Option A / B / C / ...".
SOURCE_COLS = {
    # "zh_opus": "OPUS",      # comment out to hide from voters
    "zh_nllb": "NLLB",
    "zh_claude": "Claude",
    "zh_deepseek": "DeepSeek",
}

# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_data
def load_translations():
    df = pd.read_csv(DATA_FILE)
    required = ["en_text"] + list(SOURCE_COLS.keys())
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Missing columns in CSV: {missing}")
        st.stop()
    return df


def load_votes():
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_votes(votes):
    with open(VOTES_FILE, 'w') as f:
        json.dump(votes, f, indent=2, ensure_ascii=False)


def get_shuffled_sources(row_idx, session_seed):
    """Random shuffle per row, stable within a session but different each session."""
    cols = list(SOURCE_COLS.keys())
    random.Random(f"{session_seed}-{row_idx}").shuffle(cols)
    return cols


# =============================================================================
# UI
# =============================================================================

def main():
    st.set_page_config(
        page_title="Translation Voting",
        page_icon="🗳️",
        layout="wide",
    )

    # Custom CSS
    st.markdown("""
    <style>
    .translation-card {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 16px 20px;
        margin: 8px 0;
        font-size: 17px;
        line-height: 1.6;
    }
    .en-source {
        background: #eef2ff;
        border-left: 4px solid #4f46e5;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 16px;
        margin: 8px 0 16px 0;
    }
    .vote-label {
        font-size: 13px;
        color: #666;
        margin-bottom: 2px;
    }
    .winner-badge {
        background: #10b981;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🗳️ Translation Quality Voting")
    st.caption("Compare EN→ZH translations from different systems. "
               "Translations are shown in random order to avoid bias.")

    # Voter identification
    with st.sidebar:
        st.header("👤 Your Identity")
        voter_email = st.text_input("Your email", key="voter_email",
                                     placeholder="e.g., alice@example.com")
        if not voter_email or "@" not in voter_email:
            st.warning("Enter a valid email to start voting.")
            st.stop()

        voter_name = voter_email.strip()
        voter_id = voter_name.lower()
        st.success(f"Voting as: **{voter_name}**")

    # Generate a random seed once per session (changes on browser refresh / new tab)
    if "_session_seed" not in st.session_state:
        st.session_state._session_seed = random.randint(0, 2**32)

    df = load_translations()
    votes = load_votes()
    total_rows = len(df)

    # Count how many this voter has completed
    voter_votes = {k: v for k, v in votes.items() if k.startswith(f"{voter_id}|")}
    voted_rows = set(k.split("|")[1] for k in voter_votes.keys())

    with st.sidebar:
        st.metric("Your progress", f"{len(voted_rows)}/{total_rows}")
        progress = len(voted_rows) / total_rows if total_rows > 0 else 0
        st.progress(progress)

    # Navigation
    st.divider()

    # Find first unvoted row for this voter
    first_unvoted = 0
    for i in range(total_rows):
        if str(i) not in voted_rows:
            first_unvoted = i
            break

    # Reset navigation when the voter email changes
    if st.session_state.get("_voter_id") != voter_id:
        st.session_state._voter_id = voter_id
        st.session_state._current_row = first_unvoted

    if "_current_row" not in st.session_state:
        st.session_state._current_row = first_unvoted

    col_prev, col_idx, col_next, col_jump = st.columns([1, 2, 1, 2])
    with col_idx:
        row_idx = st.number_input("Line #", min_value=0, max_value=total_rows - 1,
                                   value=st.session_state._current_row, step=1)
        st.session_state._current_row = row_idx
    with col_prev:
        st.write("")  # spacer
        if st.button("← Prev", use_container_width=True) and row_idx > 0:
            st.session_state._current_row = row_idx - 1
            st.rerun()
    with col_next:
        st.write("")
        if st.button("Next →", use_container_width=True) and row_idx < total_rows - 1:
            st.session_state._current_row = row_idx + 1
            st.rerun()
    with col_jump:
        st.write("")
        if st.button("⏭ Next unvoted", use_container_width=True):
            for i in range(total_rows):
                if str(i) not in voted_rows:
                    st.session_state._current_row = i
                    st.rerun()

    row = df.iloc[row_idx]
    voted_key = f"{voter_id}|{row_idx}"
    already_voted = voted_key in votes

    # Show status
    if already_voted:
        st.info("✅ You already voted for this line. You can change your vote below.")

    # English source
    en_text = str(row["en_text"]) if "en_text" in row.index else ""
    timestamp = str(row["timestamp"]) if "timestamp" in row.index else ""

    st.markdown("#### English subtitle")
    if timestamp:
        st.caption(f"🕐 {timestamp}")
    st.info(en_text)

    # Show translations with checkboxes (randomized order, blind evaluation)
    st.markdown("**Select all translations you consider acceptable:**")

    shuffled_cols = get_shuffled_sources(row_idx, st.session_state._session_seed)
    prev_choices = set(votes.get(voted_key, {}).get("choices", []))

    cols = st.columns(len(shuffled_cols))
    selected_options = []

    for i, col_name in enumerate(shuffled_cols):
        label = f"Option {chr(65 + i)}"
        zh_text = row.get(col_name, "")
        with cols[i]:
            if st.checkbox(label, value=(col_name in prev_choices),
                           key=f"chk_{row_idx}_{col_name}"):
                selected_options.append(col_name)
            st.markdown(f'<div class="translation-card">{zh_text}</div>',
                        unsafe_allow_html=True)

    st.write("")
    col_submit, col_skip = st.columns([3, 1])
    with col_submit:
        if st.button("Submit & Next →", type="primary", use_container_width=True):
            if selected_options:
                votes[voted_key] = {
                    "choices": selected_options,
                    "choice_labels": [SOURCE_COLS[c] for c in selected_options],
                    "voter_email": voter_name,
                    "row_idx": row_idx,
                    "en_text": en_text,
                    "timestamp": str(datetime.now()),
                }
                save_votes(votes)
                voted_rows.add(str(row_idx))
                st.success("Vote recorded!")
            # Advance to next unvoted
            next_row = row_idx + 1
            for i in range(row_idx + 1, total_rows):
                if str(i) not in voted_rows:
                    next_row = i
                    break
            st.session_state._current_row = min(next_row, total_rows - 1)
            st.rerun()
    with col_skip:
        if st.button("Skip →", use_container_width=True) and row_idx < total_rows - 1:
            st.session_state._current_row = row_idx + 1
            st.rerun()



if __name__ == "__main__":
    main()
