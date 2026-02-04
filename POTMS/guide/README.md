# 📚 POTMS Code Documentation

## ภาพรวมของโปรเจค (Project Overview)

**POTMS** (Purchase Order Tracking & Management System) เป็นระบบจัดการติดตามการสั่งซื้อของโครงการ พัฒนาด้วย Django + Firebase Firestore

---

## 📁 โครงสร้างโปรเจค

```
POTMS/
├── api/                          # Django App หลัก
│   ├── templates/                # HTML Templates (19 files)
│   ├── utils/                    # Utility functions
│   ├── views.py                  # API Views (2400+ lines)
│   ├── urls.py                   # URL routing
│   ├── models.py                 # Django models
│   └── serializers.py            # DRF serializers
├── backend/                      # Django Settings
│   ├── settings.py               # Configuration
│   ├── firebase_config.py        # Firebase setup
│   └── urls.py                   # Root URL config
├── guide/                        # Documentation
└── requirements.txt              # Dependencies
```

---

## 📖 สารบัญเอกสาร

| ไฟล์ | เนื้อหา |
|------|---------|
| [02-settings.md](02-settings.md) | Django Settings |
| [03-firebase-config.md](03-firebase-config.md) | Firebase Configuration |
| [04-authentication.md](04-authentication.md) | ระบบ Login/JWT |
| [05-views-overview.md](05-views-overview.md) | ภาพรวม Views ทั้งหมด |
| [06-urls.md](06-urls.md) | URL Patterns |
| [07-budget-system.md](07-budget-system.md) | ระบบงบประมาณ |
| [08-templates.md](08-templates.md) | HTML Templates |
| [09-utilities.md](09-utilities.md) | Utility Functions |
| [libraries_usage.md](libraries_usage.md) | รายการ Libraries |

---

## 🔧 เทคโนโลยีที่ใช้

| เทคโนโลยี | เวอร์ชัน | การใช้งาน |
|----------|---------|-----------|
| Django | 5.2.6 | Web Framework |
| Django REST Framework | 3.16.1 | REST API |
| Firebase Admin | 7.1.0 | Firebase SDK |
| Firestore | - | NoSQL Database |
| JWT | 5.3.1 | Authentication |
| TailwindCSS | CDN | Styling |
| SweetAlert2 | CDN | Alerts/Modals |

---

## 👥 Actors ในระบบ

| Actor | บทบาท |
|-------|-------|
| **User** | ผู้สั่งซื้อ/เจ้าของโครงการ |
| **Staff** | เจ้าหน้าที่พัสดุ |
| **System** | จัดการงบประมาณอัตโนมัติ |

---

## 🔄 Order Status Flow

```
Draft → Pending → WaitingBossApproval → Approved → SentToProcurement 
    → ReceivedFromProcurement → WaitingInspection → Inspected → Closed
```

| สถานะ | ความหมาย |
|-------|----------|
| Draft | ฉบับร่าง |
| Pending | รอ Staff ตรวจสอบ |
| WaitingBossApproval | รอหัวหน้าเซ็น |
| Approved | อนุมัติแล้ว |
| CorrectionNeeded | ต้องแก้ไข |
| Rejected | ปฏิเสธ |
| SentToProcurement | ส่งพัสดุแล้ว |
| ReceivedFromProcurement | รับของจากพัสดุแล้ว |
| WaitingInspection | รอตรวจรับ |
| Inspected | ตรวจรับแล้ว |
| Closed | ปิดแล้ว |

---

## 💰 Budget Flow

```
สร้างใบขอซื้อ → กันวงเงิน (reserved ↑)
    │
    ├── อนุมัติ → ตรวจรับ → บันทึกค่าจริง (used ↑, reserved ↓)
    │
    └── ปฏิเสธ/แก้ไข → คืนวงเงิน (reserved ↓)
```

---

## 📅 อัพเดทล่าสุด

- วันที่: 10/01/2026
- ไฟล์ views.py: 2,472 บรรทัด
- Templates: 19 ไฟล์
