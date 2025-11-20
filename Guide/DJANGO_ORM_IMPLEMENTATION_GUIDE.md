# 🔧 Django ORM Implementation Guide

## 📋 สรุป: ต้องแก้ไข/เพิ่มที่ไหนบ้าง

### **ไฟล์ที่ต้องแก้ไข:**

| ลำดับที่ | ไฟล์ | ประเภท | สิ่งที่ต้องแก้ไข |
|---------|------|--------|----------------|
| 1 | `POTMS/api/management/commands/populate_db.py` | ✨ **สร้างใหม่** | สร้าง command สำหรับ populate data |
| 2 | `POTMS/api/views.py` | ✅ ไม่ต้องแก้ไข | มีการใช้ Django ORM แล้ว |
| 3 | `POTMS/api/models.py` | ✅ ไม่ต้องแก้ไข | Model definitions ถูกต้อง |
| 4 | `POTMS/api/serializers.py` | ✅ ไม่ต้องแก้ไข | Serializer ถูกต้อง |

---

## 🎯 ทำไมไม่ต้องแก้ไข?

### **1. Views.py ใช้ Django ORM แล้ว** ✅

```python
# ❌ ไม่ใช้ SQL directly
# ✅ ใช้ Django ORM:

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Projects.objects.all()  # ← Django ORM
    serializer_class = ProjectSerializer
    lookup_field = 'project_code'

# ใน import_excel method:
project = Projects.objects.filter(project_code=project_code).first()  # ← ORM query
serializer.save()  # ← ORM save
```

### **2. Models.py ตั้งค่าถูกต้อง** ✅

```python
class Projects(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=50, unique=True)
    # ← Django ORM handles this
```

### **3. Serializers.py ใช้ ModelSerializer** ✅

```python
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects  # ← Linked to Django model
        fields = '__all__'
    # ← Automatically validates & serializes
```

---

## 🆕 ที่ต้องสร้างใหม่: Management Command

### **สร้างโครงสร้างไดเรกทอรี่:**

```
POTMS/api/management/
├── __init__.py
└── commands/
    ├── __init__.py
    └── populate_db.py  ← ไฟล์ที่สร้าง
```

### **ขั้นตอนการสร้าง:**

#### **Step 1: สร้างไดเรกทอรี่**

```powershell
# Navigate to POTMS/api
cd e:\DSSI-PROJECT-2568\POTMS\api

# Create directories
mkdir management
mkdir management\commands

# Create __init__.py files
echo. > management\__init__.py
echo. > management\commands\__init__.py
```

#### **Step 2: สร้างไฟล์ populate_db.py**

