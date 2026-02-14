import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Project, PurchaseOrder

def fix_budgets():
    print("Recalculating budgets for all projects...")
    projects = Project.objects.all()
    for project in projects:
        # Sum of all orders that are NOT Rejected
        orders = PurchaseOrder.objects.filter(project=project).exclude(status='Rejected')
        total_reserved = sum(o.total_amount for o in orders) or Decimal('0.00')
        
        old_reserved = project.reserved_budget
        project.reserved_budget = total_reserved
        # project.save() will auto-calculate remaining_budget
        project.save()
        
        print(f"Project '{project.project_name}' (ID: {project.project_id}):")
        print(f"  Old Reserved: {old_reserved}")
        print(f"  New Reserved: {total_reserved}")
        print(f"  Remaining: {project.remaining_budget}")

if __name__ == "__main__":
    fix_budgets()
