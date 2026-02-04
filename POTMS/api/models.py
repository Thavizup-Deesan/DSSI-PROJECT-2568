from django.db import models

# =================================================================
# Project Model (Existing - Updated)
# =================================================================
class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('พัสดุ', 'พัสดุ'),
        ('ครุภัณฑ์', 'ครุภัณฑ์'),
    ]
    
    project_code = models.CharField(max_length=50, unique=True)
    project_name = models.CharField(max_length=255)
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPE_CHOICES, default='พัสดุ')
    budget_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    budget_used = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projects'

    def __str__(self):
        return f"{self.project_code} - {self.project_name}"

    @property
    def budget_remaining(self):
        return self.budget_total - self.budget_used


# =================================================================
# User Model
# =================================================================
class User(models.Model):
    ROLE_CHOICES = [
        ('user', 'ผู้ขอซื้อ'),
        ('staff', 'พัสดุ'),
        ('boss', 'หัวหน้าภาควิชา'),
        ('admin', 'Admin'),
    ]
    
    uid = models.CharField(max_length=100, unique=True, primary_key=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    password = models.CharField(max_length=255, blank=True, default='')  # Hashed password
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.full_name} ({self.email})"


# =================================================================
# Vendor Model (Existing - Updated)
# =================================================================
class Vendor(models.Model):
    vendor_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vendors'

    def __str__(self):
        return self.vendor_name


# =================================================================
# Master Item Model (Existing - Updated)
# =================================================================
class MasterItem(models.Model):
    item_code = models.CharField(max_length=50, unique=True)
    item_name = models.CharField(max_length=255)
    standard_unit = models.CharField(max_length=50)
    category = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'master_items'

    def __str__(self):
        return self.item_name


# =================================================================
# Order Model
# =================================================================
class Order(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'ร่าง'),
        ('รอ', 'รอหัวหน้าอนุมัติ'),
        ('รอรับของ', 'รอรับของ'),
        ('รับบางส่วน', 'รับบางส่วน'),
        ('รับครบ', 'รับครบแล้ว'),
        ('Rejected', 'ไม่อนุมัติ'),
    ]
    
    ORDER_TYPE_CHOICES = [
        ('พัสดุ', 'พัสดุ'),
        ('ครุภัณฑ์', 'ครุภัณฑ์'),
    ]
    
    order_no = models.CharField(max_length=50, unique=True)
    order_title = models.CharField(max_length=255)
    order_type = models.CharField(max_length=50, choices=ORDER_TYPE_CHOICES, default='พัสดุ')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name='orders')
    requester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    requester_name = models.CharField(max_length=255, blank=True, default='')
    vendor_name = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Draft')
    total_estimated_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    required_date = models.DateField(null=True, blank=True)
    order_description = models.TextField(blank=True, default='')
    staff_note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_no} - {self.order_title}"

    @property
    def project_name(self):
        return self.project.project_name if self.project else ''

    @property
    def project_code(self):
        return self.project.project_code if self.project else ''


# =================================================================
# Order Item Model
# =================================================================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    unit = models.CharField(max_length=50)
    estimated_unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_received = models.IntegerField(default=0)

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"{self.item_name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.estimated_unit_price

    @property
    def remaining_quantity(self):
        return self.quantity - self.quantity_received


# =================================================================
# Order Image Model (NEW - For Image Upload Feature)
# =================================================================
class OrderImage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='orders/%Y/%m/')
    description = models.CharField(max_length=255, blank=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_images'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Image for {self.order.order_no}"


# =================================================================
# Delivery Record Model (For Tracking Partial Receipts)
# =================================================================
class DeliveryRecord(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='deliveries')
    delivered_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, default='')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'delivery_records'
        ordering = ['-delivered_at']


class DeliveryItem(models.Model):
    delivery = models.ForeignKey(DeliveryRecord, on_delete=models.CASCADE, related_name='items')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    quantity_received = models.IntegerField(default=0)

    class Meta:
        db_table = 'delivery_items'