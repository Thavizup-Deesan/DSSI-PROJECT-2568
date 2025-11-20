from django.db import models
class Projects(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=50, unique=True)
    project_name = models.CharField(max_length=255)
    budget_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50)

    class Meta:
        db_table = 'projects'

class Vendors(models.Model):
    vendor_id = models.AutoField(primary_key=True)
    vendor_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'vendors' 

    def __str__(self):
        return self.vendor_name

class MasterItems(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_code = models.CharField(max_length=50, unique=True)
    item_name = models.CharField(max_length=255)
    standard_unit = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True) 

    class Meta:
        db_table = 'master_items' 

    def __str__(self):
        return self.item_name