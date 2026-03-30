import streamlit as st
from services.excel_io import get_default_workbook_path, get_transactions_df, load_workbook, replace_transactions

st.title("Transactions")

workbook = load_workbook(get_default_workbook_path())
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
        replace_transactions(workbook, transactions_df)
        st.success("Deleted selected transactions")
        st.rerun()
