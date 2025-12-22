# Step 1 Run comnand
1.clone จาก Github

    git clone

2.ใช้คำสั่ง

    uv run

3.ติดตั้ง requirements

    pip install -r requirements.txt

# Step 2 Database & env
**1.สร้าง Data base ใน postgresql**

- เปิด pgAdmin > Servers > PostgreSQL > ตลิกขวาที่ Databases > create > database

**2.สร้าง env file**

    DEBUG=True
    SECRET_KEY=change-me-in-prod
    ALLOWED_HOSTS=127.0.0.1,localhost
    TIME_ZONE=Asia/Bangkok
    
    DB_NAME=
    DB_USER=
    DB_PASSWORD=
    DB_HOST=127.0.0.1
    DB_PORT=5432
    
    GEMINI_API_KEY=AIzaSyC8DmV6APH_DQLwQXjK7uU65QbGSxh3g9w

**3.ทำการ migrate**

    python manage.py migrate

**4.เอาข้อมูลลง Database**

    python manage.py loaddata data_fixed.json


# Run 2 terminals

**Terminal 1**

    python manage.py runserver

**Terminal 2**

ทำการติดตั้ง Tailwind

    npm install -D tailwindcss

Run

    npm run tw:dev
