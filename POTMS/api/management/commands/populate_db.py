"""
Django Management Command: populate_db
Populates database with initial data using Django ORM

Usage:
    python manage.py populate_db
"""

from django.core.management.base import BaseCommand
from api.models import Projects, Vendors, MasterItems
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate database with initial data using Django ORM'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        """
        Main handler for the command
        """
        self.stdout.write(self.style.SUCCESS('🚀 Starting data population...\n'))

        # Clear existing data if requested
        if options['clear']:
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
        self.stdout.write(self.style.SUCCESS('✅ Data cleared\n'))

    def populate_projects(self):
        """สร้างข้อมูล Projects"""
        self.stdout.write('📌 Creating Projects...')
        
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
                self.stdout.write(f'  ✅ Created: {project.project_code} - {project.project_name}')
                count += 1
            else:
                self.stdout.write(f'  ⏭️  Already exists: {project.project_code}')

        self.stdout.write(self.style.SUCCESS(f'✅ Total Projects created: {count}\n'))

    def populate_vendors(self):
        """สร้างข้อมูล Vendors"""
        self.stdout.write('🏢 Creating Vendors...')
        
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

        self.stdout.write(self.style.SUCCESS(f'✅ Total Vendors created: {count}\n'))

    def populate_master_items(self):
        """สร้างข้อมูล Master Items"""
        self.stdout.write('📦 Creating Master Items...')
        
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

        self.stdout.write(self.style.SUCCESS(f'✅ Total Items created: {count}\n'))

    def show_summary(self):
        """แสดงสรุปข้อมูล"""
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('✅ Data Population Completed Successfully!'))
        self.stdout.write('='*60)
        self.stdout.write(f'📊 Total Projects:     {Projects.objects.count()}')
        self.stdout.write(f'📊 Total Vendors:      {Vendors.objects.count()}')
        self.stdout.write(f'📊 Total Master Items: {MasterItems.objects.count()}')
        self.stdout.write('='*60)
