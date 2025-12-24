# 🔥 การเชื่อมต่อ Firebase Firestore

## 📍 ไฟล์ที่เกี่ยวข้อง

```
POTMS/backend/
├── firebase_config.py     # โค้ดเชื่อมต่อ Firebase
└── firebase-key.json      # กุญแจเข้าถึง (ห้ามแชร์!)
```

---

## 🤔 ทำไมใช้ Firebase Firestore?

| คุณสมบัติ | Firebase Firestore | MySQL/PostgreSQL |
|----------|-------------------|------------------|
| ประเภท | NoSQL (Document) | SQL (Relational) |
| การตั้งค่า | ง่าย ไม่ต้องติดตั้ง | ต้องติดตั้ง Server |
| Real-time | รองรับ | ไม่รองรับ |
| ราคา | ฟรี (มีโควต้า) | ต้องจ่าย |
| Hosting | Google Cloud | ต้องหาเอง |

---

## 🔧 อธิบาย firebase_config.py

```python
import firebase_admin
from firebase_admin import credentials, firestore
import os
from pathlib import Path

# 1. หา Path ของโปรเจค
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. ชื่อไฟล์ Key
KEY_FILE_NAME = 'firebase-key.json' 

# 3. สร้าง Path เต็มไปยังไฟล์ Key
CERTIFICATE_PATH = os.path.join(BASE_DIR, 'backend', KEY_FILE_NAME)

# 4. Initialize Firebase (ทำครั้งเดียว)
if not firebase_admin._apps:
    cred = credentials.Certificate(CERTIFICATE_PATH)
    firebase_admin.initialize_app(cred)

# 5. สร้างตัวเชื่อมต่อ Firestore
db = firestore.client()
```

**อธิบายทีละส่วน:**

### 1. หา Path ของโปรเจค
```python
BASE_DIR = Path(__file__).resolve().parent.parent
```
```
__file__ = "E:/DSSI-PROJECT-2568/POTMS/backend/firebase_config.py"
.parent   = "E:/DSSI-PROJECT-2568/POTMS/backend/"
.parent   = "E:/DSSI-PROJECT-2568/POTMS/"
```

### 2. สร้าง Path ไปยังไฟล์ Key
```python
CERTIFICATE_PATH = os.path.join(BASE_DIR, 'backend', KEY_FILE_NAME)
# ผลลัพธ์: "E:/DSSI-PROJECT-2568/POTMS/backend/firebase-key.json"
```

### 3. Initialize Firebase
```python
if not firebase_admin._apps:
    # ถ้ายังไม่เคย Initialize
    cred = credentials.Certificate(CERTIFICATE_PATH)
    firebase_admin.initialize_app(cred)
```

### 4. สร้างตัวเชื่อมต่อ
```python
db = firestore.client()
# ใช้ db นี้ในการอ่าน/เขียนข้อมูล
```

---

## 📚 โครงสร้างข้อมูลใน Firestore

Firestore ใช้ **Collection > Document > Fields**

```
🗄️ Firestore Database
│
├── 📁 Collection: "projects"
│   ├── 📄 Document: "abc123"
│   │   ├── project_name: "โครงการ A"
│   │   ├── budget_total: 1000000
│   │   ├── budget_reserved: 200000
│   │   ├── budget_spent: 150000
│   │   ├── status: "Active"
│   │   └── created_at: (timestamp)
│   │
│   ├── 📄 Document: "def456"
│   │   └── ...
│   │
│   └── 📄 Document: "ghi789"
│       └── ...
│
└── 📁 Collection: "users"
    ├── 📄 Document: "user001"
    │   ├── username: "john"
    │   ├── password: "pbkdf2_sha256$..."
    │   ├── role: "Admin"
    │   ├── department: "IT"
    │   └── created_at: (timestamp)
    │
    └── 📄 Document: "user002"
        └── ...
```

---

## 💻 วิธีใช้งาน Firestore ใน views.py

### Import ตัวเชื่อมต่อ
```python
from backend.firebase_config import db
```

### 1. ดึงข้อมูลทั้งหมด (GET ALL)
```python
# ดึงทุก Document ใน Collection 'projects'
docs = db.collection('projects').stream()

for doc in docs:
    print(doc.id)           # ID ของ Document
    print(doc.to_dict())    # ข้อมูลเป็น Dictionary
```

### 2. ดึงข้อมูลตัวเดียว (GET ONE)
```python
# ดึง Document ตาม ID
doc = db.collection('projects').document('abc123').get()

if doc.exists:
    print(doc.to_dict())
else:
    print("ไม่พบข้อมูล")
```

### 3. เพิ่มข้อมูล (CREATE)
```python
# วิธี 1: ให้ Firebase สร้าง ID อัตโนมัติ
update_time, doc_ref = db.collection('projects').add({
    'project_name': 'โครงการใหม่',
    'budget_total': 500000
})
print(doc_ref.id)  # ID ที่สร้างใหม่

# วิธี 2: กำหนด ID เอง
db.collection('projects').document('my-custom-id').set({
    'project_name': 'โครงการ X',
    'budget_total': 100000
})
```

### 4. แก้ไขข้อมูล (UPDATE)
```python
# อัปเดตบางฟิลด์
db.collection('projects').document('abc123').update({
    'project_name': 'ชื่อใหม่',
    'budget_total': 2000000
})
```

### 5. ลบข้อมูล (DELETE)
```python
# ลบ Document
db.collection('projects').document('abc123').delete()
```

### 6. ค้นหาข้อมูล (QUERY)
```python
# หา user ตาม username
users = db.collection('users').where('username', '==', 'john').stream()

for user in users:
    print(user.to_dict())
```

---

## 🔍 Operators ที่ใช้ได้ใน where()

| Operator | ความหมาย | ตัวอย่าง |
|----------|----------|----------|
| `==` | เท่ากับ | `.where('status', '==', 'Active')` |
| `!=` | ไม่เท่ากับ | `.where('status', '!=', 'Deleted')` |
| `<` | น้อยกว่า | `.where('budget', '<', 100000)` |
| `<=` | น้อยกว่าหรือเท่ากับ | `.where('budget', '<=', 100000)` |
| `>` | มากกว่า | `.where('budget', '>', 100000)` |
| `>=` | มากกว่าหรือเท่ากับ | `.where('budget', '>=', 100000)` |
| `in` | อยู่ในลิสต์ | `.where('status', 'in', ['Active', 'Pending'])` |

---

## ⚠️ ข้อควรระวัง

### 1. ไฟล์ firebase-key.json
```
⚠️ ห้ามอัปโหลดขึ้น GitHub!
⚠️ ห้ามแชร์ให้คนอื่น!
```

เพิ่มใน `.gitignore`:
```
firebase-key.json
```

### 2. การใช้ stream() กับ get()
```python
# stream() = ดึงหลาย Documents (ใช้ทันที)
docs = db.collection('projects').stream()
for doc in docs:
    print(doc)

# get() = ดึง Document เดียว
doc = db.collection('projects').document('id').get()
```

### 3. การจัดการ Error
```python
try:
    db.collection('projects').document('xyz').delete()
except Exception as e:
    print(f"Error: {e}")
```

---

## 📄 ไฟล์ถัดไป

→ [06-templates-html.md](./06-templates-html.md) - อธิบาย HTML Templates
