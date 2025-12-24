# 🔧 Troubleshooting Guide - แก้ปัญหาที่พบบ่อย

## 🚨 Error ที่พบบ่อยและวิธีแก้

---

### 1. Server ไม่ยอม Run

**Error:**
```
ModuleNotFoundError: No module named 'xxx'
```

**สาเหตุ:** ยังไม่ได้ติดตั้ง Library

**วิธีแก้:**
```bash
# Activate virtual environment ก่อน
# Windows:
.venv\Scripts\activate

# ติดตั้ง dependencies
pip install -r requirements.txt
```

---

### 2. Firebase Connection Error

**Error:**
```
FileNotFoundError: firebase-key.json not found
```

**สาเหตุ:** ไม่มีไฟล์ Key หรือ Path ผิด

**วิธีแก้:**
1. ตรวจสอบว่ามีไฟล์ `firebase-key.json` ใน `POTMS/backend/`
2. ดาวน์โหลด Key ใหม่จาก Firebase Console:
   - ไปที่ Project Settings → Service Accounts
   - กด "Generate new private key"
   - บันทึกเป็น `firebase-key.json`

---

### 3. CORS Error

**Error (ใน Browser Console):**
```
Access to fetch at 'http://...' has been blocked by CORS policy
```

**สาเหตุ:** Frontend และ Backend อยู่คนละ Port

**วิธีแก้:**
แก้ไขใน `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # เพิ่ม port ที่ใช้
]
```

---

### 4. Template Not Found

**Error:**
```
TemplateDoesNotExist at /api/xxx/
```

**สาเหตุ:** 
- ชื่อไฟล์ Template ผิด
- ไม่มีไฟล์ใน `templates/`

**วิธีแก้:**
1. ตรวจสอบว่ามีไฟล์อยู่ใน `POTMS/api/templates/`
2. ตรวจสอบชื่อไฟล์ใน `views.py`:
```python
def login_page(request):
    return render(request, 'login.html')  # ชื่อต้องตรง!
```

---

### 5. Database Connection Error

**Error:**
```
OperationalError: (2003, "Can't connect to MySQL server")
```

**สาเหตุ:** MySQL Server ไม่ได้รัน หรือ Settings ผิด

**วิธีแก้:**
1. เปิด MySQL Server
2. ตรวจสอบ `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'potms',          # ชื่อ Database
        'USER': 'root',           # Username
        'PASSWORD': 'xxx',        # Password
        'HOST': 'localhost',      # Host
        'PORT': '3306',           # Port
    }
}
```

---

### 6. Login ไม่ได้

**อาการ:** กรอก Username/Password ถูกต้องแต่ Login ไม่ผ่าน

**สาเหตุที่เป็นไปได้:**
1. Password ถูก Hash แบบไม่ถูกต้อง
2. ข้อมูล User ใน Firebase ไม่ถูกต้อง

**วิธีตรวจสอบ:**
```python
# เข้า Django Shell
python manage.py shell

# ทดสอบ
from django.contrib.auth.hashers import check_password, make_password

# สร้าง Hash ใหม่
new_hash = make_password('password123')
print(new_hash)

# เช็ครหัสผ่าน
result = check_password('password123', new_hash)
print(result)  # ต้องได้ True
```

---

### 7. LocalStorage ไม่มีข้อมูล User

**อาการ:** เข้าหน้า Dashboard แล้วถูก Redirect กลับหน้า Login

**สาเหตุ:** Login สำเร็จแต่ไม่ได้บันทึก LocalStorage

**วิธีตรวจสอบ:**
1. เปิด DevTools (F12) → Application → Local Storage
2. ดูว่ามี key `user` หรือไม่

**วิธีแก้ (ถ้าไม่มี):**
ตรวจสอบ JavaScript ใน `login.html`:
```javascript
if (response.ok) {
    localStorage.setItem('user', JSON.stringify(data.user));
    // ...
}
```

---

### 8. SweetAlert2 ไม่แสดง

**อาการ:** ใช้ `Swal.fire()` แต่ไม่มี Popup

**สาเหตุ:** ยังไม่ได้ Load CDN

**วิธีแก้:**
ตรวจสอบว่ามี Script นี้ใน `<head>`:
```html
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
```

---

### 9. API Returns 500 Error

**วิธีดู Error จริง:**
1. ดูใน Terminal ที่รัน Server
2. Django จะแสดง Traceback ละเอียด

**ตัวอย่าง:**
```
Internal Server Error: /api/projects/
Traceback (most recent call last):
  File "...", line xxx
    xxx
TypeError: xxx
```

---

### 10. Import Excel/CSV ไม่ได้

**Error:**
```
ModuleNotFoundError: No module named 'openpyxl'
```

**วิธีแก้:**
```bash
pip install openpyxl pandas
```

**ตรวจสอบรูปแบบไฟล์:**
- Excel ต้องมี Column: `project_name`, `budget_total`
- Row แรกต้องเป็น Header

---

## 💡 Tips การ Debug

### 1. ดู Console Log
```javascript
console.log('data:', data);
console.log('response:', response);
```

### 2. ใช้ try-catch
```javascript
try {
    const response = await fetch('/api/xxx/');
    const data = await response.json();
} catch (error) {
    console.error('Error:', error);
}
```

### 3. ดู Network Tab
- เปิด DevTools (F12) → Network
- ดู Request/Response ของ API

### 4. ใช้ print() ใน Python
```python
def my_view(request):
    print('===== DEBUG =====')
    print('request.data:', request.data)
    print('=================')
    # ...
```

---

## ยังแก้ไม่ได้?

1. ลอง Restart Server: `Ctrl+C` แล้วรันใหม่
2. Clear Browser Cache: `Ctrl+Shift+Delete`
3. ลบ `__pycache__/` แล้วรันใหม่
4. ถามใน Google โดยใช้ข้อความ Error
