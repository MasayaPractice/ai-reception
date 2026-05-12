"""
pages/scanning_cloud.py
顔認証スキャン画面（クラウド・iPad対応版）
Mac版scanning.pyのUIを踏襲
"""

import streamlit as st
from components.header import render_header
import numpy as np


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
        <div style="text-align:center; padding: 40px 0 24px;">
          <div style="font-size:64px; margin-bottom:20px;">📷</div>
          <div style="font-size:24px; font-weight:300; color:#1a2533;
                      letter-spacing:0.16em; margin-bottom:12px;">
            顔認証で受付
          </div>
          <div style="font-size:13px; color:#8fa3b8; letter-spacing:0.08em;">
            カメラの正面に顔を向けてください
          </div>
        </div>
        """, unsafe_allow_html=True)

        img_file = st.camera_input("　", label_visibility="collapsed")

        if img_file is not None:
            with st.spinner("顔を認識しています..."):
                try:
                    import face_recognition
                    from PIL import Image

                    pil_image = Image.open(img_file).convert("RGB")
                    rgb = np.array(pil_image)
                    locations = face_recognition.face_locations(rgb)

                    if not locations:
                        st.warning("顔が検出できませんでした。明るい場所でカメラの正面を向いてください。")
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
                        from components.face import extract_encoding, match_face
                        from components.db import save_visitor
                        enc = extract_encoding(rgb)
                        result = match_face(enc) if enc is not None else None

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
                    st.session_state.scan_triggered = False
                    st.session_state.page = "reception"
                    st.rerun()

        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            if st.button("キャンセル", key="cancel_btn", use_container_width=True):
                st.session_state.scan_triggered = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
