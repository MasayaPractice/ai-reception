"""
components/notification.py
通知モジュール（Slack / 将来: Teams・Chatwork等）
SFC0009: 再訪者到着通知
SFC0010: 新規来訪者到着通知
"""

import os
import requests

from datetime import datetime




def _post_slack(text: str) -> None:
    """Slack Webhook へ POST する"""
    url = os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        print("[Slack] SLACK_WEBHOOK_URL が未設定です")
        return
    try:
        requests.post(url, json={"text": text}, timeout=5)
    except Exception as e:
        print(f"[Slack] 送信エラー: {e}")


def _now_str() -> str:
    """現在時刻を「14:32」形式で返す"""
    return datetime.now().strftime("%H:%M")


def notify_walkin(name: str, company: str, purpose: str, contact: str) -> None:
    """アポなし（飛び込み）来訪の通知 — SFC0010"""
    lines = [f"🚶 *{name}様*（{company}）が到着されました"]
    lines.append(f"種別：飛び込み　／　ご用件：{purpose}")
    if contact:
        lines.append(f"担当者：{contact}")
    lines.append(f"🕐 受付時刻：{_now_str()}")
    _post_slack("\n".join(lines))


def notify_appointment(name: str, company: str, contact: str) -> None:
    """アポあり来訪の通知 — SFC0009"""
    lines = [f"🤝 *{name}様*（{company}）が到着されました"]
    lines.append("種別：アポイントあり")
    if contact:
        lines.append(f"担当者：{contact}")
    lines.append(f"🕐 受付時刻：{_now_str()}")
    _post_slack("\n".join(lines))

def _post_slack_to_user(slack_user_id: str, text: str) -> None:
    """特定のSlackユーザーにDMで通知する"""
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        _post_slack(text)
        return
    try:
        requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {token}"},
            json={"channel": slack_user_id, "text": text},
            timeout=5,
        )
    except Exception as e:
        print(f"[Slack] DM送信エラー: {e}")


def notify_with_staff(name: str, company: str, purpose: str, visit_type: str, staff: dict) -> None:
    """担当者情報を使って通知する"""
    if visit_type == "appointment":
        lines = [f"\U0001f91d *{name}様*（{company}）が到着されました"]
        lines.append("種別：アポイントあり")
    else:
        lines = [f"\U0001f6b6 *{name}様*（{company}）が到着されました"]
        lines.append(f"種別：飛び込み　／　ご用件：{purpose}")

    staff_name = staff.get("name", "担当なし")
    if staff_name and staff_name != "担当なし":
        lines.append(f"担当者：{staff_name}")
    lines.append(f"\U0001f550 受付時刻：{_now_str()}")

    text = "\n".join(lines)
    slack_user_id = staff.get("slack_user_id", "")

    if slack_user_id:
        _post_slack_to_user(slack_user_id, text)
    else:
        _post_slack(text)
