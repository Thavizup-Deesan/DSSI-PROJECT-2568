# POTMS — Purchase Order Tracking Management System

ระบบติดตามใบสั่งซื้อวัสดุ สำหรับมหาวิทยาลัยอุบลราชธานี

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.2, Django REST Framework |
| Frontend | Tailwind CSS + DaisyUI 4, Vanilla JS |
| Auth | Google OAuth 2.0 via django-allauth (เฉพาะ @ubu.ac.th) |
| Database | SQLite (dev), PostgreSQL (prod) |
| Container | Docker Compose |

## Project Structure

```
DSSI-PROJECT-2568/
├── Diagram/
│   └── class.puml              # PlantUML class diagram
├── POTMS/
│   ├── api/
│   │   ├── models.py           # 8 entities: User, Project, PurchaseOrder, ...
│   │   ├── views.py            # Class-based API views (REST)
│   │   ├── urls.py             # API routes (/api/) + Page routes
│   │   ├── allauth_adapter.py  # Custom social account adapter
│   │   ├── migrations/         # DB migrations + seed data
│   │   └── templates/          # HTML templates (DaisyUI)
│   ├── backend/
│   │   ├── settings.py
│   │   └── urls.py
│   ├── docker-compose.dev.yml
│   ├── Dockerfile
│   └── requirements.txt
└── README.md
```

## Data Model

- **User** — ผู้ใช้งาน (auto-create เมื่อ login ด้วย Google @ubu.ac.th)
  - `is_admin` — ผู้ดูแลระบบ
  - `is_officer` — เจ้าหน้าที่พัสดุ
  - `is_head` — หัวหน้าภาค
- **Project** — โครงการ (สร้างโดย Officer, มี budget tracking)
- **ProjectParticipant** — ผู้เข้าร่วมโครงการ (Requester / Committee)
- **PurchaseOrder** — ใบสั่งซื้อ (Draft → Reserved → Pending_Approval → Approved → Completed)
- **OrderItem** — รายการวัสดุในใบสั่งซื้อ
- **PartialReceive** — ใบรับของ/ใบเสร็จ (Pending_Inspection → Inspected)
- **Inspection** — ผลตรวจรับ (Pass / Reject)
- **Payment** — การเบิกจ่าย (Processing → Paid)

## Quick Start (Development)

```bash
# 1. Clone
git clone https://github.com/Thavizup-Deesan/DSSI-PROJECT-2568.git
cd DSSI-PROJECT-2568/POTMS

# 2. ตั้งค่า Google OAuth (optional)
#    สร้างไฟล์ .env หรือ export ตัวแปร:
#    GOOGLE_CLIENT_SECRET=<your-secret>

# 3. Run with Docker
docker compose -f docker-compose.dev.yml up --build

# 4. เปิดเบราว์เซอร์
#    http://localhost:8000
```

Migration จะรันอัตโนมัติพร้อม seed admin users:
- `wayo.p@ubu.ac.th` (Admin + Officer)
- `thavizup.de.66@ubu.ac.th` (Admin + Officer)

เพิ่ม admin เพิ่มเติมได้ผ่าน env `POTMS_ADMIN_EMAILS` (comma-separated)

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/auth/me/` | ข้อมูล user ปัจจุบัน |
| POST | `/api/auth/logout/` | ออกจากระบบ |

### Projects (Officer only)
| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/api/projects/` | รายการ / สร้างโครงการ |
| GET/PUT/DELETE | `/api/projects/<id>/` | รายละเอียด / แก้ไข / ลบ |
| POST | `/api/projects/<id>/start/` | เริ่มโครงการ (Draft → Active) |
| POST | `/api/projects/<id>/close/` | ปิดโครงการ |

### Participants (Officer only)
| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/api/projects/<id>/participants/` | รายชื่อ / เพิ่มผู้เข้าร่วม |
| DELETE | `/api/projects/<id>/participants/<uid>/` | ลบผู้เข้าร่วม |

### Purchase Orders
| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/api/orders/` | รายการ / สร้างใบสั่งซื้อ |
| GET/PUT | `/api/orders/<id>/` | รายละเอียด / แก้ไข |
| POST | `/api/orders/<id>/submit/` | ตรวจสอบ + กันวงเงิน |
| POST | `/api/orders/<id>/export/` | ส่งรออนุมัติ (Officer) |
| POST | `/api/orders/<id>/approve/` | อนุมัติ/ปฏิเสธ (Officer) |

### Partial Receives (Officer only)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/partial-receives/?order_id=X` | รายการใบรับของ |
| POST | `/api/partial-receives/` | สร้างใบรับของ |

### Inspections
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/inspections/?order_id=X` | รายการตรวจรับ |
| POST | `/api/inspections/` | บันทึกผลตรวจรับ |

### Payments (Officer only)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/payments/` | รายการเบิกจ่าย |
| POST | `/api/payments/` | ตั้งเบิกจ่าย |

### Admin & User Management
| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/api/admins/` | รายชื่อ / เพิ่ม admin |
| DELETE | `/api/admins/<uid>/` | ถอด admin |
| GET | `/api/users/` | รายชื่อ user ทั้งหมด (Officer) |
| PUT | `/api/users/<uid>/` | แก้ไข flags/department (Officer) |

## Purchase Order Flow

```
Draft → Submit (กันวงเงิน) → Reserved → Export (ส่งอนุมัติ)
→ Pending_Approval → Approve → Approved
→ Partial Receive → Inspection → Payment → Completed
```

## Links

- **Figma Mockup:** https://www.figma.com/design/MwMGYaHzdhh0T5nqtXiR4L/Untitled?node-id=24-544&t=U4nE53EGEkVuW28w-1
- **Google Drive:** https://drive.google.com/drive/folders/1YXr_xa2F102Yfu3A0DOHMSBixSPiH_e0?usp=sharing
- **เอกสาร:** https://docs.google.com/document/d/1ohBHaTWRGV8d1iO_BuTXY5fG235RB8ZLqQvtKmq8N20/edit?usp=sharing