```python
# POTMS/api/management/commands/populate_db.py

from django.core.management.base import BaseCommand
from django.db import connection
from api.models import Projects, Vendors, MasterItems
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate database with initial data using Django ORM'

    def handle(self, *args, **options):
        """
        Main handler for the command
        """
        self.stdout.write(self.style.SUCCESS('🚀 Starting data population...'))

        # Clear existing data (optional)
        confirm = input("Clear existing data? (y/n): ").lower()
        if confirm == 'y':
            self.clear_all_data()

        # Populate data
        self.populate_projects()
        self.populate_vendors()
        self.populate_master_items()

        # Show summary
        self.show_summary()

    def clear_all_data(self):
        """ลบข้อมูลเก่า"""
        self.stdout.write('🗑️  Clearing existing data...')
        Projects.objects.all().delete()
        Vendors.objects.all().delete()
        MasterItems.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✅ Data cleared'))

    def populate_projects(self):
        """สร้างข้อมูล Projects"""
        self.stdout.write('\n📌 Creating Projects...')
        
        projects_data = [
            {
                'project_code': 'PRJ-2568-001',
                'project_name': 'โครงการพัฒนาระบบ ERP',
                'budget_total': Decimal('5000000.00'),
                'status': 'ดำเนินการ'
            },
            {
                'project_code': 'PRJ-2568-002',
                'project_name': 'โครงการปรับปรุงห้อง Server',
                'budget_total': Decimal('1200000.00'),
                'status': 'ดำเนินการ'
            },
            {
                'project_code': 'PRJ-2568-003',
                'project_name': 'โครงการฝึกอบรมพนักงานประจำปี',
                'budget_total': Decimal('300000.00'),
                'status': 'ดำเนินการ'
            },
            {
                'project_code': 'PRJ-2568-004',
                'project_name': 'โครงการจัดซื้อคอมพิวเตอร์ใหม่',
                'budget_total': Decimal('2500000.00'),
                'status': 'ดำเนินการ'
            },
            {
                'project_code': 'PRJ-2567-009',
                'project_name': 'โครงการวิจัยตลาด Q4',
                'budget_total': Decimal('800000.00'),
                'status': 'ปิด'
            },
            {
                'project_code': 'PRJ-2568-005',
                'project_name': 'โครงการปรับปรุงภูมิทัศน์',
                'budget_total': Decimal('450000.00'),
                'status': 'ดำเนินการ'
            },
            {
                'project_code': 'PRJ-2568-006',
                'project_name': 'โครงการ CSR เพื่อสังคม',
                'budget_total': Decimal('200000.00'),
                'status': 'ดำเนินการ'
            },
            {
                'project_code': 'PRJ-2568-007',
                'project_name': 'โครงการพัฒนาระบบ Mobile App',
                'budget_total': Decimal('1500000.00'),
                'status': 'ดำเนินการ'
            },
            {
                'project_code': 'PRJ-2567-010',
                'project_name': 'โครงการซ่อมบำรุงลิฟต์',
                'budget_total': Decimal('600000.00'),
                'status': 'ปิด'
            },
            {
                'project_code': 'PRJ-2568-008',
                'project_name': 'โครงการสวัสดิการพนักงาน',
                'budget_total': Decimal('1000000.00'),
                'status': 'ดำเนินการ'
            },
        ]

        count = 0
        for data in projects_data:
            project, created = Projects.objects.get_or_create(
                project_code=data['project_code'],
                defaults={
                    'project_name': data['project_name'],
                    'budget_total': data['budget_total'],
                    'status': data['status']
                }
            )
            if created:
                self.stdout.write(f'  ✅ Created: {project.project_code}')
                count += 1
            else:
                self.stdout.write(f'  ⏭️  Already exists: {project.project_code}')

        self.stdout.write(self.style.SUCCESS(f'✅ Total Projects: {count} created'))

    def populate_vendors(self):
        """สร้างข้อมูล Vendors"""
        self.stdout.write('\n🏢 Creating Vendors...')
        
        vendors_data = [
            {
                'vendor_name': 'บริษัท เทคโนโลยี ซอลูชั่น จำกัด',
                'phone': '02-1234-5678',
                'email': 'contact@techsolution.co.th'
            },
            {
                'vendor_name': 'ห้างหุ้นส่วนจำกัด อีเลคทรอนิคส์',
                'phone': '089-123-4567',
                'email': 'sales@electronics.co.th'
            },
            {
                'vendor_name': 'บริษัท สำนักพิมพ์ มีเดีย',
                'phone': '02-9876-5432',
                'email': 'info@mediapub.co.th'
            },
            {
                'vendor_name': 'โรงแรม และ สิ่งอำนวยความสะดวก',
                'phone': '033-123-4567',
                'email': 'booking@hotelservice.co.th'
            },
            {
                'vendor_name': 'บริษัท ออฟฟิศ ซัพพลาย แพลส',
                'phone': '02-5555-1111',
                'email': 'order@officesupply.co.th'
            },
        ]

        count = 0
        for data in vendors_data:
            vendor, created = Vendors.objects.get_or_create(
                vendor_name=data['vendor_name'],
                defaults={
                    'phone': data['phone'],
                    'email': data['email']
                }
            )
            if created:
                self.stdout.write(f'  ✅ Created: {vendor.vendor_name}')
                count += 1
            else:
                self.stdout.write(f'  ⏭️  Already exists: {vendor.vendor_name}')

        self.stdout.write(self.style.SUCCESS(f'✅ Total Vendors: {count} created'))

    def populate_master_items(self):
        """สร้างข้อมูล Master Items"""
        self.stdout.write('\n📦 Creating Master Items...')
        
        items_data = [
            {
                'item_code': 'ITEM-001',
                'item_name': 'กระดาษ A4 (500 แผ่น)',
                'standard_unit': 'รีม'
            },
            {
                'item_code': 'ITEM-002',
                'item_name': 'ปากกาลูกลื่น สีดำ',
                'standard_unit': 'โหล'
            },
            {
                'item_code': 'ITEM-003',
                'item_name': 'ไม้บรรทัดขนาด 30 ซม.',
                'standard_unit': 'อัน'
            },
            {
                'item_code': 'ITEM-004',
                'item_name': 'เทปกาว 24 มม.',
                'standard_unit': 'ม้วน'
            },
            {
                'item_code': 'ITEM-005',
                'item_name': 'ยางลบดินสอ',
                'standard_unit': 'อัน'
            },
            {
                'item_code': 'ITEM-006',
                'item_name': 'กล่องไฟล์เอกสาร',
                'standard_unit': 'กล่อง'
            },
            {
                'item_code': 'ITEM-007',
                'item_name': 'สมุดบันทึก (100 หน้า)',
                'standard_unit': 'เล่ม'
            },
            {
                'item_code': 'ITEM-008',
                'item_name': 'หมึกเครื่องพิมพ์ (ม่วงแดง)',
                'standard_unit': 'ขวด'
            },
            {
                'item_code': 'ITEM-009',
                'item_name': 'เข็มกลัดทองแดง',
                'standard_unit': 'กล่อง'
            },
            {
                'item_code': 'ITEM-010',
                'item_name': 'ซองจดหมาย (16x24 ซม.)',
                'standard_unit': 'แพ็ค'
            },
        ]

        count = 0
        for data in items_data:
            item, created = MasterItems.objects.get_or_create(
                item_code=data['item_code'],
                defaults={
                    'item_name': data['item_name'],
                    'standard_unit': data['standard_unit']
                }
            )
            if created:
                self.stdout.write(f'  ✅ Created: {item.item_code}')
                count += 1
            else:
                self.stdout.write(f'  ⏭️  Already exists: {item.item_code}')

        self.stdout.write(self.style.SUCCESS(f'✅ Total Items: {count} created'))

    def show_summary(self):
        """แสดงสรุปข้อมูล"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ Data Population Completed!'))
        self.stdout.write('='*50)
        self.stdout.write(f'📊 Projects: {Projects.objects.count()}')
        self.stdout.write(f'📊 Vendors: {Vendors.objects.count()}')
        self.stdout.write(f'📊 Master Items: {MasterItems.objects.count()}')
        self.stdout.write('='*50)
```

