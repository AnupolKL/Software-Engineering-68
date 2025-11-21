import requests
import tempfile
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from .gemini_client import analyze_with_gemini
from .forms import HairAIForm
from django.contrib import messages


# แนะนำทรงผมตามรูปหน้า
def recommend_hairstyles(face_shape: str, gender: str | None = None):
    face_shape = (face_shape or "").lower()
    gender = (gender or "male").lower()

    if gender != "male":
        return []
    
    # ใช้ชื่อไฟล์ให้ตรงกับรูปที่คุณจะเอาไปวางใน static/hairstyles/
    data = {
        "round": [
            {
                "name": "Fade ด้านข้าง + ด้านบนเพิ่มวอลลุ่ม",
                "image": "hairstyles/round_fade_volume.jpg",
                "description": "ช่วยให้หน้าไม่ดูกลมเกินไป เพิ่มความสูงด้านบน"
            },
            {
                "name": "Pompadour",
                "image": "hairstyles/round_pompadour.jpg",
                "description": "ด้านข้างสั้น ด้านบนพอง ช่วยบาลานซ์หน้ากลม"
            },
            {
                "name": "Undercut ด้านข้างเตี้ย ด้านบนตั้ง",
                "image": "hairstyles/round_undercut.jpg",
                "description": "ตัดให้หน้าเรียวขึ้น ดูคมชัดขึ้น"
            },
        ],
        "oval": [
            {
                "name": "Side Part แสกข้าง",
                "image": "hairstyles/oval_sidepart.jpg",
                "description": "เข้ากับโครงหน้าส่วนใหญ่ ดูสุภาพและเรียบร้อย"
            },
            {
                "name": "Crop สั้นเท่ากันทั้งหัว",
                "image": "hairstyles/oval_crop.jpg",
                "description": "ดูแลง่าย เหมาะกับคนไม่ชอบเซ็ตผม"
            },
            {
                "name": "Slick Back",
                "image": "hairstyles/oval_slickback.jpg",
                "description": "หวีเสยหลัง ให้ลุคเรียบหรู เท่ สุภาพ"
            },
        ],
        "square": [
            {
                "name": "Buzz Cut สั้นเกรียน",
                "image": "hairstyles/square_buzz.jpg",
                "description": "เน้นความคมของกราม ดูแมนสุด ๆ"
            },
            {
                "name": "Side Part + Fade",
                "image": "hairstyles/square_sidepart_fade.jpg",
                "description": "บาลานซ์กรามเหลี่ยมให้ซอฟต์ลง"
            },
            {
                "name": "Spiky ตั้งด้านบน",
                "image": "hairstyles/square_spiky.jpg",
                "description": "เพิ่มความสูงด้านบนให้หน้าดูยาวขึ้น"
            },
        ],
        "oblong": [
            {
                "name": "ทรงมีหน้าม้า (Fringe)",
                "image": "hairstyles/oblong_fringe.jpg",
                "description": "ช่วยลดความยาวใบหน้า ให้ดูสั้นลง"
            },
            {
                "name": "Medium Length ผมปานกลางพอง ๆ",
                "image": "hairstyles/oblong_medium.jpg",
                "description": "เพิ่มวอลลุ่มด้านข้างให้หน้าดูบาลานซ์"
            },
            {
                "name": "Wavy / Curly",
                "image": "hairstyles/oblong_wavy.jpg",
                "description": "ลอนช่วยทำให้หน้าดูไม่ยาวเกินไป"
            },
        ],
        "heart": [
            {
                "name": "Textured Crop",
                "image": "hairstyles/heart_crop.jpg",
                "description": "ช่วยบาลานซ์หน้าผากกว้างและคางแหลม"
            },
            {
                "name": "Low Fade + ด้านบนฟู ๆ",
                "image": "hairstyles/heart_lowfade.jpg",
                "description": "ลดความเด่นที่หน้าผาก และเพิ่มเท็กซ์เจอร์ด้านบน"
            },
            {
                "name": "Messy Quiff",
                "image": "hairstyles/heart_messyquiff.jpg",
                "description": "เซ็ตยุ่ง ๆ ให้ลุคสบาย ๆ แต่ยังดูมีสไตล์"
            },
        ],
    }

    default_list = [
        {
            "name": "Side Part มาตรฐาน",
            "image": "hairstyles/default_sidepart.jpg",
            "description": "ทรงมาตรฐาน เข้ากับรูปหน้าหลายแบบ"
        },
        {
            "name": "Fade ด้านข้าง",
            "image": "hairstyles/default_fade.jpg",
            "description": "ด้านข้างเฟด เข้ารูป ดูทันสมัย"
        },
        {
            "name": "Crop สั้นดูแลง่าย",
            "image": "hairstyles/default_crop.jpg",
            "description": "เหมาะกับคนไม่ค่อยเซ็ตผม"
        },
    ]
    return data.get(face_shape, default_list)


def hair_ai_view(request):
    face_shape = None
    gender = None
    suggestions = None
    image_preview = None

    if request.method == "POST":
        form = HairAIForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]
            image_preview = image  # แสดงรูปใน template

            try:
                result = analyze_with_gemini(image)
                face_shape = result.get("face_shape")
                gender = result.get("gender")

                # เงื่อนไขเพศ
                if gender == "female":
                    messages.info(request, "สามารถแนะนำได้เฉพาะทรงสำหรับผมผู้ชาย")
                    suggestions = None

                elif gender == "male":
                    if face_shape:
                        suggestions = recommend_hairstyles(face_shape, gender)
                    else:
                        messages.error(request, "ไม่สามารถวิเคราะห์รูปหน้าได้")

                else:
                    messages.error(request, "ระบบไม่มั่นใจเพศจากรูปนี้")

            except Exception as e:
                print("GEMINI ERROR:", e)
                messages.error(
                    request,
                    "เกิดข้อผิดพลาดจากระบบ AI กรุณาลองใหม่อีกครั้ง"
                )

        else:
            messages.error(request, "กรุณาเลือกรูปภาพที่ถูกต้อง")

    else:
        form = HairAIForm()

    return render(request, "hairai/hair_ai.html", {
        "form": form,
        "face_shape": face_shape,
        "gender": gender,
        "suggestions": suggestions,
        "image_preview": image_preview,
    })




def call_face_shape_api(image_file):
    url = settings.HAIR_AI_API_URL
    api_key = settings.HAIR_AI_API_KEY

    files = {"file": (image_file.name, image_file.read())}
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    # รูปแบบ response สมมติ: {"face_shape": "oval", "gender": "male"}
    resp = requests.post(url, headers=headers, files=files, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    face_shape = data.get("face_shape")  # เช่น "oval"
    gender = data.get("gender")          # ถ้ามี
    return face_shape, gender

