import streamlit as st
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def login():
    # 이미 로그인 되어 있으면 바로 통과
    if st.session_state.get("authenticated", False):
        return True

    st.title("🔐 로그인")

    username = st.text_input("아이디", key="login_user")
    password = st.text_input("비밀번호", type="password", key="login_pw")

    if st.button("로그인"):
        users = st.secrets["users"]

        if username not in users:
            st.error("존재하지 않는 아이디입니다")
            return False

        input_hash = hash_password(password)
        saved_hash = users[username]["password_hash"]

        if input_hash == saved_hash:
            # ✅ 로그인 성공 처리
            st.session_state.authenticated = True
            st.session_state.user = username

            st.success(f"환영합니다, {username}님 👋")
            st.rerun()  # 🔥 이게 핵심
        else:
            st.error("비밀번호가 올바르지 않습니다")

    return False
