# 📚 คู่มือภาพรวมโปรเจค POTMS

## 🎯 POTMS คืออะไร?

**POTMS** (Project Order Tracking Management System) คือ **ระบบติดตามการสั่งซื้อโครงการ** 
ที่พัฒนาด้วย Django Framework เชื่อมต่อกับ Firebase Firestore เป็น Database

---

## 🏗️ โครงสร้างโฟลเดอร์หลัก

```
DSSI-PROJECT-2568/
├── 📁 POTMS/                    # โฟลเดอร์หลักของโปรเจค Django
│   ├── 📁 api/                  # แอปหลักที่เขียน Logic ทั้งหมด
│   │   ├── 📁 templates/        # ไฟล์ HTML ทั้งหมด
│   │   ├── views.py             # ฟังก์ชัน API และ Logic หลัก
│   │   ├── urls.py              # กำหนดเส้นทาง URL
│   │   ├── models.py            # โครงสร้างข้อมูล (แต่ใช้ Firebase แทน)
│   │   └── serializers.py       # แปลงข้อมูลเป็น JSON
│   │
│   ├── 📁 backend/              # การตั้งค่าหลักของ Django
│   │   ├── settings.py          # ตั้งค่าโปรเจค (Database, Apps, etc.)
│   │   ├── urls.py              # URL หลักของโปรเจค
│   │   ├── firebase_config.py   # เชื่อมต่อ Firebase
│   │   └── firebase-key.json    # กุญแจเข้าถึง Firebase (ห้ามแชร์!)
│   │
│   ├── manage.py                # คำสั่งจัดการ Django
│   └── requirements.txt         # รายการ Library ที่ต้องติดตั้ง
│
├── 📁 Diagram/                  # ไฟล์ Diagram ต่างๆ (PlantUML)
├── 📁 Guide/                    # คู่มือที่คุณกำลังอ่าน
└── README.md                    # คำอธิบายโปรเจคเบื้องต้น
```

---

## 🔧 เทคโนโลยีที่ใช้

| เทคโนโลยี | หน้าที่ | หมายเหตุ |
|-----------|---------|----------|
| **Django** | Web Framework หลัก | จัดการ Backend ทั้งหมด |
| **Django REST Framework** | สร้าง API | รับ-ส่งข้อมูลแบบ JSON |
| **Firebase Firestore** | Database | เก็บข้อมูล Projects, Users |
| **TailwindCSS** | UI Framework | ตกแต่งหน้าเว็บ |
| **SweetAlert2** | Popup แจ้งเตือน | แสดง Alert สวยๆ |
| **Pandas** | จัดการข้อมูล | นำเข้า Excel/CSV |

---

## 🌐 URL หลักของระบบ

| URL | หน้าที่ | ใครเข้าถึงได้ |
|-----|---------|---------------|
| `/` | หน้าแรก (Homepage) | ทุกคน |
| `/api/login-page/` | หน้าเข้าสู่ระบบ | ทุกคน |
| `/api/register-page/` | หน้าสมัครสมาชิก | ทุกคน |
| `/api/dashboard/` | ดูรายการโครงการ | User |
| `/api/staff-dashboard/` | แดชบอร์ดเจ้าหน้าที่ | Staff, Admin |
| `/api/user-management/` | จัดการผู้ใช้งาน | Admin เท่านั้น |
| `/admin/` | Django Admin | Superuser |

---

## 👥 ประเภทผู้ใช้งาน (User Roles)

```
┌─────────────────────────────────────────────────────────────┐
│                         POTMS                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│    👤 User                  👨‍💼 Staff               👑 Admin   │
│    ├─ ดูโครงการ            ├─ ดูโครงการ           ├─ ทุกอย่าง │
│    └─ ดูงบประมาณ           ├─ เพิ่ม/แก้ไขโครงการ   ├─ จัดการ   │
│                            └─ นำเข้า Excel          User      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flow การทำงานของระบบ

```
                    ┌─────────────┐
                    │  Homepage   │
                    │     /       │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Login     │
                    │ /api/login- │
                    │   page/     │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
     ┌───────────┐  ┌───────────┐  ┌───────────┐
     │   User    │  │   Staff   │  │   Admin   │
     │ Dashboard │  │ Dashboard │  │ Dashboard │
     └───────────┘  └───────────┘  └─────┬─────┘
                                         │
                                         ▼
                                   ┌───────────┐
                                   │   User    │
                                   │Management │
                                   └───────────┘
```

---

## 📦 การติดตั้งและรันโปรเจค

### 1. ติดตั้ง Dependencies
```bash
cd POTMS
pip install -r requirements.txt
```

### 2. รัน Server
```bash
python manage.py runserver
```

### 3. เปิดเบราว์เซอร์
```
http://127.0.0.1:8000/
```

---

## 📄 ไฟล์ถัดไปที่ควรอ่าน

1. [02-django-basics.md](./02-django-basics.md) - พื้นฐาน Django
2. [03-views-explanation.md](./03-views-explanation.md) - อธิบาย views.py
3. [04-urls-routing.md](./04-urls-routing.md) - อธิบาย URL Routing
4. [05-firebase-integration.md](./05-firebase-integration.md) - เชื่อมต่อ Firebase
5. [06-templates-html.md](./06-templates-html.md) - อธิบาย HTML Templates
6. [07-api-reference.md](./07-api-reference.md) - API Reference


tech stack
frontend 
- html5
- javascript 
- tailwind css

backend
- Django
- Django REST Framework
- Pandas

database
- Firebase Firestore