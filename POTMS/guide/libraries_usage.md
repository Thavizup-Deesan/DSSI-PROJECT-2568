# 📦 รายการ Libraries ของโปรเจค POTMS

## สรุป Dependencies

วิเคราะห์จาก `requirements.txt` และการใช้งานจริงใน source code

---

## ✅ Libraries ที่ใช้งานจริง

| Library | เวอร์ชัน | การใช้งาน |
|---------|----------|----------|
| Django | 5.2.6 | Framework หลัก |
| djangorestframework | 3.16.1 | REST API |
| djangorestframework-simplejwt | 5.3.1 | JWT Authentication |
| django-ratelimit | 4.1.0 | Rate limiting (ป้องกัน brute force) |
| django-cors-headers | 4.9.0 | CORS headers |
| django-extensions | 4.1 | Django utilities |
| firebase-admin | 7.1.0 | Firebase Admin SDK |
| google-cloud-firestore | 2.21.0 | Firestore database |
| pandas | 2.1.4 | จัดการข้อมูล (import CSV) |
| qrcode[pil] | >=7.4.2 | สร้าง QR Code |
| gunicorn | 23.0.0 | Production WSGI server |
| whitenoise | 6.11.0 | Static file serving |
| dj-database-url | 3.0.1 | Database URL configuration |
| PyJWT | 2.10.1 | JWT token handling |

---

## ⚠️ Libraries ที่ไม่ได้ใช้ (อาจลบได้)

| Library | เวอร์ชัน | หมายเหตุ |
|---------|----------|----------|
| openpyxl | 3.1.5 | ไม่มี import ใน code |
| PyMySQL | 1.1.2 | ไม่ได้ใช้ MySQL database |
| google-cloud-storage | 3.6.0 | เคยใช้สำหรับ file upload แต่ถูกลบออกแล้ว |

---

## 📌 Dependencies ที่เป็น Transitive (ใช้โดยอ้อม)

Libraries เหล่านี้เป็น dependencies ของ libraries อื่น ไม่ควรลบ:

- `anyio`, `asgiref` - async support
- `CacheControl`, `cachetools` - caching
- `certifi`, `cffi`, `cryptography` - SSL/security
- `google-*` packages - Firebase dependencies
- `grpcio`, `grpcio-status` - gRPC for Firebase
- `httpx`, `httpcore` - HTTP client
- `numpy` - pandas dependency
- `protobuf`, `proto-plus` - protocol buffers
- `requests` - HTTP requests
- `typing_extensions` - type hints

---

## 🔧 วิธีลบ Libraries ที่ไม่ได้ใช้

หากต้องการ clean up `requirements.txt`:

```bash
# ลบออกจาก requirements.txt
openpyxl==3.1.5
PyMySQL==1.1.2
google-cloud-storage==3.6.0
```

แล้วรัน:
```bash
pip install -r requirements.txt
```

---

## 📝 หมายเหตุ

- วิเคราะห์เมื่อ: 10/01/2026
- ไฟล์: requirements.txt (61 บรรทัด)
- Total packages: 61 packages
- ใช้งานจริง: ~14 packages (หลัก)
- ไม่ได้ใช้: ~3 packages
