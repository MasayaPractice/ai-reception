"""
app_cloud.py ― クラウド・iPad用エントリーポイント
実行: Streamlit Cloudでこのファイルをデプロイする
既存のapp.pyは変更しない

【変更履歴】
- face.py が import cv2 をトップレベルで行うため、
  クラウド起動時にクラッシュする問題を回避。
  pages のimportを起動時一括 → ページ遷移時の遅延importに変更。
- app.py・scanning.py・face.py・db.py は一切変更していない。
"""

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="AI受付システム",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def _load_css(path: str) -> None:
    css = Path(path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

_load_css("styles/main.css")

defaults = {
    "page": "top",
    "avatar_state": "waiting",
    "is_admin": False,
    "scan_triggered": False,
    "slack_sent": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

from components.db import init_db
init_db()

# ▼ CLOUD: 起動時の一括importをやめて、ページ遷移時に個別importする
#   理由: face.py が `import cv2` をトップレベルで持つため、
#         起動時に全ページをimportするとクラウドでModuleNotFoundErrorが発生する

page = st.session_state.page

if page == "top":
    from pages.top import render_top
    render_top()

elif page == "scanning":
    from cloud_pages.scanning_cloud import render_scanning
    render_scanning()

elif page == "welcome_known":
    from cloud_pages.welcome_known import render_welcome_known
    render_welcome_known()

elif page == "reception":
    from pages.reception import render_reception
    render_reception()

elif page == "reception_appt":
    from pages.reception_appt import render_reception_appt
    render_reception_appt()

elif page == "new_visitor":
    from cloud_pages.new_visitor import render_new_visitor
    render_new_visitor()

elif page == "guide":
    from pages.guide import render_guide
    render_guide()

elif page == "admin_login":
    from pages.admin_login import render_admin_login
    render_admin_login()

elif page == "admin_dashboard":
    from pages.admin_dashboard import render_admin_dashboard
    render_admin_dashboard()

else:
    from pages.top import render_top
    render_top()
# ▲ CLOUD
