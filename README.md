# Translation Quality Voting Dashboard

Blind evaluation tool for comparing EN→ZH translations from different systems.
Translations are shown in randomized order to avoid bias.

## Features
- **Blind evaluation**: translations shown as "Option A/B/C/D" in random order
- **Per-voter tracking**: each teammate's progress is tracked separately
- **Reveal after voting**: see which system produced each translation
- **Live results**: sidebar shows overall vote counts across all voters
- **Auto-advance**: after voting, jumps to next unvoted line

## Local Testing

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud (Free)

1. **Create a GitHub repo** and push these files:
   ```
   your-repo/
   ├── app.py
   ├── requirements.txt
   └── translations.csv       ← replace with your full data
   ```

2. Go to **[share.streamlit.io](https://share.streamlit.io)**

3. Click **"New app"** → select your GitHub repo → pick `app.py`

4. Click **Deploy**. You'll get a URL like: `https://your-app.streamlit.app`

5. Share the URL with teammates. Done!

## Data Format

Your `translations.csv` should have these columns:

| Column | Description |
|--------|-------------|
| `index` | Row number |
| `timestamp` | SRT timestamp (optional) |
| `en_text` | English source text |
| `zh_opus` | OPUS translation |
| `zh_nllb` | NLLB translation |
| `zh_claude` | Claude translation |
| `zh_deepseek` | DeepSeek translation |

To add/remove translation systems, edit the `SOURCE_COLS` dict in `app.py`.

## Notes on Vote Storage

Votes are stored in `votes.json` in the app directory. On Streamlit Cloud,
this file resets when the app restarts (which happens after inactivity).

For persistent storage, you could swap in Google Sheets as a backend:
```bash
pip install gspread
```
But for a quick evaluation session with teammates, the default file
storage works fine — just do your voting in one session.
