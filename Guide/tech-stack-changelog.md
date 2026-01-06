# Tech Stack Change Log - POTMS

บันทึกการเปลี่ยนแปลง Tech Stack ของโปรเจค POTMS ตามลำดับเวลา

---

## 1. Database Migration: MySQL → Firebase Firestore

### 1.1 สิ่งที่เปลี่ยน
- เปลี่ยน Primary Database จาก **MySQL** เป็น **Firebase Firestore**
- เพิ่ม `firebase_admin` package ใน requirements.txt
- สร้าง Firebase configuration และ credentials
- แก้ไข `api/views.py` ให้เชื่อมต่อกับ Firestore แทน MySQL
- เก็บข้อมูลทั้งหมด (users, projects, orders, budgets) ใน Firestore collections

### 1.2 วันที่เปลี่ยน
**22 ธันวาคม 2568** (2025-12-22)

### 1.3 เหตุผลที่เปลี่ยน
- ต้องการ deploy ใน production-level environment
- Vercel ไม่รองรับ MySQL แบบ persistent
- Firebase Firestore เป็น serverless database ที่ scale ได้ง่าย
- ไม่ต้องจัดการ database server เอง

### 1.4 ผลกระทบ
- ✅ สามารถ deploy บน Vercel ได้
- ✅ ข้อมูลเก็บบน cloud ทำให้เข้าถึงได้ทุกที่
- ✅ Realtime updates และ offline support
- ⚠️ ต้องมี Firebase project และ credentials
- ⚠️ ต้องเข้าใจ NoSQL document structure

---

## 2. Security Vulnerability Fixes

### 2.1 สิ่งที่เปลี่ยน
- สร้าง `api/utils/authz.py` - Authorization utilities สำหรับตรวจสอบสิทธิ์ staff
- สร้าง `api/utils/validators.py` - Input validation และ status transition checks
- สร้าง `api/utils/audit.py` - Audit trail logging
- อัพเดท `api/views.py` - เพิ่ม ownership verification ใน OrderApproveAPIView
- อัพเดท `backend/settings.py` - เพิ่ม security configurations

### 2.2 วันที่เปลี่ยน
**24 ธันวาคม 2568** (2025-12-24)

### 2.3 เหตุผลที่เปลี่ยน
- แก้ไข 5 Critical vulnerabilities และ 8 High priority vulnerabilities ที่พบจาก security review
- ป้องกัน staff approve orders จาก projects ที่ไม่ได้ดูแล (V3.2)
- เพิ่ม rate limiting และ request size limits (V14)
- เพิ่ม CSRF protection และ session security (V12, V8.2)

### 2.4 ผลกระทบ
- ✅ ปิด security vulnerabilities ทั้งหมดที่พบ
- ✅ มี audit trail สำหรับการ approve orders
- ✅ ระบบปลอดภัยมากขึ้น
- ⚠️ Staff ที่ไม่ได้ assign กับ project จะ approve orders ไม่ได้

---

## 3. Django Security Settings

### 3.1 สิ่งที่เปลี่ยน
อัพเดท `backend/settings.py`:
- เพิ่ม `DATA_UPLOAD_MAX_MEMORY_SIZE` และ `FILE_UPLOAD_MAX_MEMORY_SIZE` (2.5MB)
- เพิ่ม `SESSION_COOKIE_AGE` (2 ชั่วโมง)
- เพิ่ม `CSRF_COOKIE_SECURE`, `SESSION_COOKIE_SECURE`
- เพิ่ม `SECURE_BROWSER_XSS_FILTER`, `SECURE_CONTENT_TYPE_NOSNIFF`
- เพิ่ม `SECURE_SSL_REDIRECT` แบบ conditional (เฉพาะ Vercel)

### 3.2 วันที่เปลี่ยน
**26 ธันวาคม 2568** (2025-12-26)

### 3.3 เหตุผลที่เปลี่ยน
- ป้องกัน memory exhaustion attacks
- เพิ่ม session timeout สำหรับความปลอดภัย
- ป้องกัน XSS และ clickjacking attacks

### 3.4 ผลกระทบ
- ✅ Upload files ได้ไม่เกิน 2.5MB
- ✅ Session หมดอายุหลัง 2 ชั่วโมง
- ✅ มี security headers ป้องกันการโจมตี
- ⚠️ Local development ไม่ใช้ SSL redirect (เฉพาะ production)

