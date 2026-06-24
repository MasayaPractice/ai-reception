"""
components/db_cloud.py
来訪者データ管理モジュール（クラウド・Supabase対応版）
Mac版のdb.py（SQLite）とは別ファイル。Mac版は一切変更しない。
"""
import os
import streamlit as st
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
    person_id: str = None,
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
        if person_id:
            data["person_id"] = person_id
        result = client.table("visitors").insert(data).execute()
        if result.data:
            return result.data[0]["id"]
        return None
    except Exception as e:
        print(f"[DB] save_visitor エラー: {e}")
        return None


def save_face_encoding(visitor_id: int, encoding, person_id: str = None) -> bool:
    """顔特徴量をSupabaseに保存する（person_idも併せて保存）"""
    try:
        import base64
        import uuid
        client = _get_client()
        enc_bytes = encoding.tobytes() if hasattr(encoding, 'tobytes') else encoding
        enc_b64 = base64.b64encode(enc_bytes).decode('utf-8')
        if not person_id:
            person_id = str(uuid.uuid4())
        client.table("visitors").update({
            "face_encoding": enc_b64,
            "face_registered": True,
            "person_id": person_id,
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
            "id, name, company, face_encoding, person_id"
        ).eq("face_registered", True).execute()
        return result.data or []
    except Exception as e:
        print(f"[DB] get_face_encodings エラー: {e}")
        return []


def get_active_staff() -> list[dict]:
    """有効な担当者一覧を取得する"""
    try:
        client = _get_client()
        result = client.table("staff").select("*").eq(
            "is_active", True
        ).order("id").execute()
        return result.data or []
    except Exception as e:
        print(f"[DB] get_active_staff エラー: {e}")
        return []


def add_staff(name: str, slack_user_id: str) -> bool:
    """担当者を追加する"""
    try:
        client = _get_client()
        client.table("staff").insert({
            "name": name,
            "slack_user_id": slack_user_id,
            "is_active": True,
        }).execute()
        return True
    except Exception as e:
        print(f"[DB] add_staff エラー: {e}")
        return False


def update_staff(staff_id: int, name: str, slack_user_id: str, is_active: bool) -> bool:
    """担当者情報を更新する"""
    try:
        client = _get_client()
        client.table("staff").update({
            "name": name,
            "slack_user_id": slack_user_id,
            "is_active": is_active,
        }).eq("id", staff_id).execute()
        return True
    except Exception as e:
        print(f"[DB] update_staff エラー: {e}")
        return False


def delete_staff(staff_id: int) -> bool:
    """担当者を削除する"""
    try:
        client = _get_client()
        client.table("staff").delete().eq("id", staff_id).execute()
        return True
    except Exception as e:
        print(f"[DB] delete_staff エラー: {e}")
        return False


def get_visit_count(person_id: str) -> int:
    """person_idに紐づく来訪者の来訪回数を取得する（今回の来訪も含む）"""
    if not person_id:
        return 1
    try:
        client = _get_client()
        result = client.table("visitors").select("id").eq(
            "person_id", person_id
        ).execute()
        return len(result.data) if result.data else 1
    except Exception as e:
        print(f"[DB] get_visit_count エラー: {e}")
        return 1


def get_repeat_visitors() -> list[dict]:
    """常連客一覧を取得する（person_idごとに来訪回数を集計、2回目以上の人のみ）"""
    try:
        client = _get_client()
        result = client.table("visitors").select("*").execute()

        st.write(f"DEBUG raw count: {len(result.data) if result.data else 0}")
        if result.data:
            st.write(f"DEBUG sample row: {result.data[0]}")

        if not result.data:
            return []

        from collections import defaultdict
        grouped = defaultdict(list)
        for row in result.data:
            pid = row.get("person_id")
            if pid:
                grouped[pid].append(row)

        repeat_visitors = []
        for person_id, rows in grouped.items():
            if len(rows) >= 2:
                rows_sorted = sorted(rows, key=lambda r: r["visited_at"], reverse=True)
                latest = rows_sorted[0]
                repeat_visitors.append({
                    "name": latest["name"],
                    "company": latest["company"],
                    "visit_count": len(rows),
                    "last_visited_at": latest["visited_at"],
                })

        repeat_visitors.sort(key=lambda x: x["visit_count"], reverse=True)
        return repeat_visitors
    except Exception as e:
        print(f"[DB] get_repeat_visitors エラー: {e}")
        return []
