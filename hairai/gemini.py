import google.generativeai as genai
from django.conf import settings
import json
import re
import logging

logger = logging.getLogger(__name__)


def analyze_face_shape_with_gemini(image_file):
    """
    รับรูปจาก Django (InMemoryUploadedFile)
    ส่งไปให้ Google Gemini วิเคราะห์
    และพยายามดึง JSON ที่มี face_shape, gender, confidence ออกมา
    """

    # ตั้งค่า API Key
    genai.configure(api_key=settings.GEMINI_API_KEY)

    model = genai.GenerativeModel("models/gemini-2.5-flash-image")

    # อ่าน bytes จากไฟล์
    image_bytes = image_file.read()

    prompt = """
    คุณคือผู้เชี่ยวชาญด้านวิเคราะห์รูปหน้าสำหรับการตัดผม
    วิเคราะห์ภาพใบหน้าและตอบกลับเป็น JSON เท่านั้น ห้ามมีข้อความอื่น

    โครงสร้างที่ต้องส่งกลับ:

    {
      "face_shape": "oval / round / square / oblong / heart",
      "gender": "male / female / unknown",
      "confidence": 0.0 - 1.0
    }

    ห้ามอธิบายเพิ่ม ห้ามใส่คำอธิบายอื่น ห้ามใส่ Markdown หรือโค้ดบล็อก
    ให้ตอบกลับเป็น JSON ด้านบนเท่านั้น
    """

    result = model.generate_content(
        [
            prompt,
            {
                "mime_type": image_file.content_type,
                "data": image_bytes,
            },
        ]
    )

    text = (result.text or "").strip()
    print("DEBUG GEMINI RAW:", text)  #
    logger.debug("Gemini raw response: %s", text)

    # เผื่อ Gemini ใส่ ```json ... ```
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9]*\s*", "", text)
        text = re.sub(r"```$", "", text.strip())
        text = text.strip()
        print("DEBUG GEMINI STRIPPED:", text)

    # ดึงเฉพาะส่วน {...}
    if "{" in text and "}" in text:
        start = text.find("{")
        end = text.rfind("}") + 1
        candidate = text[start:end]
    else:
        candidate = text

    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as e:
        print("JSON PARSE ERROR:", e)
        logger.error("Failed to parse JSON from Gemini: %s", e)
        return {"face_shape": None, "gender": None, "confidence": 0}

    return {
        "face_shape": data.get("face_shape"),
        "gender": data.get("gender"),
        "confidence": data.get("confidence", 0),
    }
