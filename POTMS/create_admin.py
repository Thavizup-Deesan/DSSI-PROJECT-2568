import os
import django
import sys
import hashlib

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import User

def create_admin():
    uid = 'admin01'
    email = 'admin'
    password = 'admin1234'  # รหัสผ่าน
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        user, created = User.objects.get_or_create(
            uid=uid,
            defaults={
                'email': email,
                'full_name': 'System Admin',
                'department': 'IT Support',
                'password': password_hash,
                'role': 'admin',
                'is_active': True
            }
        )
        
        if not created:
            user.email = email
            user.full_name = 'System Admin'
            user.password = password_hash
            user.role = 'admin'
            user.save()
            print(f"✅ อัพเดทผู้ใช้ '{uid}' เป็น Admin เรียบร้อยแล้ว")
        else:
            print(f"✅ สร้างบัญชี Admin ใหม่: '{uid}' ({email}) เรียบร้อยแล้ว")
        
        print(f"\n📋 ข้อมูลสำหรับ Login:")
        print(f"   Username: admin")
        print(f"   Password: admin1234")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == '__main__':
    create_admin()
