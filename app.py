import streamlit as st
import pandas as pd
from auth import login
from sheets import open_sheet

# ======================
# 페이지 설정
# ======================
st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

# ======================
# 로그인
# ======================
if not login():
    st.stop()

current_user = st.session_state.user

# ======================
# 권한 설정
# ======================
ADMIN_USERS = ["도기웅", "김현주"]
is_admin = current_user in ADMIN_USERS

# ======================
# 구글 시트 설정
# ======================
SHEET_ID = "1hLoL3lTdONsSH1OOLoGeOiRw8H8tRHNTkJT5ouPIyrc"
WORKSHEET_NAME = "회계내역"

sh = open_sheet(SHEET_ID)
ws = sh.worksheet(WORKSHEET_NAME)

# ======================
# 타이틀
# ======================
st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {current_user}")

st.divider()

# ======================
# 회계 입력
# ======================
st.subheader("➕ 회계 내역 입력")

with st.form("account_form"):
    col1, col2 = st.columns(2)

    with col1:
        account_date = st.date_input("회계일자")

        if is_admin:
            income = st.number_input("입금액", min_value=0, step=1000)
            income_desc = st.text_input("입금 내역")
        else:
            income = 0
            income_desc = ""

    with col2:
        expense = st.number_input("출금액", min_value=0, step=1000)
        expense_desc = st.text_input("출금 내역")

    submitted = st.form_submit_button("저장")

    if submitted:
        if not is_admin and income > 0:
            st.error("입금 내역은 총무만 입력할 수 있습니다.")
        else:
            ws.append_row([
                account_date.strftime("%Y-%m-%d"),
                income,
                income_desc,
                expense,
                expense_desc,
                current_user
            ])
            st.success("회계 내역이 저장되었습니다.")
            st.rerun()

st.divider()

# ======================
# 회계 내역 조회
# ======================
st.subheader("📋 회계 내역")

records = ws.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.info("아직 등록된 회계 내역이 없습니다.")
else:
    st.dataframe(df, use_container_width=True)

# ======================
# 관리자 전용: 삭제
# ======================
if not df.empty:
    if is_admin:
        st.subheader("🛠 관리자 기능 (삭제)")

        selected_idx = st.selectbox(
            "삭제할 내역 선택",
            options=df.index,
            format_func=lambda x: (
                f"{df.loc[x, '회계일자']} | "
                f"입금 {df.loc[x, '입금액']} | "
                f"출금 {df.loc[x, '출금액']} | "
                f"{df.loc[x, '출금내역']}"
            )
        )

        if st.button("❌ 삭제"):
            ws.delete_rows(selected_idx + 2)  # header 보정
            st.success("삭제되었습니다.")
            st.rerun()

    else:
        st.info("⚠️ 삭제가 필요한 경우 총무에게 요청해주세요")
