from django.db import models


# =================================================================
# Entity 1: User (ผู้ใช้งานระบบ)
# Auth: Google OAuth → auto-create on first @ubu.ac.th login
# =================================================================

class User(models.Model):
    """ผู้ใช้งานระบบ — สร้างอัตโนมัติเมื่อ login ด้วย Google (@ubu.ac.th)"""

    ROLE_CHOICES = [
        ('Officer', 'เจ้าหน้าที่พัสดุ'),
        ('User', 'ผู้เข้าร่วมโครงการ'),
        ('Head', 'หัวหน้าภาค'),
    ]

    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)  # Google email (@ubu.ac.th)
    full_name = models.CharField(max_length=255, blank=True, default='')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')
    department = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.full_name} ({self.email})"


# =================================================================
# Entity 2: Project (โครงการ)
# =================================================================

class Project(models.Model):
    """โครงการ — สร้างโดย Officer"""

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Active', 'Active'),
        ('Closed', 'Closed'),
    ]

    project_id = models.AutoField(primary_key=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='projects_created',
        verbose_name='สร้างโดย'
    )
    project_name = models.CharField(max_length=255, verbose_name='ชื่อโครงการ')
    total_budget = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00,
        verbose_name='งบประมาณทั้งหมด'
    )
    reserved_budget = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00,
        verbose_name='งบที่ถูกกัน'
    )
    remaining_budget = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00,
        verbose_name='งบคงเหลือ'
    )
    start_date = models.DateField(blank=True, null=True, verbose_name='วันเริ่มต้น')
    end_date = models.DateField(blank=True, null=True, verbose_name='วันสิ้นสุด')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projects'

    def __str__(self):
        return self.project_name

    def save(self, *args, **kwargs):
        """Auto-calculate remaining_budget"""
        self.remaining_budget = self.total_budget - self.reserved_budget
        super().save(*args, **kwargs)


# =================================================================
# Entity 3: Project_Participant (ผู้เข้าร่วมโครงการ)
# Officer เพิ่ม User เข้าโครงการ → User ถึงจะเห็นโครงการนั้น
# =================================================================

class ProjectParticipant(models.Model):
    """ผู้เข้าร่วมโครงการ — กำหนดโดย Officer"""

    ROLE_IN_PROJECT_CHOICES = [
        ('Requester', 'ผู้ขอซื้อ'),
        ('Committee', 'กรรมการตรวจรับ'),
    ]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='project_participations'
    )
    role_in_project = models.CharField(
        max_length=20,
        choices=ROLE_IN_PROJECT_CHOICES,
        default='Requester',
        verbose_name='บทบาทในโครงการ'
    )

    class Meta:
        db_table = 'project_participants'
        unique_together = ['project', 'user']

    def __str__(self):
        return f"{self.user.full_name} → {self.project.project_name} ({self.role_in_project})"


# =================================================================
# Entity 4: Purchase_Order (ใบสั่งซื้อหลัก)
# =================================================================

class PurchaseOrder(models.Model):
    """ใบสั่งซื้อหลัก — สร้างโดย User (ผู้ขอซื้อ)"""

    STATUS_CHOICES = [
        ('Draft', 'ร่าง'),
        ('Reserved', 'กันวงเงินแล้ว'),
        ('Pending_Approval', 'รออนุมัติ'),
        ('Approved', 'อนุมัติแล้ว'),
        ('Rejected', 'ถูกปฏิเสธ'),
        ('Completed', 'เสร็จสิ้น'),
    ]

    order_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='โครงการ'
    )
    requester = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='orders_requested',
        verbose_name='ผู้ขอซื้อ'
    )
    approver = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='orders_approved',
        verbose_name='ผู้อนุมัติ'
    )
    order_no = models.CharField(max_length=50, verbose_name='เลขที่เอกสาร')
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00,
        verbose_name='จำนวนเงินรวม'
    )
    reason = models.TextField(blank=True, null=True, verbose_name='เหตุผลในการจัดซื้อ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Draft')

    class Meta:
        db_table = 'purchase_orders'
        unique_together = ['project', 'order_no']

    def __str__(self):
        return f"{self.order_no} - {self.project.project_name}"


