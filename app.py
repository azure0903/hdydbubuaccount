import streamlit as st
import pandas as pd
from auth import login
from sheets import open_sheet, append_row, update_row, delete_row, get_dataframe

# =========================
# 환경 설정
# =========================
st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

SHEET_ID = "1hLoL3lTdONsSH1OOLoGeOiRw8H8tRHNTkJT5ouPIyrc"
WORKSHEET_NAME = "Sheet1"

# 삭제 권한 사용자
delete_allowed_users = ["도기웅", "김현주"]

# =========================
# 로그인
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

if not login():
    st.stop()

# =========================
# 구글 시트 불러오기
# =========================
sheet = open_sheet(SHEET_ID)
df = get_dataframe(sheet, WORKSHEET_NAME)

# 컬럼 이름 확인 및 초기화
expected_cols = ["회계일자", "입금", "출금", "내역", "작성자"]
for col in expected_cols:
    if col not in df.columns:
        df[col] = ""

# =========================
# 상단 통계
# =========================
total_income = df['입금'].sum()
total_expense = df['출금'].sum()
total_balance = total_income - total_expense

st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {st.session_state.user}")

st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("총 입금", f"₩{total_income:,}")
col2.metric("총 출금", f"₩{total_expense:,}")
col3.metric("잔액", f"₩{total_balance:,}")
st.divider()

# =========================
# 회계 내역 입력
# =========================
st.subheader("➕ 회계 내역 입력")
with st.form("account_form"):
    col1, col2 = st.columns(2)
    with col1:
        account_date = st.date_input("회계일자")
        income = st.number_input("입금액", min_value=0, step=1000)
        income_desc = st.text_input("입금 내역")
    with col2:
        expense = st.number_input("출금액", min_value=0, step=1000)
        expense_desc = st.text_input("출금 내역")
    
    submitted = st.form_submit_button("저장")
    if submitted:
        append_row(sheet, account_date, income, expense, income_desc or expense_desc, st.session_state.user)
        st.success("회계 내역이 저장되었습니다.")
        st.experimental_rerun()  # 저장 후 새로고침

st.divider()

# =========================
# 회계 내역 수정 / 삭제
# =========================
st.subheader("📝 회계 내역 수정 / 삭제")

# 데이터 표시용 컬럼 추가
df['display'] = df.apply(
    lambda x: f"날짜:{x['회계일자']} | 입금:{x['입금']} | 출금:{x['출금']} | 작성자:{x['작성자']}", axis=1
)

selected_idx = st.selectbox(
    "대상 선택",
    options=df.index,
    format_func=lambda x: df.loc[x, 'display']
)

selected_row = df.loc[selected_idx]

with st.expander("수정 / 삭제"):
    new_income = st.number_input("입금액", value=int(selected_row['입금']), step=1000)
    new_expense = st.number_input("출금액", value=int(selected_row['출금']), step=1000)
    new_desc = st.text_input("내역", value=selected_row['내역'])

    if st.button("수정"):
        update_row(sheet, selected_idx + 2, new_income, new_expense, new_desc)
        st.success("수정 완료!")
        st.experimental_rerun()

    if st.session_state.user in delete_allowed_users:
        if st.button("삭제"):
            delete_row(sheet, selected_idx + 2)
            st.success("삭제 완료!")
            st.experimental_rerun()
    else:
        st.info("삭제가 필요할 경우 총무에게 요청해주세요.")
