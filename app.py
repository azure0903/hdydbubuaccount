import streamlit as st
from auth import login

st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

if not login():
    st.stop()

# ======================
# 로그인 이후 화면
# ======================

st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {st.session_state.user}")

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric("총 입금", "₩1,200,000")
col2.metric("총 출금", "₩850,000")
col3.metric("현재 잔액", "₩350,000")

st.divider()

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
        st.success("회계 내역이 저장되었습니다 (구글시트 연동 예정)")

st.divider()

st.subheader("📊 회계 현황")
st.info("구글 스프레드시트 연동 후 자동 표시됩니다")
