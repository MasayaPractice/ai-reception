"""
pages/admin_dashboard.py
管理者ダッシュボード
SFC0011: 来訪者一覧
SFC0018: 来訪ログ参照
"""

import streamlit as st
import csv
import io
from components.header import render_header
from components.db_cloud import get_all_visitors, get_visitors_by_month, delete_visitor, get_active_staff, add_staff, delete_staff
from datetime import datetime


def _require_admin() -> bool:
    if not st.session_state.get("is_admin", False):
        st.session_state.page = "admin_login"
        st.rerun()
        return False
    return True


def _export_csv(visitors: list) -> bytes:
    """来訪者データをCSV形式に変換する"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "氏名", "会社名", "用件", "担当者", "種別", "顔登録", "来訪日時"])
    for v in visitors:
        writer.writerow([
            v["id"],
            v["name"],
            v["company"] or "",
            v.get("purpose") or "",
            v.get("contact_person") or "",
            "アポあり" if v["visit_type"] == "appointment" else "飛び込み",
            "済" if v.get("face_registered") else "未",
            v["visited_at"][:16],
        ])
    return output.getvalue().encode("utf-8-sig")  # Excel対応BOM付き


def render_admin_dashboard() -> None:
    if not _require_admin():
        return

    st.markdown('<div class="reception-wrapper">', unsafe_allow_html=True)

    render_header()

    # ── ヘッダー行 ───────────────────────────────────────────
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.markdown("""
        <div style="padding: 12px 0 8px;">
          <span style="font-size:13px; font-weight:500;
                       color:#4a7fa5; letter-spacing:0.08em;">
            管理者ダッシュボード
          </span>
        </div>
        """, unsafe_allow_html=True)
    with col_logout:
        if st.button("ログアウト", key="logout_btn"):
            st.session_state.is_admin = False
            st.session_state.page = "top"
            st.rerun()

    # ── DBからデータ取得 ─────────────────────────────────────
    visitors = get_all_visitors(limit=500)
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_visitors = [v for v in visitors if v["visited_at"].startswith(today_str)]

    # ── サマリーカード ───────────────────────────────────────
    st.markdown(f"""
    <div class="admin-summary-row">
      <div class="admin-summary-card">
        <div class="admin-summary-num">{len(today_visitors)}</div>
        <div class="admin-summary-label">本日の来訪者数</div>
      </div>
      <div class="admin-summary-card">
        <div class="admin-summary-num">{len(visitors)}</div>
        <div class="admin-summary-label">累計来訪者数</div>
      </div>
      <div class="admin-summary-card">
        <div class="admin-summary-num">
          <span style="color:#4caf50; font-size:14px;">●</span> 正常
        </div>
        <div class="admin-summary-label">カメラ状態</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── CSVエクスポートボタン ────────────────────────────────
    if visitors:
        csv_data = _export_csv(visitors)
        filename = f"来訪者一覧_{datetime.now().strftime('%Y%m%d')}.csv"
        st.download_button(
            label="📥 CSVエクスポート（全来訪者）",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            key="csv_export_btn",
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── タブ ─────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 本日", "📋 全来訪者", "📊 月別集計", "⭐ 常連客", "👥 担当者管理"])

    with tab1:
        _render_visitor_table(today_visitors, empty_msg="本日の来訪者はまだいません", tab="today")

    with tab2:
        _render_visitor_table(visitors, empty_msg="来訪者データがありません", tab="all")

    with tab3:
        _render_monthly_summary()

    with tab4:
        _render_repeat_visitors()
    with tab5:
        _render_staff_management()

    st.markdown('</div>', unsafe_allow_html=True)


def _render_repeat_visitors() -> None:
    """常連客一覧を表示する"""
    from components.db_cloud import get_repeat_visitors

    st.markdown(
        "<div style='font-size:13px; color:#8fa3b8; margin-bottom:12px;'>"
        "※2回以上ご来訪いただいた方を表示しています"
        "</div>",
        unsafe_allow_html=True,
    )

    repeat_visitors = get_repeat_visitors()

    if not repeat_visitors:
        st.info("常連のお客様はまだいません")
        return

    for v in repeat_visitors:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.9); border:1px solid rgba(74,127,165,0.15);
                    border-radius:12px; padding:14px 18px; margin-bottom:8px;
                    display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-size:15px; font-weight:500; color:#1a2533;">{v['name']} 様</div>
            <div style="font-size:12px; color:#8fa3b8;">{v['company']}</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:18px; font-weight:600; color:#4a7fa5;">{v['visit_count']}回</div>
            <div style="font-size:11px; color:#b0bec5;">最終来訪：{v['last_visited_at'][:10]}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)


