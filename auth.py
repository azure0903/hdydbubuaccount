import streamlit as st
from werkzeug.security import check_password_hash

def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    st.title("🔐 로그인")

    user_id = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        users = st.secrets["users"]

        if user_id in users:
            stored_hash = users[user_id]["password_hash"]

            if check_password_hash(stored_hash, password):
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.success(f"{user_id}님 환영합니다")
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다")
        else:
            st.error("존재하지 않는 아이디입니다")

    return False
