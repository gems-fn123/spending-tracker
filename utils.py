import pandas as pd
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


def detect_columns(raw_columns):
    lower = [str(c).strip().lower() for c in raw_columns]

    find = lambda keys: next((raw_columns[i] for i, c in enumerate(lower) if any(k in c for k in keys)), None)

    return {
        "date": find(["date"]),
        "amount": find(["amount", "amt", "debit", "credit"]),
        "category": find(["category", "cat"]),
        "merchant": find(["description", "merchant", "details", "payee"]),
        "account": find(["account", "acct", "payment"]),
        "notes": find(["note"]),
    }


def parse_transactions(df, col_map, amount_sign_mode):
    df = df.copy()

    df["_date"] = pd.to_datetime(df[col_map["date"]], errors="coerce")
    df["_amount"] = pd.to_numeric(df[col_map["amount"]], errors="coerce")

    df["_category"] = df[col_map.get("category")].fillna("Uncategorized").astype(str) if col_map.get("category") in df.columns else "Uncategorized"
    df["_merchant"] = df[col_map.get("merchant")].fillna("Unknown").astype(str) if col_map.get("merchant") in df.columns else "Unknown"
    df["_account"] = df[col_map.get("account")].fillna("Unknown").astype(str) if col_map.get("account") in df.columns else "Unknown"
    df["_notes"] = df[col_map.get("notes")].fillna("").astype(str) if col_map.get("notes") in df.columns else ""

    if amount_sign_mode.startswith("expenses negative"):
        df["_expense"] = df["_amount"].apply(lambda x: x if x < 0 else 0)
        df["_income"] = df["_amount"].apply(lambda x: x if x > 0 else 0)
    else:
        df["_expense"] = df["_amount"].apply(lambda x: x if x > 0 else 0)
        df["_income"] = df["_amount"].apply(lambda x: x if x < 0 else 0)

    df["_net"] = df["_income"] + df["_expense"] if amount_sign_mode.startswith("expenses negative") else df["_income"] - df["_expense"]
    df["_year_month"] = df["_date"].dt.to_period("M").astype(str)
    return df


def build_drive_service(service_account_info):
    credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/drive"])
    return build("drive", "v3", credentials=credentials)


def upload_bytes_to_drive(service, file_bytes, filename, folder_id=None, mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
    media = MediaIoBaseUpload(BytesIO(file_bytes), mimetype=mime_type, resumable=True)
    file_metadata = {"name": filename}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    file = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()
    return file
