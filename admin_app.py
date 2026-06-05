"""
admin_app.py  ―  管理者専用エントリーポイント
実行: streamlit run admin_app.py --server.port 8502
"""

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="AI受付システム｜管理者",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def _load_css(path: str) -> None:
    css = Path(path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

_load_css("styles/main.css")

# ── セッション初期化 ──────────────────────────────────────────
defaults = {
    "page":     "admin_login",  # 管理者アプリは最初からログイン画面
    "is_admin": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── DB初期化 ──────────────────────────────────────────────────
from components.db_cloud import init_db
init_db()

# ── ルーティング（管理者画面のみ） ───────────────────────────
from pages.admin_login     import render_admin_login
from pages.admin_dashboard import render_admin_dashboard

ROUTES = {
    "admin_login":     render_admin_login,
    "admin_dashboard": render_admin_dashboard,
}

page_fn = ROUTES.get(st.session_state.page, render_admin_login)
page_fn()
