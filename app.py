import streamlit as st
import pandas as pd
from auth import login
from sheets import (
    open_sheet,
    append_account_row,
    load_account_dataframe,
    calculate_summary
)

# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

# =========================
# 로그인 처리
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# =========================
# 사이드바
# =========================
with st.sidebar:
    st.markdown("### 👤 로그인 정보")
    st.write(st.session_state.username)

    if st.button("로그아웃"):
        st.session_state.clear()
        st.rerun()

    st.divider()
    st.caption("하늘꿈연동교회\n부부청년부 회계관리")

# =========================
# 구글시트 연결
# =========================
SHEET_NAME = "하늘꿈연동교회_부부청년부_회계"
ws = open_sheet(SHEET_NAME)

# =========================
# 데이터 로딩
# =========================
df = load_account_dataframe(ws)
total_income, total_expense, balance = calculate_summary(df)

# =========================
# 헤더
# =========================
st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {st.session_state.username}")

st.divider()

# =========================
# 📊 요약 카드 (모바일 대응)
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("총 입금", f"₩{total_income:,}")
c2.metric("총 출금", f"₩{total_expense:,}")
c3.metric("현재 잔액", f"₩{balance:,}")

st.divider()

# =========================
# ➕ 회계 입력 폼
# =========================
st.subheader("➕ 회계 내역 입력")

with st.form("account_form", clear_on_submit=True):
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
        if income == 0 and expense == 0:
            st.warning("입금 또는 출금 금액을 입력해주세요.")
        else:
            append_account_row(
                ws=ws,
                account_date=account_date,
                income=income,
                income_desc=income_desc,
                expense=expense,
                expense_desc=expense_desc,
                writer=st.session_state.username
            )
            st.success("회계 내역이 저장되었습니다.")
            st.rerun()

st.divider()

# =========================
# 📋 회계 현황 테이블
# =========================
st.subheader("📋 회계 내역")

if df.empty:
    st.info("아직 등록된 회계 내역이 없습니다.")
else:
    st.dataframe(
        df.sort_values("회계일자", ascending=False),
        use_container_width=True,
        hide_index=True
    )

# =========================
# 📥 CSV 다운로드
# =========================
st.divider()
st.subheader("📥 데이터 다운로드")

csv = df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="CSV 다운로드",
    data=csv,
    file_name="하늘꿈연동교회_부부청년부_회계내역.csv",
    mime="text/csv"
)
