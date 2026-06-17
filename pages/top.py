"""
pages/top.py
トップページ（待機画面）
SFC0002: AIアバター状態切替
【変更履歴】
- iOS対応：「タップして開始」ボタン押下まで完全に静止画、押下後に動画再生
"""
import streamlit as st
import base64
from pathlib import Path
from components.header import render_header
from components.avatar import render_avatar, render_status_badge

WELCOME_VIDEO_PATH = "assets/avatar_top_welcome.mp4"
STATIC_IMAGE_PATH  = "assets/avatar.png"

def _render_static_avatar() -> None:
    """ボタン押下前：完全な静止画のみ表示（口パクなし）"""
    image_path = Path(STATIC_IMAGE_PATH)
    if image_path.exists():
        img_data = image_path.read_bytes()
        img_b64  = base64.b64encode(img_data).decode()
        ext      = image_path.suffix.lstrip(".")
        st.markdown(f"""
        <div class="avatar-section">
          <div class="avatar-placeholder" style="display:flex;align-items:center;justify-content:center;">
            <img src="data:image/{ext};base64,{img_b64}"
                 style="width:100%;height:100%;object-fit:cover;border-radius:50%;object-position:center 20%;" />
          </div>
        </div>
        """, unsafe_allow_html=True)

def render_top() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)
    render_header()
    render_status_badge(state="waiting")

    if not st.session_state.get("top_welcome_played", False):
        # ボタン押下前：完全な静止画のみ（口パクなし）
        _render_static_avatar()

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
            画面をタップして開始してください
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_l, col_c, col_r = st.columns([1, 3, 1])
        with col_c:
            if st.button("👆　タップして開始", key="tap_to_start_btn", use_container_width=True):
                st.session_state.top_welcome_played = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ボタン押下後：音声付き動画を再生
    video_path = Path(WELCOME_VIDEO_PATH)
    if video_path.exists():
        video_data = video_path.read_bytes()
        video_b64  = base64.b64encode(video_data).decode()
        st.markdown(f"""
        <div class="avatar-section">
          <div class="avatar-placeholder"
               style="display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:50%;">
            <video autoplay playsinline
              style="width:100%;height:100%;object-fit:cover;object-position:center top;border-radius:50%;">
              <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
            </video>
          </div>
        </div>
        """, unsafe_allow_html=True)
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
