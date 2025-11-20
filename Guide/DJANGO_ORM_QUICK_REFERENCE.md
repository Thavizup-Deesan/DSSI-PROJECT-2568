# 🎯 Django ORM - Quick Reference

## 📍 ต้องแก้ไข/เพิ่มที่ไหนบ้าง?

### **ตำแหน่งของไฟล์ที่สร้าง:**

```
e:\DSSI-PROJECT-2568\POTMS\
└── api\
    └── management\                          ← ✨ สร้างใหม่
        ├── __init__.py                      ← ✨ สร้างใหม่ (ว่าง)
        └── commands\                        ← ✨ สร้างใหม่
            ├── __init__.py                  ← ✨ สร้างใหม่ (ว่าง)
            └── populate_db.py               ← ✨ สร้างใหม่ (Django Command)
```

---

## 🔧 ไฟล์ที่ใช้ Django ORM (ไม่ต้องแก้ไข)

### **1. api/views.py** ✅

```python
# ✅ ใช้ Django ORM แล้ว
queryset = Projects.objects.all()                    # ← ORM
project = Projects.objects.filter(...).first()      # ← ORM
serializer.save()                                    # ← ORM
```

### **2. api/models.py** ✅

```python
# ✅ Models defined correctly
class Projects(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_code = models.CharField(...)
    # ← Django handles database mapping
```

### **3. api/serializers.py** ✅

```python
# ✅ Serializers configured correctly
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects                             # ← ORM integration
        fields = '__all__'
```

---

## 🚀 วิธีใช้ Management Command

### **Step 1: สร้างไฟล์ (ทำแล้ว)**

```
✅ ไฟล์ต่อไปนี้ถูกสร้างแล้ว:
- api/management/__init__.py
- api/management/commands/__init__.py
- api/management/commands/populate_db.py
```

### **Step 2: รัน Command**

```powershell
# เปลี่ยน directory ไปที่ POTMS
cd e:\DSSI-PROJECT-2568\POTMS

# รัน command ธรรมดา (ไม่ลบข้อมูลเก่า)
python manage.py populate_db

# รัน command พร้อมลบข้อมูลเก่า
python manage.py populate_db --clear
```

### **Output ที่คาดหวัง:**

```
🚀 Starting data population...

📌 Creating Projects...
  ✅ Created: PRJ-2568-001 - โครงการพัฒนาระบบ ERP
  ✅ Created: PRJ-2568-002 - โครงการปรับปรุงห้อง Server
  ✅ Created: PRJ-2568-003 - โครงการฝึกอบรมพนักงานประจำปี
  [... 7 more ...]
✅ Total Projects created: 10

🏢 Creating Vendors...
  ✅ Created: บริษัท เทคโนโลยี ซอลูชั่น จำกัด
  ✅ Created: ห้างหุ้นส่วนจำกัด อีเลคทรอนิคส์
  [... 3 more ...]
✅ Total Vendors created: 5

📦 Creating Master Items...
  ✅ Created: ITEM-001
  ✅ Created: ITEM-002
  [... 8 more ...]
✅ Total Items created: 10

============================================================
✅ Data Population Completed Successfully!
============================================================
📊 Total Projects:     10
📊 Total Vendors:      5
📊 Total Master Items: 10
============================================================
```

---

## 📊 Django ORM ที่ใช้ในระบบ

### **Create (INSERT)**

```python
# ในโครงการคุณ:
project = Projects.objects.create(
    project_code='PRJ-001',
    project_name='Project Name',
    budget_total=Decimal('1000000.00'),
    status='ดำเนินการ'
)
```

### **Read (SELECT)**

```python
# ดึงทั้งหมด
all_projects = Projects.objects.all()

# ดึงเฉพาะ
project = Projects.objects.get(project_code='PRJ-001')

# Filter
active_projects = Projects.objects.filter(status='ดำเนินการ')
```

### **Update (UPDATE)**

```python
# ใน views.py:
serializer.save()  # ← Django ORM handles UPDATE

# Manual update:
project = Projects.objects.get(project_code='PRJ-001')
project.project_name = 'New Name'
project.save()
```

### **Delete (DELETE)**

```python
# ใน views.py:
project.delete()  # ← Django ORM handles DELETE
```

---

## ✅ Checklist

- [x] ไฟล์ `api/management/__init__.py` สร้างแล้ว
- [x] ไฟล์ `api/management/commands/__init__.py` สร้างแล้ว
- [x] ไฟล์ `api/management/commands/populate_db.py` สร้างแล้ว
- [ ] รัน `python manage.py populate_db` ในเทอร์มินัล
- [ ] ตรวจสอบ data ใน Admin Panel: http://localhost:8000/admin/
- [ ] ตรวจสอบ data ใน API: http://localhost:8000/api/projects/
- [ ] ตรวจสอบ data ใน Web UI: http://localhost:8000/master-data/

---

## 🎓 Django ORM vs SQL

| Task       | SQL               | Django ORM                  |
| ---------- | ----------------- | --------------------------- |
| **Create** | `INSERT INTO ...` | `Model.objects.create(...)` |
| **Read**   | `SELECT ...`      | `Model.objects.all()`       |
| **Filter** | `WHERE ...`       | `.filter(...)`              |
| **Update** | `UPDATE ...`      | `instance.save()`           |
| **Delete** | `DELETE ...`      | `instance.delete()`         |
| **Join**   | `INNER JOIN ...`  | `select_related()`          |

### **ข้อดี Django ORM:**

- ✅ ปลอดภัยจาก SQL Injection
- ✅ Cross-database (MySQL, PostgreSQL, SQLite, etc.)
- ✅ ไม่ต้องเขียน SQL
- ✅ Automatic data validation
- ✅ Easy migrations

---

## 🔍 ตรวจสอบ Data

### **Via Admin Panel:**

```
1. เปิด http://localhost:8000/admin/
2. Login ด้วย admin user
3. ดูข้อมูลใน Projects, Vendors, Master Items
```

### **Via API:**

```
GET http://localhost:8000/api/projects/
GET http://localhost:8000/api/vendors/
GET http://localhost:8000/api/master-items/
```

### **Via Django Shell:**

```powershell
python manage.py shell

>>> from api.models import Projects
>>> Projects.objects.count()
10
>>> Projects.objects.first().project_name
'โครงการพัฒนาระบบ ERP'
```

---

## 📝 สรุป

### **ที่ต้องแก้:**

- ✨ สร้าง management command ใหม่ → `populate_db.py`

### **ที่ไม่ต้องแก้:**

- ✅ `views.py` - ใช้ ORM แล้ว
- ✅ `models.py` - ถูกต้อง
- ✅ `serializers.py` - ถูกต้อง
- ✅ HTML/JavaScript - เข้าถึงผ่าน API

### **ที่ต้องรัน:**

```powershell
python manage.py populate_db --clear
```

**จากนั้น reload หน้า Web ที่ http://localhost:8000/master-data/ จะเห็นข้อมูล!** 🎉
