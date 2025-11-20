# 📂 File Structure - ไฟล์ที่ต้องแก้/สร้าง

## 🎯 สรุป Quick

```
✅ ไม่ต้องแก้:
- api/views.py             (ใช้ Django ORM แล้ว)
- api/models.py            (ถูกต้อง)
- api/serializers.py       (ถูกต้อง)
- backend/urls.py          (ถูกต้อง)
- S08_Master_Data.html     (ถูกต้อง)

✨ ต้องสร้างใหม่:
- api/management/                        (ไดเรกทอรี่)
  ├── __init__.py
  └── commands/                          (ไดเรกทอรี่)
      ├── __init__.py
      └── populate_db.py                 (✨ Management Command)
```

---

## 📁 Project Structure (ปัจจุบัน)

```
e:\DSSI-PROJECT-2568\
│
└── POTMS\
    ├── manage.py
    ├── db.sqlite3 (or MySQL)
    │
    ├── backend/
    │   ├── __init__.py
    │   ├── settings.py                   ✅ ไม่ต้องแก้
    │   ├── urls.py                       ✅ ไม่ต้องแก้
    │   ├── asgi.py
    │   └── wsgi.py
    │
    └── api/
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── models.py                     ✅ ไม่ต้องแก้
        ├── views.py                      ✅ ไม่ต้องแก้
        ├── serializers.py                ✅ ไม่ต้องแก้
        ├── urls.py                       ✅ ไม่ต้องแก้
        ├── tests.py
        │
        ├── management/                   ✨ สร้างใหม่
        │   ├── __init__.py               ✨ สร้างใหม่
        │   └── commands/                 ✨ สร้างใหม่
        │       ├── __init__.py           ✨ สร้างใหม่
        │       └── populate_db.py        ✨ สร้างใหม่ ⭐
        │
        ├── templates/
        │   └── S08_Master_Data.html      ✅ ไม่ต้องแก้
        │
        ├── migrations/
        │   ├── __init__.py
        │   ├── 0001_initial.py
        │   ├── 0002_masteritems_vendors.py
        │   └── __pycache__/
        │
        ├── __pycache__/
        └── (other files)
```

---

## 🔍 รายละเอียดของแต่ละไฟล์

### **1. api/views.py** ✅ ไม่ต้องแก้

```python
# ✅ ใช้ Django ORM แล้ว
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Projects.objects.all()           # ← ORM Query
    serializer_class = ProjectSerializer

    @action(detail=False, methods=['post'], url_path='import-excel')
    def import_excel(self, request, *args, **kwargs):
        # ...
        project = Projects.objects.filter(...).first()  # ← ORM Query
        serializer.save()                               # ← ORM Save
```

### **2. api/models.py** ✅ ไม่ต้องแก้

```python
# ✅ Django ORM Models
class Projects(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=50, unique=True)
    project_name = models.CharField(max_length=255)
    budget_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50)

    class Meta:
        db_table = 'projects'
```

### **3. api/serializers.py** ✅ ไม่ต้องแก้

```python
# ✅ Serializers linked to Models
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects              # ← ORM Model
        fields = '__all__'
```

### **4. api/management/commands/populate_db.py** ✨ สร้างใหม่

```python
# ✨ NEW FILE - Management Command
from django.core.management.base import BaseCommand
from api.models import Projects, Vendors, MasterItems
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate database with initial data'

    def handle(self, *args, **options):
        # ← ใช้ Django ORM สร้าง data
        Projects.objects.get_or_create(...)
        Vendors.objects.get_or_create(...)
        MasterItems.objects.get_or_create(...)
```

---

## 🚀 ขั้นตอนการเตรียม

### **Step 1: ตรวจสอบไฟล์ที่ต้องสร้าง**

```powershell
# ตรวจสอบว่ามีไดเรกทอรี่หรือไม่
ls e:\DSSI-PROJECT-2568\POTMS\api\management

# ถ้าไม่มีจะแสดง:
# Directory: E:\DSSI-PROJECT-2568\POTMS\api\management
# Mode                 LastWriteTime         Length Name
# ----                 -----                 ------ ----
```

### **Step 2: ตรวจสอบ **init**.py**

```powershell
# ตรวจสอบ management/__init__.py
cat e:\DSSI-PROJECT-2568\POTMS\api\management\__init__.py

# ตรวจสอบ commands/__init__.py
cat e:\DSSI-PROJECT-2568\POTMS\api\management\commands\__init__.py
```

### **Step 3: ตรวจสอบ populate_db.py**

```powershell
# ดูไฟล์
ls e:\DSSI-PROJECT-2568\POTMS\api\management\commands\

# Output ที่คาดหวัง:
# __init__.py
# populate_db.py
```

---

