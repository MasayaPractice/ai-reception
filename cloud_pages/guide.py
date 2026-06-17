"""
cloud_pages/guide.py
案内メッセージ画面（クラウド・iPad対応版）
iOS対応：D-ID音声付き動画で読み上げ
"""

import streamlit as st
import base64
from pathlib import Path
from components.header import render_header
from components.notification import notify_walkin, notify_appointment, notify_with_staff


GUIDE_MESSAGES = {
    "default":   "担当者がまいります\nしばらくお待ちください",
    "meeting_a": "会議室A へお進みください\n右手の廊下を直進です",
    "meeting_b": "会議室B へお進みください\nエレベーターで3階へ",
    "reception": "受付カウンターへお越しください",
}

VOICE_VIDEO_KNOWN = "assets/avatar_waiting.mp4"
VOICE_VIDEO_NEW   = "assets/avatar_newvisitor.mp4"


def _play_voice_video(video_path_str: str) -> None:
    """D-ID音声付き動画を非表示で再生（音声のみ使用）"""
    video_path = Path(video_path_str)
    if video_path.exists():
        video_data = video_path.read_bytes()
        video_b64  = base64.b64encode(video_data).decode()
        st.markdown(f"""
        <video autoplay playsinline style="display:none;">
          <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        """, unsafe_allow_html=True)


def _send_slack_notification(name: str, company: str, is_known: bool) -> None:
    visit_type    = st.session_state.get("visit_type", "walkin")
    contact       = st.session_state.get("contact_person", "")
    purpose       = st.session_state.get("visitor_purpose", "")
    selected_staff = st.session_state.get("selected_staff", {})

    if selected_staff:
        notify_with_staff(
            name=name, company=company, purpose=purpose,
            visit_type=visit_type, staff=selected_staff,
        )
    elif visit_type == "appointment":
        notify_appointment(name=name, company=company, contact=contact)
    else:
        notify_walkin(name=name, company=company,
                      purpose=purpose, contact=contact)


def render_guide() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)

    render_header()

    visitor_name    = st.session_state.get("visitor_name", "お客様")
    visitor_company = st.session_state.get("visitor_company", "")
    is_known        = st.session_state.get("is_known", False)

    if not st.session_state.get("slack_sent", False):
        _send_slack_notification(visitor_name, visitor_company, is_known)
        st.session_state.slack_sent = True

    if not st.session_state.get("voice_played", False):
        if is_known:
            _play_voice_video(VOICE_VIDEO_KNOWN)
        else:
            _play_voice_video(VOICE_VIDEO_NEW)
        st.session_state.voice_played = True

    if is_known:
        welcome_html = f"""
        <div class="guide-welcome known">
          <div class="guide-welcome-icon">✨</div>
          <div class="guide-welcome-name">{visitor_name} 様</div>
          <div class="guide-welcome-sub">お待ちしておりました</div>
          <div class="guide-welcome-company">{visitor_company}</div>
        </div>
        """
    else:
        welcome_html = f"""
        <div class="guide-welcome new">
          <div class="guide-welcome-icon">🌸</div>
          <div class="guide-welcome-name">{visitor_name} 様</div>
          <div class="guide-welcome-sub">はじめまして、ようこそ</div>
          <div class="guide-welcome-company">{visitor_company}</div>
        </div>
        """
    st.markdown(welcome_html, unsafe_allow_html=True)

    guide_key = st.session_state.get("guide_destination", "default")
    guide_msg = GUIDE_MESSAGES.get(guide_key, GUIDE_MESSAGES["default"])
    lines     = guide_msg.split("\n")

    st.markdown(f"""
    <div class="guide-message-card">
      <div class="guide-message-icon">🗺️</div>
      <div class="guide-message-main">{lines[0]}</div>
      {"<div class='guide-message-sub'>" + lines[1] + "</div>" if len(lines) > 1 else ""}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="guide-notified">
      <span style="color:#4caf50;">●</span>
      　担当者へ通知しました
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 3, 1])
    with col_c:
        if st.button("トップ画面に戻る", key="guide_back_btn",
                     use_container_width=True):
            for key in ["visitor_name", "visitor_company", "is_known",
                        "slack_sent", "voice_played", "guide_destination",
                        "avatar_state", "visitor_purpose", "contact_person",
                        "visit_type", "face_registered", "selected_staff"]:
                st.session_state.pop(key, None)
            st.session_state.page = "top"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
