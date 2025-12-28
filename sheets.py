import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# ======================
# Google Sheets Client
# ======================
@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    return gspread.authorize(creds)


# ======================
# Spreadsheet Open
# ======================
def open_sheet_by_id(sheet_id):
    gc = get_gspread_client()
    return gc.open_by_key(sheet_id)


def get_worksheet(sheet_id, index=0):
    sh = open_sheet_by_id(sheet_id)
    return sh.get_worksheet(index)


# ======================
# Read
# ======================
def load_account_df(sheet_id):
    ws = get_worksheet(sheet_id)
    records = ws.get_all_records()

    if not records:
        return pd.DataFrame(columns=[
            "기록일자", "회계일자",
            "입금", "입금내역",
            "출금", "출금내역",
            "작성자"
        ])

    return pd.DataFrame(records)


# ======================
# Append
# ======================
def append_account_row(
    sheet_id,
    accounting_date,
    income,
    income_desc,
    expense,
    expense_desc,
    writer
):
    ws = get_worksheet(sheet_id)

    ws.append_row([
        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),  # 기록일자
        accounting_date.strftime("%Y-%m-%d"),             # 회계일자
        income,
        income_desc,
        expense,
        expense_desc,
        writer
    ])


# ======================
# Update
# ======================
def update_account_row(sheet_id, row_index, row_data: list):
    """
    row_index: DataFrame 기준 index (0부터)
    """
    ws = get_worksheet(sheet_id)
    ws.update(f"A{row_index + 2}:G{row_index + 2}", [row_data])


# ======================
# Delete
# ======================
def delete_account_row(sheet_id, row_index):
    ws = get_worksheet(sheet_id)
    ws.delete_rows(row_index + 2)
