# 🔧 อธิบาย views.py อย่างละเอียด

## 📍 views.py อยู่ที่ไหน?
```
POTMS/api/views.py
```

## 🎯 views.py ทำหน้าที่อะไร?

`views.py` คือ **สมอง** ของระบบ ทำหน้าที่:
1. รับ Request จากผู้ใช้
2. ประมวลผลข้อมูล
3. เชื่อมต่อ Database (Firebase)
4. ส่งผลลัพธ์กลับไป (HTML หรือ JSON)

---

## 📚 โครงสร้างโค้ดใน views.py

```python
# ========== ส่วน IMPORT ==========
from django.contrib.auth.hashers import make_password, check_password  # เข้ารหัสรหัสผ่าน
from rest_framework.views import APIView      # สร้าง API Class
from rest_framework.response import Response  # ส่งข้อมูล JSON กลับ
from rest_framework import status             # HTTP Status Code
from backend.firebase_config import db        # เชื่อมต่อ Firebase
import datetime                                # จัดการวันเวลา
from django.shortcuts import render           # แสดงหน้า HTML
import pandas as pd                            # อ่านไฟล์ Excel/CSV
```

---

## 🏗️ ประเภทของ View

### 1️⃣ Function-Based View (FBV)
ใช้สำหรับแสดงหน้า HTML

```python
def login_page(request):
    """
    แสดงหน้า Login
    URL: /api/login-page/
    """
    return render(request, 'login.html')
```

**อธิบาย:**
- `def login_page(request)` = ฟังก์ชันที่รับ request เข้ามา
- `request` = ข้อมูลที่ผู้ใช้ส่งมา (URL, Headers, Body)
- `render(request, 'login.html')` = บอก Django ให้แสดงไฟล์ `login.html`

### 2️⃣ Class-Based View (CBV)
ใช้สำหรับสร้าง API ที่มีหลาย Method

```python
class ProjectAPIView(APIView):
    """
    API จัดการโครงการ
    URL: /api/projects/
    """
    
    def get(self, request):
        # เมื่อผู้ใช้เรียก GET /api/projects/
        # --> ดึงข้อมูลโครงการทั้งหมด
        pass
    
    def post(self, request):
        # เมื่อผู้ใช้เรียก POST /api/projects/
        # --> สร้างโครงการใหม่
        pass
```

---

## 📦 อธิบาย API แต่ละตัว

### 1. ProjectAPIView - จัดการโครงการ

#### GET - ดึงข้อมูลโครงการทั้งหมด

```python
def get(self, request):
    try:
        # 1. เชื่อมต่อ Collection 'projects' ใน Firebase
        projects_ref = db.collection('projects')
        
        # 2. ดึงเอกสารทั้งหมด (.stream())
        docs = projects_ref.stream()

        # 3. วนลูปแปลงข้อมูลเป็น List
        project_list = []
        for doc in docs:
            item = doc.to_dict()        # แปลงเป็น Dictionary
            item['id'] = doc.id          # เพิ่ม ID ของเอกสาร
            project_list.append(item)

        # 4. ส่งข้อมูลกลับเป็น JSON
        return Response(project_list, status=status.HTTP_200_OK)

    except Exception as e:
        # ถ้ามี Error ให้ส่งข้อความกลับ
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

**Flow การทำงาน:**
```
User เรียก GET /api/projects/
        │
        ▼
