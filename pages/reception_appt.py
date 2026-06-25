"""
pages/reception_appt.py
アポイントあり — 来訪者確認フォーム
【変更履歴】
- cloud_pages/new_visitor.py をベースに作成
- 顔認識を face_cloud.py（insightface）に統一
"""
import streamlit as st
from components.header import render_header
from components.db_cloud import save_visitor, get_active_staff


def render_reception_appt() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)

    render_header()

    st.markdown('<div style="max-width:680px; margin:0 auto; width:100%;">', unsafe_allow_html=True)

    if st.button("← 戻る", key="appt_back"):
        for key in ["face_section_open", "face_registered", "captured_encoding_appt"]:
            st.session_state.pop(key, None)
        st.session_state.page = "reception"
        st.rerun()

    st.markdown("""
    <div class="form-title-block">
      <div class="form-icon">🤝</div>
      <div class="form-title">アポイントのご確認</div>
      <div class="form-subtitle">Appointment Check-in</div>
      <div class="form-desc">お名前をご入力ください。担当者にご連絡いたします。</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="visitor-form-card" style="margin-top:0;">', unsafe_allow_html=True)

        name = st.text_input("お名前　／　Name", placeholder="例：山田 太郎", key="appt_name_input")
        name_kana = st.text_input("フリガナ　／　Furigana", placeholder="例：ヤマダ タロウ", key="appt_name_kana_input")
        company = st.text_input("会社名　／　Company（任意）", placeholder="例：株式会社〇〇", key="appt_company_input")
        staff_list = get_active_staff()
        staff_names = [s["name"] for s in staff_list]
        selected_staff_name = st.selectbox(
            "担当者　／　Contact Person",
            staff_names,
            key="appt_contact_input",
        )
        selected_staff = next((s for s in staff_list if s["name"] == selected_staff_name), {})
        contact_person = selected_staff_name

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.markdown("---")

        register_face = st.checkbox("📷　顔画像登録がまだのお客様はこちらをチェックして登録をお願いします　　　　　　　　　　　　（任意・次回から自動受付）", key="appt_register_face_check")
        st.markdown('</div>', unsafe_allow_html=True)

    if register_face:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        captured_encoding = st.session_state.get("captured_encoding_appt", None)

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
                if st.button("撮り直す", key="appt_retake_btn", use_container_width=True):
                    st.session_state.pop("captured_encoding_appt", None)
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
                img_file = st.camera_input("", key="appt_face_camera")

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
                            st.session_state.captured_encoding_appt = encoding
                            st.rerun()
                    except Exception as e:
                        st.error(f"カメラの処理中にエラーが発生しました：{e}")

    error_placeholder = st.empty()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        submitted = st.button("担当者に連絡する", key="appt_submit_btn", use_container_width=True)

    if submitted:
        if not name.strip():
            with error_placeholder:
                st.error("お名前を入力してください")
        else:
            captured_encoding = st.session_state.get("captured_encoding_appt", None)
            face_registered   = captured_encoding is not None

            visitor_id = save_visitor(
                name=name.strip(), company=company.strip(),
                visit_type="appointment", contact_person=contact_person.strip(),
                is_known=True, face_registered=face_registered,
                name_kana=name_kana.strip(),
            )

            if face_registered and visitor_id:
                from components.face_cloud import save_face_encoding
                save_face_encoding(visitor_id, captured_encoding)

            st.session_state.visitor_name    = name.strip()
            st.session_state.visitor_company = company.strip()
            st.session_state.contact_person  = contact_person.strip()
            st.session_state.is_known        = True
            st.session_state.visit_type      = "appointment"
            st.session_state.face_registered = face_registered

            for key in ["face_section_open", "captured_encoding_appt"]:
                st.session_state.pop(key, None)

            st.session_state.selected_staff   = selected_staff
            st.session_state.voice_played = False
            st.session_state.slack_sent   = False
            st.session_state.page = "guide"
            st.rerun()

    st.markdown('<div class="privacy-note">🔒　入力いただいた情報は暗号化して保護されます</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