---

## ⚙️ วิธีใช้ Management Command

### **ขั้นตอนที่ 1: สร้างไฟล์**

สร้างไดเรกทอรี่ตามโครงสร้างด้านบนแล้วสร้างไฟล์ `populate_db.py`

### **ขั้นตอนที่ 2: รัน Command**

```powershell
# เข้าโฟลเดอร์ POTMS
cd e:\DSSI-PROJECT-2568\POTMS

# รัน management command
python manage.py populate_db

# Output:
# 🚀 Starting data population...
# Clear existing data? (y/n): y
# 🗑️  Clearing existing data...
# ✅ Data cleared
# 
# 📌 Creating Projects...
#   ✅ Created: PRJ-2568-001
#   ✅ Created: PRJ-2568-002
#   ...
# ✅ Total Projects: 10 created
#
# 🏢 Creating Vendors...
#   ✅ Created: บริษัท เทคโนโลยี ซอลูชั่น จำกัด
#   ...
# ✅ Total Vendors: 5 created
#
# 📦 Creating Master Items...
#   ✅ Created: ITEM-001
#   ...
# ✅ Total Items: 10 created
#
# ==================================================
# ✅ Data Population Completed!
# ==================================================
# 📊 Projects: 10
# 📊 Vendors: 5
# 📊 Master Items: 10
# ==================================================
```

