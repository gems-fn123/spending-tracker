import streamlit as st
from services.excel_io import get_default_workbook_path, load_workbook, get_transactions_df, get_budget_df
from services.insights import compute_insights

st.set_page_config(page_title="Spending Tracker", layout="wide")

def render_dashboard():
    st.title("Dashboard")

    workbook_path = get_default_workbook_path()
    workbook = load_workbook(workbook_path)
    transactions_df = get_transactions_df(workbook)
    budget_df = get_budget_df(workbook)

    insights = compute_insights(transactions_df, budget_df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Remaining Budget", f"Rp {insights['remaining_budget']:,.0f}")
    col2.metric("Total Spent This Month", f"Rp {insights['total_spent']:,.0f}")
    col3.metric(
        "Budget Used %",
        f"{(insights['total_spent'] / insights['total_budget'] * 100):.1f}%"
        if insights["total_budget"] > 0
        else "N/A",
    )

    st.subheader("Biggest Spending Category")
    if insights["biggest_by_amount"]:
        st.metric(f"By Amount: {insights['biggest_by_amount']}", f"Rp {insights['biggest_amount']:,.0f}")
    if insights["biggest_by_pct"]:
        st.metric(f"By % of Spend: {insights['biggest_by_pct']}", f"{insights['biggest_pct'] * 100:.1f}%")

    st.subheader("Categories at Risk")
    if insights["at_risk_categories"]:
        st.write(", ".join(insights["at_risk_categories"]))
    else:
        st.write("None")

    st.subheader("Projected Month-End Remaining Budget")
    st.metric("Projected Remaining", f"Rp {insights['projected_remaining']:,.0f}")

    st.subheader("Top Merchants")
    st.table(insights["top_merchants"])

    st.subheader("Largest Recent Transactions")
    st.table(insights["largest_recent"])


pages = [
    st.Page(render_dashboard, title="Dashboard", default=True),
    st.Page("pages/2_Add_Receipt.py", title="Add Receipt"),
    st.Page("pages/3_Transactions.py", title="Transactions"),
]

pg = st.navigation(pages)
pg.run()
