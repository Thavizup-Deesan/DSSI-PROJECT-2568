"""
Script to populate initial data into the database
Run: python manage.py shell < populate_data.py
Or: python populate_data.py (if DJANGO_SETTINGS_MODULE is set)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Projects, Vendors, MasterItems
from decimal import Decimal

# =====================================
# 1️⃣ ลบข้อมูลเก่า (Optional)
# =====================================
print("Clearing existing data...")
Projects.objects.all().delete()
Vendors.objects.all().delete()
MasterItems.objects.all().delete()

# =====================================
# 2️⃣ สร้างข้อมูล Projects
# =====================================
print("Creating Projects...")
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

for data in projects_data:
    project, created = Projects.objects.get_or_create(
        project_code=data['project_code'],
        defaults={
            'project_name': data['project_name'],
            'budget_total': data['budget_total'],
            'status': data['status']
        }
    )
    status_text = "✅ Created" if created else "⏭️  Already exists"
    print(f"  {status_text}: {project.project_code} - {project.project_name}")

print(f"\n✅ Total Projects: {Projects.objects.count()}")

# =====================================
# 3️⃣ สร้างข้อมูล Vendors
# =====================================
print("\nCreating Vendors...")
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

for data in vendors_data:
    vendor, created = Vendors.objects.get_or_create(
        vendor_name=data['vendor_name'],
        defaults={
            'phone': data['phone'],
            'email': data['email']
        }
    )
    status_text = "✅ Created" if created else "⏭️  Already exists"
    print(f"  {status_text}: {vendor.vendor_name}")

print(f"\n✅ Total Vendors: {Vendors.objects.count()}")

# =====================================
# 4️⃣ สร้างข้อมูล Master Items
# =====================================
print("\nCreating Master Items...")
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

for data in items_data:
    item, created = MasterItems.objects.get_or_create(
        item_code=data['item_code'],
        defaults={
            'item_name': data['item_name'],
            'standard_unit': data['standard_unit']
        }
    )
    status_text = "✅ Created" if created else "⏭️  Already exists"
    print(f"  {status_text}: {item.item_code} - {item.item_name}")

print(f"\n✅ Total Master Items: {MasterItems.objects.count()}")

# =====================================
# 5️⃣ สรุป
# =====================================
print("\n" + "="*50)
print("✅ Data Population Completed!")
print("="*50)
print(f"📊 Projects: {Projects.objects.count()}")
print(f"📊 Vendors: {Vendors.objects.count()}")
print(f"📊 Master Items: {MasterItems.objects.count()}")
print("="*50)
