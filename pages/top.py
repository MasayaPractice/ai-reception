"""
pages/top.py
トップページ（待機画面）
SFC0002: AIアバター状態切替
【変更履歴】
- 「はじめての方はこちら」ボタンを追加
- D-ID口パク動画 + Web Speech API音声を追加
- iOS対応：タップ時に音声発火するよう変更
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

    # iOS対応：画面タップ時に音声発火
    st.components.v1.html("""
    <script>
    (function() {
        function speakWelcome() {
            if (!window.speechSynthesis) return;
            if (window._welcomeSpoken) return;
            window._welcomeSpoken = true;
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("いらっしゃいませ。画面をタッチして受付をお始めください。");
            msg.lang = 'ja-JP';
            msg.rate = 0.9;
            function speak() {
                var voices = window.speechSynthesis.getVoices();
                var female = voices.find(function(v) { return v.name === 'Kyoko'; })
                          || voices.find(function(v) { return v.name === 'O-Ren'; })
                          || voices.find(function(v) { return v.lang.startsWith('ja'); });
                if (female) msg.voice = female;
                window.speechSynthesis.speak(msg);
            }
            if (window.speechSynthesis.getVoices().length > 0) {
                speak();
            } else {
                window.speechSynthesis.onvoiceschanged = speak;
            }
        }
        // 初回タップで音声発火
        window.parent.document.addEventListener('click', function onFirstClick() {
            speakWelcome();
            document.removeEventListener('click', onFirstClick);
        }, { once: true });
        // 初回タッチでも発火（iPad対応）
        window.parent.document.addEventListener('touchstart', function onFirstTouch() {
            speakWelcome();
            document.removeEventListener('touchstart', onFirstTouch);
        }, { once: true });
    })();
    </script>
    """, height=0)

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
