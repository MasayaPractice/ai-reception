"""
app.py  ―  エントリーポイント
役割: CSS読み込み・セッション初期化・ページルーティングのみ
実行: streamlit run app.py
"""

import streamlit as st
from pathlib import Path

# ── ページ設定（必ず最初） ────────────────────────────────────
st.set_page_config(
    page_title="AI受付システム",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS読み込み ───────────────────────────────────────────────
def _load_css(path: str) -> None:
    css = Path(path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

_load_css("styles/main.css")

# ── セッション初期化 ──────────────────────────────────────────
defaults = {
    "page":          "top",
    "avatar_state":  "waiting",
    "is_admin":      False,
    "scan_triggered": False,
    "slack_sent":    False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── DB初期化 ──────────────────────────────────────────────────
from components.db import init_db
init_db()

# ── ページルーティング ────────────────────────────────────────
from pages.top             import render_top
from pages.scanning        import render_scanning
from pages.welcome_known   import render_welcome_known
from pages.reception       import render_reception
from pages.reception_appt  import render_reception_appt
from pages.new_visitor     import render_new_visitor
from pages.guide           import render_guide
from pages.admin_login     import render_admin_login
from pages.admin_dashboard import render_admin_dashboard

ROUTES = {
    "top":              render_top,
    "scanning":         render_scanning,
    "welcome_known":    render_welcome_known,
    "reception":        render_reception,
    "reception_appt":   render_reception_appt,
    "new_visitor":      render_new_visitor,
    "guide":            render_guide,
    "admin_login":      render_admin_login,
    "admin_dashboard":  render_admin_dashboard,
}

page_fn = ROUTES.get(st.session_state.page, render_top)
page_fn()
