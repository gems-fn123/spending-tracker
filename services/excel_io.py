import pandas as pd
import openpyxl
from datetime import datetime
import uuid
import os

def load_workbook(file_path):
    """Load the Excel workbook."""
    return openpyxl.load_workbook(file_path)

def get_transactions_df(workbook):
    """Get the Transactions sheet as a DataFrame."""
    if "Transactions" not in workbook.sheetnames:
        # Create the sheet if it doesn't exist
        sheet = workbook.create_sheet("Transactions")
        # Add headers
        headers = ["transaction_id", "date", "month", "merchant", "description", "amount", "type", "category", "subcategory", "source", "receipt_file", "receipt_text", "notes", "created_at"]
        for col, header in enumerate(headers, 1):
            sheet.cell(row=1, column=col, value=header)
        workbook.save(workbook.filename)  # Save to create the sheet
    sheet = workbook["Transactions"]
    data = list(sheet.values)
    if len(data) <= 1:
        return pd.DataFrame(columns=data[0] if data else [])
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

def get_budget_df(workbook):
    """Get the Budget Template sheet as a DataFrame."""
    if "Budget Template" not in workbook.sheetnames:
        raise ValueError("Budget Template sheet not found")
    sheet = workbook["Budget Template"]
    data = list(sheet.values)
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

def append_transaction(workbook, transaction_data):
    """Append a transaction to the Transactions sheet."""
    sheet = workbook["Transactions"]
    # Generate transaction_id if not provided
    if "transaction_id" not in transaction_data:
        transaction_data["transaction_id"] = str(uuid.uuid4())
    if "created_at" not in transaction_data:
        transaction_data["created_at"] = datetime.now()
    if "month" not in transaction_data and "date" in transaction_data:
        transaction_data["month"] = transaction_data["date"].strftime("%Y-%m") if isinstance(transaction_data["date"], datetime) else str(transaction_data["date"])[:7]

    # Headers
    headers = ["transaction_id", "date", "month", "merchant", "description", "amount", "type", "category", "subcategory", "source", "receipt_file", "receipt_text", "notes", "created_at"]
    row = [transaction_data.get(h, "") for h in headers]
    sheet.append(row)
    workbook.save(workbook.filename)

def save_workbook(workbook, file_path):
    """Save the workbook."""
    workbook.save(file_path)