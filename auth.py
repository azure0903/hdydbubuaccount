import streamlit as st
import hashlib

def login():
    # 로그인 상태 체크용
    if 'user' not in st.session_state:
        st.session_state.user = None
        st.session_state.login_success = False  # 로그인 성공 여부

    # 로그인 UI
    if not st.session_state.login_success:
        st.markdown("## 🔐 하늘꿈연동교회 부부청년부 회계관리 로그인")
        st.caption("아이디와 비밀번호를 입력해주세요.")
        
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        login_btn = st.button("로그인")

        if login_btn:
            users = st.secrets["users"]
            if username in users:
                hashed_pw = hashlib.sha256(password.encode()).hexdigest()
                if hashed_pw == users[username]["password_hash"]:
                    st.session_state.user = username
                    st.session_state.login_success = True
                    st.success(f"{username}님 환영합니다!")
                    return True
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
            else:
                st.error("존재하지 않는 아이디입니다.")
        return False

    return True
