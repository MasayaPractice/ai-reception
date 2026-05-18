"""
components/db_cloud.py
来訪者データ管理モジュール（クラウド・Supabase対応版）
Mac版のdb.py（SQLite）とは別ファイル。Mac版は一切変更しない。
"""
import os
from datetime import datetime


def _get_client():
    """Supabaseクライアントを返す"""
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    return create_client(url, key)


def init_db() -> None:
    """Supabaseではテーブルは事前作成済みのため何もしない"""
    pass


def save_visitor(
    name: str,
    company: str,
    visit_type: str,
    purpose: str = "",
    contact_person: str = "",
    is_known: bool = False,
    face_registered: bool = False,
    face_encoding: bytes = None,
) -> int | None:
    """来訪者を保存してIDを返す"""
    try:
        client = _get_client()
        data = {
            "name": name,
            "company": company,
            "purpose": purpose,
            "contact_person": contact_person,
            "visit_type": visit_type,
            "is_known": is_known,
            "face_registered": face_registered,
            "visited_at": datetime.now().isoformat(),
        }
        result = client.table("visitors").insert(data).execute()
        if result.data:
            return result.data[0]["id"]
        return None
    except Exception as e:
        print(f"[DB] save_visitor エラー: {e}")
        return None


def save_face_encoding(visitor_id: int, encoding) -> bool:
    """顔特徴量をSupabaseに保存する"""
    try:
        import base64
        import numpy as np
        client = _get_client()
        # バイナリをbase64文字列に変換して保存
        enc_bytes = encoding.tobytes() if hasattr(encoding, 'tobytes') else encoding
        enc_b64 = base64.b64encode(enc_bytes).decode('utf-8')
        client.table("visitors").update({
            "face_encoding": enc_b64,
            "face_registered": True,
        }).eq("id", visitor_id).execute()
        return True
    except Exception as e:
        print(f"[DB] save_face_encoding エラー: {e}")
        return False


def get_all_visitors(limit: int = 100) -> list[dict]:
    """来訪者一覧を取得する（管理者画面用）"""
    try:
        client = _get_client()
        result = client.table("visitors").select("*").order(
            "visited_at", desc=True
        ).limit(limit).execute()
        return result.data or []
    except Exception as e:
        print(f"[DB] get_all_visitors エラー: {e}")
        return []


def get_visitors_by_month() -> list[dict]:
    """月別来訪者数を集計する（管理者画面用）"""
    try:
        visitors = get_all_visitors(limit=10000)
        monthly = {}
        for v in visitors:
            visited_at = v.get("visited_at", "")
            month = visited_at[:7] if visited_at else "不明"
            if month not in monthly:
                monthly[month] = {"month": month, "total": 0, "appointments": 0, "walkins": 0}
            monthly[month]["total"] += 1
            if v.get("visit_type") == "appointment":
                monthly[month]["appointments"] += 1
            else:
                monthly[month]["walkins"] += 1
        return sorted(monthly.values(), key=lambda x: x["month"], reverse=True)
    except Exception as e:
        print(f"[DB] get_visitors_by_month エラー: {e}")
        return []


def delete_visitor(visitor_id: int) -> bool:
    """来訪者をDBから削除する（管理者用）"""
    try:
        client = _get_client()
        client.table("visitors").delete().eq("id", visitor_id).execute()
        return True
    except Exception as e:
        print(f"[DB] delete_visitor エラー: {e}")
        return False


def get_face_encodings_for_matching() -> list[dict]:
    """顔認証照合用に顔特徴量を取得する"""
    try:
        client = _get_client()
        result = client.table("visitors").select(
            "id, name, company, face_encoding"
        ).eq("face_registered", True).execute()
        return result.data or []
    except Exception as e:
        print(f"[DB] get_face_encodings エラー: {e}")
        return []
