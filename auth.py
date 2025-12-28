import streamlit as st
import hashlib

# ======================
# 로그인 처리 함수
# ======================
def login():
    if "user" not in st.session_state:
        st.session_state.user = None

    st.title("💒 하늘꿈연동교회 부부청년부 회계관리 로그인")

    username = st.text_input("사용자 이름")
    password = st.text_input("비밀번호", type="password")
    login_btn = st.button("로그인")

    if login_btn:
        users = st.secrets["users"]

        if username not in users:
            st.error("존재하지 않는 사용자입니다.")
            return False

        # 비밀번호 확인 (SHA256)
        entered_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        stored_hash = users[username]["password_hash"]

        if entered_hash != stored_hash:
            st.error("비밀번호가 올바르지 않습니다.")
            return False

        # 로그인 성공
        st.session_state.user = username
        st.success(f"환영합니다, {username}님!")
        st.experimental_rerun()  # 로그인 후 페이지 새로고침
        return True

    if st.session_state.user:
        return True

    return False

# ======================
# 삭제 권한 확인
# ======================
def can_delete(user):
    # 삭제 권한 사용자 정의
    allowed_users = ["도기웅", "김현주"]
    return user in allowed_users
