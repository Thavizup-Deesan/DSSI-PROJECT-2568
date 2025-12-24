# 🔗 อธิบาย URL Routing

## 📍 ไฟล์ที่เกี่ยวข้อง

```
POTMS/
├── backend/urls.py      # URL หลักของโปรเจค
└── api/urls.py          # URL ของแอป api
```

---

## 🌐 URL Routing คืออะไร?

URL Routing คือการ **จับคู่** ระหว่าง URL ที่ผู้ใช้พิมพ์ กับ ฟังก์ชันที่จะทำงาน

```
User พิมพ์: http://127.0.0.1:8000/api/login-page/
                                   │
                    Django จับคู่กับ: login_page()
                                   │
                    แสดงหน้า: login.html
```

---

## 📁 backend/urls.py (URL หลัก)

```python
from django.contrib import admin
from django.urls import path, include
from api.views import homepage

urlpatterns = [
    # 1. Django Admin Panel
    path('admin/', admin.site.urls),
    
    # 2. Homepage (หน้าแรก)
    path('', homepage, name='homepage'),
    
    # 3. เชื่อมต่อ URL ของแอป api
    path('api/', include('api.urls')),
]
```

**อธิบาย:**

| Pattern | ความหมาย | ตัวอย่าง URL |
|---------|----------|--------------|
| `path('admin/', ...)` | ถ้า URL เริ่มด้วย `admin/` | `/admin/` |
| `path('', ...)` | ถ้า URL ว่างเปล่า (หน้าแรก) | `/` |
| `path('api/', include(...))` | ถ้า URL เริ่มด้วย `api/` ให้ไปดูใน `api/urls.py` | `/api/xxx/` |

---

## 📁 api/urls.py (URL ของแอป api)

```python
from django.urls import path
from .views import (
    ProjectAPIView, ProjectDetailAPIView, ProjectImportAPIView, 
    UserRegisterAPIView, UserLoginAPIView, StatsAPIView,
    UserListAPIView, UserDetailAPIView,
    project_dashboard, login_page, staff_dashboard, homepage, 
    register_page, user_management_page
)

urlpatterns = [
    # ===== Project APIs =====
    path('projects/', ProjectAPIView.as_view(), name='project-list-create'),
    path('projects/import/', ProjectImportAPIView.as_view(), name='project-import'),
    path('projects/<str:project_id>/', ProjectDetailAPIView.as_view(), name='project-detail'),
    
    # ===== User Management APIs =====
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<str:user_id>/', UserDetailAPIView.as_view(), name='user-detail'),
    
    # ===== Page Views (HTML) =====
    path('dashboard/', project_dashboard, name='project-dashboard'),
    path('login-page/', login_page, name='login-page'),
    path('register-page/', register_page, name='register-page'),
    path('staff-dashboard/', staff_dashboard, name='staff-dashboard'),
    path('user-management/', user_management_page, name='user-management'),
    
    # ===== Authentication APIs =====
    path('register/', UserRegisterAPIView.as_view(), name='user-register'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    
    # ===== Stats API =====
    path('stats/', StatsAPIView.as_view(), name='stats'),
]
```

---

## 🔍 อธิบาย Syntax

### 1. path() ธรรมดา

```python
path('login-page/', login_page, name='login-page')
```

| ส่วน | ความหมาย |
|------|----------|
| `'login-page/'` | URL Pattern (ต้องลงท้ายด้วย `/`) |
| `login_page` | ฟังก์ชันที่จะทำงาน (จาก views.py) |
| `name='login-page'` | ชื่อเรียก URL นี้ (ใช้อ้างอิงใน code) |

### 2. path() กับ Class-Based View

```python
path('projects/', ProjectAPIView.as_view(), name='project-list-create')
```

- `.as_view()` = แปลง Class เป็น View ที่ Django ใช้ได้

### 3. path() กับ Dynamic Parameter

```python
path('projects/<str:project_id>/', ProjectDetailAPIView.as_view(), name='project-detail')
```

| ส่วน | ความหมาย |
|------|----------|
| `<str:project_id>` | Parameter แบบ String |
| `project_id` | ชื่อตัวแปรที่จะส่งไปให้ View |

**ตัวอย่าง:**
```
URL: /api/projects/abc123/

project_id = "abc123"  <-- Django ส่งค่านี้ไปให้ View
```

---

## 🗺️ สรุป URL ทั้งหมด

### หน้าเว็บ HTML

| URL | View Function | หน้าที่ |
|-----|---------------|---------|
| `/` | `homepage` | หน้าแรก |
| `/api/login-page/` | `login_page` | หน้า Login |
| `/api/register-page/` | `register_page` | หน้าสมัครสมาชิก |
| `/api/dashboard/` | `project_dashboard` | หน้ารายการโครงการ (User) |
| `/api/staff-dashboard/` | `staff_dashboard` | หน้าแดชบอร์ด (Staff) |
| `/api/user-management/` | `user_management_page` | หน้าจัดการผู้ใช้ (Admin) |

### API Endpoints

| Method | URL | View Class | หน้าที่ |
|--------|-----|------------|---------|
| GET | `/api/projects/` | `ProjectAPIView` | ดึงโครงการทั้งหมด |
| POST | `/api/projects/` | `ProjectAPIView` | สร้างโครงการใหม่ |
| PUT | `/api/projects/{id}/` | `ProjectDetailAPIView` | แก้ไขโครงการ |
| DELETE | `/api/projects/{id}/` | `ProjectDetailAPIView` | ลบโครงการ |
| POST | `/api/projects/import/` | `ProjectImportAPIView` | นำเข้า Excel |
| GET | `/api/users/` | `UserListAPIView` | ดึงผู้ใช้ทั้งหมด |
| GET/PUT/DELETE | `/api/users/{id}/` | `UserDetailAPIView` | จัดการผู้ใช้ |
| POST | `/api/register/` | `UserRegisterAPIView` | สมัครสมาชิก |
| POST | `/api/login/` | `UserLoginAPIView` | เข้าสู่ระบบ |
| GET | `/api/stats/` | `StatsAPIView` | ดึงสถิติ |

---

## 🔄 Flow การ Route URL

```
User: http://127.0.0.1:8000/api/projects/abc123/

Step 1: backend/urls.py
        ├── path('api/', include('api.urls'))
        └── ตรง! ไปต่อที่ api/urls.py

Step 2: api/urls.py
        ├── URL ที่เหลือ: projects/abc123/
        ├── path('projects/<str:project_id>/', ...)
        └── ตรง! project_id = "abc123"

Step 3: views.py
        ├── เรียก ProjectDetailAPIView
        └── ส่ง project_id="abc123" ไปด้วย
```

---

## 💡 Tips

### ใช้ name เพื่ออ้างอิง URL

```python
# ใน Template HTML
<a href="{% url 'login-page' %}">Login</a>

# ใน Python
from django.urls import reverse
url = reverse('login-page')  # ได้ '/api/login-page/'
```

### ลำดับ path() สำคัญ!

```python
# ❌ ผิด! import จะไม่ทำงาน
path('projects/<str:project_id>/', ...),  # จะจับ 'import' ด้วย!
path('projects/import/', ...),

# ✅ ถูก! import อยู่ก่อน
path('projects/import/', ...),  # เช็คก่อน
path('projects/<str:project_id>/', ...),  # ที่เหลือ
```

---

## 📄 ไฟล์ถัดไป

→ [05-firebase-integration.md](./05-firebase-integration.md) - การเชื่อมต่อ Firebase
