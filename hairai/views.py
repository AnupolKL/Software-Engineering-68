import requests
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from .gemini import analyze_face_shape_with_gemini
from .forms import HairAIForm
from django.contrib import messages


# แนะนำทรงผมตามรูปหน้า
def recommend_hairstyles(face_shape: str, gender: str | None = None):
    face_shape = (face_shape or "").lower()
    data = {
        "round": [
            "ทรง Fade ด้านข้าง + ด้านบนเพิ่มวอลลุ่ม",
            "ทรง Pompadour",
            "ทรง Undercut ด้านข้างเตี้ย ด้านบนตั้ง"
        ],
        "oval": [
            "ทรง Side Part แสกข้าง",
            "ทรง Crop สั้นเท่ากันทั้งหัว",
            "ทรง Slick Back"
        ],
        "square": [
            "ทรง Buzz Cut สั้นเกรียน",
            "ทรง Side Part + Fade",
            "ทรง Spiky ตั้งๆ ด้านบน"
        ],
        "oblong": [
            "ทรงมีหน้าม้า (Fringe)",
            "ทรง Medium Length ผมปานกลางพองๆ",
            "ทรง Curly / Wavy"
        ],
        "heart": [
            "ทรง Textured Crop",
            "ทรง Low Fade + ปล่อยด้านบนฟูๆ",
            "ทรง Messy Quiff"
        ],
    }
    default_list = [
        "ทรง Side Part มาตรฐาน",
        "ทรง Fade ด้านข้าง",
        "ทรง Crop สั้นดูแลง่าย"
    ]
    return data.get(face_shape, default_list)

def hair_ai_view(request):
    result = None
    suggestions = None
    image_preview = None
    face_shape = None
    gender = None

    if request.method == "POST":
        form = HairAIForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]
            image_preview = image

            print("DEBUG VIEW: form.is_valid() = True")  # 👈 เช็คว่ามา POST จริง

            try:
                # ✅ เรียก Gemini จริง
                result = analyze_face_shape_with_gemini(image)
                print("DEBUG RESULT DICT:", result)

                if result:
                    face_shape = (result.get("face_shape") or "").lower()
                    gender = result.get("gender")

                    if face_shape:
                        suggestions = recommend_hairstyles(face_shape, gender)
                    else:
                        messages.error(
                            request,
                            "AI ไม่สามารถวิเคราะห์รูปหน้าได้ กรุณาลองอัปโหลดรูปอื่น"
                        )
                else:
                    messages.error(request, "AI ไม่ได้ส่งผลลัพธ์กลับมา")

            except Exception as e:
                print("DEBUG EXCEPTION:", e)
                messages.error(request, f"เกิดข้อผิดพลาดจาก AI: {e}")

        else:
            print("DEBUG VIEW: form.is_valid() = False, errors =", form.errors)
            messages.error(request, "กรุณาเลือกไฟล์รูปภาพให้ถูกต้อง")
    else:
        form = HairAIForm()

    return render(request, "hairai/hair_ai.html", {
        "form": form,
        "result": result,
        "suggestions": suggestions,
        "image_preview": image_preview,
        "face_shape": face_shape,
        "gender": gender,
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