┌─────────────────────────┐
│  db.collection()        │  ← เชื่อมต่อ Firebase
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  .stream()              │  ← ดึง Documents ทั้งหมด
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  for doc in docs:       │  ← วนลูป
│    item = doc.to_dict() │  ← แปลงเป็น {}
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Response(project_list) │  ← ส่ง JSON กลับ
└─────────────────────────┘
```

#### POST - สร้างโครงการใหม่

```python
def post(self, request):
    try:
        # 1. รับข้อมูลจาก Request Body
        data = request.data
        
        # 2. เตรียมข้อมูลโครงการใหม่
        new_project = {
            'project_name': data.get('project_name'),      # ชื่อโครงการ
            'budget_total': float(data.get('budget_total', 0)),  # งบประมาณ
            'budget_reserved': 0.0,    # งบจอง (เริ่มต้น 0)
            'budget_spent': 0.0,       # งบใช้ไปแล้ว (เริ่มต้น 0)
            'status': data.get('status', 'Active'),  # สถานะ
            'created_at': datetime.datetime.now()    # วันที่สร้าง
        }

        # 3. บันทึกลง Firebase
        # add() จะสร้าง ID อัตโนมัติ
        update_time, doc_ref = db.collection('projects').add(new_project)

        # 4. ส่งผลลัพธ์กลับ
        return Response({
            'id': doc_ref.id,
            'message': 'สร้างโครงการสำเร็จแล้ว'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

---

### 2. ProjectDetailAPIView - แก้ไข/ลบโครงการ

#### DELETE - ลบโครงการ

```python
def delete(self, request, project_id):
    """
    URL: DELETE /api/projects/{project_id}/
    ตัวอย่าง: DELETE /api/projects/abc123/
    """
    try:
        # ลบเอกสารตาม ID
        db.collection('projects').document(project_id).delete()
        
        return Response({'message': 'ลบสำเร็จ'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

**อธิบาย `project_id`:**
- มาจาก URL เช่น `/api/projects/abc123/`
- Django จะจับค่า `abc123` ใส่ในตัวแปร `project_id`

#### PUT - แก้ไขโครงการ

```python
def put(self, request, project_id):
    try:
        data = request.data
        
        # เตรียมข้อมูลที่จะอัปเดต
        update_data = {
            'project_name': data.get('project_name'),
            'budget_total': float(data.get('budget_total', 0))
        }
        
        # ถ้ามี status ส่งมา ให้อัปเดตด้วย
        if data.get('status'):
            update_data['status'] = data.get('status')

        # อัปเดตใน Firebase
        db.collection('projects').document(project_id).update(update_data)

        return Response({'message': 'แก้ไขสำเร็จ'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

---

### 3. UserLoginAPIView - ระบบ Login

```python
class UserLoginAPIView(APIView):
    def post(self, request):
        try:
            data = request.data
            username = data.get('username')
            password = data.get('password')

            # 1. ค้นหา username ใน Firebase
            users_ref = db.collection('users').where('username', '==', username).stream()
            
            user_found = None
            for doc in users_ref:
                user_found = doc.to_dict()
                user_found['id'] = doc.id
                break  # เจอตัวแรกแล้วหยุด

            # 2. ตรวจสอบรหัสผ่าน
            if user_found and check_password(password, user_found['password']):
                # รหัสผ่านถูกต้อง!
                return Response({
                    'message': 'เข้าสู่ระบบสำเร็จ',
                    'user': {
                        'id': user_found['id'],
                        'username': user_found['username'],
                        'role': user_found['role'],
                        'department': user_found['department']
                    }
                }, status=status.HTTP_200_OK)
            else:
                # รหัสผ่านผิด
                return Response(
                    {'error': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

**ฟังก์ชันสำคัญ:**
- `check_password(รหัสที่ส่งมา, รหัสที่เก็บในDB)` = เช็คว่าตรงกันไหม
- `make_password(รหัสผ่าน)` = เข้ารหัสก่อนบันทึก (ใช้ตอน Register)

---

## 🔒 การเข้ารหัสรหัสผ่าน

```python
from django.contrib.auth.hashers import make_password, check_password

# ตอน Register (บันทึกลง DB)
password_hash = make_password('mypassword123')
# ผลลัพธ์: 'pbkdf2_sha256$720000$xxx...xxx'

# ตอน Login (เช็ครหัสผ่าน)
is_valid = check_password('mypassword123', password_hash)
# ผลลัพธ์: True หรือ False
```

---

## 📊 HTTP Status Codes ที่ใช้

| Code | ความหมาย | ใช้เมื่อไหร่ |
|------|----------|-------------|
| `200 OK` | สำเร็จ | ดึงข้อมูล, แก้ไข, ลบ สำเร็จ |
| `201 Created` | สร้างสำเร็จ | สร้างข้อมูลใหม่สำเร็จ |
| `400 Bad Request` | Request ไม่ถูกต้อง | ข้อมูลไม่ครบ, Error ทั่วไป |
| `401 Unauthorized` | ไม่มีสิทธิ์ | Login ผิด |
| `404 Not Found` | ไม่พบข้อมูล | หา ID ไม่เจอ |

---

## 📄 ไฟล์ถัดไป

→ [04-urls-routing.md](./04-urls-routing.md) - อธิบาย URL Routing
