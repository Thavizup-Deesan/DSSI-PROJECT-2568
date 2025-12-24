import requests
import json

# กำหนด URL
BASE_URL = 'http://127.0.0.1:8000/api'

# 1. ข้อมูลสำหรับสมัคร Admin Account
# ===================================================================
# เปลี่ยน username ได้ ถ้าซ้ำจะแจ้ง Error
# role สามารถเป็น: 'User', 'Staff', 'Admin'
# ===================================================================
register_data = {
    'username': 'admin01',           # ชื่อผู้ใช้
    'password': 'admin1234',         # รหัสผ่าน
    'role': 'Admin',                 # ประเภท: Admin
    'department': 'ผู้ดูแลระบบ'       # แผนก
}

print("--- 1. ทดสอบสมัครสมาชิก (Register) ---")
try:
    resp = requests.post(f'{BASE_URL}/register/', json=register_data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- 2. ทดสอบเข้าสู่ระบบ (Login) ---")
login_data = {
    'username': 'admin01',
    'password': 'admin1234'
}
try:
    resp = requests.post(f'{BASE_URL}/login/', json=login_data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")

    if resp.status_code == 200:
        print("✅ ล็อกอินสำเร็จ! (พร้อมเอา User ID ไปใช้งานต่อ)")
    else:
        print("❌ ล็อกอินล้มเหลว")

except Exception as e:
    print(f"Error: {e}")