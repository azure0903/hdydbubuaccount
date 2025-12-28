import streamlit as st
import hashlib

def login():
    if 'user' not in st.session_state:
        st.session_state.user = None

    users = st.secrets["users"]

    if st.session_state.user is None:
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        login_btn = st.button("로그인")

        if login_btn:
            if username in users:
                hashed_pw = hashlib.sha256(password.encode()).hexdigest()
                if hashed_pw == users[username]["password_hash"]:
                    st.session_state.user = username
                    st.success(f"{username}님 환영합니다!")
                    st.experimental_rerun()
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
            else:
                st.error("존재하지 않는 아이디입니다.")
        return False
    return True