## ⚙️ วิธีใช้ Management Command

### **Basic Usage**

```powershell
# ไป POTMS directory
cd e:\DSSI-PROJECT-2568\POTMS

# รัน command
python manage.py populate_db
```

### **With --clear flag**

```powershell
# รัน command พร้อมลบข้อมูลเก่า
python manage.py populate_db --clear
```

### **List all available commands**

```powershell
python manage.py help

# หรือ
python manage.py populate_db --help
```

---

## 📋 ตารางไฟล์: ก่อน vs หลัง

### **ก่อน (Before):**

```
api/
├── views.py             ✅
├── models.py            ✅
├── serializers.py       ✅
├── urls.py              ✅
├── admin.py
├── apps.py
├── tests.py
├── migrations/
└── templates/
```

### **หลัง (After):**

```
api/
├── views.py             ✅
├── models.py            ✅
├── serializers.py       ✅
├── urls.py              ✅
├── admin.py
├── apps.py
├── tests.py
├── migrations/
├── templates/
└── management/          ✨ NEW
    ├── __init__.py      ✨ NEW
    └── commands/        ✨ NEW
        ├── __init__.py  ✨ NEW
        └── populate_db.py ✨ NEW
```

---

## ✅ Verification Checklist

- [x] `api/management/` ไดเรกทอรี่ถูกสร้าง
- [x] `api/management/__init__.py` ถูกสร้าง (ว่าง)
- [x] `api/management/commands/` ไดเรกทอรี่ถูกสร้าง
- [x] `api/management/commands/__init__.py` ถูกสร้าง (ว่าง)
- [x] `api/management/commands/populate_db.py` ถูกสร้าง
- [ ] **ต้องรัน:** `python manage.py populate_db --clear`

---

## 🎯 ที่ที่ต้องแก้ไข (สรุป)

### **ในไฟล์ที่เขียน Django ORM:**

1. **views.py** ✅ ไม่ต้องแก้

   - มีการใช้ `Projects.objects.all()` แล้ว
   - มีการใช้ `serializer.save()` แล้ว

2. **models.py** ✅ ไม่ต้องแก้

   - Model definitions ถูกต้อง
   - Django ORM จะแปลงเป็น SQL

3. **serializers.py** ✅ ไม่ต้องแก้

   - ModelSerializer จัดการ ORM validation

4. **urls.py** ✅ ไม่ต้องแก้

   - Router configuration ถูกต้อง

5. **S08_Master_Data.html** ✅ ไม่ต้องแก้
   - ใช้ fetch API ไป backend ที่ใช้ ORM

### **ที่ต้องสร้าง:**

1. **populate_db.py** ✨ สร้างใหม่
   - Management command ใช้ ORM populate data
   - ใช้ `get_or_create()` method
   - ใช้ `objects.all()` query

---

## 📝 Example Django ORM Usage

### **ในระบบของคุณ:**

```python
# ❌ SQL (ไม่ใช้)
INSERT INTO projects (project_code, project_name, budget_total, status)
VALUES ('PRJ-001', 'Project', 5000000.00, 'ดำเนินการ')

# ✅ Django ORM (ใช้)
Projects.objects.create(
    project_code='PRJ-001',
    project_name='Project',
    budget_total=Decimal('5000000.00'),
    status='ดำเนินการ'
)
```

---

## 🎓 Django ORM Model Methods

```python
# Create
project = Projects.objects.create(...)

# Read All
projects = Projects.objects.all()

# Read One
project = Projects.objects.get(project_code='PRJ-001')

# Filter
active = Projects.objects.filter(status='ดำเนินการ')

# Filter + Get
project = Projects.objects.filter(project_code='PRJ-001').first()

# Get or Create
project, created = Projects.objects.get_or_create(
    project_code='PRJ-001',
    defaults={'project_name': 'Project'}
)

# Update
project.project_name = 'New Name'
project.save()

# Delete
project.delete()

# Delete Many
Projects.objects.filter(status='ปิด').delete()

# Count
count = Projects.objects.count()

# Bulk Create
projects = [Projects(...), Projects(...)]
Projects.objects.bulk_create(projects)
```

---

## 🔗 Related Files

- 📄 `DJANGO_ORM_IMPLEMENTATION_GUIDE.md` - Full implementation guide
- 📄 `DJANGO_ORM_QUICK_REFERENCE.md` - Quick reference commands
- 📄 `API_REQUEST_RESPONSE_GUIDE.md` - API request/response examples
- 📄 `CODE_EXAMPLES_REQUEST_RESPONSE.md` - Code examples

---

**สรุป:** ต้องสร้าง `api/management/commands/populate_db.py` และรัน `python manage.py populate_db --clear` เท่านั้น! 🎉
