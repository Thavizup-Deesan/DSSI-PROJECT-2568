# 📖 พื้นฐาน Django Framework

## 🤔 Django คืออะไร?

**Django** คือ **Web Framework** ของ Python ที่ช่วยให้สร้างเว็บไซต์ได้ง่ายและรวดเร็ว
โดยใช้แนวคิด **MVT** (Model-View-Template)

---

## 🏛️ สถาปัตยกรรม MVT

```
┌─────────────────────────────────────────────────────────────────┐
│                         MVT Pattern                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌───────────┐      ┌───────────┐      ┌───────────┐           │
│   │   Model   │◄────►│   View    │◄────►│ Template  │           │
│   │ (ข้อมูล)  │      │ (ตรรกะ)   │      │  (HTML)   │           │
│   └───────────┘      └───────────┘      └───────────┘           │
│        │                  ▲                   │                  │
│        │                  │                   │                  │
│        ▼                  │                   ▼                  │
│   ┌─────────────┐    ┌────────┐         ┌─────────────┐         │
│   │  Database   │    │  URL   │         │   Browser   │         │
│   │ (Firebase)  │    │ Router │         │   (ผู้ใช้)   │         │
│   └─────────────┘    └────────┘         └─────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

| ส่วนประกอบ | ความหมาย | ไฟล์ในโปรเจค |
|------------|----------|--------------|
| **Model** | โครงสร้างข้อมูล | `models.py` (แต่เราใช้ Firebase) |
| **View** | ตรรกะ/การประมวลผล | `views.py` |
| **Template** | หน้าตา HTML | โฟลเดอร์ `templates/` |

---

## 📁 โครงสร้างโปรเจค Django มาตรฐาน

```
POTMS/                          # Root โปรเจค
├── backend/                    # โฟลเดอร์ Settings หลัก
│   ├── __init__.py            # บอกว่าเป็น Python Package
│   ├── settings.py            # ⭐ ตั้งค่าทั้งหมด
│   ├── urls.py                # URL หลักของโปรเจค
│   ├── wsgi.py                # สำหรับ Production Server
│   └── asgi.py                # สำหรับ Async Server
│
├── api/                        # แอปที่เราสร้างเอง
│   ├── __init__.py
│   ├── views.py               # ⭐ โค้ด Logic หลัก
│   ├── urls.py                # URL ของแอปนี้
│   ├── models.py              # โครงสร้างข้อมูล
│   └── templates/             # ไฟล์ HTML
│
└── manage.py                   # ⭐ คำสั่งจัดการโปรเจค
```

---

## ⚙️ อธิบาย settings.py

ไฟล์ `backend/settings.py` เป็นหัวใจของโปรเจค Django:

```python
# ===== 1. INSTALLED_APPS =====
# รายการแอปที่โปรเจคใช้งาน
INSTALLED_APPS = [
    'corsheaders',      # อนุญาตให้เว็บอื่นเรียก API
    'rest_framework',   # สร้าง REST API
    'api',              # แอปที่เราสร้างเอง ⭐
    'django.contrib.admin',     # หน้า Admin
    'django.contrib.auth',      # ระบบ Authentication
    ...
]

# ===== 2. MIDDLEWARE =====
# ตัวกลางที่ทำงานทุก Request
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.middleware.security.SecurityMiddleware',
    ...
]

# ===== 3. DATABASE =====
# การเชื่อมต่อฐานข้อมูล (แต่เราใช้ Firebase แทน)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'potms',
        ...
    }
}

# ===== 4. ALLOWED_HOSTS =====
# Domain ที่อนุญาตให้เข้าถึง
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']
```

---

## 🔗 URL Routing ทำงานอย่างไร?

```
User เปิด: http://127.0.0.1:8000/api/login-page/

                    ┌─────────────────────────┐
                    │   backend/urls.py       │
                    │   (URL หลัก)            │
                    └───────────┬─────────────┘
                                │
                    path('api/', include('api.urls'))
                                │
                                ▼
                    ┌─────────────────────────┐
                    │     api/urls.py         │
                    │   (URL ของแอป api)      │
                    └───────────┬─────────────┘
                                │
                    path('login-page/', login_page)
                                │
                                ▼
                    ┌─────────────────────────┐
                    │     api/views.py        │
                    │   def login_page():     │
                    └───────────┬─────────────┘
                                │
                    return render('login.html')
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ api/templates/login.html│
                    │   (หน้าเว็บ HTML)        │
                    └─────────────────────────┘
```

---

## 📝 คำสั่ง manage.py ที่ใช้บ่อย

```bash
# รัน Development Server
python manage.py runserver

# รันบน Port อื่น
python manage.py runserver 8080

# สร้าง Migration (สำหรับ Database)
python manage.py makemigrations

# Apply Migration
python manage.py migrate

# สร้าง Superuser (Admin)
python manage.py createsuperuser

# เปิด Python Shell
python manage.py shell
```

---

## 🎯 สรุปง่ายๆ

| คำถาม | คำตอบ |
|-------|-------|
| User เข้าเว็บ | Django รับ Request |
| Django ดูว่า URL ตรงกับอะไร | `urls.py` |
| Django เรียกโค้ดที่จัดการ | `views.py` |
| views.py ดึงข้อมูล | จาก Firebase |
| views.py ส่งข้อมูลไปแสดง | `templates/*.html` |
| User เห็นหน้าเว็บ | HTML + CSS (Tailwind) |

---

## 📄 ไฟล์ถัดไป

→ [03-views-explanation.md](./03-views-explanation.md) - อธิบาย views.py อย่างละเอียด
