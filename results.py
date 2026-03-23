"""
Results Viewer — run separately: streamlit run results.py
Shows full voting results broken down by system, voter, and line.
"""

import streamlit as st
import pandas as pd
from sheets import load_votes

SOURCE_COLS = {
    # "zh_opus": "OPUS",
    "zh_nllb": "NLLB",
    "zh_claude": "Claude",
    "zh_deepseek": "DeepSeek",
}

st.set_page_config(page_title="Results", page_icon="📊", layout="wide")
st.title("📊 Translation Voting — Results")

if st.button("Refresh"):
    load_votes.clear()
    st.rerun()

votes = load_votes()

if not votes:
    st.warning("No votes recorded yet.")
    st.stop()

# Build a flat dataframe — one row per voter+line+system chosen
records = []
for key, v in votes.items():
    voter, row_idx = key.split("|", 1)
    choices = v.get("choices") or ([v["choice"]] if v.get("choice") else [])
    labels = v.get("choice_labels") or [SOURCE_COLS.get(c, c) for c in choices]
    for col, label in zip(choices, labels):
        records.append({
            "voter_email": v.get("voter_email", voter),
            "row_idx": int(row_idx),
            "en_text": v.get("en_text", ""),
            "choice_col": col,
            "system": label,
            "voted_at": v.get("timestamp", ""),
        })

df = pd.DataFrame(records).sort_values(["row_idx", "voter_email"])

# ── Overall leaderboard ────────────────────────────────────────────────────────
st.header("Overall leaderboard")
counts = df["system"].value_counts().reset_index()
counts.columns = ["System", "Votes"]
counts["Share"] = (counts["Votes"] / counts["Votes"].sum() * 100).round(1).astype(str) + "%"
st.dataframe(counts, hide_index=True, use_container_width=True)

# ── Votes per voter ────────────────────────────────────────────────────────────
st.header("Votes by voter")
voter_counts = df.groupby(["voter_email", "system"]).size().unstack(fill_value=0)
st.dataframe(voter_counts, use_container_width=True)

# ── Per-line breakdown ─────────────────────────────────────────────────────────
st.header("Per-line breakdown")
line_pivot = df.pivot_table(index=["row_idx", "en_text"], columns="system",
                             aggfunc="size", fill_value=0).reset_index()
st.dataframe(line_pivot, hide_index=True, use_container_width=True)

# ── Raw votes table ────────────────────────────────────────────────────────────
with st.expander("Raw votes"):
    st.dataframe(df, hide_index=True, use_container_width=True)
