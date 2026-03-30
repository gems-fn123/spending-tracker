import pandas as pd
from datetime import datetime

def compute_insights(transactions_df, budget_df):
    """Compute dashboard insights from transactions and budget."""
    # Assuming transactions_df has columns: date, amount, category, etc.
    # Assuming budget_df has Category and BudgetAmount

    # Filter to current month
    current_month = datetime.now().strftime("%Y-%m")
    monthly_tx = transactions_df[transactions_df["month"] == current_month]

    # Total spent this month
    total_spent = monthly_tx["amount"].sum()

    # Spend by category
    spend_by_category = monthly_tx.groupby("category")["amount"].sum()

    # Budget totals
    total_budget = budget_df["BudgetAmount"].sum()

    # Remaining budget
    remaining_budget = total_budget - total_spent

    # Biggest spending category by amount
    if not spend_by_category.empty:
        biggest_by_amount = spend_by_category.idxmax()
        biggest_amount = spend_by_category.max()
    else:
        biggest_by_amount = None
        biggest_amount = 0

    # Biggest by percentage
    if not spend_by_category.empty:
        pct_spend = spend_by_category / spend_by_category.sum()
        biggest_by_pct = pct_spend.idxmax()
        biggest_pct = pct_spend.max()
    else:
        biggest_by_pct = None
        biggest_pct = 0

    # Categories at risk (budget used >= 90%)
    budget_used_pct = {}
    for cat in budget_df["Category"]:
        budget = budget_df[budget_df["Category"] == cat]["BudgetAmount"].iloc[0] if not budget_df[budget_df["Category"] == cat].empty else 0
        spent = spend_by_category.get(cat, 0)
        if budget > 0:
            budget_used_pct[cat] = spent / budget

    at_risk = [cat for cat, pct in budget_used_pct.items() if pct >= 0.9]

    # Projected month-end remaining (assuming linear burn rate)
    days_in_month = (datetime.now().replace(day=28) + pd.Timedelta(days=4)).replace(day=1) - pd.Timedelta(days=1)
    days_passed = datetime.now().day
    daily_burn = total_spent / days_passed if days_passed > 0 else 0
    projected_spend = daily_burn * days_in_month.day
    projected_remaining = total_budget - projected_spend

    # Top merchants
    top_merchants = monthly_tx.groupby("merchant")["amount"].sum().sort_values(ascending=False).head(5)

    # Largest recent transactions
    largest_recent = monthly_tx.sort_values("amount", ascending=False).head(5)

    return {
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining_budget": remaining_budget,
        "biggest_by_amount": biggest_by_amount,
        "biggest_amount": biggest_amount,
        "biggest_by_pct": biggest_by_pct,
        "biggest_pct": biggest_pct,
        "at_risk_categories": at_risk,
        "projected_remaining": projected_remaining,
        "top_merchants": top_merchants,
        "largest_recent": largest_recent,
    }