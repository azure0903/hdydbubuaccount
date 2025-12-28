import streamlit as st
import pandas as pd
from datetime import date

from auth import login
from sheets import (
    load_account_df,
    append_account_row,
    update_account_row,
    delete_account_row
)

# ======================
# Config
# ======================
st.set_page_config(
    page_title="하늘꿈연동교회 부부청년부 회계관리",
    layout="wide"
)

SHEET_ID = "1hLoL3lTdONsSH1OOLoGeOiRw8H8tRHNTkJT5ouPIyrc"

# ======================
# Login
# ======================
if not login():
    st.stop()

# ======================
# Header
# ======================
st.title("💒 하늘꿈연동교회 부부청년부 회계관리")
st.caption(f"로그인 사용자: {st.session_state.user}")

st.divider()

# ======================
# Load Data
# ======================
df = load_account_df(SHEET_ID)

# 숫자 컬럼 정리
for col in ["입금", "출금"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

total_income = int(df["입금"].sum()) if not df.empty else 0
total_expense = int(df["출금"].sum()) if not df.empty else 0
balance = total_income - total_expense

# ======================
# Metrics
# ======================
c1, c2, c3 = st.columns(3)
c1.metric("총 입금", f"₩{total_income:,}")
c2.metric("총 출금", f"₩{total_expense:,}")
c3.metric("현재 잔액", f"₩{balance:,}")

st.divider()

# ======================
# Input Form
# ======================
st.subheader("➕ 회계 내역 입력")

with st.form("account_form", clear_on_submit=True):
    c1, c2 = st.columns(2)

    with c1:
        accounting_date = st.date_input("회계일자", value=date.today())
        income = st.number_input("입금액", min_value=0, step=1000)
        income_desc = st.text_input("입금 내역")

    with c2:
        expense = st.number_input("출금액", min_value=0, step=1000)
        expense_desc = st.text_input("출금 내역")

    submitted = st.form_submit_button("저장")

    if submitted:
        append_account_row(
            SHEET_ID,
            accounting_date,
            income,
            income_desc,
            expense,
            expense_desc,
            st.session_state.user
        )
        st.success("회계 내역이 저장되었습니다")
        st.rerun()

st.divider()

# ======================
# Account Table
# ======================
st.subheader("📊 회계 현황")

if df.empty:
    st.info("등록된 회계 내역이 없습니다.")
else:
    for idx, row in df.iterrows():
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])

            with c1:
                st.write(
                    f"📅 {row['회계일자']} | "
                    f"입금 ₩{int(row['입금']):,} / 출금 ₩{int(row['출금']):,}"
                )
                st.caption(
                    f"입금내역: {row['입금내역']} / "
                    f"출금내역: {row['출금내역']}"
                )
                st.caption(f"작성자: {row['작성자']}")

            with c4:
                if st.button("✏️ 수정", key=f"edit_{idx}"):
                    st.session_state.edit_index = idx

                if st.button("🗑 삭제", key=f"delete_{idx}"):
                    delete_account_row(SHEET_ID, idx)
                    st.success("삭제되었습니다")
                    st.rerun()

        # ======================
        # Edit Mode
        # ======================
        if st.session_state.get("edit_index") == idx:
            with st.form(f"edit_form_{idx}"):
                ed1, ed2 = st.columns(2)

                with ed1:
                    e_date = st.date_input("회계일자", pd.to_datetime(row["회계일자"]))
                    e_income = st.number_input("입금액", value=int(row["입금"]), step=1000)
                    e_income_desc = st.text_input("입금 내역", row["입금내역"])

                with ed2:
                    e_expense = st.number_input("출금액", value=int(row["출금"]), step=1000)
                    e_expense_desc = st.text_input("출금 내역", row["출금내역"])

                if st.form_submit_button("수정 저장"):
                    update_account_row(
                        SHEET_ID,
                        idx,
                        [
                            row["기록일자"],
                            e_date.strftime("%Y-%m-%d"),
                            e_income,
                            e_income_desc,
                            e_expense,
                            e_expense_desc,
                            row["작성자"]
                        ]
                    )
                    st.session_state.pop("edit_index")
                    st.success("수정되었습니다")
                    st.rerun()

    st.divider()

    # ======================
    # CSV Download
    # ======================
    st.download_button(
        "📥 CSV 다운로드",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="회계내역.csv",
        mime="text/csv"
    )
