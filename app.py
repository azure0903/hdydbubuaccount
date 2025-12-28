import streamlit as st
import pandas as pd
from datetime import datetime
from auth import login
from sheets import get_gspread_client, open_sheet, append_row, update_row, delete_row, get_dataframe

# ======================
# 페이지 설정
# ======================
st.set_page_config(
    page_title="💒 하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

# ======================
# 로그인 처리
# ======================
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    if not login():
        st.stop()

# ======================
# 스프레드시트 연동
# ======================
SHEET_ID = "1hLoL3lTdONsSH1OOLoGeOiRw8H8tRHNTkJT5ouPIyrc"
SHEET_NAME = "Sheet1"

sheet = open_sheet(SHEET_ID)
df = get_dataframe(sheet, SHEET_NAME)

# ======================
# 숫자형 변환 및 총액 계산
# ======================
df['입금'] = pd.to_numeric(df['입금'], errors='coerce').fillna(0)
df['출금'] = pd.to_numeric(df['출금'], errors='coerce').fillna(0)

total_income = df['입금'].sum()
total_expense = df['출금'].sum()
balance = total_income - total_expense

# ======================
# 상단 KPI
# ======================
st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {st.session_state.user}")
st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("총 입금", f"₩{int(total_income):,}")
col2.metric("총 출금", f"₩{int(total_expense):,}")
col3.metric("현재 잔액", f"₩{int(balance):,}")
st.divider()

# ======================
# 회계 내역 입력
# ======================
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
        append_row(
            sheet,
            record_date,
            account_date.strftime("%Y-%m-%d"),
            income,
            income_desc,
            expense,
            expense_desc,
            st.session_state.user
        )
        st.success("회계 내역이 저장되었습니다.")
        st.experimental_rerun()

st.divider()

# ======================
# 회계 내역 수정/삭제
# ======================
st.subheader("📝 회계 내역 수정 / 삭제")

# 삭제 권한 사용자
delete_allowed_users = ["도기웅", "김현주"]

if df.empty:
    st.info("등록된 회계 내역이 없습니다.")
else:
    # 선택 UI
    df['display'] = df.apply(
        lambda x: f"날짜:{x['회계일자']} | 입금:{x['입금']} | 출금:{x['출금']} | 작성자:{x['작성자']}",
        axis=1
    )
    selected_idx = st.selectbox(
        "대상 선택",
        df.index,
        format_func=lambda x: df.loc[x, 'display']
    )
    selected_row = df.loc[selected_idx]

    # 수정
    with st.form("modify_form"):
        new_income = st.number_input("입금액", value=int(selected_row['입금']))
        new_income_desc = st.text_input("입금 내역", value=selected_row['입금내역'])
        new_expense = st.number_input("출금액", value=int(selected_row['출금']))
        new_expense_desc = st.text_input("출금 내역", value=selected_row['출금내역'])

        modify_submitted = st.form_submit_button("수정")
        if modify_submitted:
            update_row(
                sheet,
                selected_idx + 2,  # 시트 행 번호 (헤더 포함)
                new_income,
                new_income_desc,
                new_expense,
                new_expense_desc
            )
            st.success("회계 내역이 수정되었습니다.")
            st.experimental_rerun()

    # 삭제
    if st.session_state.user in delete_allowed_users:
        if st.button("삭제"):
            delete_row(sheet, selected_idx + 2)
            st.success("회계 내역이 삭제되었습니다.")
            st.experimental_rerun()
    else:
        st.info("삭제가 필요하면 총무에게 요청하세요.")
