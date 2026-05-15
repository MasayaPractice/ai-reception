"""
cloud_pages/welcome_known.py
再訪者ウェルカム画面（クラウド・iPad対応版）
Web Speech APIで音声読み上げ
"""

import streamlit as st
from components.header import render_header
from components.notification import notify_appointment


def _speak(text: str) -> None:
    """音声読み上げ（Web Speech API・iPad対応）"""
    js = f"""
    <script>
    (function() {{
        if (!window.parent.speechSynthesis) return;
        window.parent.speechSynthesis.cancel();
        var msg = new window.parent.SpeechSynthesisUtterance("{text}");
        msg.lang = 'ja-JP';
        msg.voiceURI = 'O-Ren';
        msg.rate = 0.9;
        msg.pitch = 1.0;
        setTimeout(function() {{
            window.parent.speechSynthesis.speak(msg);
        }}, 300);
    }})();
    </script>
    """
    st.components.v1.html(js, height=0)


def render_welcome_known() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)

    render_header()

    visitor_name    = st.session_state.get("visitor_name", "お客様")
    visitor_company = st.session_state.get("visitor_company", "")

    if not st.session_state.get("slack_sent", False):
        notify_appointment(
            name=visitor_name,
            company=visitor_company,
            contact="",
        )
        st.session_state.slack_sent = True

    if not st.session_state.get("voice_played", False):
        _speak(f"{visitor_name}様、お待ちしておりました。担当者がまいります。")
        st.session_state.voice_played = True

    st.markdown(f"""
    <div style="text-align:center; padding: 48px 0 24px;">
      <div style="font-size:56px; margin-bottom:16px;">✨</div>
      <div style="font-size:13px; color:#4a7fa5; letter-spacing:0.2em;
                  text-transform:uppercase; margin-bottom:12px;">
        Welcome Back
      </div>
      <div style="font-size:36px; font-weight:300; color:#1a2533;
                  letter-spacing:0.16em; margin-bottom:8px;">
        {visitor_name} 様
      </div>
      <div style="font-size:11px; color:#b0bec5; letter-spacing:0.18em;
                  text-transform:uppercase; margin-top:10px;">
        担当者
      </div>
      <div style="font-size:22px; color:#4a7fa5; letter-spacing:0.08em;
                  font-weight:400; margin-top:2px;">
        {visitor_company}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;
                width:200px; margin:0 auto 24px;">
      <div style="flex:1; height:1px;
                  background:linear-gradient(90deg,transparent,#8ab4d0,transparent);">
      </div>
      <div style="width:5px; height:5px; border-radius:50%;
                  background:#8ab4d0;"></div>
      <div style="flex:1; height:1px;
                  background:linear-gradient(90deg,transparent,#8ab4d0,transparent);">
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(255,255,255,0.92);
                border:1px solid rgba(74,127,165,0.16);
                border-radius:20px; padding:28px 24px;
                text-align:center; margin-bottom:16px;">
      <div style="font-size:28px; margin-bottom:12px;">🗺️</div>
      <div style="font-size:18px; font-weight:400; color:#1a2533;
                  letter-spacing:0.1em; line-height:1.7;">
        お待ちしておりました<br>担当者がまいります
      </div>
      <div style="font-size:12px; color:#8fa3b8; margin-top:10px;">
        そのままお待ちください
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; font-size:12px; color:#8fa3b8;
                letter-spacing:0.08em; margin-bottom:24px;">
      <span style="color:#4caf50;">●</span>　担当者へ通知しました
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-bottom:12px;
                font-size:12px; color:#8fa3b8;">
      表示が違う場合はこちら
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        if st.button("私ではありません", key="not_me_btn", use_container_width=True):
            for key in ["visitor_name", "visitor_company", "is_known", "slack_sent"]:
                st.session_state.pop(key, None)
            st.session_state.page = "reception"
            st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    col_l2, col_c2, col_r2 = st.columns([1, 2, 1])
    with col_c2:
        if st.button("トップ画面に戻る", key="top_btn", use_container_width=True):
            for key in ["visitor_name", "visitor_company", "is_known",
                        "slack_sent", "voice_played", "scan_triggered"]:
                st.session_state.pop(key, None)
            st.session_state.page = "top"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)