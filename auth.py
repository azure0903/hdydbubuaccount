import streamlit as st
import hashlib

def login():
    if "user" not in st.session_state:
        st.session_state.user = None

    users = st.secrets["users"]

    with st.form("login_form"):
        st.subheader("로그인")
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")

        if submitted:
            if username in users:
                hashed_input = hashlib.sha256(password.encode()).hexdigest()
                if hashed_input == users[username]["password_hash"]:
                    st.session_state.user = username
                    st.success(f"{username}님, 환영합니다!")
                    return True
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
            else:
                st.error("존재하지 않는 아이디입니다.")
            return False
    return st.session_state.user is not None
