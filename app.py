import streamlit as st
from auth import login
from sheets import open_sheet, get_dataframe, append_row, update_row, delete_row
from datetime import datetime

SHEET_ID = "1hLoL3lTdONsSH1OOLoGeOiRw8H8tRHNTkJT5ouPIyrc"
SHEET_NAME = "Sheet1"
ADMIN_USERS = ["도기웅", "김현주"]

st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

# ========================
# 로그인
# ========================
if not login():
    st.stop()

# ========================
# 구글시트 불러오기
# ========================
sheet = open_sheet(SHEET_ID)
df = get_dataframe(sheet, SHEET_NAME)

# ========================
# 총 수입/총 지출/잔액 계산
# ========================
if not df.empty:
    df['입금'] = pd.to_numeric(df['입금'], errors='coerce').fillna(0)
    df['출금'] = pd.to_numeric(df['출금'], errors='coerce').fillna(0)
    total_income = df['입금'].sum()
    total_expense = df['출금'].sum()
else:
    total_income = total_expense = 0
balance = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("총 입금", f"₩{total_income:,}")
col2.metric("총 출금", f"₩{total_expense:,}")
col3.metric("현재 잔액", f"₩{balance:,}")

st.divider()

# ========================
# 회계 내역 입력
# ========================
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
        record_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        append_row(sheet, record_date, account_date.strftime("%Y-%m-%d"), income, income_desc, expense, expense_desc, st.session_state.user)
        st.success("회계 내역이 저장되었습니다.")
        st.experimental_rerun()

st.divider()

# ========================
# 회계 내역 수정/삭제
# ========================
st.subheader("📝 회계 내역 수정 / 삭제")
if df.empty:
    st.info("저장된 회계 내역이 없습니다.")
else:
    df['display'] = df.apply(
        lambda x: f"날짜:{x['회계일자']} | 입금:{x['입금']} | 출금:{x['출금']} | 작성자:{x['작성자']}", axis=1
    )

    selected_idx = st.selectbox(
        "대상 선택",
        df.index,
        format_func=lambda x: df.loc[x, 'display']
    )

    selected_row = df.loc[selected_idx]

    with st.form("edit_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_account_date = st.date_input("회계일자", value=pd.to_datetime(selected_row['회계일자']))
            new_income = st.number_input("입금액", value=int(selected_row['입금']))
            new_income_desc = st.text_input("입금 내역", value=selected_row['입금내역'])
        with col2:
            new_expense = st.number_input("출금액", value=int(selected_row['출금']))
            new_expense_desc = st.text_input("출금 내역", value=selected_row['출금내역'])

        edit_submitted = st.form_submit_button("수정")
        delete_submitted = st.form_submit_button("삭제")

        if edit_submitted:
            update_row(
                sheet, selected_idx+2,  # header 포함해서 row 번호
                new_account_date.strftime("%Y-%m-%d"),
                new_income, new_income_desc,
                new_expense, new_expense_desc,
                st.session_state.user
            )
            st.success("수정 완료")
            st.experimental_rerun()

        if delete_submitted:
            if st.session_state.user in ADMIN_USERS:
                delete_row(sheet, selected_idx+2)
                st.success("삭제 완료")
                st.experimental_rerun()
            else:
                st.warning("삭제 권한이 없습니다. 삭제가 필요하면 총무에게 요청하세요.")