def _render_visitor_table(visitors: list, empty_msg: str, tab: str) -> None:
    """来訪者テーブルを描画する"""
    if not visitors:
        st.info(empty_msg)
        return

    for i, v in enumerate(visitors):
        with st.container(border=True):
            col_name, col_badges = st.columns([3, 2])

            with col_name:
                st.markdown(f"**{v['name']} 様**")

            with col_badges:
                if v["visit_type"] == "appointment":
                    visit_badge = "<span style='background:#e8f4fd;color:#4a7fa5;border-radius:8px;padding:2px 10px;font-size:11px;'>🤝 アポあり</span>"
                else:
                    visit_badge = "<span style='background:#f0f8ee;color:#5a9a4a;border-radius:8px;padding:2px 10px;font-size:11px;'>🚶 飛び込み</span>"

                if v.get("face_registered"):
                    face_badge = "<span style='background:#fff3e0;color:#e65100;border-radius:8px;padding:2px 10px;font-size:11px;margin-left:6px;'>📷 顔登録済み</span>"
                else:
                    face_badge = ""

                st.markdown(
                    f"<div style='display:flex;gap:6px;align-items:center;justify-content:flex-end;'>{visit_badge}{face_badge}</div>",
                    unsafe_allow_html=True
                )

            st.caption(
                f"🏢 {v['company'] or '—'}　"
                f"📋 用件：{v.get('purpose') or '—'}　"
                f"担当者：{v.get('contact_person') or '—'}　"
                f"🕐 {v['visited_at'][:16]}"
            )

            # ── 削除ボタン ────────────────────────────────────
            col_spacer, col_del = st.columns([4, 1])
            with col_del:
                key = f"del_{tab}_{v['id']}_{i}"
                confirm_key = f"confirm_{tab}_{v['id']}_{i}"

                if st.session_state.get(confirm_key):
                    st.warning("本当に削除しますか？")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("削除する", key=f"yes_{key}", type="primary"):
                            delete_visitor(v["id"])
                            st.session_state.pop(confirm_key, None)
                            st.rerun()
                    with col_no:
                        if st.button("キャンセル", key=f"no_{key}"):
                            st.session_state.pop(confirm_key, None)
                            st.rerun()
                else:
                    if st.button("🗑️ 削除", key=key):
                        st.session_state[confirm_key] = True
                        st.rerun()


def _render_monthly_summary() -> None:
    """月別集計を描画する"""
    monthly = get_visitors_by_month()

    if not monthly:
        st.info("データがありません")
        return

    for row in monthly:
        year, month = row["month"].split("-")
        month_label = f"{year}年{int(month)}月"

        total    = row["total"]
        appt     = row["appointments"]
        walk     = row["walkins"]
        appt_pct = int(appt / total * 100) if total > 0 else 0

        with st.container(border=True):
            st.markdown(f"**📅 {month_label}　{total} 件**")

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.metric("🤝 アポあり", f"{appt} 件")
            with col2:
                st.metric("🚶 飛び込み", f"{walk} 件")
            with col3:
                st.metric("アポあり率", f"{appt_pct}%")

            st.caption(f"アポあり {appt_pct}%　／　飛び込み {100 - appt_pct}%")
            st.progress(appt_pct / 100)

def _render_staff_management() -> None:
    """担当者管理タブを描画する"""
    st.markdown("### 担当者一覧")

    staff_list = get_active_staff()

    for s in staff_list:
        with st.container(border=True):
            col_name, col_slack, col_del = st.columns([2, 3, 1])
            with col_name:
                st.markdown(f"**{s['name']}**")
            with col_slack:
                st.caption(f"Slack ID: {s['slack_user_id'] or '未設定'}")
            with col_del:
                if s['name'] != '担当なし':
                    if st.button("🗑️", key=f"del_staff_{s['id']}"):
                        delete_staff(s['id'])
                        st.rerun()

    st.markdown("---")
    st.markdown("### 担当者を追加")

    with st.form("add_staff_form", clear_on_submit=True):
        new_name = st.text_input("担当者名", placeholder="例：山田")
        new_slack_id = st.text_input("Slack ユーザーID", placeholder="例：UXXXXXXXX")
        submitted = st.form_submit_button("追加する")

        if submitted:
            if not new_name.strip():
                st.error("担当者名を入力してください")
            else:
                if add_staff(new_name.strip(), new_slack_id.strip()):
                    st.success(f"✅ {new_name} を追加しました")
                    st.rerun()
                else:
                    st.error("追加に失敗しました")
