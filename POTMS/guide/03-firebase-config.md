# 🔥 Firebase Configuration

## ไฟล์: `backend/firebase_config.py`

อธิบายการเชื่อมต่อ Firebase Firestore

---

## Full Code

```python
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
```

---

## อธิบายทีละบรรทัด

### 1. Import Libraries

```python
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from pathlib import Path
```

| Library | การใช้งาน |
|---------|----------|
| `firebase_admin` | Firebase Admin SDK |
| `credentials` | โหลด service account key |
| `firestore` | เชื่อมต่อ Firestore database |
| `os` | อ่าน environment variables |
| `json` | parse JSON string |
| `pathlib.Path` | จัดการ file paths |

---

### 2. กำหนด BASE_DIR

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```

| ขั้นตอน | ผลลัพธ์ |
|---------|--------|
| `__file__` | `backend/firebase_config.py` |
| `.resolve()` | absolute path |
| `.parent` | `backend/` |
| `.parent.parent` | `POTMS/` (root) |

---

### 3. ตรวจสอบการ Initialize

```python
if not firebase_admin._apps:
```

**ทำไมต้องตรวจ?**  
เพราะ Firebase SDK จะ error ถ้า initialize ซ้ำ  
`firebase_admin._apps` เป็น dictionary เก็บ app ที่ initialize แล้ว

---

### 4. โหลด Credentials

```python
# Production (Vercel)
firebase_key_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
if firebase_key_json:
    cred_dict = json.loads(firebase_key_json)
    cred = credentials.Certificate(cred_dict)

# Local Development
else:
    KEY_FILE_NAME = 'firebase-key.json'
    CERTIFICATE_PATH = os.path.join(BASE_DIR, 'backend', KEY_FILE_NAME)
    cred = credentials.Certificate(CERTIFICATE_PATH)
```

| Environment | วิธีโหลด |
|-------------|---------|
| Production | อ่านจาก env var → parse JSON → สร้าง dict |
| Local | อ่านจากไฟล์ `firebase-key.json` |

---

### 5. Initialize App

```python
firebase_admin.initialize_app(cred)
```

สร้าง Firebase app instance พร้อมใช้งาน

---

### 6. สร้าง Database Client

```python
db = firestore.client()
```

สร้าง Firestore client สำหรับ CRUD operations  
Export ไปใช้ใน views.py: `from backend.firebase_config import db`

---

## การใช้งานใน views.py

```python
from backend.firebase_config import db

# Create
db.collection('orders').add({'name': 'test'})

# Read
doc = db.collection('orders').document('order_id').get()

# Update
db.collection('orders').document('order_id').update({'status': 'Approved'})

# Delete
db.collection('orders').document('order_id').delete()

# Query
orders = db.collection('orders').where('status', '==', 'Pending').stream()
```

---

## Firestore Collections ในโปรเจค

| Collection | ข้อมูล |
|------------|--------|
| `users` | ผู้ใช้งานระบบ |
| `projects` | โครงการและงบประมาณ |
| `orders` | ใบขอซื้อ |
| `suborders` | ใบสั่งซื้อย่อย |
| `audit_logs` | บันทึกการใช้งาน |
