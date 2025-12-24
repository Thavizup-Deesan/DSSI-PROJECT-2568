# ใช้ Python 3.10 ตัวเล็ก (Slim)
FROM python:3.10-slim

# ตั้งค่า Environment
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# ตั้ง Folder ทำงาน
WORKDIR /app

# Copy ไฟล์ requirements และติดตั้ง
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy โค้ดทั้งหมดเข้า Container
COPY . /app/

# รวบรวม Static Files
RUN python manage.py collectstatic --noinput

# คำสั่งรัน Server ผ่าน Gunicorn
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 backend.wsgi:application