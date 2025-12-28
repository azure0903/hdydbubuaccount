import streamlit as st
import pandas as pd
from datetime import date
import gspread
import bcrypt
from google.oauth2.service_account import Credentials

# ======================
# 기본 설정
# ======================
st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

# ======================
# 로그인 로직
# ======================
def login():
    if "user_id" in st.session_state:
        return True

    st.markdown("## 🔐 로그인")

    user_id = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        users = st.secrets["USERS"]

        if user_id not in users:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
            return False

        stored_hash = users[user_id].encode()

        if bcrypt.checkpw(password.encode(), stored_hash):
            st.session_state["user_id"] = user_id
            st.success("로그인 성공")
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

    return False


def logout():
    if st.sidebar.button("🚪 로그아웃"):
        st.session_state.clear()
        st.rerun()


if not login():
    st.stop()

USER_ID = st.session_state["user_id"]

# ======================
# Google Sheet 연결
# ======================
@st.cache_resource
def connect_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(creds)
    return gc.open("모임회계").worksheet("원장")

sheet = connect_sheet()

@st.cache_data(ttl=30)
def load_data():
    return pd.DataFrame(sheet.get_all_records())

df = load_data()

# ======================
# 회계 입력 폼
# ======================
def accounting_form():
    with st.expander("➕ 회계 입력", expanded=False):
        with st.form("account_form", clear_on_submit=True):
            acc_date = st.date_input("회계일자", date.today())
            deposit = st.number_input("입금", min_value=0, step=1000)
            deposit_desc = st.text_input("입금 내역")
            withdraw = st.number_input("출금", min_value=0, step=1000)
            withdraw_desc = st.text_input("출금 내역")

            submit = st.form_submit_button("저장")

            if submit:
                if deposit == 0 and withdraw == 0:
                    st.error("입금 또는 출금 중 하나는 필수입니다.")
                    return
                if deposit > 0 and withdraw > 0:
                    st.error("입금과 출금은 동시에 입력할 수 없습니다.")
                    return

                sheet.append_row([
                    date.today().isoformat(),     # 기록일자
                    acc_date.isoformat(),        # 회계일자
                    deposit,
                    deposit_desc,
                    withdraw,
                    withdraw_desc,
                    USER_ID                      # 작성자
                ])

                st.success("저장 완료")
                st.cache_data.clear()

# ======================
# 대시보드
# ======================
def dashboard(df):
    if df.empty:
        st.info("회계 내역이 없습니다.")
        return

    df["입금"] = pd.to_numeric(df["입금"], errors="coerce").fillna(0)
    df["출금"] = pd.to_numeric(df["출금"], errors="coerce").fillna(0)

    total_in = int(df["입금"].sum())
    total_out = int(df["출금"].sum())
    balance = total_in - total_out

    st.markdown("### 📊 회계 현황")
    st.metric("총 입금", f"{total_in:,} 원")
    st.metric("총 출금", f"{total_out:,} 원")
    st.metric("현재 잔액", f"{balance:,} 원")

    st.divider()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 CSV 다운로드",
        csv,
        "회계원장.csv",
        "text/csv"
    )

    st.divider()

    st.markdown("### 📄 회계 원장")
    st.dataframe(
        df.sort_values("회계일자", ascending=False),
        use_container_width=True,
        hide_index=True
    )

# ======================
# 메인 UI
# ======================
st.sidebar.markdown(f"👤 로그인: **{USER_ID}**")
logout()

st.title("💰 하늘꿈연동교회 부부청년부 회계관리")

accounting_form()
dashboard(df)
