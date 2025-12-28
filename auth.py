import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

WORKSHEET_NAME = "Sheet1"

@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return gspread.authorize(creds)

def open_sheet(sheet_id):
    gc = get_gspread_client()
    return gc.open_by_key(sheet_id)

def get_dataframe(sheet, worksheet_name=WORKSHEET_NAME):
    ws = sheet.worksheet(worksheet_name)
    data = ws.get_all_records()
    return pd.DataFrame(data)

def append_row(sheet, account_date, income, expense, desc, writer, worksheet_name=WORKSHEET_NAME):
    ws = sheet.worksheet(worksheet_name)
    ws.append_row([str(account_date), income, expense, desc, writer])

def update_row(sheet, row_idx, account_date, income, expense, desc, writer, worksheet_name=WORKSHEET_NAME):
    ws = sheet.worksheet(worksheet_name)
    ws.update(f"A{row_idx}", str(account_date))
    ws.update(f"B{row_idx}", income)
    ws.update(f"C{row_idx}", expense)
    ws.update(f"D{row_idx}", desc)
    ws.update(f"E{row_idx}", writer)

def delete_row(sheet, row_idx, worksheet_name=WORKSHEET_NAME):
    ws = sheet.worksheet(worksheet_name)
    ws.delete_rows(row_idx)
