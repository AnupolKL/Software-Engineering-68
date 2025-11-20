import google.generativeai as genai
from django.conf import settings
import json

def analyze_face_shape_with_gemini(image_file):
    """
    รับรูปจาก Django (InMemoryUploadedFile)
    ส่งไปให้ Google Gemini วิเคราะห์
    """

    # ตั้งค่า API Key
    genai.configure(api_key=settings.GEMINI_API_KEY)

    model = genai.GenerativeModel("gemini-1.5-flash")

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
    """

    result = model.generate_content(
        [prompt, {"mime_type": image_file.content_type, "data": image_bytes}]
    )

    response_text = result.text.strip()

    try:
        return json.loads(response_text)
    except:
        return {"face_shape": None, "gender": None, "confidence": 0}
