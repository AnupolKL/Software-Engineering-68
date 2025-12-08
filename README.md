1.git clone

2.pip install -r requirements.txt

3. สร้าง env file
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

4.python manage.py migrate

5.python manage.py loaddata data_fixed.json