"""
pages/guide.py
案内メッセージ画面
SFC0005: 再訪者ウェルカム表示
SFC0008: 案内メッセージ表示
SFC0009/0010: Slack通知
"""

import streamlit as st
from components.header import render_header
from components.notification import notify_walkin, notify_appointment


# ── 案内メッセージ設定 ────────────────────────────────────────
GUIDE_MESSAGES = {
    "default":   "担当者がまいります\nしばらくお待ちください",
    "meeting_a": "会議室A へお進みください\n右手の廊下を直進です",
    "meeting_b": "会議室B へお進みください\nエレベーターで3階へ",
    "reception": "受付カウンターへお越しください",
}

def _speak(text: str) -> None:
    """音声読み上げ（Web Speech API・iPad対応）"""
    js = f"""
    <script>
    (function() {{
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{text}");
        msg.lang = 'ja-JP';
        msg.rate = 0.9;
        msg.pitch = 1.0;
        setTimeout(function() {{
            window.speechSynthesis.speak(msg);
        }}, 300);
    }})();
    </script>
    """
    st.components.v1.html(js, height=0)

def _send_slack_notification(name: str, company: str, is_known: bool) -> None:
    """Slack通知 SFC0009 / SFC0010"""
    visit_type = st.session_state.get("visit_type", "walkin")
    contact    = st.session_state.get("contact_person", "")
    purpose    = st.session_state.get("visitor_purpose", "")

    if visit_type == "appointment":
        notify_appointment(name=name, company=company, contact=contact)
    else:
        notify_walkin(name=name, company=company,
                      purpose=purpose, contact=contact)


def render_guide() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)

    render_header()

    # ── session_state から来訪者情報を取得 ──────────────────
    visitor_name    = st.session_state.get("visitor_name", "お客様")
    visitor_company = st.session_state.get("visitor_company", "")
    is_known        = st.session_state.get("is_known", False)

    # ── Slack通知（初回表示時のみ） ───────────────────────────
    if not st.session_state.get("slack_sent", False):
        _send_slack_notification(visitor_name, visitor_company, is_known)
        st.session_state.slack_sent = True

    # ── 音声読み上げ（初回表示時のみ） ───────────────────────
    if not st.session_state.get("voice_played", False):
        if is_known:
            voice_text = f"{visitor_name}様、お待ちしておりました。担当者がまいります。"
        else:
            voice_text = "ありがとうございます。担当者にご連絡いたします。しばらくお待ちください。"
        _speak(voice_text)
        st.session_state.voice_played = True

    # ── ウェルカムメッセージ ─────────────────────────────────
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

    # ── 案内メッセージカード ─────────────────────────────────
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

    # ── Slack通知済みバッジ ──────────────────────────────────
    st.markdown("""
    <div class="guide-notified">
      <span style="color:#4caf50;">●</span>
      　担当者へ通知しました
    </div>
    """, unsafe_allow_html=True)

    # ── トップに戻るボタン ────────────────────────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 3, 1])
    with col_c:
        if st.button("トップ画面に戻る", key="guide_back_btn",
                     use_container_width=True):
            for key in ["visitor_name", "visitor_company", "is_known",
                        "slack_sent", "voice_played", "guide_destination",
                        "avatar_state", "visitor_purpose", "contact_person",
                        "visit_type", "face_registered"]:
                st.session_state.pop(key, None)
            st.session_state.page = "top"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)