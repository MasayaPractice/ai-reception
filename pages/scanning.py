"""
pages/scanning.py
顔認証スキャン中画面
SFC0001: カメラ自動検知
SFC0004: 来訪者DB照合

DETECTION_MODE:
  "button" → 今回実装。ボタン1回でスキャン開始
  "auto"   → 将来: threadingで常時監視
  "sensor" → 将来: 人感センサー連携
"""

import streamlit as st
import time
import subprocess
import threading
from components.header import render_header
from components.face import capture_face_image, extract_encoding, match_face
# --- 追加: データベース保存用 ---
from components.db import save_visitor 

DETECTION_MODE = "button"


def _speak(text: str) -> None:
    """音声読み上げ（osascript経由 - macOS Kyoko使用）"""
    def _run():
        try:
            subprocess.run(
                ["osascript", "-e", f'say "{text}" using "Kyoko"'],
                check=True
            )
        except Exception as e:
            print(f"[音声] エラー: {e}")
    threading.Thread(target=_run, daemon=True).start()


def render_scanning() -> None:
    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)

    render_header()

    scan_triggered = st.session_state.get("scan_triggered", False)

    if not scan_triggered:
        # ── スキャン前：カメラアイコンと説明 ────────────────
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
        # ── スキャン中：スピナー表示 → 自動で照合 ────────────
        st.markdown("""
        <div style="text-align:center; padding: 60px 0 32px;">
          <div style="font-size:64px; margin-bottom:20px;">🔍</div>
          <div style="font-size:22px; font-weight:300; color:#1a2533;
                      letter-spacing:0.16em; margin-bottom:12px;">
            認証中です...
          </div>
          <div style="font-size:13px; color:#8fa3b8; letter-spacing:0.08em;">
            そのままお待ちください
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("顔を認識しています..."):
            rgb = capture_face_image()

        # ── 撮影失敗 ─────────────────────────────────────────
        if rgb is None:
            st.error("カメラが起動できませんでした。しばらくお待ちください。")
            st.session_state.scan_triggered = False
            col_l, col_c, col_r = st.columns([1, 2, 1])
            with col_c:
                if st.button("再試行", key="retry_btn", use_container_width=True):
                    st.session_state.scan_triggered = True
                    st.rerun()
                if st.button("手動で受付する →", key="manual_err_btn", use_container_width=True):
                    st.session_state.page = "reception"
                    st.rerun()

        else:
            enc = extract_encoding(rgb)

            # ── 顔未検出 ─────────────────────────────────────
            if enc is None:
                st.warning("顔が検出できませんでした。明るい場所でカメラの正面を向いてください。")
                _speak("顔が検出できませんでした。明るい場所でカメラの正面を向いてください。")
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
                # ── DB照合 ───────────────────────────────────
                result = match_face(enc)

                if result:
                    # ✅ 一致 → セッションに保存
                    st.session_state.visitor_name    = result["name"]
                    st.session_state.visitor_company = result["company"]
                    st.session_state.is_known        = True
                    
                    # --- 追加: 管理者画面に表示されるようデータベースへ保存 ---
                    save_visitor(
                        name=result["name"],
                        company=result["company"],
                        visit_type="appointment", # 顔認証でもアポありとして扱う
                        contact_person="",         # DBに担当者情報があれば result.get("contact_person") に変更可
                        is_known=True,
                    )

                    st.session_state.scan_triggered  = False
                    st.session_state.voice_played    = False
                    st.session_state.slack_sent      = False
                    st.session_state.page            = "welcome_known"
                    st.rerun()

                else:
                    # ❌ 不一致 → メッセージ＋音声＋ボタン表示
                    st.session_state.scan_triggered = False
                    st.warning("申し訳ございません、顔認証できませんでした。手動にてご入力をお願いいたします。")
                    _speak("申し訳ございません、顔認証できませんでした。手動にてご入力をお願いいたします。")
                    col_l, col_c, col_r = st.columns([1, 2, 1])
                    with col_c:
                        if st.button("もう一度試す", key="retry3_btn", use_container_width=True):
                            st.session_state.scan_triggered = True
                            st.rerun()
                        if st.button("手動で受付する →", key="manual3_btn", use_container_width=True):
                            st.session_state.page = "reception"
                            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)