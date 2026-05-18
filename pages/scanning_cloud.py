"""
pages/scanning_cloud.py
顔認証スキャン画面（クラウド・iPad対応版）
insightface使用・Web Speech APIで音声読み上げ
Mac版 scanning.py と同じUX・UI
"""

import streamlit as st
from components.header import render_header
import numpy as np


AUTO_CAPTURE_JS = """
<script>
(function() {
    function tryCapture() {
        const btns = window.parent.document.querySelectorAll('button');
        for (const btn of btns) {
            if (btn.innerText && btn.innerText.includes('Take Photo')) {
                btn.style.display = 'none';
                setTimeout(() => btn.click(), 1500);
                return;
            }
        }
        setTimeout(tryCapture, 300);
    }
    tryCapture();
})();
</script>
"""


def _speak(text: str) -> None:
    """Web Speech APIで音声読み上げ（iPad・ブラウザ対応、Mac版osascriptの代替）"""
    js = f"""
    <script>
    (function() {{
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{text}");
        msg.lang = 'ja-JP';
        msg.rate = 0.9;
        msg.pitch = 1.0;
        // iPad/iOSでは音声リストが遅延ロードされるため少し待つ
        setTimeout(function() {{
            window.speechSynthesis.speak(msg);
        }}, 300);
    }})();
    </script>
    """
    st.components.v1.html(js, height=0)


def render_scanning() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)
    render_header()

    scan_triggered = st.session_state.get("scan_triggered", False)

    if not scan_triggered:
        st.markdown("""
        <div style="text-align:center; padding: 60px 0 32px;">
          <div style="font-size:64px; margin-bottom:20px;">📷</div>
          <div style="font-size:24px; font-weight:300; color:#1a2533;
                      letter-spacing:0.16em; margin-bottom:12px;">
            顔認証で受付
          </div>
          <div style="font-size:13px; color:#8fa3b8; letter-spacing:0.08em;
                      line-height:1.9;">
            カメラの正面に顔を向けて<br>下のボタンを押してください
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            if st.button("📷　顔認証をはじめる", key="scan_btn", use_container_width=True):
                st.session_state.scan_triggered = True
                st.rerun()

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_l2, col_c2, col_r2 = st.columns([1, 2, 1])
        with col_c2:
            if st.button("手動で受付する →", key="manual_btn", use_container_width=True):
                st.session_state.scan_triggered = False
                st.session_state.page = "reception"
                st.rerun()

    else:
        st.markdown("""
        <div style="text-align:center; padding: 40px 0 16px;">
          <div style="font-size:64px; margin-bottom:20px;">🔍</div>
          <div style="font-size:22px; font-weight:300; color:#1a2533;
                      letter-spacing:0.16em; margin-bottom:8px;">
            認証中です...
          </div>
          <div style="font-size:13px; color:#8fa3b8; letter-spacing:0.08em;">
            そのままお待ちください
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.components.v1.html(AUTO_CAPTURE_JS, height=0)
        img_file = st.camera_input("　", label_visibility="collapsed")

        if img_file is not None:
            with st.spinner("顔を認識しています..."):
                try:
                    from PIL import Image
                    from components.face_cloud import extract_encoding, match_face
                    from components.db_cloud import save_visitor

                    pil_image = Image.open(img_file).convert("RGB")
                    rgb = np.array(pil_image)
                    enc = extract_encoding(rgb)

                    if enc is None:
                        st.warning("顔が検出できませんでした。明るい場所でカメラの正面を向いてください。")
                        _speak("顔が検出できませんでした。もう一度お試しください。")
                        st.session_state.scan_triggered = False
                        col_l, col_c, col_r = st.columns([1, 2, 1])
                        with col_c:
                            if st.button("もう一度試す", key="retry2_btn", use_container_width=True):
                                st.session_state.scan_triggered = True
                                st.rerun()
                            if st.button("手動で受付する →", key="manual2_btn", use_container_width=True):
                                st.session_state.page = "reception"
                                st.rerun()
                    else:
                        result = match_face(enc)

                        if result:
                            save_visitor(
                                name=result["name"],
                                company=result["company"],
                                visit_type="appointment",
                                contact_person="",
                                is_known=True,
                            )
                            st.session_state.visitor_name    = result["name"]
                            st.session_state.visitor_company = result["company"]
                            st.session_state.is_known        = True
                            st.session_state.scan_triggered  = False
                            st.session_state.voice_played    = False
                            st.session_state.slack_sent      = False
                            st.session_state.page            = "welcome_known"
                            st.rerun()
                        else:
                            st.warning("申し訳ございません、顔認証できませんでした。手動にてご入力をお願いいたします。")
                            _speak("申し訳ございません、顔認証できませんでした。手動にてご入力をお願いいたします。")
                            st.session_state.scan_triggered = False
                            col_l, col_c, col_r = st.columns([1, 2, 1])
                            with col_c:
                                if st.button("もう一度試す", key="retry3_btn", use_container_width=True):
                                    st.session_state.scan_triggered = True
                                    st.rerun()
                                if st.button("手動で受付する →", key="manual3_btn", use_container_width=True):
                                    st.session_state.page = "reception"
                                    st.rerun()

                except Exception as e:
                    st.error(f"エラーが発生しました：{e}")
                    st.session_state.scan_triggered = False
                    col_l, col_c, col_r = st.columns([1, 2, 1])
                    with col_c:
                        if st.button("もう一度試す", key="retry_err_btn", use_container_width=True):
                            st.session_state.scan_triggered = True
                            st.rerun()
                        if st.button("手動で受付する →", key="manual_err_btn", use_container_width=True):
                            st.session_state.page = "reception"
                            st.rerun()

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            if st.button("キャンセル", key="cancel_btn", use_container_width=True):
                st.session_state.scan_triggered = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
