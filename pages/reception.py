"""
pages/reception.py
受付選択画面 — アポあり / なし で行き先を分岐
"""
import streamlit as st
from components.header import render_header
from components.avatar import render_status_badge


def render_reception() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)

    render_header()
    render_status_badge(state="waiting")

    st.markdown("""
    <div class="welcome-block" style="margin-top:24px;">
      <div class="welcome-main" style="font-size:28px;">ご用件をお選びください</div>
      <div class="welcome-en">Please select your purpose</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("""
        <div class="purpose-card">
          <div class="purpose-icon">🤝</div>
          <div class="purpose-title">アポイントあり</div>
          <div class="purpose-desc">ご予約・お打ち合わせの方</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("こちらへ →", key="appt_btn", use_container_width=True):
            st.session_state.visit_type = "appointment"
            st.session_state.page = "reception_appt"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="purpose-card">
          <div class="purpose-icon">🚶</div>
          <div class="purpose-title">アポイントなし</div>
          <div class="purpose-desc">飛び込みでのご来訪の方</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("こちらへ →", key="walkin_btn", use_container_width=True):
            st.session_state.visit_type = "walkin"
            st.session_state.page = "new_visitor"
            st.rerun()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    col_l2, col_c2, col_r2 = st.columns([1, 3, 1])
    with col_c2:
        if st.button("← トップに戻る", key="reception_back", use_container_width=True):
            st.session_state.page = "top"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)