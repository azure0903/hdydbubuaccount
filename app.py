import streamlit as st
import pandas as pd
from auth import login
from sheets import get_gspread_client, open_sheet, get_dataframe, append_row, update_row, delete_row

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
    st.stop()  # 로그인 안되면 여기서 멈춤

# ======================
# 변수 정의
# ======================
SHEET_ID = "1hLoL3lTdONsSH1OOLoGeOiRw8H8tRHNTkJT5ouPIyrc"
WORKSHEET_NAME = "Sheet1"
ADMIN_USERS = ["도기웅", "김현주"]

# ======================
# 구글 시트 연결
# ======================
client = get_gspread_client()
sheet = open_sheet(SHEET_ID)

# ======================
# 데이터 가져오기
# ======================
try:
    df = get_dataframe(sheet, WORKSHEET_NAME)
except Exception as e:
    st.error(f"시트 데이터를 가져오는 중 오류가 발생했습니다: {e}")
    st.stop()

# ======================
# 총액 표시
# ======================
total_income = df['입금'].sum() if '입금' in df.columns else 0
total_expense = df['출금'].sum() if '출금' in df.columns else 0
balance = total_income - total_expense

st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {st.session_state.user}")
st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("총 입금", f"₩{total_income:,}")
col2.metric("총 출금", f"₩{total_expense:,}")
col3.metric("현재 잔액", f"₩{balance:,}")
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
        desc_value = (income_desc if income_desc else "") or (expense_desc if expense_desc else "")
        writer_value = st.session_state.user if st.session_state.user else "Unknown"
        try:
            append_row(sheet, account_date, income, expense, desc_value, writer_value, WORKSHEET_NAME)
            st.success("회계 내역이 저장되었습니다.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"저장 중 오류가 발생했습니다: {e}")

st.divider()

# ======================
# 회계 내역 수정 / 삭제
# ======================
st.subheader("📝 회계 내역 수정 / 삭제")
if not df.empty:
    df['display'] = df.apply(
        lambda x: f"날짜:{x.get('회계일자','')} | 입금:{x.get('입금',0)} | 출금:{x.get('출금',0)} | 작성자:{x.get('작성자','')}",
        axis=1
    )

    selected_idx = st.selectbox(
        "대상 선택",
        df.index,
        format_func=lambda x: df.loc[x, 'display']
    )

    selected_row = df.loc[selected_idx]

    st.write("선택된 내역:")
    st.text(selected_row['display'])

    # 수정 폼
    with st.form("edit_form"):
        new_income = st.number_input("입금액", value=int(selected_row.get('입금',0)))
        new_expense = st.number_input("출금액", value=int(selected_row.get('출금',0)))
        new_desc = st.text_input("내역", value=selected_row.get('내역',''))

        submitted_edit = st.form_submit_button("수정")

        if submitted_edit:
            try:
                update_row(sheet, selected_idx, new_income, new_expense, new_desc, WORKSHEET_NAME)
                st.success("회계 내역이 수정되었습니다.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"수정 중 오류가 발생했습니다: {e}")

    # 삭제 버튼 (권한 있는 사용자만)
    if st.session_state.user in ADMIN_USERS:
        if st.button("삭제"):
            try:
                delete_row(sheet, selected_idx, WORKSHEET_NAME)
                st.success("회계 내역이 삭제되었습니다.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"삭제 중 오류가 발생했습니다: {e}")
    else:
        st.info("삭제가 필요할 경우 총무에게 요청해주세요.")
else:
    st.info("저장된 회계 내역이 없습니다.")
