import streamlit as st
from auth import login
from sheets import open_sheet, get_dataframe, append_row, update_row, delete_row
import pandas as pd

SHEET_ID = "1hLoL3lTdONsSH1OOLoGeOiRw8H8tRHNTkJT5ouPIyrc"
WORKSHEET_NAME = "Sheet1"

st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

if not login():
    st.stop()

sheet = open_sheet(SHEET_ID)
df = get_dataframe(sheet, WORKSHEET_NAME)

# =======================
# 총액 표시
# =======================
total_income = df['입금'].sum() if not df.empty else 0
total_expense = df['출금'].sum() if not df.empty else 0
balance = total_income - total_expense

st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {st.session_state.user}")
st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("총 입금", f"₩{total_income:,}")
col2.metric("총 출금", f"₩{total_expense:,}")
col3.metric("현재 잔액", f"₩{balance:,}")
st.divider()

# =======================
# 회계 내역 입력
# =======================
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
        desc_value = income_desc if income_desc else expense_desc
        append_row(sheet, account_date, income, expense, desc_value, st.session_state.user, WORKSHEET_NAME)
        st.success("회계 내역이 저장되었습니다.")
        st.experimental_rerun()

st.divider()

# =======================
# 회계 내역 수정/삭제
# =======================
st.subheader("📝 회계 내역 수정 / 삭제")
if not df.empty:
    df['display'] = df.apply(
        lambda x: f"날짜:{x['회계일자']} | 입금:{x['입금']} | 출금:{x['출금']} | 작성자:{x['작성자']}", axis=1
    )
    selected_idx = st.selectbox(
        "대상 선택",
        options=df.index,
        format_func=lambda x: df.loc[x, 'display']
    )

    selected_row = df.loc[selected_idx]

    col1, col2 = st.columns(2)
    with col1:
        new_income = st.number_input("입금액", value=int(selected_row['입금']))
        new_income_desc = st.text_input("입금 내역", value=selected_row['입금 내역'])
    with col2:
        new_expense = st.number_input("출금액", value=int(selected_row['출금']))
        new_expense_desc = st.text_input("출금 내역", value=selected_row['출금 내역'])

    # 권한 체크: 삭제 가능 사용자
    can_delete = st.session_state.user in ['도기웅', '김현주']

    if st.button("수정"):
        new_desc = new_income_desc if new_income_desc else new_expense_desc
        update_row(sheet, selected_idx + 2, selected_row['회계일자'], new_income, new_expense, new_desc, st.session_state.user)
        st.success("수정되었습니다.")
        st.experimental_rerun()

    if can_delete:
        if st.button("삭제"):
            delete_row(sheet, selected_idx + 2)
            st.success("삭제되었습니다.")
            st.experimental_rerun()
    else:
        st.info("삭제가 필요할 경우 총무에게 요청해주세요.")
