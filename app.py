import streamlit as st
import os
import tempfile

st.set_page_config(page_title="Spending Tracker", layout="wide")

# Upload workbook
st.sidebar.header("Workbook")
uploaded_file = st.sidebar.file_uploader("Upload spending Excel workbook", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(uploaded_file.getvalue())
        st.session_state["workbook_path"] = tmp.name
    st.sidebar.success("Workbook loaded")

    # Navigation
    pages = [
        st.Page("pages/1_Dashboard.py", title="Dashboard"),
        st.Page("pages/2_Add_Receipt.py", title="Add Receipt"),
        st.Page("pages/3_Transactions.py", title="Transactions"),
    ]

    pg = st.navigation(pages)
    pg.run()
else:
    st.info("Please upload your spending Excel workbook to begin.")
