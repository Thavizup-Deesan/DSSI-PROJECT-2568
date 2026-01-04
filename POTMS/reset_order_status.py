"""
Reset Order Status Script
สคริปต์สำหรับ Reset สถานะ Order กลับเป็น ReceivedFromProcurement
"""
import sys
import os

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from backend.firebase_config import db
import datetime

# Order ID ที่ต้องการ Reset
ORDER_ID = 'R7MB3dbbS7w9Fzac6nOC'  # จาก URL ในรูปภาพ

def reset_order_status():
    try:
        # Update สถานะเป็น ReceivedFromProcurement
        db.collection('orders').document(ORDER_ID).update({
            'status': 'ReceivedFromProcurement',  # รับของจากพัสดุแล้ว
            'updated_at': datetime.datetime.now()
        })
        
        print(f"✅ Reset Order {ORDER_ID} เป็นสถานะ 'ReceivedFromProcurement' (รับของจากพัสดุแล้ว) สำเร็จ!")
        print("📌 สามารถกดปุ่ม 'สร้าง Sub-order' ได้แล้ว")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    reset_order_status()
