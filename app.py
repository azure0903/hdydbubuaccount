import streamlit as st
import pandas as pd
from auth import login
from sheets import open_sheet, append_row, update_row, delete_row, get_dataframe

# =====================
# 페이지 설정
# =====================
st.set_page_config(
    page_title="💒 하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

# =====================
# 로그인
# =====================
st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
if not login():
    st.stop()

st.caption(f"로그인 사용자: {st.session_state.user}")
st.divider()

# =====================
# 스프레드시트 설정
# =====================
SHEET_ID = "1hLoL3lTdONsSH1OOLoGeOiRw8H8tRHNTkJT5ouPIyrc"
SHEET_NAME = "Sheet1"
sheet = open_sheet(SHEET_ID)
ws = sheet.worksheet(SHEET_NAME)

# =====================
# 데이터 가져오기
# =====================
df = get_dataframe(sheet, SHEET_NAME)

# =====================
# 총합 요약
# =====================
total_income = df['입금'].sum() if '입금' in df.columns else 0
total_expense = df['출금'].sum() if '출금' in df.columns else 0
balance = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("총 입금", f"₩{total_income:,}")
col2.metric("총 출금", f"₩{total_expense:,}")
col3.metric("현재 잔액", f"₩{balance:,}")

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
        append_row(
            sheet,
            str(pd.Timestamp.now().date()),  # 기록일자
            str(account_date),               # 회계일자
            income,
            income_desc,
            expense,
            expense_desc,
            st.session_state.user
        )
        st.success("회계 내역이 스프레드시트에 저장되었습니다.")
        st.experimental_rerun()

st.divider()

# =====================
# 회계 내역 수정 / 삭제
# =====================
st.subheader("📝 회계 내역 수정 / 삭제")

if not df.empty:
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

    st.write("선택된 내역:")
    st.write(selected_row)

    # 권한 체크
    can_delete = st.session_state.user in ['도기웅', '김현주']

    st.write("🔧 수정")
    with st.form("edit_form"):
        new_income = st.number_input("입금액", value=int(selected_row['입금']))
        new_income_desc = st.text_input("입금 내역", value=selected_row['입금내역'])
        new_expense = st.number_input("출금액", value=int(selected_row['출금']))
        new_expense_desc = st.text_input("출금 내역", value=selected_row['출금내역'])
        submitted_edit = st.form_submit_button("수정")

        if submitted_edit:
            update_row(
                sheet,
                selected_idx + 2,  # gspread는 1부터 시작, header 포함
                str(pd.Timestamp.now().date()),
                str(selected_row['회계일자']),
                new_income,
                new_income_desc,
                new_expense,
                new_expense_desc,
                st.session_state.user
            )
            st.success("수정 완료")
            st.experimental_rerun()

    st.write("🗑️ 삭제")
    if can_delete:
        if st.button("삭제"):
            delete_row(sheet, selected_idx + 2)
            st.success("삭제 완료")
            st.experimental_rerun()
    else:
        st.info("삭제 권한이 없습니다. 필요 시 총무에게 요청하세요.")

else:
    st.info("등록된 회계 내역이 없습니다.")
