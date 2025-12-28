# app.py
import streamlit as st
import pandas as pd
from auth import login
from sheets import get_gspread_client, open_sheet, get_dataframe, append_row, update_row, delete_row

# =====================
# 페이지 설정
# =====================
st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

# =====================
# 로그인 처리
# =====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    if login():  # login()이 True 반환 시
        st.session_state.logged_in = True
        st.success(f"{st.session_state.user}님, 로그인 되었습니다!")
        # rerun 제거하고 다음 코드는 그대로 진행
else:
    st.title("하늘꿈연동교회 부부청년부 회계관리")

# =====================
# 로그인 이후 화면
# =====================
st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {st.session_state.user}")
st.divider()

# =====================
# 구글 시트 연결
# =====================
SHEET_ID = "1hLoL3lTdONsSH1OOLoGeOiRw8H8tRHNTkJT5ouPIyrc"
WORKSHEET_NAME = "Sheet1"

gc = get_gspread_client()
sheet = open_sheet(SHEET_ID)
try:
    df = get_dataframe(sheet, WORKSHEET_NAME)
except Exception:
    df = pd.DataFrame()

# 컬럼 체크 및 기본값
expected_columns = ["기록일자","회계일자","입금","입금내역","출금","출금내역","작성자"]
for col in expected_columns:
    if col not in df.columns:
        df[col] = ""

# =====================
# 총액 계산 및 UI
# =====================
total_income = pd.to_numeric(df['입금'], errors='coerce').sum()
total_expense = pd.to_numeric(df['출금'], errors='coerce').sum()
balance = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("총 입금", f"₩{total_income:,.0f}")
col2.metric("총 출금", f"₩{total_expense:,.0f}")
col3.metric("현재 잔액", f"₩{balance:,.0f}")
st.divider()

# =====================
# 회계 내역 입력
# =====================
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
        new_row = [
            pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            str(account_date),
            income,
            income_desc,
            expense,
            expense_desc,
            st.session_state.user
        ]
        append_row(sheet, WORKSHEET_NAME, new_row)
        st.success("회계 내역이 저장되었습니다.")
        st.experimental_rerun()

# =====================
# 회계 내역 수정 / 삭제
# =====================
st.subheader("📝 회계 내역 수정 / 삭제")

# display 컬럼 생성
df['display'] = df.apply(
    lambda x: f"날짜:{x.get('회계일자','')} | 입금:{x.get('입금','')} | 출금:{x.get('출금','')} | 작성자:{x.get('작성자','')}",
    axis=1
)

if not df.empty:
    selected_idx = st.selectbox(
        "대상 선택",
        df.index,
        format_func=lambda x: df.loc[x, 'display']
    )

    selected_row = df.loc[selected_idx]

    col1, col2, col3 = st.columns(3)
    with col1:
        new_income = st.number_input("입금액", value=int(selected_row['입금']))
        new_income_desc = st.text_input("입금 내역", value=selected_row['입금내역'])
    with col2:
        new_expense = st.number_input("출금액", value=int(selected_row['출금']))
        new_expense_desc = st.text_input("출금 내역", value=selected_row['출금내역'])
    with col3:
        st.text(f"작성자: {selected_row['작성자']}")

    # 수정 버튼
    if st.button("수정"):
        updated_row = [
            selected_row['기록일자'],
            selected_row['회계일자'],
            new_income,
            new_income_desc,
            new_expense,
            new_expense_desc,
            selected_row['작성자']
        ]
        update_row(sheet, WORKSHEET_NAME, selected_idx+2, updated_row)  # +2 : 시트 헤더 포함
        st.success("회계 내역이 수정되었습니다.")
        st.experimental_rerun()

    # 삭제 버튼 (권한 제한)
    if st.session_state.user in ["도기웅", "김현주"]:
        if st.button("삭제"):
            delete_row(sheet, WORKSHEET_NAME, selected_idx+2)
            st.success("회계 내역이 삭제되었습니다.")
            st.experimental_rerun()
    else:
        st.info("삭제가 필요할 경우 총무에게 요청해주세요.")
else:
    st.info("저장된 회계 내역이 없습니다.")
