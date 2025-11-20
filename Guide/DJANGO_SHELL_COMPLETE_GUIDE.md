# 🐚 Django Shell + Django ORM - Complete Guide

## 1️⃣ เปิด Django Shell

### **Step 1: เข้าไปยัง POTMS Directory**

```powershell
cd e:\DSSI-PROJECT-2568\POTMS
```

### **Step 2: เปิด Django Shell**

```powershell
python manage.py shell
```

### **Output ที่คาดหวัง:**

```
Python 3.x.x (default, ...)
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>>
```

---

## 2️⃣ Import Models

### **Import ทั้งหมด:**

```python
>>> from api.models import Projects, Vendors, MasterItems
>>> from decimal import Decimal
```

### **ตรวจสอบว่า Import สำเร็จ:**

```python
>>> Projects
<class 'api.models.Projects'>

>>> Vendors
<class 'api.models.Vendors'>

>>> MasterItems
<class 'api.models.MasterItems'>
```

---

## 3️⃣ CREATE - สร้างข้อมูล

### **3.1 สร้างโครงการ (Project) เพียงรายการเดียว**

```python
# สร้าง object ใหม่
>>> project = Projects.objects.create(
...     project_code='PRJ-SHELL-001',
...     project_name='โครงการทดสอบ Shell',
...     budget_total=Decimal('1500000.00'),
...     status='ดำเนินการ'
... )

# ตรวจสอบ object ที่สร้าง
>>> project
<Projects: Projects object (1)>

>>> project.project_code
'PRJ-SHELL-001'

>>> project.project_name
'โครงการทดสอบ Shell'

>>> project.budget_total
Decimal('1500000.00')
```

### **3.2 สร้างผู้ขาย (Vendor)**

```python
>>> vendor = Vendors.objects.create(
...     vendor_name='บริษัท ทดสอบ Shell',
...     phone='081-234-5678',
...     email='test@shell.co.th'
... )

>>> vendor
<Vendors: บริษัท ทดสอบ Shell>
```

### **3.3 สร้างรายการพัสดุ (Master Item)**

```python
>>> item = MasterItems.objects.create(
...     item_code='ITEM-SHELL-001',
...     item_name='รายการทดสอบ',
...     standard_unit='อัน'
... )

>>> item
<MasterItems: รายการทดสอบ>
```

### **3.4 สร้างหลายรายการพร้อมกัน (Bulk Create)**

```python
>>> projects_list = [
...     Projects(
...         project_code='PRJ-BULK-001',
...         project_name='Bulk Project 1',
...         budget_total=Decimal('2000000.00'),
...         status='ดำเนินการ'
...     ),
...     Projects(
...         project_code='PRJ-BULK-002',
...         project_name='Bulk Project 2',
...         budget_total=Decimal('3000000.00'),
...         status='ปิด'
...     ),
... ]

>>> Projects.objects.bulk_create(projects_list)
[<Projects: Projects object (2)>, <Projects: Projects object (3)>]
```

---

## 4️⃣ READ - ดึงข้อมูล

### **4.1 ดึงข้อมูลทั้งหมด**

```python
# ดึงทั้งหมด
>>> all_projects = Projects.objects.all()
>>> all_projects
<QuerySet [<Projects: Projects object (1)>, <Projects: Projects object (2)>, ...]>

# ดูจำนวน
>>> all_projects.count()
3

# Loop ผ่านทุกรายการ
>>> for project in all_projects:
...     print(f"{project.project_code} - {project.project_name}")
...
PRJ-SHELL-001 - โครงการทดสอบ Shell
PRJ-BULK-001 - Bulk Project 1
PRJ-BULK-002 - Bulk Project 2
```

### **4.2 ดึงรายการเดียว (Get)**

```python
# ดึงด้วย project_code
>>> project = Projects.objects.get(project_code='PRJ-SHELL-001')
>>> project.project_name
'โครงการทดสอบ Shell'

# ดึงด้วย project_id (PK)
>>> project = Projects.objects.get(project_id=1)

# ✅ ถ้าไม่มีจะ raise DoesNotExist
>>> Projects.objects.get(project_code='NOT-EXIST')
Traceback (most recent call last):
  ...
api.models.Projects.DoesNotExist: Projects matching query does not exist.
```

