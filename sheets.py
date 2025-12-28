import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# ======================
# gspread 클라이언트 생성 (캐시)
# ======================
@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return gspread.authorize(creds)

# ======================
# 스프레드시트 열기
# ======================
def open_sheet(sheet_id):
    gc = get_gspread_client()
    return gc.open_by_key(sheet_id)

# ======================
# 시트를 DataFrame으로 변환
# ======================
def get_dataframe(sheet, worksheet_name):
    ws = sheet.worksheet(worksheet_name)
    data = ws.get_all_records()
    df = pd.DataFrame(data)
    return df

# ======================
# 행 추가
# ======================
def append_row(sheet, record_date, account_date, income, income_desc, expense, expense_desc, author):
    ws = sheet.worksheet("Sheet1")
    ws.append_row([
        record_date,
        account_date,
        income,
        income_desc,
        expense,
        expense_desc,
        author
    ])

# ======================
# 행 수정
# row_number: 시트 기준 행 번호 (헤더 포함)
# ======================
def update_row(sheet, row_number, new_income, new_income_desc, new_expense, new_expense_desc):
    ws = sheet.worksheet("Sheet1")
    ws.update(f"C{row_number}", new_income)        # 입금
    ws.update(f"D{row_number}", new_income_desc)   # 입금 내역
    ws.update(f"E{row_number}", new_expense)       # 출금
    ws.update(f"F{row_number}", new_expense_desc)  # 출금 내역

# ======================
# 행 삭제
# ======================
def delete_row(sheet, row_number):
    ws = sheet.worksheet("Sheet1")
    ws.delete_rows(row_number)
