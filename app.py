import streamlit as st
from datetime import datetime
from auth import login
from sheets import open_sheet
import pandas as pd

# ======================
# 페이지 설정
# ======================
st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

# 🔥 이 구조가 핵심
if not login():
    st.stop()

# ======================
# 여기부터는 로그인 후 화면
# ======================
st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {st.session_state.user}")

# ======================
# 구글 시트 연결
# ======================
SHEET_NAME = "하늘꿈연동교회 부부청년부 2026"
ws = open_sheet(SHEET_NAME).get_worksheet(0)

# ======================
# 데이터 로드
# ======================
def load_data():
    data = ws.get_all_records()
    return pd.DataFrame(data)

df = load_data()

# ======================
# 타이틀
# ======================
st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {user}")

st.divider()

# ======================
# 요약 지표
# ======================
total_income = df["입금액"].sum() if not df.empty else 0
total_expense = df["출금액"].sum() if not df.empty else 0
balance = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("총 입금", f"₩{total_income:,}")
col2.metric("총 출금", f"₩{total_expense:,}")
col3.metric("현재 잔액", f"₩{balance:,}")

st.divider()

# ======================
# 신규 회계 입력
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
        ws.append_row([
            account_date.strftime("%Y-%m-%d"),
            income,
            income_desc,
            expense,
            expense_desc,
            user,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
        st.success("✅ 회계 내역이 저장되었습니다")
        st.rerun()

st.divider()

# ======================
# 회계 현황 (조회 / 수정 / 삭제)
# ======================
st.subheader("📊 회계 현황")

if df.empty:
    st.info("등록된 회계 내역이 없습니다.")
else:
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("✏️ 수정 / 🗑 삭제")

    selected_index = st.selectbox(
        "수정 또는 삭제할 행 선택",
        df.index,
        format_func=lambda x: f"{df.loc[x, '날짜']} | 입금 {df.loc[x,'입금액']:,} / 출금 {df.loc[x,'출금액']:,}"
    )

    selected_row = df.loc[selected_index]

    with st.form("edit_form"):
        col1, col2 = st.columns(2)

        with col1:
            edit_date = st.date_input("회계일자", pd.to_datetime(selected_row["날짜"]))
            edit_income = st.number_input("입금액", value=int(selected_row["입금액"]), step=1000)
            edit_income_desc = st.text_input("입금 내역", selected_row["입금내역"])

        with col2:
            edit_expense = st.number_input("출금액", value=int(selected_row["출금액"]), step=1000)
            edit_expense_desc = st.text_input("출금 내역", selected_row["출금내역"])

        col_edit, col_delete = st.columns(2)
        update = col_edit.form_submit_button("수정")
        delete = col_delete.form_submit_button("삭제")

        row_number = selected_index + 2  # 헤더 포함 보정

        if update:
            ws.update(f"A{row_number}:G{row_number}", [[
                edit_date.strftime("%Y-%m-%d"),
                edit_income,
                edit_income_desc,
                edit_expense,
                edit_expense_desc,
                user,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]])
            st.success("✏️ 수정 완료")
            st.rerun()

        if delete:
            ws.delete_rows(row_number)
            st.success("🗑 삭제 완료")
            st.rerun()
