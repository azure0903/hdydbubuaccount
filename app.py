import streamlit as st
from auth import login
from sheets import open_sheet
import pandas as pd

st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

# 로그인
if not login():
    st.stop()

# 상단 표시
st.sidebar.success(f"👤 {st.session_state.user_id} 로그인 중")

menu = st.sidebar.radio(
    "메뉴",
    ["대시보드", "회계 입력", "회계 현황", "CSV 다운로드"]
)

# 시트 열기
sheet = open_sheet("하늘꿈연동교회 부부청년부 회계관리")
ws = sheet.worksheet("원장")

# 데이터 로드
data = ws.get_all_records()
df = pd.DataFrame(data)

# 대시보드
if menu == "대시보드":
    st.header("📊 회계 요약")

    total_in = df["입금"].sum()
    total_out = df["출금"].sum()
    balance = total_in - total_out

    c1, c2, c3 = st.columns(3)
    c1.metric("총 입금", f"{total_in:,.0f}원")
    c2.metric("총 출금", f"{total_out:,.0f}원")
    c3.metric("잔액", f"{balance:,.0f}원")

# 회계 입력
if menu == "회계 입력":
    st.header("✍️ 회계 입력")

    with st.form("account_form"):
        date = st.date_input("회계일자")
        income = st.number_input("입금", min_value=0)
        income_desc = st.text_input("입금 내역")
        expense = st.number_input("출금", min_value=0)
        expense_desc = st.text_input("출금 내역")

        submit = st.form_submit_button("저장")

        if submit:
            ws.append_row([
                str(date),
                income,
                income_desc,
                expense,
                expense_desc,
                st.session_state.user_id
            ])
            st.success("저장 완료")
            st.rerun()

# 회계 현황
if menu == "회계 현황":
    st.header("📋 회계 원장")
    st.dataframe(df, use_container_width=True)

# CSV 다운로드
if menu == "CSV 다운로드":
    st.header("⬇ CSV 다운로드")

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "다운로드",
        csv,
        "회계내역.csv",
        "text/csv"
    )
