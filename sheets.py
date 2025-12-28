import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

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

def get_dataframe(sheet, worksheet_name="Sheet1"):
    ws = sheet.worksheet(worksheet_name)
    data = ws.get_all_records()
    return pd.DataFrame(data)

def append_row(sheet, row, worksheet_name="Sheet1"):
    ws = sheet.worksheet(worksheet_name)
    ws.append_row(row)

def update_row(sheet, row_index, row_data, worksheet_name="Sheet1"):
    ws = sheet.worksheet(worksheet_name)
    ws.update(f"A{row_index+2}:G{row_index+2}", [row_data])  # 헤더 제외

def delete_row(sheet, row_index, worksheet_name="Sheet1"):
    ws = sheet.worksheet(worksheet_name)
    ws.delete_rows(row_index+2)
