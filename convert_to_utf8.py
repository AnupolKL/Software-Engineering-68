import json

# ชื่อไฟล์ต้นฉบับและไฟล์ใหม่
input_path = "data.json"
output_path = "data_fixed.json"

# 1) อ่านไฟล์แบบ binary
with open(input_path, "rb") as f:
    raw = f.read()

# 2) decode ด้วย encoding เดิม (tis-620)
text = raw.decode("tis-620", errors="replace")

# 3) ลอง parse เป็น JSON
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    print("JSON โครงสร้างไม่ถูกต้อง:", e)
    # ถ้าอยากเก็บแค่ text UTF-8 เฉย ๆ (ยังไม่ parse JSON) ก็เขียนไฟล์แบบนี้ได้
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("เขียนเป็น text UTF-8 แล้วที่:", output_path)
else:
    # 4) ถ้า JSON ถูกต้อง → เขียนเป็น UTF-8 สวย ๆ
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("แปลงเป็น UTF-8 เรียบร้อย:", output_path)