### **4.3 Filter - กรองข้อมูล**

```python
# Filter โครงการที่ยังดำเนินการ
>>> active_projects = Projects.objects.filter(status='ดำเนินการ')
>>> active_projects
<QuerySet [<Projects: Projects object (1)>, <Projects: Projects object (2)>]>

>>> for p in active_projects:
...     print(f"{p.project_code}: {p.status}")
...
PRJ-SHELL-001: ดำเนินการ
PRJ-BULK-001: ดำเนินการ

# Filter โครงการที่ปิด
>>> closed_projects = Projects.objects.filter(status='ปิด')
>>> closed_projects.count()
1
```

### **4.4 Filter Multiple Conditions**

```python
# โครงการ AND (ดำเนินการ AND มี code PRJ-SHELL)
>>> from django.db.models import Q

>>> projects = Projects.objects.filter(
...     status='ดำเนินการ',
...     project_code__startswith='PRJ-SHELL'
... )

# โครงการ OR
>>> projects = Projects.objects.filter(
...     Q(status='ดำเนินการ') | Q(status='ปิด')
... )
```

### **4.5 Get or Filter First**

```python
# ถ้ามี return, ถ้าไม่มี return None
>>> project = Projects.objects.filter(project_code='NOT-EXIST').first()
>>> project is None
True

# Safe get
>>> project = Projects.objects.get_or_create(
...     project_code='PRJ-SAFE-001',
...     defaults={'project_name': 'Safe Project', 'status': 'ดำเนินการ'}
... )
>>> project
(<Projects: Projects object (4)>, True)  # (object, created)
```

### **4.6 Order By**

```python
# เรียงจากน้อยไปมาก
>>> projects = Projects.objects.all().order_by('budget_total')

# เรียงจากมากไปน้อย
>>> projects = Projects.objects.all().order_by('-budget_total')

# ดูข้อมูล
>>> for p in projects:
...     print(f"{p.project_code}: ฿{p.budget_total}")
...
```

### **4.7 Limit (Slice)**

```python
# ดึง 3 รายการแรก
>>> Projects.objects.all()[:3]

# ดึงรายการที่ 2-4
>>> Projects.objects.all()[1:4]

# ดึง 1 รายการแรก
>>> Projects.objects.all().first()
```

---

## 5️⃣ UPDATE - แก้ไขข้อมูล

### **5.1 แก้ไขแล้ว Save**

```python
# ดึงออบเจค
>>> project = Projects.objects.get(project_code='PRJ-SHELL-001')

# แก้ไขค่า
>>> project.project_name = 'โครงการทดสอบ Shell (Updated)'
>>> project.budget_total = Decimal('2000000.00')

# บันทึก
>>> project.save()

# ตรวจสอบ
>>> project = Projects.objects.get(project_code='PRJ-SHELL-001')
>>> project.project_name
'โครงการทดสอบ Shell (Updated)'
```

### **5.2 Update Multiple Records**

```python
# Update ทุกโครงการที่ใช้เวลา
>>> Projects.objects.filter(status='ปิด').update(status='ดำเนินการ')
1  # จำนวนที่ update

# ตรวจสอบ
>>> Projects.objects.filter(status='ดำเนินการ').count()
4
```

### **5.3 Update Specific Field**

```python
# เปลี่ยนเฉพาะ budget ของโครงการเดียว
>>> project = Projects.objects.get(project_code='PRJ-SHELL-001')
>>> project.budget_total = Decimal('5000000.00')
>>> project.save()
```

---

## 6️⃣ DELETE - ลบข้อมูล

### **6.1 ลบรายการเดียว**

```python
# ดึงออบเจค
>>> project = Projects.objects.get(project_code='PRJ-SHELL-001')

# ลบ
>>> project.delete()
(1, {'api.Projects': 1})  # (deleted_count, deleted_by_type)

# ตรวจสอบ
>>> Projects.objects.filter(project_code='PRJ-SHELL-001').exists()
False
```

