"""
Firestore to PostgreSQL Migration Script
=========================================
This script migrates data from Firebase Firestore to PostgreSQL.

Usage:
    python migrate_firestore_to_postgres.py

Requirements:
    - Firebase credentials (firebase-key.json)
    - PostgreSQL database configured in Django settings
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import User, Project, Order, OrderItem, Vendor, MasterItem
from backend.firebase_config import db
from django.utils import timezone
from datetime import datetime

def migrate_users():
    """Migrate users from Firestore to PostgreSQL"""
    print("\n=== Migrating Users ===")
    users_ref = db.collection('users')
    count = 0
    
    for doc in users_ref.stream():
        data = doc.to_dict()
        uid = doc.id
        
        try:
            user, created = User.objects.update_or_create(
                uid=uid,
                defaults={
                    'email': data.get('email', f'{uid}@placeholder.com'),
                    'full_name': data.get('name', data.get('full_name', '')),
                    'department': data.get('department', ''),
                    'phone': data.get('phone', ''),
                    'role': data.get('role', 'user'),
                    'is_active': data.get('is_active', True)
                }
            )
            status = "Created" if created else "Updated"
            print(f"  {status}: {user.email}")
            count += 1
        except Exception as e:
            print(f"  Error migrating user {uid}: {e}")
    
    print(f"  Total users migrated: {count}")
    return count

def migrate_projects():
    """Migrate projects from Firestore to PostgreSQL"""
    print("\n=== Migrating Projects ===")
    projects_ref = db.collection('projects')
    count = 0
    
    for doc in projects_ref.stream():
        data = doc.to_dict()
        
        try:
            project, created = Project.objects.update_or_create(
                project_code=data.get('project_code', doc.id),
                defaults={
                    'project_name': data.get('project_name', ''),
                    'budget_total': float(data.get('budget_total', 0)),
                    'budget_used': float(data.get('budget_used', 0)),
                    'status': data.get('status', 'Active')
                }
            )
            status = "Created" if created else "Updated"
            print(f"  {status}: {project.project_code} - {project.project_name}")
            count += 1
        except Exception as e:
            print(f"  Error migrating project {doc.id}: {e}")
    
    print(f"  Total projects migrated: {count}")
    return count

def migrate_orders():
    """Migrate orders from Firestore to PostgreSQL"""
    print("\n=== Migrating Orders ===")
    orders_ref = db.collection('orders')
    count = 0
    
    for doc in orders_ref.stream():
        data = doc.to_dict()
        order_no = data.get('order_no', doc.id)
        
        try:
            # Find related project
            project = None
            project_code = data.get('project_code')
            if project_code:
                project = Project.objects.filter(project_code=project_code).first()
            
            # Find related user
            requester = None
            requester_id = data.get('requester_id')
            if requester_id:
                requester = User.objects.filter(uid=requester_id).first()
            
            # Parse dates
            created_at = data.get('created_at')
            if created_at and hasattr(created_at, 'isoformat'):
                created_at = timezone.make_aware(datetime.fromisoformat(created_at.isoformat().replace('Z', '+00:00')))
            else:
                created_at = timezone.now()
            
            submitted_at = data.get('submitted_at')
            if submitted_at and hasattr(submitted_at, 'isoformat'):
                submitted_at = timezone.make_aware(datetime.fromisoformat(submitted_at.isoformat().replace('Z', '+00:00')))
            else:
                submitted_at = None
            
            # Create or update order
            order, created = Order.objects.update_or_create(
                order_no=order_no,
                defaults={
                    'order_title': data.get('order_title', ''),
                    'project': project,
                    'requester': requester,
                    'requester_name': data.get('requester_name', ''),
                    'vendor_name': data.get('vendor_name', ''),
                    'status': data.get('status', 'Draft'),
                    'total_estimated_price': float(data.get('total_estimated_price', 0)),
                    'required_date': data.get('required_date'),
                    'order_description': data.get('order_description', ''),
                    'staff_note': data.get('staff_note', ''),
                    'submitted_at': submitted_at
                }
            )
            
            # Migrate order items
            items = data.get('items', [])
            if created or not order.items.exists():
                order.items.all().delete()
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        item_name=item.get('item_name', ''),
                        quantity=int(item.get('quantity', 1)),
                        unit=item.get('unit', ''),
                        estimated_unit_price=float(item.get('estimated_unit_price', 0)),
                        quantity_received=int(item.get('quantity_received', 0))
                    )
            
            status = "Created" if created else "Updated"
            print(f"  {status}: {order.order_no} ({len(items)} items)")
            count += 1
        except Exception as e:
            print(f"  Error migrating order {order_no}: {e}")
    
    print(f"  Total orders migrated: {count}")
    return count

def migrate_vendors():
    """Migrate vendors from Firestore to PostgreSQL"""
    print("\n=== Migrating Vendors ===")
    vendors_ref = db.collection('vendors')
    count = 0
    
    for doc in vendors_ref.stream():
        data = doc.to_dict()
        
        try:
            vendor, created = Vendor.objects.update_or_create(
                vendor_name=data.get('vendor_name', doc.id),
                defaults={
                    'phone': data.get('phone', ''),
                    'email': data.get('email', ''),
                    'address': data.get('address', '')
                }
            )
            status = "Created" if created else "Updated"
            print(f"  {status}: {vendor.vendor_name}")
            count += 1
        except Exception as e:
            print(f"  Error migrating vendor {doc.id}: {e}")
    
    print(f"  Total vendors migrated: {count}")
    return count

def migrate_master_items():
    """Migrate master items from Firestore to PostgreSQL"""
    print("\n=== Migrating Master Items ===")
    items_ref = db.collection('master_items')
    count = 0
    
    for doc in items_ref.stream():
        data = doc.to_dict()
        
        try:
            item, created = MasterItem.objects.update_or_create(
                item_code=data.get('item_code', doc.id),
                defaults={
                    'item_name': data.get('item_name', ''),
                    'standard_unit': data.get('standard_unit', data.get('unit', '')),
                    'category': data.get('category', '')
                }
            )
            status = "Created" if created else "Updated"
            print(f"  {status}: {item.item_code} - {item.item_name}")
            count += 1
        except Exception as e:
            print(f"  Error migrating item {doc.id}: {e}")
    
    print(f"  Total items migrated: {count}")
    return count

def main():
    print("=" * 60)
    print("Firestore to PostgreSQL Migration")
    print("=" * 60)
    
    # Run migrations
    user_count = migrate_users()
    project_count = migrate_projects()
    vendor_count = migrate_vendors()
    item_count = migrate_master_items()
    order_count = migrate_orders()
    
    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"  Users:        {user_count}")
    print(f"  Projects:     {project_count}")
    print(f"  Vendors:      {vendor_count}")
    print(f"  Master Items: {item_count}")
    print(f"  Orders:       {order_count}")
    print("\nMigration completed!")

if __name__ == '__main__':
    main()
