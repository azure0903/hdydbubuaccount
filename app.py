import streamlit as st
from auth import login
from sheets import open_sheet, append_row, update_row, delete_row, get_dataframe
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="💒 하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

# ===============================
# 로그인
# ===============================
if not login():
    st.stop()

st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {st.session_state.user}")
st.divider()

# ===============================
# Google Sheet 연결
# ===============================
SHEET_ID = "1hLoL3lTdONsSH1OOLoGeOiRw8H8tRHNTkJT5ouPIyrc"
WORKSHEET_NAME = "Sheet1"
sheet = open_sheet(SHEET_ID)

# ===============================
# 데이터 읽기
# ===============================
try:
    df = get_dataframe(sheet, WORKSHEET_NAME)
except Exception:
    df = pd.DataFrame(columns=["기록일자","회계일자","입금","입금내역","출금","출금내역","작성자"])

# ===============================
# 총액 계산
# ===============================
total_income = df["입금"].sum() if "입금" in df.columns else 0
total_expense = df["출금"].sum() if "출금" in df.columns else 0
current_balance = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("총 입금", f"₩{total_income:,}")
col2.metric("총 출금", f"₩{total_expense:,}")
col3.metric("현재 잔액", f"₩{current_balance:,}")

st.divider()

# ===============================
# 회계 내역 입력 폼
# ===============================
st.subheader("➕ 회계 내역 입력")

with st.form("account_form"):
    col1, col2 = st.columns(2)
    with col1:
        account_date = st.date_input("회계일자", datetime.today())
        income = st.number_input("입금액", min_value=0, step=1000)
        income_desc = st.text_input("입금 내역")
    with col2:
        expense = st.number_input("출금액", min_value=0, step=1000)
        expense_desc = st.text_input("출금 내역")

    submitted = st.form_submit_button("저장")
    if submitted:
        record = [
            datetime.today().strftime("%Y-%m-%d"),
            account_date.strftime("%Y-%m-%d"),
            income,
            income_desc,
            expense,
            expense_desc,
            st.session_state.user
        ]
        append_row(sheet, WORKSHEET_NAME, record)
        st.success("회계 내역이 저장되었습니다.")
        st.experimental_rerun()

st.divider()

# ===============================
# 회계 내역 표시
# ===============================
st.subheader("📊 회계 현황")

if not df.empty:
    df_display = df.copy()
    df_display.index += 1  # 1부터 시작 (헤더 포함)
    
    # 삭제 권한 확인
    can_delete = st.session_state.user in ["도기웅", "김현주"]
    
    for idx, row in df_display.iterrows():
        st.write(f"**{idx}. {row['회계일자']}** | 입금: {row['입금']} | 출금: {row['출금']} | 작성자: {row['작성자']}")
        cols = st.columns([1,1,1])
        if can_delete:
            if cols[0].button("삭제", key=f"del_{idx}"):
                delete_row(sheet, WORKSHEET_NAME, idx+1)  # 시트는 1-based index
                st.success("해당 내역이 삭제되었습니다.")
                st.experimental_rerun()
        else:
            cols[0].write("삭제 필요 시 총무에게 요청해주세요")