# =================================================================
# Entity 5: Order_Item (รายการวัสดุ)
# =================================================================

class OrderItem(models.Model):
    """รายการวัสดุในใบสั่งซื้อ"""

    item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE,
        related_name='items',
        verbose_name='ใบสั่งซื้อ'
    )
    material_name = models.CharField(max_length=255, verbose_name='ชื่อวัสดุ')
    quantity = models.IntegerField(default=1, verbose_name='จำนวน')
    unit = models.CharField(max_length=50, default='ชิ้น', verbose_name='หน่วย')
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name='ราคาต่อหน่วย'
    )
    total_price = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00,
        verbose_name='ราคารวม'
    )

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"{self.material_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        """Auto-calculate total_price"""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


# =================================================================
# Entity 6: Partial_Receive (ใบรับของ/ใบเสร็จ)
# Activity: สร้างใบสั่งซื้อย่อย พร้อมแนบใบเสร็จ (.pdf/.jpg)
# =================================================================

class PartialReceive(models.Model):
    """ใบรับของ/ใบเสร็จ — บันทึกการรับของแต่ละครั้ง"""

    STATUS_CHOICES = [
        ('Pending_Inspection', 'รอตรวจรับ'),
        ('Inspected', 'ตรวจรับแล้ว'),
    ]

    receive_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE,
        related_name='partial_receives',
        verbose_name='ใบสั่งซื้อ'
    )
    recorded_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='partial_receives_recorded',
        verbose_name='บันทึกโดย'
    )
    receipt_no = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name='เลขที่ใบเสร็จ'
    )
    receipt_file_path = models.CharField(
        max_length=500, blank=True, null=True,
        verbose_name='ไฟล์ใบเสร็จ (PDF/JPG)'
    )
    received_date = models.DateTimeField(auto_now_add=True, verbose_name='วันที่รับของ')
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pending_Inspection'
    )

    class Meta:
        db_table = 'partial_receives'

    def __str__(self):
        return f"PR-{self.receive_id} ({self.order.order_no})"


# =================================================================
# Entity 7: Inspection (ผลการตรวจรับ)
# Activity: กก.ตรวจรับ: ตรวจนับจำนวน/คุณภาพ
# =================================================================

class Inspection(models.Model):
    """ผลการตรวจรับ — โดยกรรมการตรวจรับ"""

    RESULT_CHOICES = [
        ('Pass', 'ผ่าน'),
        ('Reject', 'ไม่ผ่าน'),
    ]

    inspection_id = models.AutoField(primary_key=True)
    partial_receive = models.OneToOneField(
        PartialReceive, on_delete=models.CASCADE,
        related_name='inspection',
        verbose_name='ใบรับของ'
    )
    committee = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='inspections_done',
        verbose_name='กรรมการตรวจรับ'
    )
    inspection_date = models.DateTimeField(auto_now_add=True, verbose_name='วันที่ตรวจรับ')
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, verbose_name='ผลตรวจรับ')
    comment = models.TextField(blank=True, null=True, verbose_name='หมายเหตุ')

    class Meta:
        db_table = 'inspections'

    def __str__(self):
        return f"Inspection-{self.inspection_id} ({self.result})"


# =================================================================
# Entity 8: Payment (การเบิกจ่าย)
# Activity: ตั้งเบิกจ่ายเงิน (Ready for Payment)
# =================================================================

class Payment(models.Model):
    """การเบิกจ่าย — Officer ตั้งเบิกหลังรับของครบ"""

    STATUS_CHOICES = [
        ('Processing', 'กำลังดำเนินการ'),
        ('Paid', 'จ่ายแล้ว'),
    ]

    payment_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='โครงการ'
    )
    related_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='ใบสั่งซื้อที่เกี่ยวข้อง'
    )
    amount_paid = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00,
        verbose_name='จำนวนเงินที่เบิก'
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='วันที่เบิกจ่าย')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Processing')

    class Meta:
        db_table = 'payments'

    def __str__(self):
        return f"Payment-{self.payment_id} ({self.status})"
