import streamlit as st
import pandas as pd
from auth import login
from sheets import open_sheet, get_dataframe, append_row, update_row, delete_row

# =====================
# 페이지 설정
# =====================
st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

# =====================
# 로그인
# =====================
if not login():
    st.stop()

st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {st.session_state.user}")
st.divider()

# =====================
# 구글 시트 연결
# =====================
SHEET_ID = "1hLoL3lTdONsSH1OOLoGeOiRw8H8tRHNTkJT5ouPIyrc"
WORKSHEET_NAME = "Sheet1"

sheet = open_sheet(SHEET_ID)
df = get_dataframe(sheet, WORKSHEET_NAME)

# 컬럼 공백 제거
df.columns = df.columns.str.strip()

# =====================
# 상단 총액 표시
# =====================
total_income = df['입금'].sum() if '입금' in df.columns else 0
total_expense = df['출금'].sum() if '출금' in df.columns else 0
current_balance = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("총 입금", f"₩{total_income:,}")
col2.metric("총 출금", f"₩{total_expense:,}")
col3.metric("현재 잔액", f"₩{current_balance:,}")

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
            str(pd.Timestamp.now().date()),  # 기록일자
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

st.divider()

# =====================
# 회계 내역 수정 / 삭제
# =====================
st.subheader("📝 회계 내역 수정 / 삭제")

if df.empty:
    st.info("저장된 회계 내역이 없습니다.")
else:
    # 선택 박스 표시
    df['display'] = df.apply(
        lambda x: f"날짜:{x['회계일자']} | 입금:{x['입금']} | 출금:{x['출금']} | 작성자:{x['작성자']}", axis=1
    )
    selected_idx = st.selectbox(
        "대상 선택",
        options=df.index,
        format_func=lambda x: df.loc[x, 'display']
    )

    selected_row = df.loc[selected_idx]

    st.write("선택된 내역:")
    st.json(selected_row.to_dict())

    # 수정
    st.subheader("수정")
    col1, col2 = st.columns(2)
    with col1:
        edit_income = st.number_input("입금액", value=int(selected_row['입금']))
        edit_income_desc = st.text_input("입금 내역", value=selected_row['입금내역'])
    with col2:
        edit_expense = st.number_input("출금액", value=int(selected_row['출금']))
        edit_expense_desc = st.text_input("출금 내역", value=selected_row['출금내역'])

    if st.button("수정 저장"):
        update_row(
            sheet,
            WORKSHEET_NAME,
            selected_idx + 2,  # 시트는 1부터, 헤더 포함
            [
                selected_row['기록일자'],
                selected_row['회계일자'],
                edit_income,
                edit_income_desc,
                edit_expense,
                edit_expense_desc,
                selected_row['작성자']
            ]
        )
        st.success("회계 내역이 수정되었습니다.")
        st.experimental_rerun()

    # 삭제
    st.subheader("삭제")
    if st.session_state.user in ['도기웅', '김현주']:
        if st.button("삭제"):
            delete_row(sheet, WORKSHEET_NAME, selected_idx + 2)
            st.success("선택된 내역이 삭제되었습니다.")
            st.experimental_rerun()
    else:
        st.info("삭제가 필요할 경우, 총무에게 요청해주세요.")
