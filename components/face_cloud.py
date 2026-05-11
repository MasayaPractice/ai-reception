"""
components/face_cloud.py
クラウド・iPad対応版の顔認証コア処理
st.camera_input() でiPadカメラを使用
"""
import cv2
import face_recognition
import numpy as np
import sqlite3
from pathlib import Path
import streamlit as st
from PIL import Image
import io

DB_PATH = Path("data/visitors.db")
TOLERANCE = 0.45

def capture_face_image():
    """
    st.camera_input()でiPadカメラから撮影してRGB画像を返す。
    ※ クラウド版：この関数はscanning.pyから直接呼ばず、
       scanning_cloud.pyでst.camera_input()を使う。
    """
    pass

def pil_to_rgb(pil_image) -> np.ndarray:
    """PIL画像をRGB numpy配列に変換"""
    return np.array(pil_image.convert("RGB"))

def extract_encoding(rgb_image) -> np.ndarray | None:
    locations = face_recognition.face_locations(rgb_image)
    if not locations:
        return None
    def face_area(loc):
        top, right, bottom, left = loc
        return (bottom - top) * (right - left)
    largest = max(locations, key=face_area)
    encodings = face_recognition.face_encodings(rgb_image, [largest])
    if not encodings:
        return None
    return encodings[0]

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
