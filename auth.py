import streamlit as st
import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def login():
    st.title("🔐 하늘꿈연동교회 부부청년부 회계관리")

    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        users = st.secrets.get("USERS", {})

        if username not in users:
            st.error("존재하지 않는 아이디입니다.")
            return False

        input_hash = hash_password(password)
        stored_hash = users[username]["password_hash"]

        if input_hash == stored_hash:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"{username}님 환영합니다 🙏")
            return True
        else:
            st.error("비밀번호가 올바르지 않습니다.")
            return False

    return False
