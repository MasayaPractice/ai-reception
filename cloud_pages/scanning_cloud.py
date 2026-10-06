"""
pages/scanning_cloud.py
顔認証スキャン画面（クラウド・iPad対応版）
insightface使用・Web Speech APIで音声読み上げ（女性音声・Kyoko）
【変更履歴】
- 顔認証前に担当者選択プルダウンを追加
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
    """iOS対応：D-ID事前生成動画で音声再生（display:none）"""
    import base64
    from pathlib import Path
    video_map = {
        "顔が検出できませんでした。もう一度お試しください。": "assets/avatar_error_noface.mp4",
        "申し訳ございません、顔認証できませんでした。手動にてご入力をお願いいたします。": "assets/avatar_error_noauth.mp4",
    }
    video_path_str = video_map.get(text)
    if not video_path_str:
        return
    video_path = Path(video_path_str)
    if video_path.exists():
        video_data = video_path.read_bytes()
        video_b64  = base64.b64encode(video_data).decode()
        st.markdown(f"""
        <video autoplay playsinline style="display:none;">
          <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        """, unsafe_allow_html=True)


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
            担当者を選択してから<br>カメラの正面に顔を向けてください
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 担当者選択プルダウン ──────────────────────────────
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            try:
                from components.db_cloud import get_active_staff
                staff_list = get_active_staff()
            except Exception:
                staff_list = []

            staff_list_filtered = [s for s in staff_list if s["name"] != "担当なし"]
            staff_options = [{"id": None, "name": "担当なし", "slack_user_id": ""}] + staff_list_filtered
            staff_names   = [s["name"] for s in staff_options]
            selected_idx  = st.selectbox(
                "担当者を選択してください",
                range(len(staff_names)),
                format_func=lambda i: staff_names[i],
                key="scan_staff_idx",
            )
            st.session_state.selected_staff = staff_options[selected_idx]

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_l2, col_c2, col_r2 = st.columns([1, 2, 1])
        with col_c2:
            if st.button("📷　顔認証をはじめる", key="scan_btn", use_container_width=True):
                st.session_state.scan_triggered = True
                st.rerun()

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_l3, col_c3, col_r3 = st.columns([1, 2, 1])
        with col_c3:
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
                            selected_staff = st.session_state.get("selected_staff", {})
                            person_id = result.get("person_id")
                            save_visitor(
                                name=result["name"],
                                company=result["company"],
                                visit_type="appointment",
                                contact_person=selected_staff.get("name", ""),
                                is_known=True,
                                face_registered=True,
                                person_id=person_id,
                            )
                            from components.db_cloud import get_visit_count
                            visit_count = get_visit_count(person_id)
                            st.session_state.visitor_name    = result["name"]
                            st.session_state.visitor_company = result["company"]
                            st.session_state.is_known        = True
                            st.session_state.visit_count     = visit_count
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
