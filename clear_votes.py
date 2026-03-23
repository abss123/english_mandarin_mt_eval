"""
Clear all votes — run with: python clear_votes.py
Prompts for confirmation before deleting.
"""

import os
import json

VOTES_FILE = "votes.json"

if not os.path.exists(VOTES_FILE):
    print("No votes file found. Nothing to clear.")
else:
    with open(VOTES_FILE) as f:
        votes = json.load(f)
    print(f"Found {len(votes)} vote(s) in {VOTES_FILE}.")
    confirm = input("Type 'yes' to permanently delete all votes: ").strip().lower()
    if confirm == "yes":
        os.remove(VOTES_FILE)
        print("All votes cleared.")
    else:
        print("Aborted. No votes were deleted.")
