import streamlit as st
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    st.title("🔐 로그인")

    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        users = st.secrets.get("USERS", {})

        if username in users:
            hashed_input_pw = hash_password(password)
            if hashed_input_pw == users[username]:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.success(f"{username}님 환영합니다 🙏")
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다")
        else:
            st.error("존재하지 않는 아이디입니다")

    return False
