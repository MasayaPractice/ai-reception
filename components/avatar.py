"""
components/avatar.py
アバター表示エリア
将来: 動画ループ（st.video）やD-ID API連携もここに集約する
"""
import streamlit as st
import base64
from pathlib import Path

# アバターの状態定義
AVATAR_STATES = {
    "waiting":  {"label": "AIが待機中",   "image": "assets/avatar.png"},
    "greeting": {"label": "挨拶中",       "image": "assets/avatar.png"},
    "guiding":  {"label": "案内中",       "image": "assets/avatar.png"},
}

def render_status_badge(state: str = "waiting") -> None:
    """ステータスバッジ（波形アニメーション付き）を描画する"""
    label = AVATAR_STATES.get(state, AVATAR_STATES["waiting"])["label"]
    st.markdown(f"""
    <div style="display:flex;justify-content:center;margin-top:8px">
      <div class="status-badge">
        <div class="wave">
          <span></span><span></span><span></span><span></span><span></span>
        </div>
        {label}
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_avatar(state: str = "waiting") -> None:
    """
    アバターエリアを描画する。
    現状: 静止画アバター表示
    将来の拡張ポイント:
      - 状態別画像（avatar_waiting.png / avatar_greeting.png など）
      - st.video() で動画を再生
      - D-ID API レスポンスの動画URLを渡してリアルタイム再生
    """
    image_path = AVATAR_STATES.get(state, AVATAR_STATES["waiting"])["image"]

    if image_path and Path(image_path).exists():
        # ── 静止画アバター ────────────────────────────────────
        img_data = Path(image_path).read_bytes()
        img_b64  = base64.b64encode(img_data).decode()
        ext      = Path(image_path).suffix.lstrip(".")
        st.markdown(f"""
        <div class="avatar-section">
          <div class="avatar-placeholder" style="display:flex;align-items:center;justify-content:center;">
            <img src="data:image/{ext};base64,{img_b64}"
                 style="width:100%; height:100%; object-fit:cover; border-radius:50%;
                        animation:floatY 5s ease-in-out infinite;" />
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── プレースホルダー（画像がない場合） ────────────────
        st.markdown("""
        <div class="avatar-section">
          <div class="avatar-placeholder">
            <div class="avatar-glow"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)