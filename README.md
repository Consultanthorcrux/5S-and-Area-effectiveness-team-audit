# Simpolo Audit Portal

A Streamlit web interface for:

- **AET KPI audits** across Q, P, D, C and S
- **5S audits** using the supplied Simpolo checklist
- Department-wise selection for:
  - Slip House & Spray Dryer
  - Press & Glazeline
  - Kiln, Polishing & Sorting
- Automatic percentage score and A/B/C/D grade
- Audit history and CSV download

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Upload all repository contents to GitHub.
2. In Streamlit Community Cloud, select the repository.
3. Set the main file path to `app.py`.
4. Deploy.

## Scoring

Each checkpoint/category is rated from 0 to 4. The score is normalized to 100%.

- A: > 90%
- B: > 80% to 90%
- C: 60% to 80%
- D: < 60%

## Data storage note

The starter app uses SQLite (`audit_data.db`). This is convenient locally, but Streamlit Community Cloud local storage is not permanent across every restart or redeployment. For production, replace SQLite with Supabase, PostgreSQL, Google Sheets, or another persistent store.

## Source checklist

The file `data/5S Checksheet - Simpolo.xlsx` is included for reference. The app reads the cleaned checklist from `data/five_s_checklist.json`.
