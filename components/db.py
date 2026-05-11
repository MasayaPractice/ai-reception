"""
components/db.py
来訪者データ管理モジュール
SFC0007: 来訪者情報DB登録
SFC0011: 来訪者一覧取得（管理者画面用）
将来の拡張:
- face_encoding カラム追加（SFC0003）
- face_registered カラム追加（SFC0006改）
- persons / visits テーブル分割（案B移行時）
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/visitors.db")


def init_db() -> None:
    """DBとテーブルを初期化する（起動時に1回呼ぶだけでOK）"""
    DB_PATH.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                name           TEXT    NOT NULL,
                company        TEXT,
                purpose        TEXT,
                contact_person TEXT,
                visit_type     TEXT    NOT NULL,  -- appointment / walkin
                is_known       INTEGER DEFAULT 0,  -- 0: 初回 / 1: 再訪
                face_registered INTEGER DEFAULT 0, -- 0: 未登録 / 1: 登録済み（将来）
                face_encoding  BLOB,               -- 顔特徴量（将来）
                visited_at     TEXT    NOT NULL
            )
        """)
        conn.commit()


def save_visitor(
    name: str,
    company: str,
    visit_type: str,
    purpose: str = "",
    contact_person: str = "",
    is_known: bool = False,
    face_registered: bool = False,
    face_encoding: bytes = None,
) -> int:
    """来訪者を保存してIDを返す"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO visitors
                (name, company, purpose, contact_person,
                 visit_type, is_known, face_registered, face_encoding, visited_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            company,
            purpose,
            contact_person,
            visit_type,
            1 if is_known else 0,
            1 if face_registered else 0,
            face_encoding,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        conn.commit()
        return cursor.lastrowid


def get_all_visitors(limit: int = 100) -> list[dict]:
    """来訪者一覧を取得する（管理者画面用）"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT * FROM visitors
            ORDER BY visited_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]


def get_visitor_by_name(name: str) -> dict | None:
    """名前で来訪者を検索する（将来: 再訪者判定用）"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("""
            SELECT * FROM visitors
            WHERE name = ?
            ORDER BY visited_at DESC
            LIMIT 1
        """, (name,)).fetchone()
        return dict(row) if row else None


def get_visitors_by_month() -> list[dict]:
    """月別来訪者数を集計する（管理者画面用）"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT
                strftime('%Y-%m', visited_at) AS month,
                COUNT(*) AS total,
                SUM(CASE WHEN visit_type = 'appointment' THEN 1 ELSE 0 END) AS appointments,
                SUM(CASE WHEN visit_type = 'walkin' THEN 1 ELSE 0 END) AS walkins
            FROM visitors
            GROUP BY month
            ORDER BY month DESC
        """).fetchall()
        return [dict(row) for row in rows]


def delete_visitor(visitor_id: int) -> bool:
    """来訪者をDBから削除する（管理者用）"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM visitors WHERE id = ?", (visitor_id,))
            conn.commit()
        return True
    except Exception:
        return False