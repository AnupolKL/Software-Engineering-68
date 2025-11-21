from deepface import DeepFace
import cv2
from math import dist


def analyze_face_with_deepface(image_path: str):
    """
    ใช้ DeepFace วิเคราะห์รูปหน้า
    คืน dict: {"face_shape": ..., "gender": ..., "confidence": ...}
    - gender: male / female / unknown
    - face_shape: oval / round / square / oblong / heart / unknown
    """

    try:
        analysis = DeepFace.analyze(
            img_path=image_path,
            actions=['gender'],
            enforce_detection=True
        )

        if isinstance(analysis, list):
            analysis = analysis[0]

        # ---------- วิเคราะห์เพศ ----------
        gender = "unknown"
        confidence = 0.0

        gender_raw = analysis.get("gender")
        if isinstance(gender_raw, dict):
            man_score = float(gender_raw.get("Man", 0))
            woman_score = float(gender_raw.get("Woman", 0))
            # เอาแค่ถ้ามั่นใจเกิน 60%
            if man_score >= woman_score and man_score >= 60:
                gender = "male"
                confidence = man_score / 100.0
            elif woman_score > man_score and woman_score >= 60:
                gender = "female"
                confidence = woman_score / 100.0
            else:
                gender = "unknown"
                confidence = max(man_score, woman_score) / 100.0
        else:
            # fallback แบบหยาบ ๆ
            if str(gender_raw).lower().startswith("m"):
                gender = "male"
            elif str(gender_raw).lower().startswith("f"):
                gender = "female"
            confidence = 0.5

        # ---------- วิเคราะห์รูปหน้าแบบ conservative ----------
        region = analysis.get("region") or {}
        x, y, w, h = region.get("x"), region.get("y"), region.get("w"), region.get("h")

        face_shape = "unknown"
        if w and h and h != 0:
            ratio = w / h  # กว้าง / สูง

            # ถ้ากว้างใกล้เคียงสูงมาก ๆ → กลม
            if 0.9 <= ratio <= 1.1:
                face_shape = "round"
            # ถ้ายาวกว่ากว้างชัดเจน → oblong
            elif ratio < 0.75:
                face_shape = "oblong"
            # ถ้ากึ่งกลางไม่สุดโต่ง → oval
            else:
                face_shape = "oval"

        return {
            "face_shape": face_shape,
            "gender": gender,
            "confidence": confidence,
        }

    except Exception as e:
        print("DEEPFACE ERROR:", e)
        return {"face_shape": None, "gender": None, "confidence": 0.0}