### **6.2 ลบหลายรายการ**

```python
# ลบทั้งหมดที่มี status ปิด
>>> deleted_count, _ = Projects.objects.filter(status='ปิด').delete()
>>> print(f"ลบไป {deleted_count} รายการ")
ลบไป 2 รายการ
```

### **6.3 ลบทั้งหมด**

```python
# ⚠️ ระวัง! ลบทั้งหมด
>>> Projects.objects.all().delete()
(10, {'api.Projects': 10})
```

---

## 7️⃣ ADVANCED Queries

### **7.1 Count**

```python
# นับทั้งหมด
>>> Projects.objects.count()
10

# นับตามเงื่อนไข
>>> Projects.objects.filter(status='ดำเนินการ').count()
7
```

### **7.2 Exists**

```python
# ตรวจสอบว่ามีหรือไม่
>>> Projects.objects.filter(project_code='PRJ-001').exists()
True

>>> Projects.objects.filter(project_code='NOT-EXIST').exists()
False
```

### **7.3 Values (Get specific columns)**

```python
# ดึงเฉพาะ code กับ name
>>> projects = Projects.objects.all().values('project_code', 'project_name')
>>> projects
<QuerySet [{'project_code': 'PRJ-001', 'project_name': 'Project 1'}, ...]>

# Loop
>>> for p in projects:
...     print(p['project_code'], p['project_name'])
```

### **7.4 Values List**

```python
# ดึงเป็น tuple
>>> Projects.objects.all().values_list('project_code', 'project_name')
<QuerySet [('PRJ-001', 'Project 1'), ('PRJ-002', 'Project 2'), ...]>

# ดึงเป็น list แบน
>>> Projects.objects.all().values_list('project_code', flat=True)
<QuerySet ['PRJ-001', 'PRJ-002', 'PRJ-003']>
```

### **7.5 Distinct**

```python
# ดึงเฉพาะค่าที่ไม่ซ้ำ
>>> Projects.objects.values('status').distinct()
<QuerySet [{'status': 'ดำเนินการ'}, {'status': 'ปิด'}]>
```

### **7.6 Aggregation**

```python
from django.db.models import Sum, Avg, Count, Max, Min

# รวมทั้ง budget
>>> Projects.objects.aggregate(
...     total_budget=Sum('budget_total'),
...     avg_budget=Avg('budget_total'),
...     max_budget=Max('budget_total'),
...     min_budget=Min('budget_total'),
...     count=Count('project_id')
... )
{'total_budget': Decimal('15000000.00'), 'avg_budget': Decimal('1500000.00'), ...}
```

---

## 8️⃣ Practical Examples

### **Example 1: สร้างข้อมูล Complete**

```python
>>> # Import
>>> from api.models import Projects, Vendors, MasterItems
>>> from decimal import Decimal

>>> # สร้าง Project
>>> p1 = Projects.objects.create(
...     project_code='PRJ-EX-001',
...     project_name='โครงการตัวอย่าง',
...     budget_total=Decimal('5000000.00'),
...     status='ดำเนินการ'
... )

>>> # สร้าง Vendor
>>> v1 = Vendors.objects.create(
...     vendor_name='บริษัท ตัวอย่าง',
...     phone='02-1234-5678',
...     email='example@vendor.co.th'
... )

>>> # สร้าง Item
>>> i1 = MasterItems.objects.create(
...     item_code='ITEM-EX-001',
...     item_name='รายการตัวอย่าง',
...     standard_unit='กล่อง'
... )

>>> # ตรวจสอบ
>>> Projects.objects.count()
1
>>> Vendors.objects.count()
1
>>> MasterItems.objects.count()
1
```

### **Example 2: ค้นหาและแก้ไข**

