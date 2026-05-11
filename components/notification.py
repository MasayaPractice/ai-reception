"""
components/notification.py
通知モジュール（Slack / 将来: Teams・Chatwork等）
SFC0009: 再訪者到着通知
SFC0010: 新規来訪者到着通知
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


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