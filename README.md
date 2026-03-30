# Spending Tracker (Streamlit)

A personal finance dashboard using an Excel file as the main source of truth, implemented with Streamlit for easy GitHub-based version control and deployment.

## Features
- Excel upload and sheet/column detection
- Data normalization: date, amount, category, merchant, account
- KPI cards: total income, total expenses, net cash flow
- Spending by category, monthly trend, top merchants, largest transactions
- Recurring payment detection heuristic
- Budget vs actual comparison (optional CSV upload)
- Filters by date, category, merchant, account
- Export filtered data to CSV/Excel

## Quick start
1. Clone repository
2. Create virtual env: `python -m venv venv && source venv/bin/activate`
3. Install deps: `pip install -r requirements.txt`
4. Run: `streamlit run app.py`
5. Upload your Excel workbook and choose the sheet and columns

## Google Drive integration (optional)
1. Create a Google Cloud project, enable Google Drive API
2. Create service account and download JSON key
3. Share target Drive folder with service account email
4. In Streamlit, choose Drive backup and provide JSON credentials or set `gcp_service_account` in `st.secrets`
5. Optionally set `gdrive_folder_id` (Drive folder ID) in sidebar for organized backups

## Optional password protection
1. Create `.streamlit/secrets.toml` with:

```toml
auth = { enabled = true, password = "your-secret-password" }
gcp_service_account = { ...your JSON contents... }
```

2. On Streamlit Cloud, set the same under App settings > Secrets.

## Deployment
- GitHub + Streamlit Cloud (free tier): link to repo, add `requirements.txt`, set `streamlit run app.py`
- Alternatives: Railway, Heroku

## Notes
- The app assumes expenses and incomes are recognized by sign convention: choose in sidebar.
- If categories are inconsistent, you can normalize in Excel or map in code.
- Budget file format: columns `Category`, `BudgetAmount`.
