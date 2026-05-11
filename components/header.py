"""
components/header.py
ヘッダーバー（ロゴ + リアルタイム時計）
"""

import streamlit as st
from datetime import datetime


def _get_clock_html() -> str:
    """現在時刻・日付のHTMLを返す（JSで自動更新）"""
    now = datetime.now()
    days = ["月", "火", "水", "木", "金", "土", "日"]
    time_str = now.strftime("%H:%M")
    date_str = f"{now.month}月{now.day}日（{days[now.weekday()]}）"
    return f"""
    <div class="clock-area">
      <div class="clock-time" id="js-clock">{time_str}</div>
      <div class="clock-date" id="js-date">{date_str}</div>
    </div>
    <script>
      // Streamlitのリロードに頼らずJSで時計を更新
      (function tick() {{
        const now = new Date();
        const hh  = String(now.getHours()).padStart(2,'0');
        const mm  = String(now.getMinutes()).padStart(2,'0');
        const days = ['日','月','火','水','木','金','土'];
        const dateStr = (now.getMonth()+1)+'月'+now.getDate()+'日（'+days[now.getDay()]+'）';
        const el = document.getElementById('js-clock');
        const dl = document.getElementById('js-date');
        if (el) el.textContent = hh+':'+mm;
        if (dl) dl.textContent = dateStr;
        setTimeout(tick, 10000);  // 10秒ごとに更新
      }})();
    </script>
    """


def render_header() -> None:
    """ヘッダーバーを描画する"""
    st.markdown(f"""
    <div class="header-bar">
      <div class="logo-area">
        <div class="logo-icon">🏢</div>
        <div>
          <div class="logo-name">Reception AI</div>
          <div class="logo-sub">Smart Front Desk</div>
        </div>
      </div>
      {_get_clock_html()}
    </div>
    """, unsafe_allow_html=True)
