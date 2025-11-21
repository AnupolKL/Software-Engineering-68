import requests
from django.conf import settings


def analyze_with_eden(image_file):
    """
    ใช้ Eden AI วิเคราะห์รูปหน้า: gender + bounding box
    คืน dict {"face_shape": str|None, "gender": str|None}
    """

    if not settings.EDENAI_API_KEY:
        raise RuntimeError("EDENAI_API_KEY is not set")

    # ✅ endpoint ที่ถูกต้อง (มี /image/ และมี / ปิดท้าย)
    url = "https://api.edenai.run/v2/image/face_detection/"

    headers = {
        "Authorization": f"Bearer {settings.EDENAI_API_KEY}",
        # อย่าระบุ content-type เอง ปล่อยให้ requests จัดการ multipart/form-data ให้
    }

    # EdenAI ต้องการ field ชื่อ "file" (ไม่ใช่ "files")
    files = {
        "file": (image_file.name, image_file.read(), image_file.content_type or "image/jpeg")
    }

    # body เป็น form data ปกติ
    data = {
        "providers": "amazon,google",   # เลือก provider ที่ EdenAI รองรับ
        "response_as_dict": "true",
        "attributes_as_list": "true",
        "show_base_64": "false",
        "show_original_response": "false",
    }

    resp = requests.post(url, headers=headers, data=data, files=files, timeout=60)
    resp.raise_for_status()
    result = resp.json()

    # ----------------- เลือก provider ที่ success ตัวแรก -----------------
    provider_data = None
    provider_name = None
    for provider_name, v in result.items():
        if isinstance(v, dict) and v.get("status") == "success":
            provider_data = v
            break

    if not provider_data:
        # ไม่มี provider ไหน success เลย
        print("EDEN DEBUG: no provider success", result)
        return {"face_shape": None, "gender": None}

    items = provider_data.get("items") or []
    if not items:
        return {"face_shape": None, "gender": None}

    face = items[0]  # สมมติใช้ใบหน้าแรก

    # ----------------- gender -----------------
    gender = None
    if "gender" in face and isinstance(face["gender"], list) and face["gender"]:
        best = max(face["gender"], key=lambda g: g.get("score", 0))
        if best.get("score", 0) >= 0.6:
            gender_label = (best.get("label") or "").lower()
            if "male" in gender_label:
                gender = "male"
            elif "female" in gender_label:
                gender = "female"

    # ----------------- face shape แบบ strict จากอัตราส่วนใบหน้า -----------------
    face_shape = None
    box = face.get("bbox") or face.get("bounding_box") or {}
    w = box.get("w") or box.get("width")
    h = box.get("h") or box.get("height")

    if w and h and h != 0:
        ratio = w / h  # กว้าง / สูง

        # rule เข้ม ๆ แบบเดิม
        if 0.95 <= ratio <= 1.1:
            face_shape = "round"
        elif ratio <= 0.75:
            face_shape = "oblong"
        elif 0.75 < ratio < 0.95:
            face_shape = "oval"
        else:
            face_shape = None

    print("DEBUG EDEN:", provider_name, "face_shape:", face_shape, "gender:", gender)
    return {
        "face_shape": face_shape,
        "gender": gender,
    }
