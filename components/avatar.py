"""
components/avatar.py
アバター表示エリア
D-ID口パク動画（assets/avatar_talking.mp4）を使用
"""
import streamlit as st
import base64
from pathlib import Path

AVATAR_STATES = {
    "waiting":  {"label": "AIが待機中",   "image": "assets/avatar.png"},
    "greeting": {"label": "挨拶中",       "image": "assets/avatar.png"},
    "guiding":  {"label": "案内中",       "image": "assets/avatar.png"},
}

VIDEO_PATH = "assets/avatar_talking.mp4"


def render_status_badge(state: str = "waiting") -> None:
    label = AVATAR_STATES.get(state, AVATAR_STATES["waiting"])["label"]
    st.markdown(f"""
    <div style="display:flex;justify-content:center;margin-top:8px">
      <div class="status-badge">
        <div class="wave">
          <span></span><span></span><span></span><span></span><span></span>
        </div>
        {label}
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_avatar(state: str = "waiting") -> None:
    video_path = Path(VIDEO_PATH)
    if video_path.exists():
        video_data = video_path.read_bytes()
        video_b64  = base64.b64encode(video_data).decode()
        st.markdown(f"""
        <div class="avatar-section">
          <div class="avatar-placeholder" style="display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:50%;">
            <video autoplay loop muted playsinline
              style="width:100%;height:100%;object-fit:cover;object-position:center top;border-radius:50%;">
              <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
            </video>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        image_path = AVATAR_STATES.get(state, AVATAR_STATES["waiting"])["image"]
        if image_path and Path(image_path).exists():
            img_data = Path(image_path).read_bytes()
            img_b64  = base64.b64encode(img_data).decode()
            ext      = Path(image_path).suffix.lstrip(".")
            st.markdown(f"""
            <div class="avatar-section">
              <div class="avatar-placeholder" style="display:flex;align-items:center;justify-content:center;">
                <img src="data:image/{ext};base64,{img_b64}"
                     style="width:100%;height:100%;object-fit:cover;border-radius:50%;object-position:center 20%;
                            animation:floatY 5s ease-in-out infinite;" />
              </div>
            </div>
            """, unsafe_allow_html=True)
