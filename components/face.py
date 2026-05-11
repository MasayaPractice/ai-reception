"""
components/face.py
顔認証コア処理
SFC0003: 顔特徴量抽出
SFC0004: 来訪者DB照合
SFC0007: 顔特徴量DB保存
"""
import cv2
import face_recognition
import numpy as np
import sqlite3
from pathlib import Path

DB_PATH = Path("data/visitors.db")
CAMERA_INDEX = 1       # 環境に合わせて変更（0 or 1 or 2）
TOLERANCE = 0.45       # 照合の閾値（低いほど厳格）
CAMERA_WARMUP = 1.5    # カメラ起動待機秒数


def capture_face_image():
    """
    カメラで1枚撮影してRGB画像を返す。
    失敗時は None を返す。
    """
    import time
    cap = cv2.VideoCapture(CAMERA_INDEX)
    time.sleep(CAMERA_WARMUP)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def extract_encoding(rgb_image) -> np.ndarray | None:
    """
    RGB画像から顔の特徴量（128次元）を抽出して返す。
    複数顔がある場合は最も大きい顔（カメラに最も近い人）を使用。
    顔が検出できない場合は None を返す。
    """
    locations = face_recognition.face_locations(rgb_image)
    if not locations:
        return None

    # 最も大きい顔を選ぶ（top, right, bottom, left）
    def face_area(loc):
        top, right, bottom, left = loc
        return (bottom - top) * (right - left)

    largest = max(locations, key=face_area)
    encodings = face_recognition.face_encodings(rgb_image, [largest])
    if not encodings:
        return None
    return encodings[0]


def save_face_encoding(visitor_id: int, encoding: np.ndarray) -> bool:
    """
    来訪者IDに紐づけて顔特徴量をDBに保存する。
    成功時は True を返す。
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                UPDATE visitors
                SET face_encoding = ?, face_registered = 1
                WHERE id = ?
            """, (encoding.tobytes(), visitor_id))
            conn.commit()
        return True
    except Exception:
        return False


def match_face(encoding: np.ndarray) -> dict | None:
    """
    特徴量をDBの全来訪者と照合し、一致する来訪者を返す。
    一致しない場合は None を返す。
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT id, name, company, face_encoding
            FROM visitors
            WHERE face_registered = 1 AND face_encoding IS NOT NULL
        """).fetchall()

    if not rows:
        return None

    known_encodings = []
    known_visitors  = []
    for row in rows:
        try:
            enc = np.frombuffer(row["face_encoding"], dtype=np.float64)
            known_encodings.append(enc)
            known_visitors.append(dict(row))
        except Exception:
            continue

    if not known_encodings:
        return None

    matches   = face_recognition.compare_faces(known_encodings, encoding, tolerance=TOLERANCE)
    distances = face_recognition.face_distance(known_encodings, encoding)

    if not any(matches):
        return None

    best_idx = int(np.argmin(distances))
    if matches[best_idx]:
        return known_visitors[best_idx]
    return None