---

## 4. Dependencies Update

### 3.1 สิ่งที่เปลี่ยน
อัพเดท `requirements.txt`:
- `numpy`: 2.3.4 → **1.26.4**
- `pandas`: 2.3.3 → **2.1.4**
- ลบ `django-cors-headers==4.3.1` ที่ซ้ำซ้อน (เหลือเฉพาะ 4.9.0)

### 3.2 วันที่เปลี่ยน
**29 ธันวาคม 2568** (2025-12-29)

### 3.3 เหตุผลที่เปลี่ยน
- `numpy 2.3.4` และ `pandas 2.3.3` ต้องการ Python 3.11+ แต่ Docker ใช้ Python 3.10
- มี `django-cors-headers` ซ้ำ 2 version ทำให้ pip install ล้มเหลว

### 3.4 ผลกระทบ
- ✅ Docker build สำเร็จ
- ✅ Compatible กับ Python 3.10
- ✅ Vercel deployment ยังทำงานปกติ
- ⚠️ ใช้ numpy/pandas version เก่ากว่า (แต่ stable และเพียงพอ)

---

## 5. Docker Production Setup

### 4.1 สิ่งที่เปลี่ยน
เพิ่มไฟล์ใหม่:
- `Dockerfile.prod` - Production Dockerfile
- `docker-compose.yml` - Production orchestration (Django + Nginx + Redis)
- `docker-compose.dev.yml` - Development setup
- `nginx/nginx.conf` - Nginx reverse proxy configuration
- `.dockerignore` - Optimize build context
- `.env.example` - Environment variables template

### 4.2 วันที่เปลี่ยน
**4 มกราคม 2569** (2026-01-04)

### 4.3 เหตุผลที่เปลี่ยน
- ต้องการ production-ready deployment option นอกเหนือจาก Vercel
- ต้องการ containerized environment ที่ deploy ได้ทุกที่
- ต้องการ Nginx reverse proxy สำหรับ rate limiting และ security

### 4.4 ผลกระทบ
- ✅ สามารถ deploy บน Docker/Kubernetes ได้
- ✅ Vercel ยังทำงานปกติ (ไม่กระทบ)
- ✅ มี Nginx rate limiting ป้องกัน DDoS
- ⚠️ ต้องติดตั้ง Docker Desktop สำหรับ local Docker deployment

---

## 6. Database Configuration Update

### 5.1 สิ่งที่เปลี่ยน
อัพเดท `backend/settings.py`:
- เพิ่มการตรวจสอบ `DOCKER` environment variable
- Docker environment ใช้ SQLite แทน MySQL

อัพเดท `docker-compose.yml`:
- เพิ่ม `DOCKER=1` environment variable

### 5.2 วันที่เปลี่ยน
**4 มกราคม 2569** (2026-01-04)

### 5.3 เหตุผลที่เปลี่ยน
- Docker container ไม่มี MySQL client ติดตั้ง
- ข้อมูลจริงเก็บใน Firebase Firestore อยู่แล้ว
- Django ต้องการ database แค่สำหรับ session เท่านั้น

### 5.4 ผลกระทบ
- ✅ Docker รันได้โดยไม่ต้องติดตั้ง MySQL
- ✅ Firebase Firestore ยังเป็น primary data store
- ✅ Local development ยังใช้ MySQL ได้ปกติ
- ✅ Vercel ยังใช้ SQLite เหมือนเดิม

---

## 📋 สรุป Tech Stack ปัจจุบัน

| Component | Technology | Version |
|-----------|------------|---------|
| Backend Framework | Django | 5.2.6 |
| REST API | Django REST Framework | 3.16.1 |
| Authentication | SimpleJWT | 5.3.1 |
| Primary Database | Firebase Firestore | - |
| Django Database | SQLite (Docker/Vercel) / MySQL (Local) | - |
| Web Server | Gunicorn | 23.0.0 |
| Reverse Proxy | Nginx | Alpine |
| Cache | Redis | 7-Alpine |
| Container | Docker | Desktop |
| Cloud Hosting | Vercel | - |

---

*อัพเดทล่าสุด: 5 มกราคม 2569*