---

## 🎯 Django ORM วิธีใช้อื่น ๆ

### **1. ใช้ Django Shell** (Interactive)

```powershell
python manage.py shell

# ภายในแล้ว:
from api.models import Projects
from decimal import Decimal

# Create
project = Projects.objects.create(
    project_code='PRJ-2568-011',
    project_name='โครงการใหม่',
    budget_total=Decimal('1000000.00'),
    status='ดำเนินการ'
)

# Read
all_projects = Projects.objects.all()
specific_project = Projects.objects.get(project_code='PRJ-2568-001')

# Update
project.project_name = 'โครงการใหม่ (Updated)'
project.save()

# Delete
project.delete()

# Query (Filter)
active_projects = Projects.objects.filter(status='ดำเนินการ')
```

### **2. ใช้ Bulk Create** (สร้างหลายรายการ)

```python
projects_list = [
    Projects(project_code='PRJ-X', project_name='Project X', ...),
    Projects(project_code='PRJ-Y', project_name='Project Y', ...),
]
Projects.objects.bulk_create(projects_list)
```

### **3. ใช้ get_or_create** (สร้างถ้าไม่มี, ได้ถ้ามี)

```python
project, created = Projects.objects.get_or_create(
    project_code='PRJ-2568-001',
    defaults={
        'project_name': 'โครงการ',
        'budget_total': Decimal('1000000.00'),
        'status': 'ดำเนินการ'
    }
)
if created:
    print('สร้างใหม่')
else:
    print('มีอยู่แล้ว')
```

---

## 📊 ตารางเปรียบเทียบ: SQL vs Django ORM

| Operation | SQL | Django ORM |
|-----------|-----|-----------|
| **Create** | `INSERT INTO projects (...) VALUES (...)` | `Projects.objects.create(...)` |
| **Read All** | `SELECT * FROM projects` | `Projects.objects.all()` |
| **Read One** | `SELECT * FROM projects WHERE project_code='PRJ-001'` | `Projects.objects.get(project_code='PRJ-001')` |
| **Filter** | `SELECT * FROM projects WHERE status='ดำเนินการ'` | `Projects.objects.filter(status='ดำเนินการ')` |
| **Update** | `UPDATE projects SET project_name='...' WHERE id=1` | `project.project_name='...'; project.save()` |
| **Delete** | `DELETE FROM projects WHERE id=1` | `project.delete()` |

---

## ✅ สรุป: Django ORM ใช้ที่ไหนบ้าง

### **ปัจจุบัน (ใช้ ORM แล้ว):**
- ✅ `views.py` - ใช้ `Projects.objects.all()` และ `.filter()`
- ✅ `models.py` - Definition ของ Models
- ✅ `serializers.py` - Automatic model serialization
- ✅ `urls.py` - Router configuration

### **ที่ต้องเพิ่ม:**
- ✨ `management/commands/populate_db.py` - Management command สำหรับ populate data
- ✨ `populate_data.py` - Script standalone (หรือใช้ management command แทน)

### **ที่ไม่ต้องแก้:**
- HTML/JavaScript UI - เข้าถึงข้อมูลผ่าน API (views.py ใช้ ORM)

**สรุป:** โครงการคุณใช้ Django ORM อยู่แล้ว! แค่ต้องเพิ่ม management command เพื่อ populate initial data เท่านั้น 🎉

