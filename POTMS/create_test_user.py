"""
Script to create test user
Run with: py create_test_user.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import User

def create_test_users():
    print("Creating test users...")
    
    users_data = [
        {
            'uid': 'test_user_1',
            'email': 'user@test.com',
            'full_name': 'ผู้ใช้ทดสอบ',
            'department': 'ภาควิชาวิศวกรรมคอมพิวเตอร์',
            'phone': '0812345678',
            'role': 'user',
        },
        {
            'uid': 'test_staff_1',
            'email': 'staff@test.com',
            'full_name': 'เจ้าหน้าที่พัสดุ',
            'department': 'ฝ่ายพัสดุ',
            'phone': '0823456789',
            'role': 'staff',
        },
        {
            'uid': 'test_boss_1',
            'email': 'boss@test.com',
            'full_name': 'หัวหน้าภาควิชา',
            'department': 'ภาควิชาวิศวกรรมคอมพิวเตอร์',
            'phone': '0834567890',
            'role': 'boss',
        },
    ]
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            uid=user_data['uid'],
            defaults=user_data
        )
        if created:
            print(f"✓ Created: {user.full_name} ({user.email}) - Role: {user.role}")
        else:
            print(f"- Already exists: {user.full_name} ({user.email})")
    
    print("\n" + "=" * 50)
    print("Test Login Credentials:")
    print("=" * 50)
    print("Email: user@test.com (ผู้ขอซื้อ)")
    print("Email: staff@test.com (พัสดุ)")
    print("Email: boss@test.com (หัวหน้าภาควิชา)")
    print("=" * 50)

if __name__ == '__main__':
    create_test_users()