```python
>>> # ค้นหา
>>> project = Projects.objects.get(project_code='PRJ-EX-001')

>>> # แก้ไข
>>> project.project_name = 'โครงการตัวอย่าง (Updated)'
>>> project.budget_total = Decimal('6000000.00')
>>> project.save()

>>> # ตรวจสอบ
>>> p = Projects.objects.get(project_code='PRJ-EX-001')
>>> print(f"{p.project_name}: ฿{p.budget_total}")
โครงการตัวอย่าง (Updated): ฿6000000.00
```

### **Example 3: ค้นหาเงื่อนไขซับซ้อน**

```python
>>> # โครงการที่ดำเนินการ และมีงบประมาณมากกว่า 1 ล้าน
>>> projects = Projects.objects.filter(
...     status='ดำเนินการ',
...     budget_total__gte=Decimal('1000000.00')
... )

>>> for p in projects:
...     print(f"{p.project_code}: ฿{p.budget_total}")
```

### **Example 4: ลบข้อมูล**

```python
>>> # ลบโครงการเดียว
>>> project = Projects.objects.get(project_code='PRJ-EX-001')
>>> project.delete()

>>> # ตรวจสอบ
>>> Projects.objects.filter(project_code='PRJ-EX-001').exists()
False
```

### **Example 5: Import Data จาก List**

```python
>>> # ข้อมูล
>>> data = [
...     {'project_code': 'PRJ-IMPORT-001', 'project_name': 'Import 1', 'budget_total': 1000000, 'status': 'ดำเนินการ'},
...     {'project_code': 'PRJ-IMPORT-002', 'project_name': 'Import 2', 'budget_total': 2000000, 'status': 'ดำเนินการ'},
... ]

>>> # สร้าง objects
>>> projects = [Projects(**d) for d in data]

>>> # Bulk create
>>> Projects.objects.bulk_create(projects)

>>> # ตรวจสอบ
>>> Projects.objects.filter(project_code__startswith='PRJ-IMPORT').count()
2
```

---

## 9️⃣ Useful Commands

### **ดูข้อมูลทั้งหมด**

```python
>>> # Projects
>>> Projects.objects.all().values()
<QuerySet [{'project_id': 1, 'project_code': 'PRJ-001', ...}, ...]>

>>> # Vendors
>>> Vendors.objects.all().values()

>>> # Items
>>> MasterItems.objects.all().values()
```

### **ดูจำนวน**

```python
>>> Projects.objects.count()
10

>>> Vendors.objects.count()
5

>>> MasterItems.objects.count()
10
```

### **SQL Query ที่ Django สร้าง**

```python
# ดู SQL query ที่ Django สร้าง
>>> qs = Projects.objects.filter(status='ดำเนินการ')
>>> print(qs.query)
SELECT "api_projects"."project_id", "api_projects"."project_code", ...
FROM "api_projects" WHERE "api_projects"."status" = 'ดำเนินการ'
```

### **Help Command**

```python
# ขอความช่วยเหลือ
>>> help(Projects.objects)

# ขอความช่วยเหลือสำหรับ method
>>> help(Projects.objects.create)
```

---

## 🔟 Exit Django Shell

### **ออกจาก Shell**

```python
>>> exit()
# หรือ
>>> quit()
# หรือ Ctrl+Z (Windows) หรือ Ctrl+D (Linux/Mac)
```

---

## 📋 Quick Reference - Common Commands

| Task              | Command                                                              |
| ----------------- | -------------------------------------------------------------------- |
| **Import Models** | `from api.models import Projects, Vendors, MasterItems`              |
| **Create**        | `Projects.objects.create(project_code='...', ...)`                   |
| **Read All**      | `Projects.objects.all()`                                             |
| **Read One**      | `Projects.objects.get(project_code='PRJ-2568-001')`                           |
| **Filter**        | `Projects.objects.filter(status='ดำเนินการ')`                              |
| **Count**         | `Projects.objects.count()`                                           |
| **Update**        | `project.save()` after modifying                                     |
| **Delete**        | `project.delete()`                                                   |
| **Exists**        | `Projects.objects.filter(...).exists()`                              |
| **Bulk Create**   | `Projects.objects.bulk_create([obj1, obj2])`                         |
| **Bulk Update**   | `Projects.objects.filter(...).update(field=value)`                   |
| **Get or Create** | `Projects.objects.get_or_create(project_code='...', defaults={...})` |
| **Values**        | `Projects.objects.values('field1', 'field2')`                        |
| **Order By**      | `Projects.objects.order_by('field')` or `order_by('-field')`         |

