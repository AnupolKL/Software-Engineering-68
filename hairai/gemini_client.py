from django.conf import settings
import google.generativeai as genai
import json

genai.configure(api_key=settings.GEMINI_API_KEY)

MODEL = "gemini-2.0-flash" # รุ่นที่ใช้วิเคราะห์ภาพ


def _clean_gemini_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        if text.endswith("```"):
            text = text[3:-3].strip()
        else:
            text = text[3:].strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return text


def analyze_with_gemini(uploaded_file, image_bytes: bytes):
    
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
"""

    response = model.generate_content(
        [
            prompt,
            {
                "mime_type": uploaded_file.content_type or "image/jpeg",
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
