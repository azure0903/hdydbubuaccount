# sheets.py
import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# =====================
# gspread 클라이언트 캐시
# =====================
@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return gspread.authorize(creds)


# =====================
# 시트 열기
# =====================
def open_sheet(sheet_id):
    gc = get_gspread_client()
    return gc.open_by_key(sheet_id)


# =====================
# DataFrame 가져오기
# =====================
def get_dataframe(sheet, worksheet_name):
    try:
        ws = sheet.worksheet(worksheet_name)
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        return df
    except gspread.exceptions.WorksheetNotFound:
        st.warning(f"워크시트 '{worksheet_name}'을(를) 찾을 수 없습니다.")
        return pd.DataFrame()


# =====================
# 행 추가
# =====================
def append_row(sheet, worksheet_name, row_values):
    ws = sheet.worksheet(worksheet_name)
    ws.append_row(row_values, value_input_option="USER_ENTERED")


# =====================
# 행 수정
# =====================
def update_row(sheet, worksheet_name, row_index, row_values):
    ws = sheet.worksheet(worksheet_name)
    for col_idx, value in enumerate(row_values, start=1):
        ws.update_cell(row_index, col_idx, value)


# =====================
# 행 삭제
# =====================
def delete_row(sheet, worksheet_name, row_index):
    ws = sheet.worksheet(worksheet_name)
    ws.delete_rows(row_index)
