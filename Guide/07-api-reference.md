# 📡 API Reference

## 🔗 Base URL

```
http://127.0.0.1:8000/api/
```

---

## 📋 สารบัญ API

| หมวด | Endpoints |
|------|-----------|
| [Projects](#projects-api) | จัดการโครงการ |
| [Authentication](#authentication-api) | Login/Register |
| [Users](#users-api) | จัดการผู้ใช้ |
| [Stats](#stats-api) | สถิติ |

---

## 📁 Projects API

### GET /api/projects/
ดึงรายการโครงการทั้งหมด

**Request:**
```http
GET /api/projects/
```

**Response (200 OK):**
```json
[
    {
        "id": "abc123",
        "project_name": "โครงการ A",
        "budget_total": 1000000.0,
        "budget_reserved": 200000.0,
        "budget_spent": 150000.0,
        "status": "Active",
        "created_at": "2024-01-15T10:30:00"
    },
    {
        "id": "def456",
        "project_name": "โครงการ B",
        "budget_total": 500000.0,
        "budget_reserved": 0.0,
        "budget_spent": 0.0,
        "status": "Pending",
        "created_at": "2024-01-20T14:00:00"
    }
]
```

---

### POST /api/projects/
สร้างโครงการใหม่

**Request:**
```http
POST /api/projects/
Content-Type: application/json

{
    "project_name": "โครงการใหม่",
    "budget_total": 1000000,
    "status": "Active"
}
```

**Response (201 Created):**
```json
{
    "id": "xyz789",
    "message": "สร้างโครงการสำเร็จแล้ว"
}
```

**Response (400 Bad Request):**
```json
{
    "error": "ข้อความ Error"
}
```

---

### PUT /api/projects/{project_id}/
แก้ไขโครงการ

**Request:**
```http
PUT /api/projects/abc123/
Content-Type: application/json

{
    "project_name": "ชื่อใหม่",
    "budget_total": 2000000,
    "status": "Completed"
}
```

**Response (200 OK):**
```json
{
    "message": "แก้ไขสำเร็จ"
}
```

---

### DELETE /api/projects/{project_id}/
ลบโครงการ

**Request:**
```http
DELETE /api/projects/abc123/
```

**Response (200 OK):**
```json
{
    "message": "ลบสำเร็จ"
}
```

---

### POST /api/projects/import/
นำเข้าโครงการจาก Excel/CSV

**Request:**
```http
POST /api/projects/import/
Content-Type: multipart/form-data

file: [ไฟล์ Excel/CSV]
```

**รูปแบบไฟล์ที่รองรับ:**
| Column | ความหมาย |
|--------|----------|
| `project_name` | ชื่อโครงการ |
| `budget_total` | งบประมาณ |

**Response (201 Created):**
```json
{
    "message": "นำเข้าข้อมูลสำเร็จ 5 โครงการ"
}
```

---

## 🔐 Authentication API

### POST /api/register/
สมัครสมาชิกใหม่

**Request:**
```http
POST /api/register/
Content-Type: application/json

{
    "username": "john",
    "password": "secret123",
    "role": "User",
    "department": "IT"
}
```

**Response (201 Created):**
```json
{
    "message": "ลงทะเบียนสำเร็จ"
}
```

**Response (400 Bad Request):**
```json
{
    "error": "ชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว"
}
```

---

### POST /api/login/
เข้าสู่ระบบ

**Request:**
```http
POST /api/login/
Content-Type: application/json

{
    "username": "john",
    "password": "secret123"
}
```

**Response (200 OK):**
```json
{
    "message": "เข้าสู่ระบบสำเร็จ",
    "user": {
        "id": "user001",
        "username": "john",
        "role": "Admin",
        "department": "IT"
    }
}
```

**Response (401 Unauthorized):**
```json
{
    "error": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
}
```

---

## 👥 Users API

### GET /api/users/
ดึงรายชื่อผู้ใช้ทั้งหมด (สำหรับ Admin)

**Request:**
```http
GET /api/users/
```

**Response (200 OK):**
```json
[
    {
        "id": "user001",
        "username": "john",
        "role": "Admin",
        "department": "IT",
        "created_at": "2024-01-10T09:00:00"
    },
    {
        "id": "user002",
        "username": "jane",
        "role": "Staff",
        "department": "Finance",
        "created_at": "2024-01-12T10:30:00"
    }
]
```

> ⚠️ **หมายเหตุ:** ไม่ส่ง password กลับเพื่อความปลอดภัย

---

### GET /api/users/{user_id}/
ดึงข้อมูลผู้ใช้รายบุคคล

**Request:**
```http
GET /api/users/user001/
```

**Response (200 OK):**
```json
{
    "id": "user001",
    "username": "john",
    "role": "Admin",
    "department": "IT",
    "created_at": "2024-01-10T09:00:00"
}
```

**Response (404 Not Found):**
```json
{
    "error": "ไม่พบผู้ใช้ที่ระบุ"
}
```

---

### PUT /api/users/{user_id}/
แก้ไขข้อมูลผู้ใช้

**Request:**
```http
PUT /api/users/user001/
Content-Type: application/json

{
    "role": "Staff",
    "department": "HR",
    "password": "newpassword123"   // Optional
}
```

**Response (200 OK):**
```json
{
    "message": "แก้ไขข้อมูลผู้ใช้สำเร็จ"
}
```

---

### DELETE /api/users/{user_id}/
ลบผู้ใช้ออกจากระบบ

**Request:**
```http
DELETE /api/users/user001/
```

**Response (200 OK):**
```json
{
    "message": "ลบผู้ใช้สำเร็จ"
}
```

---

## 📊 Stats API

### GET /api/stats/
ดึงสถิติสำหรับ Dashboard

**Request:**
```http
GET /api/stats/
```

**Response (200 OK):**
```json
{
    "pending": 5,
    "approved": 10,
    "in_progress": 3,
    "completed": 25,
    "total_projects": 43
}
```

---

## 📜 HTTP Status Codes

| Code | ความหมาย | ใช้เมื่อ |
|------|----------|----------|
| `200` | OK | Request สำเร็จ |
| `201` | Created | สร้างข้อมูลสำเร็จ |
| `400` | Bad Request | ข้อมูลไม่ถูกต้อง |
| `401` | Unauthorized | ไม่มีสิทธิ์ / Login ผิด |
| `404` | Not Found | ไม่พบข้อมูล |
| `500` | Server Error | Error ภายใน Server |

---

## 💻 ตัวอย่างการเรียก API ด้วย JavaScript

### ดึงโครงการทั้งหมด
```javascript
const response = await fetch('/api/projects/');
const projects = await response.json();
console.log(projects);
```

### สร้างโครงการใหม่
```javascript
const response = await fetch('/api/projects/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        project_name: 'โครงการใหม่',
        budget_total: 1000000,
        status: 'Active'
    })
});

if (response.ok) {
    const data = await response.json();
    console.log('Created:', data.id);
}
```

### Login
```javascript
const response = await fetch('/api/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'john',
        password: 'secret123'
    })
});

if (response.ok) {
    const data = await response.json();
    localStorage.setItem('user', JSON.stringify(data.user));
} else {
    const error = await response.json();
    alert(error.error);
}
```

---

## 🧪 ทดสอบ API ด้วย cURL

```bash
# GET Projects
curl -X GET http://127.0.0.1:8000/api/projects/

# POST Create Project
curl -X POST http://127.0.0.1:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{"project_name":"Test","budget_total":100000}'

# POST Login
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"secret123"}'

# DELETE Project
curl -X DELETE http://127.0.0.1:8000/api/projects/abc123/
```

---

## 📄 จบการอธิบาย

หวังว่าเอกสารทั้งหมดนี้จะช่วยให้เข้าใจโปรเจค POTMS ได้ง่ายขึ้นครับ! 🎉
