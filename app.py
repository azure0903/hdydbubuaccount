import streamlit as st
from auth import login
from sheets import open_sheet, get_dataframe, append_row, update_row, delete_row
import pandas as pd

st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

if not login():
    st.stop()

st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {st.session_state.user}")
st.divider()

# ===== 구글 시트 연동 =====
SHEET_ID = "1hLoL3lTdONsSH1OOLoGeOiRw8H8tRHNTkJT5ouPIyrc"
sheet = open_sheet(SHEET_ID)
df = get_dataframe(sheet)

# ===== 총계 표시 =====
total_income = df['입금액'].sum()
total_expense = df['출금액'].sum()
balance = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("총 입금액", f"₩{total_income:,}")
col2.metric("총 출금액", f"₩{total_expense:,}")
col3.metric("현재 잔액", f"₩{balance:,}")
st.divider()

# ===== 회계 입력 폼 =====
st.subheader("➕ 회계 내역 입력")
with st.form("account_form"):
    col1, col2 = st.columns(2)
    with col1:
        account_date = st.date_input("회계일자")
        income = st.number_input("입금액", min_value=0, step=1000)
        income_desc = st.text_input("입금내역")
    with col2:
        expense = st.number_input("출금액", min_value=0, step=1000)
        expense_desc = st.text_input("출금내역")

    submitted = st.form_submit_button("저장")
    if submitted:
        append_row(sheet, [
            str(pd.Timestamp("today").date()),  # 기록일자
            str(account_date),
            income,
            income_desc,
            expense,
            expense_desc,
            st.session_state.user
        ])
        st.success("회계 내역이 저장되었습니다.")
        st.experimental_rerun()

st.divider()
st.subheader("📊 회계 현황")
df = get_dataframe(sheet)  # 최신화
if df.empty:
    st.info("등록된 내역이 없습니다.")
else:
    # 삭제 권한 확인
    can_delete = st.session_state.user in ["도기웅", "김현주"]

    def format_row(x):
        return f"입금 {df.loc[x, '입금']} | {df.loc[x, '입금내역']} | 출금 {df.loc[x, '출금']} | {df.loc[x, '출금내역']} | 작성자 {df.loc[x, '작성자']}"

    selected_idx = st.selectbox(
        "대상 선택",
        options=df.index,
        format_func=format_row
    )

    col1, col2 = st.columns([3,1])
    with col1:
        st.write(df.loc[selected_idx])
    with col2:
        if can_delete:
            if st.button("삭제"):
                delete_row(sheet, selected_idx)
                st.success("선택 항목이 삭제되었습니다.")
                st.experimental_rerun()
        else:
            st.info("삭제가 필요할 경우 총무에게 요청해주세요.")

# ===== CSV 다운로드 =====
csv = df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="CSV 다운로드",
    data=csv,
    file_name="account_history.csv",
    mime="text/csv"
)
