import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# ===============================
# Google Sheets 연결
# ===============================
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

# ===============================
# CRUD 함수
# ===============================

def append_row(sheet, worksheet_name, row_values):
    ws = sheet.worksheet(worksheet_name)
    ws.append_row(row_values)

def update_row(sheet, worksheet_name, row_index, row_values):
    ws = sheet.worksheet(worksheet_name)
    for col_index, value in enumerate(row_values, start=1):
        ws.update_cell(row_index, col_index, value)

def delete_row(sheet, worksheet_name, row_index):
    ws = sheet.worksheet(worksheet_name)
    ws.delete_row(row_index)

def get_dataframe(sheet, worksheet_name):
    ws = sheet.worksheet(worksheet_name)
    data = ws.get_all_records()
    df = pd.DataFrame(data)
    return df
