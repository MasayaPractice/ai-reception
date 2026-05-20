"""
pages/reception_appt.py
アポイントあり — 来訪者確認フォーム
"""
import streamlit as st
from components.header import render_header
from components.notification import notify_appointment
from components.db_cloud import save_visitor


def render_reception_appt() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)

    render_header()

    if st.button("← 戻る", key="appt_back"):
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

    st.markdown('<div class="visitor-form-card">', unsafe_allow_html=True)

    with st.form("appt_form", clear_on_submit=False):
        name = st.text_input(
            "お名前　／　Name",
            placeholder="例：山田 太郎",
            key="appt_name_input",
        )
        company = st.text_input(
            "会社名　／　Company（任意）",
            placeholder="例：株式会社〇〇",
            key="appt_company_input",
        )
        contact_person = st.text_input(
            "担当者名　／　Contact Person（任意）",
            placeholder="例：鈴木",
            key="appt_contact_input",
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "担当者に連絡する",
                use_container_width=True,
            )

        if submitted:
            if not name.strip():
                st.error("お名前を入力してください")
            else:
                st.session_state.visitor_name    = name.strip()
                st.session_state.visitor_company = company.strip()
                st.session_state.contact_person  = contact_person.strip()
                st.session_state.is_known        = True
                st.session_state.visit_type      = "appointment"

                save_visitor(
                    name=name.strip(),
                    company=company.strip(),
                    visit_type="appointment",
                    contact_person=contact_person.strip(),
                    is_known=True,
                )

                # Slack通知はguide.pyで行うため、ここでは送らない
                # notify_appointment(...)  ← 削除（二重送信防止）

                st.session_state.voice_played = False  # ← 追加
                st.session_state.slack_sent   = False  # ← 追加（二重送信防止）
                st.session_state.page = "guide"
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="privacy-note">
      🔒　入力いただいた情報は暗号化して保護されます
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)