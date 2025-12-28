import streamlit as st
import hashlib

def login():
    if 'user' not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
        return True

    st.subheader("로그인")
    username = st.text_input("사용자 이름")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        users = st.secrets["users"]
        if username in users:
            hashed_input = hashlib.sha256(password.encode()).hexdigest()
            if hashed_input == users[username]["password_hash"]:
                st.session_state.user = username
                st.experimental_rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
        else:
            st.error("사용자를 찾을 수 없습니다.")
    return False
