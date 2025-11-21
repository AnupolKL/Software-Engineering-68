from django.conf import settings
import google.generativeai as genai
import json

genai.configure(api_key=settings.GEMINI_API_KEY)

MODEL = "gemini-2.0-flash" # รุ่นที่ใช้วิเคราะห์ภาพ


def _clean_gemini_json(text: str) -> str:
    """
    รับข้อความจาก Gemini แล้วตัด ```json ... ``` ออก
    ให้เหลือเฉพาะ JSON เนื้อใน
    """
    text = text.strip()

    # ถ้ามาในรูป ```json ... ```
    if text.startswith("```"):
        # ตัดเครื่องหมาย ``` ด้านท้ายออกก่อน
        if text.endswith("```"):
            text = text[3:-3].strip()
        else:
            text = text[3:].strip()

        # ถ้าเปิดมาด้วยคำว่า json ให้ตัดออก
        if text.lower().startswith("json"):
            text = text[4:].strip()

    return text


def analyze_with_gemini(image_file):
    """
    วิเคราะห์ใบหน้าในรูปโดยใช้ Gemini API
    คืน dict = {"face_shape":..., "gender":...}
    """

    # อ่านไฟล์เป็น bytes
    image_bytes = image_file.read()

    model = genai.GenerativeModel(MODEL)

    prompt = """
คุณคือผู้เชี่ยวชาญด้านการออกแบบทรงผมและวิเคราะห์รูปหน้า
วิเคราะห์ภาพด้านล่างนี้และตอบเป็น JSON เท่านั้น
ห้ามใช้ข้อความอื่นที่ไม่ใช่ JSON

รูปแบบ JSON:
{
  "face_shape": "round / oval / oblong / square / heart / unknown",
  "gender": "male / female / unknown"
}

กรุณาวิเคราะห์อย่างแม่นยำที่สุด:
- face_shape ให้เลือกจาก 5 แบบนี้เท่านั้น (round, oval, oblong, square, heart)
- gender ให้ตอบ male หรือ female เท่านั้น ถ้าไม่ชัดเจนให้ตอบ unknown
"""

    response = model.generate_content(
        [
            prompt,
            {
                "mime_type": image_file.content_type or "image/jpeg",
                "data": image_bytes,
            },
        ]
    )

    raw_text = (response.text or "").strip()
    cleaned = _clean_gemini_json(raw_text)

    try:
        data = json.loads(cleaned)
    except Exception as e:
        print("GEMINI PARSE ERROR RAW:", raw_text)
        print("GEMINI PARSE ERROR CLEANED:", cleaned)
        print("GEMINI PARSE EXCEPTION:", e)
        return {"face_shape": None, "gender": None}

    return {
        "face_shape": data.get("face_shape"),
        "gender": data.get("gender"),
    }
