"""
Script เพื่อรีเซ็ตงบประมาณทุกโครงการ
- ตั้งค่า budget_spent = 0
- ตั้งค่า budget_reserved = 0
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
from pathlib import Path

# กำหนด Path
BASE_DIR = Path(__file__).resolve().parent
KEY_FILE_NAME = 'firebase-key.json'
CERTIFICATE_PATH = os.path.join(BASE_DIR, 'backend', KEY_FILE_NAME)

# Initialize Firebase
cred = credentials.Certificate(CERTIFICATE_PATH)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def reset_all_project_budgets():
    print("🔄 กำลังรีเซ็ตงบประมาณทุกโครงการ...")
    
    # ดึงโครงการทั้งหมด
    projects_ref = db.collection('projects')
    projects = projects_ref.stream()
    
    count = 0
    for project in projects:
        project_id = project.id
        project_data = project.to_dict()
        project_name = project_data.get('project_name', 'Unknown')
        
        # อัปเดตให้ spent และ reserved เป็น 0
        projects_ref.document(project_id).update({
            'budget_spent': 0,
            'budget_reserved': 0
        })
        
        print(f"✅ รีเซ็ต: {project_name}")
        count += 1
    
    print(f"\n🎉 รีเซ็ตเสร็จสิ้น! ทั้งหมด {count} โครงการ")

if __name__ == "__main__":
    confirm = input("⚠️  คุณแน่ใจหรือไม่ว่าต้องการรีเซ็ตงบทุกโครงการ? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_all_project_budgets()
    else:
        print("❌ ยกเลิกการรีเซ็ต")
