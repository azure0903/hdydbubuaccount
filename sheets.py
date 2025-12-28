import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime


# =========================
# Google Sheets 연결
# =========================
@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return gspread.authorize(creds)


def open_sheet(sheet_name: str, worksheet_name: str = "Sheet1"):
    """
    Google Spreadsheet / Worksheet 열기
    """
    gc = get_gspread_client()
    sh = gc.open(sheet_name)
    return sh.worksheet(worksheet_name)


# =========================
# 데이터 구조
# =========================
COLUMNS = [
    "기록일자",
    "회계일자",
    "입금",
    "입금내역",
    "출금",
    "출금내역",
    "작성자"
]


# =========================
# 초기 시트 세팅
# =========================
def ensure_header(ws):
    """
    시트가 비어있으면 헤더 자동 생성
    """
    if ws.row_count == 0 or ws.cell(1, 1).value != COLUMNS[0]:
        ws.insert_row(COLUMNS, index=1)


# =========================
# 회계 데이터 추가
# =========================
def append_account_row(
    ws,
    account_date,
    income,
    income_desc,
    expense,
    expense_desc,
    writer
):
    ensure_header(ws)

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 기록일자
        account_date.strftime("%Y-%m-%d"),             # 회계일자
        income if income > 0 else "",
        income_desc,
        expense if expense > 0 else "",
        expense_desc,
        writer
    ]

    ws.append_row(row, value_input_option="USER_ENTERED")


# =========================
# 전체 회계 데이터 조회
# =========================
def load_account_dataframe(ws) -> pd.DataFrame:
    records = ws.get_all_records()

    if not records:
        return pd.DataFrame(columns=COLUMNS)

    df = pd.DataFrame(records)

    # 숫자 컬럼 정리
    df["입금"] = pd.to_numeric(df["입금"], errors="coerce").fillna(0)
    df["출금"] = pd.to_numeric(df["출금"], errors="coerce").fillna(0)

    return df


# =========================
# 합계 계산
# =========================
def calculate_summary(df: pd.DataFrame):
    total_income = int(df["입금"].sum())
    total_expense = int(df["출금"].sum())
    balance = total_income - total_expense

    return total_income, total_expense, balance
