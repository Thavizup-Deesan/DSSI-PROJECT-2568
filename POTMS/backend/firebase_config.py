import firebase_admin
from firebase_admin import credentials, firestore
import os
from pathlib import Path

# กำหนด Path ไปยังไฟล์ Base Directory (โฟลเดอร์ที่มี manage.py)
# หมายเหตุ: การคำนวณ path อาจต่างกันเล็กน้อยตามโครงสร้าง แต่ถ้าไฟล์ json อยู่คู่กับ settings.py ให้ใช้แบบนี้
BASE_DIR = Path(__file__).resolve().parent.parent

# ชื่อไฟล์ Key ที่คุณโหลดมา (แก้ชื่อให้ตรงกับไฟล์ของคุณ)
KEY_FILE_NAME = 'firebase-key.json' 

# สร้าง Path เต็มไปยังไฟล์ Key
# สมมติว่าไฟล์ key อยู่ในโฟลเดอร์ backend (ที่เดียวกับไฟล์นี้)
CERTIFICATE_PATH = os.path.join(BASE_DIR, 'backend', KEY_FILE_NAME)

# ตรวจสอบว่าเคย Initialize ไปแล้วหรือยัง (เพื่อป้องกัน Error เวลา Run ซ้ำ)
if not firebase_admin._apps:
    cred = credentials.Certificate(CERTIFICATE_PATH)
    firebase_admin.initialize_app(cred)

# สร้างตัวแปร db เพื่อเอาไปใช้ใน views.py
db = firestore.client()