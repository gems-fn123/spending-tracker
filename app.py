import os
import json
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime

from utils import detect_columns, parse_transactions, build_drive_service, upload_bytes_to_drive

st.set_page_config(page_title="Spending Tracker Dashboard", layout="wide")

# --- optional access control ---
auth_config = st.secrets.get("auth", {}) if hasattr(st, "secrets") else {}
if auth_config.get("enabled", False):
    st.sidebar.header("Security")
    auth_password = st.sidebar.text_input("Enter app access code", type="password")
    if auth_password != auth_config.get("password", ""):
        st.warning("Access code is required. Set secrets.auth.password in Streamlit Cloud or .streamlit/secrets.toml.")
        st.stop()

st.title("Spending Tracker Dashboard")

st.sidebar.header("Data source")
uploaded_file = st.sidebar.file_uploader("Upload spending Excel workbook", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("Please upload an Excel file to begin. Typical columns: Date, Amount, Category, Description, Account.")
    st.stop()

try:
    xls = pd.ExcelFile(uploaded_file)
except Exception as e:
    st.error(f"Could not read the file: {e}")
    st.stop()

sheets = xls.sheet_names
sheet = st.sidebar.selectbox("Select sheet", sheets)

raw = pd.read_excel(xls, sheet_name=sheet)
raw_columns = list(raw.columns)

st.sidebar.subheader("Column mapping (auto-detected)")
st.sidebar.write(raw_columns)

col_guesses = detect_columns(raw_columns)

col_date = st.sidebar.selectbox("Date column", [None] + raw_columns, index=(raw_columns.index(col_guesses.get("date")) + 1) if col_guesses.get("date") in raw_columns else 0)
col_amount = st.sidebar.selectbox("Amount column", [None] + raw_columns, index=(raw_columns.index(col_guesses.get("amount")) + 1) if col_guesses.get("amount") in raw_columns else 0)
col_category = st.sidebar.selectbox("Category column", [None] + raw_columns, index=(raw_columns.index(col_guesses.get("category")) + 1) if col_guesses.get("category") in raw_columns else 0)
col_desc = st.sidebar.selectbox("Description/Merchant column", [None] + raw_columns, index=(raw_columns.index(col_guesses.get("merchant")) + 1) if col_guesses.get("merchant") in raw_columns else 0)
col_account = st.sidebar.selectbox("Account column", [None] + raw_columns, index=(raw_columns.index(col_guesses.get("account")) + 1) if col_guesses.get("account") in raw_columns else 0)
col_notes = st.sidebar.selectbox("Notes column", [None] + raw_columns, index=(raw_columns.index(col_guesses.get("notes")) + 1) if col_guesses.get("notes") in raw_columns else 0)

if col_date is None or col_amount is None:
    st.error("You must select Date and Amount columns to continue.")
    st.stop()

# --- preprocessing ---
amount_sign_mode = st.sidebar.radio("Amount sign convention", ["expenses negative (typical accounting)", "expenses positive"], index=0)

col_map = {"date": col_date, "amount": col_amount}
if col_category is not None:
    col_map["category"] = col_category
if col_desc is not None:
    col_map["merchant"] = col_desc
if col_account is not None:
    col_map["account"] = col_account
if col_notes is not None:
    col_map["notes"] = col_notes

try:
    df = parse_transactions(raw, col_map, amount_sign_mode)
except Exception as e:
    st.error(f"Data parsing failed: {e}")
    st.stop()

st.sidebar.subheader("Google Drive integration")
service_account_info = None
folder_id = None

if st.sidebar.checkbox("Enable Google Drive backup", value=False):
    gdrive_mode = st.sidebar.radio("Drive credentials source", ["From st.secrets", "Upload JSON file"], index=0)
    if gdrive_mode == "From st.secrets":
        service_account_info = st.secrets.get("gcp_service_account") if hasattr(st, "secrets") else None
        if not service_account_info:
            st.sidebar.warning("Add gcp_service_account in Streamlit secrets.")
    else:
        json_file = st.sidebar.file_uploader("Upload Service Account JSON", type=["json"])
        if json_file is not None:
            service_account_info = json.load(json_file)

    folder_id = st.sidebar.text_input("Google Drive folder ID (optional)")

    if service_account_info:
        try:
            drive_service = build_drive_service(service_account_info)
            st.sidebar.success("Drive service initialized")
        except Exception as e:
            st.sidebar.error(f"Couldn't initialize Drive service: {e}")
            drive_service = None
    else:
        drive_service = None
else:
    drive_service = None

# --- filtering ---
st.sidebar.subheader("Filters")
with st.sidebar.expander("Date & categories"):
    min_date = df["_date"].min()
    max_date = df["_date"].max()
    date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    category_options = sorted(df["_category"].dropna().unique())
    selected_categories = st.multiselect("Categories", category_options, default=category_options)

    merchant_options = sorted(df["_merchant"].dropna().unique())
    selected_merchants = st.multiselect("Merchants", merchant_options, default=merchant_options)

    account_options = sorted(df["_account"].dropna().unique())
    selected_accounts = st.multiselect("Accounts", account_options, default=account_options)

    show_incomes = st.checkbox("Include incomes", value=True)
    show_expenses = st.checkbox("Include expenses", value=True)

mask = (df["_date"] >= pd.to_datetime(date_range[0])) & (df["_date"] <= pd.to_datetime(date_range[1]))
mask &= df["_category"].isin(selected_categories)
mask &= df["_merchant"].isin(selected_merchants)
mask &= df["_account"].isin(selected_accounts)
if not show_incomes:
    mask &= df["_income"] == 0
if not show_expenses:
    mask &= df["_expense"] == 0

df_f = df.loc[mask].copy()

# --- summaries ---
if amount_sign_mode.startswith("expenses negative"):
    total_income = df_f["_income"].sum()
    total_expense = -df_f["_expense"].sum()
else:
    total_income = df_f["_income"].sum()
    total_expense = df_f["_expense"].sum()
net_cash = total_income - total_expense

st.subheader("Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"{total_income:,.2f}")
col2.metric("Total Expense", f"{total_expense:,.2f}")
col3.metric("Net Cash Flow", f"{net_cash:,.2f}")

cat_summary = df_f.groupby("_category").agg(
    expense=("_expense", lambda x: -x.sum() if amount_sign_mode.startswith("expenses negative") else x.sum()),
    income=("_income", "sum"),
)
cat_summary["net"] = cat_summary["income"] - cat_summary["expense"]
cat_summary = cat_summary.sort_values("expense", ascending=False)

st.subheader("Spending by Category")
st.bar_chart(cat_summary["expense"].head(10))

monthly = df_f.groupby("_year_month").agg(income=('_income', 'sum'), expense=('_expense', 'sum'))
if amount_sign_mode.startswith("expenses negative"):
    monthly['expense'] = -monthly['expense']
monthly['net'] = monthly['income'] - monthly['expense']

st.subheader("Monthly Trend")
st.line_chart(monthly[["income", "expense", "net"]])

merchant_summary = df_f.groupby("_merchant").agg(
    total=("_amount", lambda x: -x[x < 0].sum() if amount_sign_mode.startswith("expenses negative") else x[x > 0].sum()),
    transactions=("_amount", "count"),
).sort_values("total", ascending=False).head(10)

st.subheader("Top Merchants")
st.table(merchant_summary)

st.subheader("Largest Transactions")
largest_tx = df_f.assign(abs_amount=df_f["_amount"].abs()).sort_values("abs_amount", ascending=False).head(15)
st.write(largest_tx[[col_date, col_amount, "_category", "_merchant", "_account", "_notes"]])

st.subheader("Recurring / Subscription Candidates")
recurrence = df_f.copy()
recurrence["_month_day"] = recurrence["_date"].dt.day
flagged = recurrence.groupby(["_merchant", "_category"]).agg(
    n_transactions=("_amount", "count"),
    avg_amount=("_amount", "mean"),
    std_amount=("_amount", "std"),
).query("n_transactions >= 3").sort_values("n_transactions", ascending=False)
st.write(flagged.head(20))

st.subheader("Budget vs Actual")
if st.sidebar.checkbox("Enable budget comparison", value=False):
    budget_csv = st.sidebar.file_uploader("Upload budget CSV (columns: Category, BudgetAmount)", type=["csv"])
    if budget_csv is not None:
        budget_df = pd.read_csv(budget_csv)
        if "Category" in budget_df.columns and "BudgetAmount" in budget_df.columns:
            merged = budget_df.merge(cat_summary.reset_index().rename(columns={"_category": "Category", "expense": "Actual"}), how="left", left_on="Category", right_on="_category")
            merged["Actual"] = merged["Actual"].fillna(0)
            merged["Variance"] = merged["BudgetAmount"] - merged["Actual"]
            st.table(merged[["Category", "BudgetAmount", "Actual", "Variance"]])
        else:
            st.warning("Budget file must contain Category and BudgetAmount columns")

with st.expander("Filtered transactions"):
    st.write(df_f.sort_values("_date", ascending=False).head(100))

with st.expander("Export data"):
    st.download_button("Download filtered data as CSV", data=df_f.to_csv(index=False).encode("utf-8"), file_name="spending_filtered.csv", mime="text/csv")

    towrite = BytesIO()
    df_f.to_excel(towrite, index=False, engine="openpyxl")
    towrite.seek(0)
    st.download_button("Download filtered data as Excel", data=towrite.getvalue(), file_name="spending_filtered.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if drive_service is not None:
        if st.button("Upload filtered Excel to Google Drive"):
            try:
                xls_bytes = towrite.getvalue()
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"spending_filtered_{now}.xlsx"
                saved = upload_bytes_to_drive(drive_service, xls_bytes, filename, folder_id or None)
                st.success(f"Saved to Google Drive: {saved.get('webViewLink', saved.get('id'))}")
            except Exception as ex:
                st.error(f"Drive upload failed: {ex}")

st.markdown("---")
st.caption("Assumptions: date + amount must be mapped; amount sign convention selected; drive upload requires service account credentials and folder access.")
