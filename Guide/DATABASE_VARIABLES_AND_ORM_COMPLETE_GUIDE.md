# 📚 ฐานข้อมูล ตัวแปร Request/Response และ Django ORM - คู่มือละเอียด

---

## 📖 สารบัญ

1. [ฐานข้อมูล](#1-ฐานข้อมูล)
2. [ตัวแปรและหน้าที่](#2-ตัวแปรและหน้าที่)
3. [Request/Response Flow](#3-requestresponse-flow)
4. [Django ORM](#4-django-orm-basic)
5. [Django Shell ใช้งาน](#5-django-shell-ใช้งาน)

---

---

# 1. 📊 ฐานข้อมูล

## 1.1 ชื่อฐานข้อมูล

```
ฐานข้อมูล: potms
ประเภท: MySQL
ที่อยู่: localhost:3306
User: root
```

## 1.2 ตารางในฐานข้อมูล

### **ตาราที่ 1: projects**

ตารางนี้เก็บข้อมูลโครงการ

```
┌─────────────────────────────────────────────────────────────────┐
│ Table: projects                                                 │
├──────────────────┬──────────────┬─────────────────┬──────────────┤
│ Column           │ Type         │ Key             │ Description  │
├──────────────────┼──────────────┼─────────────────┼──────────────┤
│ project_id       │ INT          │ PK (Primary)    │ ID เดี่ยว    │
│ project_code     │ VARCHAR(50)  │ UNIQUE          │ รหัสโครงการ  │
│ project_name     │ VARCHAR(255) │ -               │ ชื่อโครงการ  │
│ budget_total     │ DECIMAL(12,2)│ -               │ งบประมาณ     │
│ status           │ VARCHAR(50)  │ -               │ สถานะ        │
└──────────────────┴──────────────┴─────────────────┴──────────────┘
```

**ตัวอย่างข้อมูล:**

```
project_id = 1
project_code = "PRJ-001"
project_name = "โครงการทดสอบ"
budget_total = 1500000.00
status = "ดำเนินการ"
```

---

### **ตาราที่ 2: vendors**

ตารางนี้เก็บข้อมูลผู้ขาย/บริษัท

```
┌─────────────────────────────────────────────────────────┐
│ Table: vendors                                          │
├──────────────────┬──────────────┬─────────────────┬─────┤
│ Column           │ Type         │ Key             │ Desc│
├──────────────────┼──────────────┼─────────────────┼─────┤
│ vendor_id        │ INT          │ PK (Primary)    │ ID  │
│ vendor_name      │ VARCHAR(255) │ -               │ ชื่อ│
│ phone            │ VARCHAR(50)  │ -               │ โทร │
│ email            │ VARCHAR(255) │ -               │ อี่ │
└──────────────────┴──────────────┴─────────────────┴─────┘
```

**ตัวอย่างข้อมูล:**

```
vendor_id = 1
vendor_name = "บริษัท A & B"
phone = "02-1234-5678"
email = "contact@ab.co.th"
```

---

### **ตาราที่ 3: master_items**

ตารางนี้เก็บข้อมูลรายการพัสดุ/สินค้า

```
┌────────────────────────────────────────────────────────────────┐
│ Table: master_items                                            │
├──────────────────┬──────────────┬─────────────────┬────────────┤
│ Column           │ Type         │ Key             │ Description│
├──────────────────┼──────────────┼─────────────────┼────────────┤
│ item_id          │ INT          │ PK (Primary)    │ ID เดี่ยว  │
│ item_code        │ VARCHAR(50)  │ UNIQUE          │ รหัสรายการ │
│ item_name        │ VARCHAR(255) │ -               │ ชื่อรายการ │
│ standard_unit    │ VARCHAR(50)  │ -               │ หน่วย      │
│ created_at       │ DATETIME     │ -               │ เวลาสร้าง  │
└──────────────────┴──────────────┴─────────────────┴────────────┘
```

**ตัวอย่างข้อมูล:**

```
item_id = 1
item_code = "ITEM-001"
item_name = "โต๊ะประชุม"
standard_unit = "ตัว"
created_at = "2024-11-19 10:30:00"
```

---

## 1.3 ความสัมพันธ์ระหว่างตาราง

```
projects (1) ──→ (many) vendors
projects (1) ──→ (many) master_items
vendors  (1) ──→ (many) master_items
```

**หมายเหตุ:** ปัจจุบันการเชื่อมต่อยังไม่มี Foreign Key ที่ชัดเจน แต่สามารถสร้างได้ตามต้องการ

---

---

# 2. 🏷️ ตัวแปรและหน้าที่

## 2.1 ตัวแปรในตาราง Projects

### **1. project_id (AutoField)**

```
🔹 ชื่อ: project_id
🔹 ประเภท: Integer (Auto-increment)
🔹 ข้อมูล: 1, 2, 3, 4, 5, ...
🔹 หน้าที่:
   - Primary Key (PK) สำหรับระบุโครงการแต่ละรายการ
   - Django สร้างอัตโนมัติ ไม่ต้องใส่เอง
   - ใช้ในการ UPDATE/DELETE
🔹 ตัวอย่าง SQL: SELECT * FROM projects WHERE project_id = 1
```

**ใช้ใน Django ORM:**

```python
# ดึงด้วย PK
>>> project = Projects.objects.get(project_id=1)

# Update
>>> project = Projects.objects.get(pk=1)
>>> project.project_name = "ชื่อใหม่"
>>> project.save()

# Delete
>>> Projects.objects.filter(pk=1).delete()
```

---

### **2. project_code (CharField, UNIQUE)**

```
🔹 ชื่อ: project_code
🔹 ประเภท: String (ไม่ซ้ำกัน)
🔹 ข้อมูล: "PRJ-001", "PRJ-002", "PRJ-SHELL-001"
🔹 หน้าที่:
   - รหัสประจำตัวโครงการ
   - ใช้ระบุโครงการแบบ Human-readable
   - UNIQUE = ห้ามมีรหัสซ้ำ
   - ใช้ในการค้นหา/อัพเดท เพราะ readable กว่า ID
🔹 ตัวอย่าง SQL: SELECT * FROM projects WHERE project_code = 'PRJ-001'
```

**ใช้ใน Django ORM:**

```python
# ดึงด้วย code
>>> project = Projects.objects.get(project_code='PRJ-001')

# Filter
>>> projects = Projects.objects.filter(project_code__startswith='PRJ-')

# Check unique
>>> Projects.objects.filter(project_code='PRJ-001').exists()
True

# Update
>>> project = Projects.objects.get(project_code='PRJ-001')
>>> project.budget_total = 2000000
>>> project.save()

# Get or Create
>>> project, created = Projects.objects.get_or_create(
...     project_code='PRJ-NEW',
...     defaults={'project_name': 'New', 'status': 'ดำเนินการ'}
... )
```

---

### **3. project_name (CharField)**

```
🔹 ชื่อ: project_name
🔹 ประเภท: String
🔹 ข้อมูล: "โครงการทดสอบ", "Project A", "โครงการ A & B"
🔹 หน้าที่:
   - ชื่อเต็มของโครงการ
   - ใช้สำหรับแสดงผล (Display)
   - ประกาศให้ผู้ใช้ทั่วไปอ่าน
🔹 ตัวอย่าง SQL: SELECT project_name FROM projects
```

**ใช้ใน Django ORM:**

```python
# ดึงเฉพาะชื่อ
>>> projects = Projects.objects.values('project_name')

# Search
>>> projects = Projects.objects.filter(
...     project_name__icontains='ทดสอบ'  # case-insensitive
... )

# List ทั้งหมด
>>> for p in Projects.objects.all():
...     print(p.project_name)
```

---

### **4. budget_total (DecimalField)**

```
🔹 ชื่อ: budget_total
🔹 ประเภท: Decimal (ทศนิยม 2 ตำแหน่ง)
🔹 ข้อมูล: 1500000.00, 2000000.50
🔹 หน้าที่:
   - ยอดงบประมาณโครงการทั้งสิ้น
   - เก็บเป็นทศนิยม 2 ตำแหน่ง สำหรับเงิน
   - ใช้ในการคำนวณและรายงาน
   - ค่าเริ่มต้น = 0.00
🔹 ตัวอย่าง SQL: SELECT SUM(budget_total) FROM projects
```

**ใช้ใน Django ORM:**

```python
from decimal import Decimal
from django.db.models import Sum, Avg

# สร้างด้วย Decimal
>>> project = Projects.objects.create(
...     project_code='PRJ-NEW',
...     project_name='โครงการใหม่',
...     budget_total=Decimal('1500000.00'),
...     status='ดำเนินการ'
... )

# Filter เงื่อนไข
>>> projects = Projects.objects.filter(
...     budget_total__gte=Decimal('1000000')  # ≥ 1 ล้าน
... )

# Aggregate (รวม)
>>> result = Projects.objects.aggregate(
...     total=Sum('budget_total'),
...     average=Avg('budget_total')
... )
>>> print(result['total'])  # ยอดรวมทั้งหมด
```

---

### **5. status (CharField)**

```
🔹 ชื่อ: status
🔹 ประเภท: String
🔹 ข้อมูล: "ดำเนินการ", "ปิด", "หยุดชั่วคราว", "ยกเลิก"
🔹 หน้าที่:
   - สถานะของโครงการ
   - ใช้กรองข้อมูล
   - สำหรับ Reporting/Dashboard
🔹 ตัวอย่าง SQL: SELECT * FROM projects WHERE status = 'ดำเนินการ'
```

**ใช้ใน Django ORM:**

```python
# Filter ตามสถานะ
>>> active = Projects.objects.filter(status='ดำเนินการ')
>>> closed = Projects.objects.filter(status='ปิด')

# นับตามสถานะ
>>> count = Projects.objects.filter(status='ดำเนินการ').count()
>>> print(f"โครงการดำเนินการ: {count}")

# Update สถานะ
>>> Projects.objects.filter(status='ยกเลิก').update(status='ปิด')

# Distinct - ดูเฉพาะค่า unique
>>> status_list = Projects.objects.values('status').distinct()
>>> for s in status_list:
...     print(s['status'])
ดำเนินการ
ปิด
หยุดชั่วคราว
ยกเลิก
```

---

## 2.2 ตัวแปรในตาราง Vendors

### **1. vendor_id (AutoField)**

```
🔹 ชื่อ: vendor_id
🔹 ประเภท: Integer (Auto-increment)
🔹 ข้อมูล: 1, 2, 3, ...
🔹 หน้าที่: Primary Key สำหรับผู้ขาย
```

---

### **2. vendor_name (CharField)**

```
🔹 ชื่อ: vendor_name
🔹 ประเภท: String
🔹 ข้อมูล: "บริษัท A & B", "บริษัท ABC จำกัด"
🔹 หน้าที่: ชื่อบริษัทผู้ขาย
```

**ใช้ใน Django ORM:**

```python
# ดึง vendor
>>> vendor = Vendors.objects.get(vendor_name='บริษัท A & B')

# Search
>>> vendors = Vendors.objects.filter(
...     vendor_name__icontains='บริษัท'
... )

# Create
>>> vendor = Vendors.objects.create(
...     vendor_name='บริษัท XYZ',
...     phone='02-1234-5678',
...     email='info@xyz.co.th'
... )
```

---

### **3. phone (CharField, optional)**

```
🔹 ชื่อ: phone
🔹 ประเภท: String (ไม่บังคับ)
🔹 ข้อมูล: "02-1234-5678", "081-9876543"
🔹 หน้าที่: เบอร์โทรศัพท์บริษัท
```

---

### **4. email (EmailField, optional)**

```
🔹 ชื่อ: email
🔹 ประเภท: Email (ไม่บังคับ)
🔹 ข้อมูล: "contact@vendor.co.th"
🔹 หน้าที่: อีเมลติดต่อ
```

---

## 2.3 ตัวแปรในตาราง MasterItems

### **1. item_id (AutoField)**

```
🔹 ชื่อ: item_id
🔹 ประเภท: Integer (Auto-increment)
🔹 หน้าที่: Primary Key
```

---

### **2. item_code (CharField, UNIQUE)**

```
🔹 ชื่อ: item_code
🔹 ประเภท: String (ไม่ซ้ำกัน)
🔹 ข้อมูล: "ITEM-001", "ITEM-TABLE-01"
🔹 หน้าที่: รหัสประจำตัวรายการ
```

**ใช้ใน Django ORM:**

```python
# ดึงด้วย code
>>> item = MasterItems.objects.get(item_code='ITEM-001')

# Get or Create
>>> item, created = MasterItems.objects.get_or_create(
...     item_code='ITEM-NEW',
...     defaults={'item_name': 'New Item', 'standard_unit': 'อัน'}
... )
```

---

### **3. item_name (CharField)**

```
🔹 ชื่อ: item_name
🔹 ประเภท: String
🔹 ข้อมูล: "โต๊ะประชุม", "เก้าอี้สำนักงาน"
🔹 หน้าที่: ชื่อรายการ
```

---

### **4. standard_unit (CharField)**

```
🔹 ชื่อ: standard_unit
🔹 ประเภท: String
🔹 ข้อมูล: "ตัว", "ชิ้น", "เซ็ต", "กล่อง"
🔹 หน้าที่: หน่วยนับมาตรฐาน
```

**ใช้ใน Django ORM:**

```python
# ดึงเฉพาะหน่วย
>>> units = MasterItems.objects.values('standard_unit').distinct()
>>> for u in units:
...     print(u['standard_unit'])
ตัว
ชิ้น
เซ็ต
```

---

### **5. created_at (DateTimeField)**

```
🔹 ชื่อ: created_at
🔹 ประเภท: DateTime (auto-filled)
🔹 ข้อมูล: "2024-11-19 10:30:00"
🔹 หน้าที่: เวลาที่สร้างรายการ
🔹 หมายเหตุ: auto_now_add=True = Django เพิ่มเวลาอัตโนมัติ
```

**ใช้ใน Django ORM:**

```python
# Filter ตามเวลา
from django.utils import timezone
from datetime import timedelta

# สร้างได้ 7 วันที่ผ่านมา
>>> one_week_ago = timezone.now() - timedelta(days=7)
>>> recent_items = MasterItems.objects.filter(created_at__gte=one_week_ago)

# เรียงตามเวลา
>>> items = MasterItems.objects.order_by('-created_at')  # ใหม่ที่สุดก่อน
```

---

---

# 3. 🔄 Request/Response Flow

## 3.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                             │
│                   (HTML + JavaScript)                       │
│                    S08_Master_Data.html                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 1. JavaScript Fetch API
                       │    (JSON Request)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Django URL Router                         │
│                     (urls.py)                               │
│  /api/projects/     → ProjectViewSet                        │
│  /api/vendors/      → VendorViewSet                         │
│  /api/master-items/ → MasterItemViewSet                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 2. Route Match
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    ViewSet                                  │
│                 (views.py)                                  │
│  - GET:     ProjectViewSet.list()                           │
│  - POST:    ProjectViewSet.create()                         │
│  - PUT:     ProjectViewSet.update()                         │
│  - DELETE:  ProjectViewSet.destroy()                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 3. Serializer Validation
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Serializer                                 │
│              (serializers.py)                               │
│  - ProjectSerializer                                        │
│  - VendorSerializer                                         │
│  - MasterItemSerializer                                     │
│  ✅ Validate JSON → Python Dict                             │
│  ✅ Validate Python Dict → ORM Model                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 4. ORM Query
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               Django ORM                                    │
│              (models.py)                                    │
│  - Projects.objects.all() [GET]                             │
│  - Projects.objects.create() [POST]                         │
│  - Projects.objects.filter().update() [PUT]                 │
│  - Projects.objects.filter().delete() [DELETE]              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 5. SQL Execute
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  MySQL Database                             │
│                    (potms)                                  │
│  - projects table                                           │
│  - vendors table                                            │
│  - master_items table                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 6. Return Result
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Django ORM → Python                            │
│              Model Instance (Object)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 7. Serializer to JSON
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              JSON Response                                  │
│           (REST Framework)                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 8. Send to Frontend
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 Frontend                                    │
│  - Process JSON                                             │
│  - Update DOM (Display)                                     │
│  - Update Table/Chart                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 3.2 REST API Endpoints

### **Projects Endpoints**

#### **1. GET /api/projects/ - ดึงทั้งหมด**

**Request:**

```javascript
// JavaScript Fetch
fetch("http://localhost:8000/api/projects/")
  .then((res) => res.json())
  .then((data) => console.log(data));
```

**Response (JSON):**

```json
[
  {
    "project_id": 1,
    "project_code": "PRJ-001",
    "project_name": "โครงการทดสอบ",
    "budget_total": "1500000.00",
    "status": "ดำเนินการ"
  },
  {
    "project_id": 2,
    "project_code": "PRJ-002",
    "project_name": "โครงการ A",
    "budget_total": "2000000.00",
    "status": "ปิด"
  }
]
```

**Django ORM:**

```python
# ในใน views.py ProjectViewSet.list()
>>> queryset = Projects.objects.all()  # SQL: SELECT * FROM projects
>>> serializer = ProjectSerializer(queryset, many=True)
>>> serializer.data  # → JSON format
```

---

#### **2. GET /api/projects/{project_code}/ - ดึงเฉพาะรายการเดียว**

**Request:**

```javascript
fetch("http://localhost:8000/api/projects/PRJ-001/")
  .then((res) => res.json())
  .then((data) => console.log(data));
```

**Response:**

```json
{
  "project_id": 1,
  "project_code": "PRJ-001",
  "project_name": "โครงการทดสอบ",
  "budget_total": "1500000.00",
  "status": "ดำเนินการ"
}
```

**Django ORM:**

```python
# ใน views.py ProjectViewSet.retrieve()
>>> project = Projects.objects.get(project_code='PRJ-001')
>>> serializer = ProjectSerializer(project)
>>> serializer.data  # → JSON
```

---

#### **3. POST /api/projects/ - สร้างใหม่**

**Request:**

```javascript
fetch("http://localhost:8000/api/projects/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    project_code: "PRJ-NEW",
    project_name: "โครงการใหม่",
    budget_total: "3000000.00",
    status: "ดำเนินการ",
  }),
})
  .then((res) => res.json())
  .then((data) => console.log(data));
```

**Response:**

```json
{
  "project_id": 3,
  "project_code": "PRJ-NEW",
  "project_name": "โครงการใหม่",
  "budget_total": "3000000.00",
  "status": "ดำเนินการ"
}
```

**Django ORM:**

```python
# ใน views.py ProjectViewSet.create()
>>> data = {
...     'project_code': 'PRJ-NEW',
...     'project_name': 'โครงการใหม่',
...     'budget_total': '3000000.00',
...     'status': 'ดำเนินการ'
... }
>>> serializer = ProjectSerializer(data=data)
>>> if serializer.is_valid():
...     serializer.save()  # SQL: INSERT INTO projects ...
...     print(serializer.data)  # → JSON Response
```

---

#### **4. PUT /api/projects/{project_code}/ - แก้ไข**

**Request:**

```javascript
fetch("http://localhost:8000/api/projects/PRJ-001/", {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    project_name: "ชื่อใหม่",
    budget_total: "2500000.00",
  }),
})
  .then((res) => res.json())
  .then((data) => console.log(data));
```

**Response:**

```json
{
  "project_id": 1,
  "project_code": "PRJ-001",
  "project_name": "ชื่อใหม่",
  "budget_total": "2500000.00",
  "status": "ดำเนินการ"
}
```

**Django ORM:**

```python
# ใน views.py ProjectViewSet.update()
>>> project = Projects.objects.get(project_code='PRJ-001')
>>> project.project_name = 'ชื่อใหม่'
>>> project.budget_total = Decimal('2500000.00')
>>> project.save()  # SQL: UPDATE projects SET ...
```

---

#### **5. DELETE /api/projects/{project_code}/ - ลบ**

**Request:**

```javascript
fetch("http://localhost:8000/api/projects/PRJ-001/", {
  method: "DELETE",
}).then((res) => console.log("ลบสำเร็จ"));
```

**Response:**

```
204 No Content (success)
```

**Django ORM:**

```python
# ใน views.py ProjectViewSet.destroy()
>>> project = Projects.objects.get(project_code='PRJ-001')
>>> project.delete()  # SQL: DELETE FROM projects WHERE project_code = 'PRJ-001'
```

---

### **Vendors Endpoints**

#### **GET /api/vendors/ - ดึงทั้งหมด**

**Request:**

```javascript
fetch("http://localhost:8000/api/vendors/")
  .then((res) => res.json())
  .then((data) => console.log(data));
```

**Response:**

```json
[
  {
    "vendor_id": 1,
    "vendor_name": "บริษัท A & B",
    "phone": "02-1234-5678",
    "email": "contact@ab.co.th"
  }
]
```

---

#### **POST /api/vendors/ - สร้างใหม่**

**Request:**

```javascript
fetch("http://localhost:8000/api/vendors/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    vendor_name: "บริษัท XYZ",
    phone: "081-1234567",
    email: "xyz@xyz.co.th",
  }),
});
```

**Django ORM:**

```python
>>> vendor = Vendors.objects.create(
...     vendor_name='บริษัท XYZ',
...     phone='081-1234567',
...     email='xyz@xyz.co.th'
... )
```

---

### **Master Items Endpoints**

#### **GET /api/master-items/ - ดึงทั้งหมด**

**Request:**

```javascript
fetch("http://localhost:8000/api/master-items/")
  .then((res) => res.json())
  .then((data) => console.log(data));
```

**Response:**

```json
[
  {
    "item_id": 1,
    "item_code": "ITEM-001",
    "item_name": "โต๊ะประชุม",
    "standard_unit": "ตัว",
    "created_at": "2024-11-19T10:30:00Z"
  }
]
```

---

---

# 4. 🐍 Django ORM - Basic

## 4.1 ORM คืออะไร?

```
ORM = Object-Relational Mapping
    = แปลง Database (SQL) → Python Objects (OOP)

❌ ไม่ต้องเขียน SQL เอง:
   SELECT * FROM projects WHERE status = 'ดำเนินการ'

✅ ใช้ Python ORM แทน:
   Projects.objects.filter(status='ดำเนินการ')
```

---

## 4.2 Models (ORM Models)

### **ทำไมต้องใช้ Models?**

```
Models เป็นตัวแทนของตาราง Database ในโค้ด Python

Database Table    →    Python Model Class
projects          →    class Projects
vendors           →    class Vendors
master_items      →    class MasterItems
```

---

### **Project Model Detail**

```python
# POTMS/api/models.py

from django.db import models

class Projects(models.Model):
    # ตัวแปรแต่ละตัว = Column ในตาราง

    project_id = models.AutoField(primary_key=True)
    # ❌ ไม่ต้องสร้างเอง = Django สร้างอัตโนมัติ
    # ✅ Unique = ไม่มีสองรายการที่มี ID เดียวกัน

    project_code = models.CharField(max_length=50, unique=True)
    # ✅ CharField = String สูงสุด 50 ตัวอักษร
    # ✅ unique=True = ห้ามมีรหัสซ้ำกัน

    project_name = models.CharField(max_length=255)
    # String สูงสุด 255 ตัวอักษร

    budget_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    # DecimalField = ทศนิยม
    # max_digits=12 = ทั้งหมด 12 ตัว
    # decimal_places=2 = ทศนิยม 2 ตำแหน่ง
    # default=0.00 = ค่าเริ่มต้น

    status = models.CharField(max_length=50)
    # สถานะโครงการ

    class Meta:
        db_table = 'projects'  # ชื่อตารางใน MySQL
```

---

## 4.3 Serializers (Data Validation)

### **Serializer คืออะไร?**

```
Serializer = ตัวแปลง & ตรวจสอบข้อมูล

JSON (Request) → Serializer → Validate → Model → Database
Database → Model → Serializer → JSON (Response) → Frontend
```

---

### **ProjectSerializer Detail**

```python
# POTMS/api/serializers.py

from rest_framework import serializers
from .models import Projects

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects  # เชื่อมกับ Model
        fields = '__all__'  # ใช้ทุก field จาก Model
```

**ตัวอย่างการใช้:**

```python
# Data from Frontend
request_data = {
    'project_code': 'PRJ-001',
    'project_name': 'โครงการทดสอบ',
    'budget_total': '1500000.00',
    'status': 'ดำเนินการ'
}

# Validate และ Save
serializer = ProjectSerializer(data=request_data)
if serializer.is_valid():
    serializer.save()  # Save to DB
    print(serializer.data)  # Return JSON
else:
    print(serializer.errors)  # Show validation errors
```

---

---

# 5. 🐚 Django Shell - ใช้งาน

## 5.1 เปิด Django Shell

### **Step 1: ไปไดเรกทอรี่ POTMS**

```powershell
cd e:\DSSI-PROJECT-2568\POTMS
```

---

### **Step 2: เปิด Shell**

```powershell
python manage.py shell
```

**Output:**

```
Python 3.x.x (main, ...)
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>>
```

---

## 5.2 Import Models

```python
>>> from api.models import Projects, Vendors, MasterItems
>>> from decimal import Decimal
```

**ตรวจสอบ:**

```python
>>> Projects
<class 'api.models.Projects'>

>>> Vendors
<class 'api.models.Vendors'>

>>> MasterItems
<class 'api.models.MasterItems'>
```

---

## 5.3 CREATE - สร้างข้อมูล

### **สร้างโครงการเดียว**

```python
>>> project = Projects.objects.create(
...     project_code='PRJ-SHELL-001',
...     project_name='โครงการทดสอบ Shell',
...     budget_total=Decimal('1500000.00'),
...     status='ดำเนินการ'
... )

>>> project
<Projects: Projects object (1)>

>>> project.project_code
'PRJ-SHELL-001'

>>> project.project_name
'โครงการทดสอบ Shell'

>>> project.budget_total
Decimal('1500000.00')
```

---

### **สร้างหลายรายการพร้อมกัน (Bulk)**

```python
>>> projects_list = [
...     Projects(
...         project_code='PRJ-BULK-001',
...         project_name='Bulk 1',
...         budget_total=Decimal('2000000.00'),
...         status='ดำเนินการ'
...     ),
...     Projects(
...         project_code='PRJ-BULK-002',
...         project_name='Bulk 2',
...         budget_total=Decimal('3000000.00'),
...         status='ปิด'
...     ),
... ]

>>> Projects.objects.bulk_create(projects_list)
[<Projects: Projects object (2)>, <Projects: Projects object (3)>]
```

---

### **สร้าง Vendor**

```python
>>> vendor = Vendors.objects.create(
...     vendor_name='บริษัท ทดสอบ',
...     phone='02-1234-5678',
...     email='test@co.th'
... )

>>> vendor
<Vendors: บริษัท ทดสอบ>

>>> vendor.vendor_name
'บริษัท ทดสอบ'
```

---

### **สร้าง Master Item**

```python
>>> item = MasterItems.objects.create(
...     item_code='ITEM-SHELL-001',
...     item_name='รายการทดสอบ',
...     standard_unit='อัน'
... )

>>> item
<MasterItems: รายการทดสอบ>

>>> item.item_code
'ITEM-SHELL-001'
```

---

## 5.4 READ - ดึงข้อมูล

### **ดึงทั้งหมด**

```python
>>> all_projects = Projects.objects.all()
>>> all_projects
<QuerySet [<Projects: Projects object (1)>, <Projects: Projects object (2)>]>

>>> all_projects.count()
2

# Loop
>>> for project in all_projects:
...     print(f"{project.project_code} - {project.project_name}")
PRJ-SHELL-001 - โครงการทดสอบ Shell
PRJ-BULK-001 - Bulk 1
```

---

### **ดึงรายการเดียว (Get)**

```python
>>> project = Projects.objects.get(project_code='PRJ-SHELL-001')
>>> project.project_name
'โครงการทดสอบ Shell'

# ดึงด้วย ID
>>> project = Projects.objects.get(project_id=1)
```

---

### **Filter - กรองข้อมูล**

```python
# โครงการที่ดำเนินการ
>>> active = Projects.objects.filter(status='ดำเนินการ')
>>> active.count()
2

# โครงการที่งบประมาณมากกว่า 1 ล้าน
>>> expensive = Projects.objects.filter(
...     budget_total__gte=Decimal('1000000')
... )

# โครงการที่มี code ขึ้นต้นด้วย PRJ-SHELL
>>> shell_projects = Projects.objects.filter(
...     project_code__startswith='PRJ-SHELL'
... )
```

---

### **Filter + Order By**

```python
# เรียงจากน้อยไปมาก
>>> projects = Projects.objects.all().order_by('budget_total')

# เรียงจากมากไปน้อย
>>> projects = Projects.objects.all().order_by('-budget_total')

# ดูข้อมูล
>>> for p in projects:
...     print(f"{p.project_name}: ฿{p.budget_total}")
```

---

### **First/Limit**

```python
# ดึง 1 รายการแรก
>>> first = Projects.objects.all().first()

# ดึง 3 รายการแรก
>>> first_three = Projects.objects.all()[:3]
```

---

## 5.5 UPDATE - แก้ไขข้อมูล

### **Edit แล้ว Save**

```python
# ดึง object
>>> project = Projects.objects.get(project_code='PRJ-SHELL-001')

# แก้ไข
>>> project.project_name = 'โครงการใหม่'
>>> project.budget_total = Decimal('2000000.00')

# Save
>>> project.save()

# ตรวจสอบ
>>> p = Projects.objects.get(project_code='PRJ-SHELL-001')
>>> p.project_name
'โครงการใหม่'
```

---

### **Update Multiple**

```python
# Update ทั้ง QuerySet
>>> Projects.objects.filter(status='ปิด').update(
...     status='ดำเนินการ'
... )
1  # จำนวนที่ update

# ตรวจสอบ
>>> Projects.objects.filter(status='ดำเนินการ').count()
```

---

## 5.6 DELETE - ลบข้อมูล

### **ลบรายการเดียว**

```python
>>> project = Projects.objects.get(project_code='PRJ-SHELL-001')
>>> project.delete()
(1, {'api.Projects': 1})  # (count, details)

# ตรวจสอบ
>>> Projects.objects.filter(project_code='PRJ-SHELL-001').exists()
False
```

---

### **ลบ Multiple**

```python
# ลบทั้ง QuerySet
>>> deleted_count, _ = Projects.objects.filter(status='ปิด').delete()
>>> print(f"ลบไป {deleted_count} รายการ")
ลบไป 2 รายการ
```

---

## 5.7 Advanced Queries

### **Count**

```python
>>> Projects.objects.count()
5

>>> Projects.objects.filter(status='ดำเนินการ').count()
3
```

---

### **Exists (Check)**

```python
>>> Projects.objects.filter(project_code='PRJ-001').exists()
True

>>> Projects.objects.filter(project_code='NOT-EXIST').exists()
False
```

---

### **Values (Get Specific Columns)**

```python
>>> projects = Projects.objects.all().values('project_code', 'project_name')
>>> projects
<QuerySet [{'project_code': 'PRJ-001', 'project_name': 'Project 1'}, ...]>

>>> for p in projects:
...     print(p)
```

---

### **Aggregate (รวม/นับ)**

```python
from django.db.models import Sum, Avg, Count, Max, Min

>>> result = Projects.objects.aggregate(
...     total_budget=Sum('budget_total'),
...     avg_budget=Avg('budget_total'),
...     max_budget=Max('budget_total'),
...     count=Count('project_id')
... )

>>> result
{
    'total_budget': Decimal('15000000.00'),
    'avg_budget': Decimal('1500000.00'),
    'max_budget': Decimal('3000000.00'),
    'count': 10
}

>>> result['total_budget']
Decimal('15000000.00')
```

---

### **Distinct (Unique Values)**

```python
>>> statuses = Projects.objects.values('status').distinct()
>>> for s in statuses:
...     print(s['status'])
ดำเนินการ
ปิด
```

---

### **Get or Create**

```python
>>> project, created = Projects.objects.get_or_create(
...     project_code='PRJ-UNIQUE-001',
...     defaults={
...         'project_name': 'Unique Project',
...         'status': 'ดำเนินการ'
...     }
... )

>>> created  # True = สร้างใหม่, False = มีอยู่แล้ว
True

# ถ้า run ครั้งที่ 2
>>> project, created = Projects.objects.get_or_create(
...     project_code='PRJ-UNIQUE-001',
...     defaults={...}
... )
>>> created
False  # ได้ของเดิม ไม่ได้สร้างใหม่
```

---

## 5.8 SQL Query ที่ Django สร้าง

### **ดู SQL เบื้องหลัง**

```python
# Create Query Set
>>> qs = Projects.objects.filter(status='ดำเนินการ')

# ดู SQL
>>> print(qs.query)
SELECT "api_projects"."project_id",
       "api_projects"."project_code",
       "api_projects"."project_name",
       "api_projects"."budget_total",
       "api_projects"."status"
FROM "api_projects"
WHERE "api_projects"."status" = 'ดำเนินการ'
```

---

## 5.9 Exit Django Shell

```python
>>> exit()
# หรือ
>>> quit()
# หรือ Ctrl+Z (Windows) แล้ว Enter
```

---

## 5.10 Complete Workflow Example

```python
# 1. เปิด Shell
# python manage.py shell

# 2. Import
>>> from api.models import Projects, Vendors, MasterItems
>>> from decimal import Decimal
>>> from django.db.models import Sum

# 3. ดูจำนวนทั้งหมด
>>> Projects.objects.count()
5

# 4. ดึงและแสดง
>>> for p in Projects.objects.all():
...     print(f"{p.project_code}: {p.project_name} (฿{p.budget_total})")

# 5. Filter ตามเงื่อนไข
>>> active = Projects.objects.filter(status='ดำเนินการ')
>>> active.count()
3

# 6. สร้างข้อมูล
>>> new_project = Projects.objects.create(
...     project_code='PRJ-NEW-001',
...     project_name='New Project',
...     budget_total=Decimal('2500000.00'),
...     status='ดำเนินการ'
... )
>>> new_project.project_id
6

# 7. อัพเดท
>>> p = Projects.objects.get(project_code='PRJ-001')
>>> p.status = 'ปิด'
>>> p.save()

# 8. ลบ
>>> Projects.objects.filter(project_code='PRJ-NEW-001').delete()
(1, {'api.Projects': 1})

# 9. รวม/นับ
>>> result = Projects.objects.aggregate(
...     total_budget=Sum('budget_total')
... )
>>> print(f"รวมทั้งหมด: ฿{result['total_budget']}")

# 10. Exit
>>> exit()
```

---

## 5.11 Common Operations Quick Reference

| Task            | Command                                                            |
| --------------- | ------------------------------------------------------------------ |
| Import          | `from api.models import Projects, Vendors, MasterItems`            |
| **CREATE**      |                                                                    |
| สร้างเดียว      | `Projects.objects.create(project_code='...', ...)`                 |
| สร้างหลาย       | `Projects.objects.bulk_create([obj1, obj2])`                       |
| Get or Create   | `Projects.objects.get_or_create(code='...', defaults={...})`       |
| **READ**        |                                                                    |
| ดึงทั้งหมด      | `Projects.objects.all()`                                           |
| ดึงเดียว        | `Projects.objects.get(project_code='...')`                         |
| Filter          | `Projects.objects.filter(status='...')`                            |
| Filter multiple | `Projects.objects.filter(status='...', budget_total__gte=1000000)` |
| First           | `Projects.objects.all().first()`                                   |
| Limit           | `Projects.objects.all()[:5]`                                       |
| Order           | `Projects.objects.all().order_by('-budget_total')`                 |
| Count           | `Projects.objects.count()`                                         |
| Exists          | `Projects.objects.filter(...).exists()`                            |
| Values          | `Projects.objects.values('field1', 'field2')`                      |
| Distinct        | `Projects.objects.values('status').distinct()`                     |
| Aggregate       | `Projects.objects.aggregate(Sum('budget_total'))`                  |
| **UPDATE**      |                                                                    |
| Edit & Save     | `p.field = value; p.save()`                                        |
| Update Many     | `Projects.objects.filter(...).update(field=value)`                 |
| **DELETE**      |                                                                    |
| ลบเดียว         | `project.delete()`                                                 |
| ลบหลาย          | `Projects.objects.filter(...).delete()`                            |
| ลบทั้งหมด       | `Projects.objects.all().delete()`                                  |

---

---

# 📝 สรุป

## **3 Layer Architecture**

```
┌─────────────────────────────────────────┐
│ Frontend (HTML + JavaScript + Fetch)    │ ← ผู้ใช้ interact
├─────────────────────────────────────────┤
│ Backend (Django REST Framework)         │ ← ประมวลผลข้อมูล
│  - URLs → Views → Serializers           │
├─────────────────────────────────────────┤
│ Database (MySQL + ORM)                  │ ← เก็บข้อมูล
│  - Models → ORM → SQL                   │
└─────────────────────────────────────────┘
```

---

## **CRUD Operations**

```
CREATE  ← POST   ← ✅ Projects.objects.create()
READ    ← GET    ← ✅ Projects.objects.all() / .get() / .filter()
UPDATE  ← PUT    ← ✅ project.save() หรือ .update()
DELETE  ← DELETE ← ✅ project.delete()
```

---

## **Data Flow**

```
Frontend Input
    ↓
JavaScript Fetch (JSON)
    ↓
Django URLs
    ↓
ViewSet (CREATE/READ/UPDATE/DELETE)
    ↓
Serializer (Validate)
    ↓
Django ORM (Models)
    ↓
MySQL (Database)
    ↓
(Return Back)
```

---

## **Django Shell คำสั่งพื้นฐาน**

```python
# Import
from api.models import Projects, Vendors, MasterItems
from decimal import Decimal

# Create
Projects.objects.create(project_code='...', ...)

# Read
Projects.objects.all()
Projects.objects.get(project_code='...')
Projects.objects.filter(status='ดำเนินการ')

# Update
project.field = value; project.save()
Projects.objects.filter(...).update(field=value)

# Delete
project.delete()
Projects.objects.filter(...).delete()
```

---

## **ข้อดีของ ORM**

```
✅ ไม่ต้องเขียน SQL
✅ ปลอดภัยจาก SQL Injection
✅ Code อ่านง่าย
✅ ใช้ได้กับ Database หลายแบบ
✅ ลดข้อผิดพลาด
```

---

**🎉 ขอบคุณที่อ่าน! ลองใช้ Django Shell ดูเลย!** 🚀
