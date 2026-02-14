from decimal import Decimal
import django.db.models.deletion
from django.db import migrations, models


def safe_initialize_db(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        # Check if 'users' table exists and add missing columns
        cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'users'")
        if cursor.fetchone()[0] > 0:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'is_admin'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'is_officer'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN is_officer BOOLEAN DEFAULT FALSE")
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'is_head'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN is_head BOOLEAN DEFAULT FALSE")
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'role'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'User'")


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunPython(safe_initialize_db),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('project_id', models.AutoField(primary_key=True, serialize=False)),
                ('project_name', models.CharField(max_length=255, verbose_name='ชื่อโครงการ')),
                ('total_budget', models.DecimalField(decimal_places=2, default=0.0, max_digits=15, verbose_name='งบประมาณทั้งหมด')),
                ('reserved_budget', models.DecimalField(decimal_places=2, default=0.0, max_digits=15, verbose_name='งบที่ถูกกัน')),
                ('remaining_budget', models.DecimalField(decimal_places=2, default=0.0, max_digits=15, verbose_name='งบคงเหลือ')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='วันเริ่มต้น')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='วันสิ้นสุด')),
                ('status', models.CharField(choices=[('Draft', 'Draft'), ('Active', 'Active'), ('Closed', 'Closed')], default='Draft', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'projects',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('full_name', models.CharField(blank=True, default='', max_length=255)),
                ('is_admin', models.BooleanField(default=False, verbose_name='ผู้ดูแลระบบ')),
                ('is_officer', models.BooleanField(default=False, verbose_name='เจ้าหน้าที่พัสดุ')),
                ('is_head', models.BooleanField(default=False, verbose_name='หัวหน้าภาค')),
                ('role', models.CharField(choices=[('Admin', 'Admin'), ('Officer', 'Officer'), ('User', 'User'), ('Committee', 'Committee')], default='User', max_length=20, verbose_name='บทบาท')),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_no', models.CharField(max_length=50, verbose_name='เลขที่เอกสาร')),
                ('total_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=15, verbose_name='จำนวนเงินรวม')),
                ('reason', models.TextField(blank=True, null=True, verbose_name='เหตุผลในการจัดซื้อ')),
                ('rejection_reason', models.TextField(blank=True, null=True, verbose_name='เหตุผลที่ปฏิเสธ')),
                ('inspection_committee_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='กรรมการตรวจรับ (ระบุเอง)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('Draft', 'ร่าง'), ('Reserved', 'กันวงเงินแล้ว'), ('Pending_Approval', 'รออนุมัติ'), ('Approved', 'อนุมัติแล้ว'), ('Rejected', 'ถูกปฏิเสธ'), ('Completed', 'เสร็จสิ้น')], default='Draft', max_length=30)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='api.project', verbose_name='โครงการ')),
                ('approver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_approved', to='api.user', verbose_name='ผู้อนุมัติ')),
                ('inspection_committee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_inspected', to='api.user', verbose_name='กรรมการตรวจรับ (User)')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders_requested', to='api.user', verbose_name='ผู้ขอซื้อ')),
            ],
            options={
                'db_table': 'purchase_orders',
                'unique_together': {('project', 'order_no')},
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0.0, max_digits=15, verbose_name='จำนวนเงินที่เบิก')),
                ('payment_date', models.DateTimeField(auto_now_add=True, verbose_name='วันที่เบิกจ่าย')),
                ('status', models.CharField(choices=[('Processing', 'กำลังดำเนินการ'), ('Paid', 'จ่ายแล้ว')], default='Processing', max_length=20)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='api.project', verbose_name='โครงการ')),
                ('related_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='api.purchaseorder', verbose_name='ใบสั่งซื้อที่เกี่ยวข้อง')),
            ],
            options={
                'db_table': 'payments',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('material_name', models.CharField(max_length=255, verbose_name='ชื่อวัสดุ')),
                ('quantity', models.IntegerField(default=1, verbose_name='จำนวน')),
                ('unit', models.CharField(default='ชิ้น', max_length=50, verbose_name='หน่วย')),
                ('unit_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='ราคาต่อหน่วย')),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=15, verbose_name='ราคารวม')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='api.purchaseorder', verbose_name='ใบสั่งซื้อ')),
            ],
            options={
                'db_table': 'order_items',
            },
        ),
        migrations.AddField(
            model_name='project',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects_created', to='api.user', verbose_name='สร้างโดย'),
        ),
        migrations.CreateModel(
            name='PartialReceive',
            fields=[
                ('receive_id', models.AutoField(primary_key=True, serialize=False)),
                ('receipt_no', models.CharField(blank=True, max_length=100, null=True, verbose_name='เลขที่ใบเสร็จ')),
                ('receipt_file_path', models.CharField(blank=True, max_length=500, null=True, verbose_name='ไฟล์ใบเสร็จ (PDF/JPG)')),
                ('received_date', models.DateTimeField(auto_now_add=True, verbose_name='วันที่รับของ')),
                ('status', models.CharField(choices=[('Pending_Inspection', 'รอตรวจรับ'), ('Inspected', 'ตรวจรับแล้ว')], default='Pending_Inspection', max_length=30)),
                ('committee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_inspections', to='api.user', verbose_name='กรรมการตรวจรับ (ผู้ได้รับมอบหมาย)')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partial_receives', to='api.purchaseorder', verbose_name='ใบสั่งซื้อ')),
                ('recorded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partial_receives_recorded', to='api.user', verbose_name='บันทึกโดย')),
            ],
            options={
                'db_table': 'partial_receives',
            },
        ),
        migrations.CreateModel(
            name='Inspection',
            fields=[
                ('inspection_id', models.AutoField(primary_key=True, serialize=False)),
                ('inspection_date', models.DateTimeField(auto_now_add=True, verbose_name='วันที่ตรวจรับ')),
                ('result', models.CharField(choices=[('Pass', 'ผ่าน'), ('Reject', 'ไม่ผ่าน')], max_length=10, verbose_name='ผลตรวจรับ')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='หมายเหตุ')),
                ('partial_receive', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='inspection', to='api.partialreceive', verbose_name='ใบรับของ')),
                ('committee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inspections_done', to='api.user', verbose_name='กรรมการตรวจรับ')),
            ],
            options={
                'db_table': 'inspections',
            },
        ),
        migrations.CreateModel(
            name='ProjectParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_in_project', models.CharField(choices=[('Requester', 'ผู้ขอซื้อ'), ('Committee', 'กรรมการตรวจรับ')], default='Requester', max_length=20, verbose_name='บทบาทในโครงการ')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='api.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_participations', to='api.user')),
            ],
            options={
                'db_table': 'project_participants',
                'unique_together': {('project', 'user')},
            },
        ),
        migrations.CreateModel(
            name='PartialReceiveItem',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=0, verbose_name='จำนวนที่รับ')),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_records', to='api.orderitem', verbose_name='รายการสั่งซื้อ')),
                ('partial_receive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receive_items', to='api.partialreceive', verbose_name='ใบรับของ')),
            ],
            options={
                'verbose_name': 'รายการรับของ',
                'verbose_name_plural': 'รายการรับของ',
                'db_table': 'partial_receive_items',
            },
        ),
    ]
