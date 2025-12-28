import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# =========================
# 구글 시트 클라이언트
# =========================
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

# =========================
# 데이터 가져오기
# =========================
def get_dataframe(sheet, worksheet_name="Sheet1"):
    ws = sheet.worksheet(worksheet_name)
    data = ws.get_all_records()
    df = pd.DataFrame(data)
    return df

# =========================
# 행 추가
# =========================
def append_row(sheet, account_date, income, expense, desc, writer, worksheet_name="Sheet1"):
    ws = sheet.worksheet(worksheet_name)
    ws.append_row([str(account_date), income, expense, desc, writer])

# =========================
# 행 수정
# row_index는 시트 기준 (1부터 시작, 헤더 포함)
# =========================
def update_row(sheet, row_index, income, expense, desc, worksheet_name="Sheet1"):
    ws = sheet.worksheet(worksheet_name)
    ws.update(f'B{row_index}', income)
    ws.update(f'C{row_index}', expense)
    ws.update(f'D{row_index}', desc)

# =========================
# 행 삭제
# row_index는 시트 기준 (1부터 시작, 헤더 포함)
# =========================
def delete_row(sheet, row_index, worksheet_name="Sheet1"):
    ws = sheet.worksheet(worksheet_name)
    ws.delete_rows(row_index)
