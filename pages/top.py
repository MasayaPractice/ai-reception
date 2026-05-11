"""
pages/top.py
トップページ（待機画面）
SFC0002: AIアバター状態切替
"""

import streamlit as st
from components.header import render_header
from components.avatar import render_avatar, render_status_badge


def render_top() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)

    render_header()

    render_status_badge(state="waiting")

    avatar_state = st.session_state.get("avatar_state", "waiting")
    render_avatar(state=avatar_state)

    st.markdown("""
    <div class="welcome-block">
      <div class="welcome-main">いらっしゃいませ</div>
      <div class="welcome-en">Welcome</div>
      <div class="divider">
        <div class="div-line"></div>
        <div class="div-dot"></div>
        <div class="div-line"></div>
      </div>
      <div class="sub-msg">
        画面をタッチして受付を開始してください<br>AIがご案内いたします
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CTA：スキャン画面へ ───────────────────────────────────
    col_l, col_c, col_r = st.columns([1, 3, 1])
    with col_c:
        if st.button("▶  受付をはじめる", key="start_btn", use_container_width=True):
            # scan_triggered をリセットしてスキャン画面へ
            st.session_state.scan_triggered = False
            st.session_state.page = "scanning"
            st.rerun()

    st.markdown("""
    <div class="footer-hint">
      画面をタッチして開始
      <div class="page-dots">
        <div class="page-dot active"></div>
        <div class="page-dot"></div>
        <div class="page-dot"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
