"""
components/face_cloud.py
クラウド・iPad対応版の顔認証コア処理
deepfaceを使用（dlibビルド不要）
face.py（Mac版）とDB互換性なし（encodingの形式が異なる）

【変更履歴】
- face-recognition → deepface に変更（Streamlit Cloudでのdlibビルドエラーのため）
- encoding形式: numpy float64配列（128次元）→ numpy float32配列（512次元, ArcFace）
- Mac版face.pyとのDB互換性なし（将来の共有時は変換スクリプトが必要）
"""

import numpy as np
import sqlite3
from pathlib import Path

DB_PATH = Path("data/visitors.db")
TOLERANCE = 0.6  # コサイン距離の閾値（低いほど厳格）


def extract_encoding(rgb_image) -> np.ndarray | None:
    """
    RGB画像から顔の特徴量を抽出して返す。
    deepface + ArcFaceモデルを使用。
    顔が検出できない場合は None を返す。
    """
    try:
        from deepface import DeepFace
        import cv2

        # BGRに変換してからdeepfaceに渡す
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

        result = DeepFace.represent(
            img_path=bgr_image,
            model_name="ArcFace",
            enforce_detection=True,
            detector_backend="opencv",
        )

        if not result:
            return None

        encoding = np.array(result[0]["embedding"], dtype=np.float32)
        return encoding

    except Exception:
        return None


def save_face_encoding(visitor_id: int, encoding: np.ndarray) -> bool:
    """
    来訪者IDに紐づけて顔特徴量をDBに保存する。
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
    コサイン類似度で照合。
    """
    try:
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
        known_visitors = []

        for row in rows:
            try:
                enc = np.frombuffer(row["face_encoding"], dtype=np.float32)
                if enc.shape[0] == encoding.shape[0]:  # 同じ次元のみ照合
                    known_encodings.append(enc)
                    known_visitors.append(dict(row))
            except Exception:
                continue

        if not known_encodings:
            return None

        # コサイン類似度で照合
        best_score = -1
        best_idx = -1

        for i, known_enc in enumerate(known_encodings):
            # コサイン類似度
            dot = np.dot(encoding, known_enc)
            norm = np.linalg.norm(encoding) * np.linalg.norm(known_enc)
            if norm == 0:
                continue
            similarity = dot / norm

            if similarity > best_score:
                best_score = similarity
                best_idx = i

        # 閾値以上なら一致と判定
        if best_score >= TOLERANCE and best_idx >= 0:
            return known_visitors[best_idx]

        return None

    except Exception:
        return None
