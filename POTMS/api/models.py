from django.db import models

# =================================================================
# Master Data Entities
# =================================================================

class User(models.Model):
    """ผู้ใช้งานระบบ"""
    ROLE_CHOICES = [
        ('User', 'User'),
        ('Staff', 'Staff'),
        ('Admin', 'Admin'),
    ]
    
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255, default='')  # ✅ Added for Auth Migration
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')
    department = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class Project(models.Model):
    """โครงการ"""
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    project_id = models.AutoField(primary_key=True)
    ubufmis_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='รหัส UBUFMIS')
    project_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    project_name = models.CharField(max_length=255)
    
    # Budget breakdown fields
    budget_compensation = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='ค่าตอบแทน')
    budget_usage = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='ค่าใช้สอย')
    budget_materials = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='ค่าวัสดุ')
    budget_equipment = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='ค่าครุภัณฑ์')
    budget_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='งบทั้งหมด')
    budget_reserved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='งบที่ถูกจอง')
    budget_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='งบจ่ายจริง')
    
    responsible_person = models.CharField(max_length=255, blank=True, null=True, verbose_name='ผู้รับผิดชอบโครงการ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'projects'
    
    def __str__(self):
        return self.project_name
    
    @property
    def budget_available(self):
        """งบคงเหลือ = งบทั้งหมด - งบที่ถูกจอง"""
        return self.budget_total - self.budget_reserved


class ProjectAssignment(models.Model):
    """มอบหมายโครงการ - กำหนดผู้รับผิดชอบโครงการ"""
    assignment_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assignments_made')
    assigned_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True, verbose_name='หมายเหตุ')
    
    class Meta:
        db_table = 'project_assignments'
        unique_together = ['project', 'user']
    
    def __str__(self):
        return f"{self.user.username} -> {self.project.project_name}"


# =================================================================
# Transaction Entities
# =================================================================

class MainOrder(models.Model):
    """ใบสั่งซื้อหลัก"""
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Ordered', 'Ordered'),
        ('CorrectionNeeded', 'CorrectionNeeded'),
        ('SentToProcurement', 'SentToProcurement'),
        ('Closed', 'Closed'),
    ]
    
    order_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='orders')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_requested', verbose_name='ผู้สั่ง')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_approved', verbose_name='ผู้อนุมัติ')
    order_no = models.CharField(max_length=50, unique=True, verbose_name='เลขที่เอกสาร')
    vendor_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='ชื่อร้านค้า/บริษัท')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Draft')
    total_estimated_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='ราคารวมประมาณการ')
    inspection_committee = models.TextField(blank=True, null=True, verbose_name='รายชื่อกรรมการตรวจรับ')
    staff_note = models.TextField(blank=True, null=True, verbose_name='บันทึกสิ่งที่ต้องแก้ไขจาก Staff')
    
    # ✅ Added fields for standard order form
    order_title = models.CharField(max_length=255, default='', verbose_name='เรื่อง')
    order_description = models.TextField(blank=True, null=True, verbose_name='รายละเอียด')
    required_date = models.DateField(blank=True, null=True, verbose_name='วันที่ต้องการใช้งาน')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'main_orders'
    
    def __str__(self):
        return f"{self.order_no} - {self.project.project_name}"


class OrderItem(models.Model):
    """รายการสินค้าในใบสั่งซื้อ"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Received', 'Received'),
        ('Cancelled', 'Cancelled'),
    ]
    
    item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(MainOrder, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    quantity_requested = models.IntegerField(default=1)
    unit = models.CharField(max_length=50)
    estimated_unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    product_link = models.URLField(max_length=500, blank=True, null=True, verbose_name='ลิงก์สินค้า')
    remarks = models.TextField(blank=True, null=True, verbose_name='หมายเหตุ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    class Meta:
        db_table = 'order_items'
    
    def __str__(self):
        return f"{self.item_name} x {self.quantity_requested}"
    
    @property
    def estimated_total_price(self):
        return self.quantity_requested * self.estimated_unit_price


class SubOrder(models.Model):
    """ใบตรวจรับ/รับของ"""
    STATUS_CHOICES = [
        ('WaitingInspection', 'WaitingInspection'),
        ('Inspected', 'Inspected'),
        ('HandedOver', 'HandedOver'),
    ]
    
    sub_order_id = models.AutoField(primary_key=True)
    main_order = models.ForeignKey(MainOrder, on_delete=models.CASCADE, related_name='sub_orders')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sub_orders_received')
    sub_order_no = models.CharField(max_length=50, unique=True)
    received_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='WaitingInspection')
    note = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'sub_orders'
    
    def __str__(self):
        return f"{self.sub_order_no}"


class InspectionDetail(models.Model):
    """รายละเอียดการรับของ"""
    inspection_id = models.AutoField(primary_key=True)
    sub_order = models.ForeignKey(SubOrder, on_delete=models.CASCADE, related_name='inspection_details')
    item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='inspections')
    qty_received = models.IntegerField(default=0)
    actual_unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_actual_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    qr_code = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'inspection_details'
    
    def __str__(self):
        return f"Inspection: {self.item.item_name} x {self.qty_received}"


# =================================================================
# Additional Master Data (เพิ่มเติมจาก ER Diagram)
# =================================================================

class Vendor(models.Model):
    """ร้านค้า/บริษัท"""
    vendor_id = models.AutoField(primary_key=True)
    vendor_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'vendors'
    
    def __str__(self):
        return self.vendor_name


class MasterItem(models.Model):
    """รายการสินค้ามาตรฐาน (Product Catalog)"""
    item_id = models.AutoField(primary_key=True)
    item_code = models.CharField(max_length=50, unique=True)
    item_name = models.CharField(max_length=255)
    standard_unit = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'master_items'
    
    def __str__(self):
        return self.item_name


# =================================================================
# Audit / History Tracking
# =================================================================

class OrderEditHistory(models.Model):
    """ประวัติการแก้ไขใบขอซื้อ - บันทึกค่าก่อนและหลังแก้ไขอัตโนมัติ"""
    ACTION_CHOICES = [
        ('create', 'สร้างใหม่'),
        ('update', 'แก้ไข'),
        ('status_change', 'เปลี่ยนสถานะ'),
        ('delete', 'ลบ'),
    ]
    
    history_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(MainOrder, on_delete=models.CASCADE, related_name='edit_history')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='order_changes')
    changed_at = models.DateTimeField(auto_now_add=True)
    
    # ค่าก่อนแก้ไข (JSON)
    before_data = models.JSONField(null=True, blank=True, verbose_name='ข้อมูลก่อนแก้ไข')
    # ค่าหลังแก้ไข (JSON)
    after_data = models.JSONField(null=True, blank=True, verbose_name='ข้อมูลหลังแก้ไข')
    
    # รายการ fields ที่เปลี่ยนแปลง
    changed_fields = models.JSONField(null=True, blank=True, verbose_name='ฟิลด์ที่เปลี่ยนแปลง')
    
    # หมายเหตุ
    notes = models.TextField(blank=True, null=True, verbose_name='หมายเหตุ')
    
    class Meta:
        db_table = 'order_edit_history'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"[{self.action}] {self.order.order_no} - {self.changed_at.strftime('%d/%m/%Y %H:%M')}"