---

## 🎓 Tips & Tricks

### **Tip 1: Lazy Evaluation**

```python
# Query ไม่ถูกรัน ข้อนี้
>>> qs = Projects.objects.filter(status='ดำเนินการ')

# Query รัน ข้อนี้
>>> list(qs)
>>> qs.count()
>>> for p in qs: pass
```

### **Tip 2: Pretty Print**

```python
# ติดตั้ง pprint
>>> from pprint import pprint
>>> pprint(list(Projects.objects.all().values()))
```

### **Tip 3: Check Existence**

```python
# ✅ ถูก
>>> if Projects.objects.filter(project_code='PRJ-001').exists():
...     print("มี")

# ❌ ผิด (ใช้ try-except แทน)
>>> try:
...     p = Projects.objects.get(project_code='NOT-EXIST')
... except Projects.DoesNotExist:
...     print("ไม่มี")
```

---

## ⚠️ Common Mistakes

### **Mistake 1: Forgetting to Import**

```python
# ❌ ผิด
>>> Projects.objects.all()
NameError: name 'Projects' is not defined

# ✅ ถูก
>>> from api.models import Projects
>>> Projects.objects.all()
```

### **Mistake 2: Forgetting to Save**

```python
# ❌ ผิด - changes ไม่ถูก save
>>> p = Projects.objects.get(project_code='PRJ-001')
>>> p.project_name = 'New Name'
# (forgot to call .save())

# ✅ ถูก
>>> p = Projects.objects.get(project_code='PRJ-001')
>>> p.project_name = 'New Name'
>>> p.save()
```

### **Mistake 3: Multiple Queries**

```python
# ❌ ผิด - ใช้ memory มาก
>>> for project in Projects.objects.all():
...     vendor = Vendors.objects.get(vendor_id=project.vendor_id)  # Query ใหม่ทุกครั้ง

# ✅ ถูก - ดึงมา 1 ครั้ง
>>> projects = Projects.objects.all()
>>> vendors = {v.vendor_id: v for v in Vendors.objects.all()}
>>> for project in projects:
...     vendor = vendors.get(project.vendor_id)
```

---

## 📝 Complete Workflow Example

```python
# 1. เปิด Django Shell
# python manage.py shell

# 2. Import
>>> from api.models import Projects, Vendors, MasterItems
>>> from decimal import Decimal

# 3. ดูจำนวน
>>> Projects.objects.count()
10

# 4. ดึงทั้งหมด
>>> all_projects = Projects.objects.all()

# 5. Filter
>>> active = Projects.objects.filter(status='ดำเนินการ')
>>> active.count()
7

# 6. Get เฉพาะ
>>> p1 = Projects.objects.get(project_code='PRJ-001')
>>> p1.project_name
'Project Name'

# 7. Update
>>> p1.project_name = 'Updated Name'
>>> p1.save()

# 8. Create
>>> new_p = Projects.objects.create(
...     project_code='PRJ-NEW',
...     project_name='New Project',
...     budget_total=Decimal('1000000.00'),
...     status='ดำเนินการ'
... )

# 9. Delete
>>> p_delete = Projects.objects.get(project_code='PRJ-DELETE')
>>> p_delete.delete()

# 10. Exit
>>> exit()
```

---

## 🎯 สรุป

### **Django Shell คือ:**

- Interactive Python environment
- เข้าถึง Django ORM ได้เลย
- ใช้ดึง/สร้าง/แก้ไข/ลบข้อมูล
- ไม่ต้องเขียน SQL

### **ขั้นตอนการใช้:**

1. `python manage.py shell`
2. `from api.models import Projects, Vendors, MasterItems`
3. ใช้ `Projects.objects.xxx()`
4. `exit()`


**ทุกคำสั่ง CRUD ทำได้ใน Django Shell! 🚀**
