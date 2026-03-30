import streamlit as st
import pandas as pd
from services.excel_io import load_workbook, get_transactions_df, save_workbook

st.title("Transactions")

if "workbook_path" not in st.session_state:
    st.error("Workbook not loaded.")
    st.stop()

workbook = load_workbook(st.session_state["workbook_path"])
transactions_df = get_transactions_df(workbook)

# Filters
st.sidebar.subheader("Filters")
month_filter = st.sidebar.selectbox("Month", ["All"] + sorted(transactions_df["month"].unique().tolist()) if not transactions_df.empty else ["All"])
category_filter = st.sidebar.multiselect("Category", transactions_df["category"].unique().tolist() if not transactions_df.empty else [])
merchant_filter = st.sidebar.text_input("Merchant contains")

# Apply filters
filtered_df = transactions_df.copy()
if month_filter != "All":
    filtered_df = filtered_df[filtered_df["month"] == month_filter]
if category_filter:
    filtered_df = filtered_df[filtered_df["category"].isin(category_filter)]
if merchant_filter:
    filtered_df = filtered_df[filtered_df["merchant"].str.contains(merchant_filter, case=False, na=False)]

st.dataframe(filtered_df)

# Edit functionality (simple delete for now)
if not filtered_df.empty:
    selected_indices = st.multiselect("Select transactions to delete", filtered_df.index.tolist())
    if st.button("Delete selected"):
        transactions_df = transactions_df.drop(selected_indices)
        # Update the workbook
        sheet = workbook["Transactions"]
        sheet.delete_rows(2, sheet.max_row)  # Clear existing data
        for row in transactions_df.itertuples(index=False):
            sheet.append(row)
        save_workbook(workbook, st.session_state["workbook_path"])
        st.success("Deleted selected transactions")
        st.rerun()