from django.core.management.base import BaseCommand
from api.models import User, Project, MainOrder, OrderItem
from backend.firebase_config import db
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Migrate data from Firebase Firestore to PostgreSQL'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting migration from Firebase...'))
        
        self.migrate_users()
        self.migrate_projects()
        self.migrate_orders()
        
        self.stdout.write(self.style.SUCCESS('Migration completed successfully!'))

    def migrate_users(self):
        self.stdout.write('Migrating Users...')
        users_ref = db.collection('users').stream()
        count = 0
        for doc in users_ref:
            data = doc.to_dict()
            firestore_id = doc.id
            username = data.get('username')
            
            # Skip if username missing
            if not username:
                continue
                
            # Check if user exists by username OR firestore_id
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'firestore_id': firestore_id,
                    'role': data.get('role', 'User'),
                    'department': data.get('department', ''),
                    'password': data.get('password', '') # Already hashed from Firebase
                }
            )
            
            if not created:
                # Update existing user if needed, but preserve ID
                user.firestore_id = firestore_id
                if not user.password and data.get('password'):
                     user.password = data.get('password')
                user.save()
            
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Migrated {count} users.'))

    def migrate_projects(self):
        self.stdout.write('Migrating Projects...')
        projects_ref = db.collection('projects').stream()
        count = 0
        for doc in projects_ref:
            data = doc.to_dict()
            firestore_id = doc.id
            
            project, created = Project.objects.get_or_create(
                firestore_id=firestore_id,
                defaults={
                    'project_name': data.get('project_name', 'Untitled Project'),
                    'project_code': data.get('project_code'),
                    'budget_total': data.get('budget_total', 0),
                    'budget_reserved': data.get('budget_reserved', 0),
                    'budget_spent': data.get('budget_spent', 0),
                    'status': data.get('status', 'Active')
                }
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Migrated {count} projects.'))

    def migrate_orders(self):
        self.stdout.write('Migrating Orders...')
        orders_ref = db.collection('orders').stream()
        count = 0
        
        # Cache users and projects for faster lookup
        users_map = {u.firestore_id: u for u in User.objects.all() if u.firestore_id}
        projects_map = {p.firestore_id: p for p in Project.objects.all() if p.firestore_id}

        for doc in orders_ref:
            data = doc.to_dict()
            firestore_id = doc.id
            
            # Resolve Relationships
            requester_id = data.get('requester_id')
            project_id = data.get('project_id')
            
            requester = users_map.get(requester_id)
            project = projects_map.get(project_id)
            
            if not requester or not project:
                self.stdout.write(self.style.ERROR(f'Skipping Order {firestore_id}: Missing requester ({requester_id}) or project ({project_id})'))
                continue

            # Create Main Order
            order, created = MainOrder.objects.get_or_create(
                firestore_id=firestore_id,
                defaults={
                    'order_no': data.get('order_no') or f"ORD-{firestore_id[:6].upper()}",
                    'project': project,
                    'requester': requester,
                    'vendor_name': data.get('vendor_name', ''),
                    'status': data.get('status', 'Draft'),
                    'total_estimated_price': data.get('total_estimated_price', 0),
                    'staff_note': data.get('staff_note', ''),
                    # Add created_at handling if needed 
                }
            )
            
            # Migrate Order Items
            items = data.get('items', [])
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    item_name=item.get('item_name') or item.get('name', 'Unknown Item'),
                    quantity_requested=item.get('quantity_requested') or item.get('quantity', 1),
                    unit=item.get('unit', 'ea'),
                    estimated_unit_price=item.get('estimated_unit_price') or item.get('unit_price', 0),
                    product_link=item.get('product_link', ''),
                    remarks=item.get('remarks', ''),
                    status=item.get('status', 'Pending')
                )
            
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Migrated {count} orders.'))
