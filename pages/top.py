"""
pages/top.py
トップページ（待機画面）
SFC0002: AIアバター状態切替
【変更履歴】
- 「はじめての方はこちら」ボタンを追加
- iOS対応：D-ID音声付き動画（最初の1回）→無音ループ動画に切り替え
"""
import streamlit as st
import base64
from pathlib import Path
from components.header import render_header
from components.avatar import render_avatar, render_status_badge

WELCOME_VIDEO_PATH = "assets/avatar_top_welcome.mp4"

def _render_welcome_video() -> None:
    """初回案内：音声付き動画を1回だけ再生し、終了後に無音ループへ切り替え"""
    video_path = Path(WELCOME_VIDEO_PATH)
    if not video_path.exists():
        return
    video_data = video_path.read_bytes()
    video_b64  = base64.b64encode(video_data).decode()
    st.markdown(f"""
    <div class="avatar-section">
      <div class="avatar-placeholder" id="welcome-avatar-box"
           style="display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:50%;">
        <video id="welcome-video" autoplay playsinline
          style="width:100%;height:100%;object-fit:cover;object-position:center top;border-radius:50%;">
          <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
      </div>
    </div>
    <script>
    (function() {{
        var v = document.getElementById('welcome-video');
        if (v) {{
            v.addEventListener('ended', function() {{
                window._topWelcomeDone = true;
            }});
        }}
    }})();
    </script>
    """, unsafe_allow_html=True)

def render_top() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)
    render_header()
    render_status_badge(state="waiting")

    if not st.session_state.get("top_welcome_played", False):
        _render_welcome_video()
        st.session_state.top_welcome_played = True
    else:
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
    col_l, col_c, col_r = st.columns([1, 3, 1])
    with col_c:
        if st.button("📷　顔認証で受付する", key="start_btn", use_container_width=True):
            st.session_state.scan_triggered = False
            st.session_state.page = "scanning"
            st.rerun()
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("👋　はじめての方はこちら", key="new_visitor_btn", use_container_width=True):
            st.session_state.page = "reception"
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
