import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from pathlib import Path

# กำหนด Path ไปยังไฟล์ Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ตรวจสอบว่าเคย Initialize ไปแล้วหรือยัง
if not firebase_admin._apps:
    # ลองอ่านจาก Environment Variable ก่อน (สำหรับ Vercel/Production)
    firebase_key_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
    
    if firebase_key_json:
        # ใช้ Environment Variable
        cred_dict = json.loads(firebase_key_json)
        cred = credentials.Certificate(cred_dict)
    else:
        # ใช้ไฟล์ JSON (สำหรับ Local Development)
        KEY_FILE_NAME = 'firebase-key.json'
        CERTIFICATE_PATH = os.path.join(BASE_DIR, 'backend', KEY_FILE_NAME)
        cred = credentials.Certificate(CERTIFICATE_PATH)
    
    firebase_admin.initialize_app(cred)

# สร้างตัวแปร db เพื่อเอาไปใช้ใน views.py
db = firestore.client()