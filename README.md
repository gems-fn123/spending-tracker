# Spending Tracker (Streamlit)

A personal finance dashboard with OCR receipt processing, using an Excel workbook as the source of truth. Implemented with Streamlit for multi-page navigation, easy deployment, and receipt scanning.

## Features
- **Dashboard**: Budget tracking, spending insights, top merchants, largest transactions
- **Add Receipt**: Upload or camera capture receipts, OCR with PaddleOCR, parse merchant/date/amount, review and confirm transactions
- **Transactions**: View, filter, and edit transactions from the normalized Transactions sheet
- Excel workbook with Transactions sheet for data storage
- Category auto-suggestion based on merchant patterns
- Google Drive integration for backups

## Quick start
1. Clone repository
2. Create virtual env: `python -m venv venv && source venv/bin/activate`
3. Install deps: `pip install -r requirements.txt`
4. Run: `streamlit run app.py`
5. Upload your Excel workbook (ensure it has "Budget Template" and "Transactions" sheets)

## Workbook Structure
- **Budget Template**: Categories and budget amounts
- **Transactions**: Normalized transaction data (added automatically if missing)
- **Maret 2026**: Optional presentation sheet

## OCR Setup
- Uses PaddleOCR for receipt text extraction
- Preprocessing with OpenCV for better accuracy
- Parser extracts merchant, date, amount
- Review form before saving to avoid errors

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
- GitHub + Streamlit Community Cloud (free tier): link to repo, add `requirements.txt` and `packages.txt`, set `streamlit run app.py`
- Alternatives: Railway, Heroku

## Notes
- Start with one receipt = one transaction for simplicity
- Categories defined in `config/categories.yml`
- Merchant rules in `config/merchant_rules.yml` for auto-suggestion
