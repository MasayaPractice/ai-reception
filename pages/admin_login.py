"""
pages/admin_login.py
管理者ログイン画面
SFC0017: 管理画面ログイン認証
"""

import streamlit as st
from components.header import render_header
import hashlib
import os


# TODO: 本番では .env + bcrypt に移行する
# 現状は開発用のシンプルなハッシュ認証
_ADMIN_PASSWORD_HASH = hashlib.sha256(b"admin1234").hexdigest()


def _check_password(password: str) -> bool:
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return hashed == _ADMIN_PASSWORD_HASH


def render_admin_login() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)

    render_header()

    # ── 戻るボタン ───────────────────────────────────────────
    if st.button("← トップに戻る", key="admin_back"):
        st.session_state.page = "top"
        st.rerun()

    # ── タイトル ─────────────────────────────────────────────
    st.markdown("""
    <div class="form-title-block">
      <div class="form-icon">🔐</div>
      <div class="form-title">管理者ログイン</div>
      <div class="form-subtitle">Administrator Login</div>
      <div class="form-desc">管理者専用エリアです</div>
    </div>
    """, unsafe_allow_html=True)

    # ── ログインフォーム ─────────────────────────────────────
    st.markdown('<div class="visitor-form-card">', unsafe_allow_html=True)

    with st.form("admin_login_form"):
        admin_id = st.text_input(
            "管理者ID",
            placeholder="admin",
            key="admin_id_input",
        )
        password = st.text_input(
            "パスワード",
            type="password",
            placeholder="••••••••",
            key="admin_pw_input",
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("ログイン", use_container_width=True)

        if submitted:
            if admin_id.strip() == "admin" and _check_password(password):
                st.session_state.is_admin    = True
                st.session_state.page        = "admin_dashboard"
                st.rerun()
            else:
                st.error("IDまたはパスワードが正しくありません")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="privacy-note">
      開発中のデフォルトパスワード：admin1234
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
