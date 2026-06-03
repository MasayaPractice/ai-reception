"""
cloud_pages/new_visitor.py
アポイントなし（飛び込み）入力フォーム
クラウド・iPad対応版（insightface使用）
"""

import streamlit as st
from components.header import render_header
from components.db_cloud import save_visitor


def render_new_visitor() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)

    render_header()

    st.markdown('<div style="max-width:680px; margin:0 auto; width:100%;">', unsafe_allow_html=True)

    if st.button("← 戻る", key="back_btn"):
        for key in ["face_section_open", "face_registered", "captured_encoding"]:
            st.session_state.pop(key, None)
        st.session_state.page = "reception"
        st.rerun()

    st.markdown("""
    <div class="form-title-block">
      <div class="form-icon">👋</div>
      <div class="form-title">はじめまして</div>
      <div class="form-subtitle">Walk-in Visit</div>
      <div class="form-desc">お名前・会社名・ご用件をご入力ください</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="visitor-form-card" style="margin-top:0;">', unsafe_allow_html=True)

    company = st.text_input("会社名　／　Company", placeholder="例：株式会社〇〇", key="company_input")
    name = st.text_input("お名前　／　Name", placeholder="例：山田 太郎", key="name_input")
    purpose = st.selectbox("ご用件　／　Purpose", ["営業・提案", "納品・引き取り", "求人・採用関連", "その他"], key="purpose_input")
    contact_person = st.text_input("担当者名（わかる場合）　／　Contact Person", placeholder="例：鈴木（不明な場合は空欄）", key="contact_input")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown("---")

    register_face = st.checkbox("📷　顔画像登録がまだのお客様はこちらをチェックして登録をお願いします（任意・次回から自動受付）", key="register_face_check")

    st.markdown('</div>', unsafe_allow_html=True)

    if register_face:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        captured_encoding = st.session_state.get("captured_encoding", None)

        if captured_encoding is not None:
            st.markdown("""
            <div style="max-width:680px; margin:0 auto;
                        background:rgba(232,248,240,0.9);
                        border:1.5px solid rgba(74,165,107,0.3);
                        border-radius:16px; padding:20px; text-align:center;">
              <div style="font-size:32px; margin-bottom:8px;">✅</div>
              <div style="font-size:13px; font-weight:500; color:#1a5c35; letter-spacing:.1em;">
                顔写真の登録が完了しました
              </div>
              <div style="font-size:10px; color:#5a9a6e; margin-top:6px;">
                次回のご来訪から自動で受付できます
              </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            col_l, col_c, col_r = st.columns([1, 2, 1])
            with col_c:
                if st.button("撮り直す", key="retake_btn", use_container_width=True):
                    st.session_state.pop("captured_encoding", None)
                    st.rerun()
        else:
            st.markdown("""
            <div style="max-width:680px; margin:0 auto;
                        background:rgba(240,247,252,0.9);
                        border:1.5px solid rgba(74,127,165,0.2);
                        border-radius:16px; padding:20px; text-align:center;">
              <div style="font-size:36px; margin-bottom:8px;">📸</div>
              <div style="font-size:13px; font-weight:500; color:#1a2533; letter-spacing:.1em; margin-bottom:4px;">
                顔写真の撮影
              </div>
              <div style="font-size:10px; color:#8fa3b8; letter-spacing:.07em; line-height:1.8; margin-bottom:14px;">
                登録しておくと次回から自動で受付できます<br>
                顔写真は暗号化して保護されます 🔒
              </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            col_l, col_c, col_r = st.columns([1, 2, 1])
            with col_c:
                st.markdown("""
<style>
button[data-testid="stCameraInputButton"] {
    background-color: #5b8fa8 !important;
    color: transparent !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 10px 24px !important;
    font-size: 15px !important;
    width: 100% !important;
    cursor: pointer !important;
    position: relative !important;
}
button[data-testid="stCameraInputButton"]::before {
    content: "📷　撮影する";
    color: white;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    white-space: nowrap;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)
                img_file = st.camera_input("", key="face_camera")

            if img_file is not None:
                with st.spinner("顔を認識しています..."):
                    try:
                        import numpy as np
                        from PIL import Image
                        from components.face_cloud import extract_encoding
                        pil_image = Image.open(img_file).convert("RGB")
                        rgb = np.array(pil_image)
                        encoding = extract_encoding(rgb)
                        if encoding is None:
                            st.warning("顔が検出できませんでした。明るい場所でカメラの正面を向いて再度お試しください。")
                        else:
                            st.session_state.captured_encoding = encoding
                            st.rerun()
                    except Exception as e:
                        st.error(f"カメラの処理中にエラーが発生しました：{e}")

    error_placeholder = st.empty()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        submitted = st.button("登録して受付を完了する", key="submit_btn", use_container_width=True)

    if submitted:
        errors = []
        if not company.strip():
            errors.append("会社名を入力してください")
        if not name.strip():
            errors.append("お名前を入力してください")
        if errors:
            with error_placeholder:
                for e in errors:
                    st.error(e)
        else:
            captured_encoding = st.session_state.get("captured_encoding", None)
            face_registered = captured_encoding is not None
            visitor_id = save_visitor(
                name=name.strip(), company=company.strip(), visit_type="walkin",
                purpose=purpose, contact_person=contact_person.strip(),
                is_known=False, face_registered=face_registered,
            )
            if face_registered and visitor_id:
                from components.face_cloud import save_face_encoding
                save_face_encoding(visitor_id, captured_encoding)
            st.session_state.visitor_name    = name.strip()
            st.session_state.visitor_company = company.strip()
            st.session_state.visitor_purpose = purpose
            st.session_state.contact_person  = contact_person.strip()
            st.session_state.is_known        = False
            st.session_state.visit_type      = "walkin"
            st.session_state.face_registered = face_registered
            for key in ["face_section_open", "captured_encoding"]:
                st.session_state.pop(key, None)
            st.session_state.voice_played = False
            st.session_state.slack_sent   = False
            st.session_state.page = "guide"
            st.rerun()

    st.markdown('<div class="privacy-note">🔒　入力いただいた情報は暗号化して保護されます</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)