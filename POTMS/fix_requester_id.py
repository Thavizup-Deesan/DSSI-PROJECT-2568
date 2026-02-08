"""
สคริปต์แก้ไข requester_id ใน Orders ที่มีปัญหา
รัน: python fix_requester_id.py
"""
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase (ถ้ายังไม่ได้ init)
if not firebase_admin._apps:
    cred = credentials.Certificate('backend/firebase-key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ID ที่ถูกต้อง (จาก User Collection)
CORRECT_USER_ID = "5d3Ui06F02s7KjHfT0hT"  # มีเลข 0 (ศูนย์)

# ID ที่ผิด (ที่ถูกบันทึกใน Orders)
WRONG_USER_ID = "5d3Ui06F02s7KjHfTOhT"    # มีตัว O (โอ)

def fix_requester_ids():
    """แก้ไข requester_id ใน orders ทั้งหมดที่มี ID ผิด"""
    print(f"กำลังค้นหา orders ที่มี requester_id = '{WRONG_USER_ID}'...")
    
    orders_ref = db.collection('orders')
    query = orders_ref.where('requester_id', '==', WRONG_USER_ID).stream()
    
    count = 0
    for doc in query:
        print(f"  แก้ไข order: {doc.id}")
        doc.reference.update({'requester_id': CORRECT_USER_ID})
        count += 1
    
    print(f"\n✅ แก้ไขสำเร็จ {count} รายการ")
    return count

if __name__ == "__main__":
    fix_requester_ids()
