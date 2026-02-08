"""
Script to fix database migration issues
Run with: py fix_database.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

def fix_database():
    print("=" * 50)
    print("Fixing database migration issues...")
    print("=" * 50)
    
    with connection.cursor() as cursor:
        # Drop api tables that are causing conflicts
        tables_to_drop = [
            'delivery_items',
            'delivery_records', 
            'order_images',
            'order_items',
            'orders',
            'master_items',
            'vendors',
            'users',
            'projects',
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
                print(f"✓ Dropped table: {table}")
            except Exception as e:
                print(f"✗ Error dropping {table}: {e}")
        
        # Clear api migrations from django_migrations table
        try:
            cursor.execute("DELETE FROM django_migrations WHERE app = 'api';")
            print("✓ Cleared api migrations from django_migrations")
        except Exception as e:
            print(f"✗ Error clearing migrations: {e}")
    
    print("=" * 50)
    print("Done! Now run:")
    print("  py manage.py migrate")
    print("  py manage.py runserver")
    print("=" * 50)

if __name__ == '__main__':
    fix_database()
