"""
components/face_cloud.py
クラウド・iPad対応版の顔認証コア処理
insightface buffalo_l使用
"""

import numpy as np
import sqlite3
from pathlib import Path

DB_PATH = Path("data/visitors.db")
THRESHOLD = 0.4


def _get_app():
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(640, 640))
    return app


def extract_encoding(rgb_image) -> np.ndarray | None:
    try:
        import cv2
        app = _get_app()
        bgr = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        faces = app.get(bgr)
        if not faces:
            return None
        largest = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
        return largest.embedding.astype(np.float32)
    except Exception:
        return None


def save_face_encoding(visitor_id: int, encoding: np.ndarray) -> bool:
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
                if enc.shape[0] == encoding.shape[0]:
                    known_encodings.append(enc)
                    known_visitors.append(dict(row))
            except Exception:
                continue

        if not known_encodings:
            return None

        best_dist = float("inf")
        best_idx = -1

        for i, known_enc in enumerate(known_encodings):
            norm_a = np.linalg.norm(encoding)
            norm_b = np.linalg.norm(known_enc)
            if norm_a == 0 or norm_b == 0:
                continue
            cosine_sim = np.dot(encoding, known_enc) / (norm_a * norm_b)
            dist = 1 - cosine_sim
            if dist < best_dist:
                best_dist = dist
                best_idx = i

        if best_dist <= THRESHOLD and best_idx >= 0:
            return known_visitors[best_idx]

        return None

    except Exception:
        return None
