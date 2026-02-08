import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from pathlib import Path

# Setup Firebase (Copy of firebase_config logic but for standalone script)
# Setup Firebase (Copy of firebase_config logic but for standalone script)
BASE_DIR = Path(__file__).resolve().parent # Inside POTMS
KEY_FILE_NAME = 'firebase-key.json'
CERTIFICATE_PATH = os.path.join(BASE_DIR, 'backend', KEY_FILE_NAME)

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(CERTIFICATE_PATH)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Error loading certificate from {CERTIFICATE_PATH}: {e}")
        exit(1)

db = firestore.client()

def seed_products():
    products = [
        {"item_name": "กระดาษ A4 80g (Double A)", "item_code": "P-001", "estimated_price": 135, "standard_unit": "รีม"},
        {"item_name": "กระดาษ A4 70g (Idea)", "item_code": "P-002", "estimated_price": 115, "standard_unit": "รีม"},
        {"item_name": "ปากกาลูกลื่นสีน้ำเงิน (Lancer)", "item_code": "P-003", "estimated_price": 7, "standard_unit": "ด้าม"},
        {"item_name": "ปากกาลูกลื่นสีแดง (Lancer)", "item_code": "P-004", "estimated_price": 7, "standard_unit": "ด้าม"},
        {"item_name": "ปากกาลูกลื่นสีดำ (Lancer)", "item_code": "P-005", "estimated_price": 7, "standard_unit": "ด้าม"},
        {"item_name": "ดินสอไม้ 2B", "item_code": "P-006", "estimated_price": 15, "standard_unit": "กล่อง"},
        {"item_name": "ไส้ดินสอกด 0.5 2B", "item_code": "P-007", "estimated_price": 15, "standard_unit": "หลอด"},
        {"item_name": "ยางลบสีขาว (Staedtler)", "item_code": "P-008", "estimated_price": 10, "standard_unit": "ก้อน"},
        {"item_name": "ไม้บรรทัดเหล็ก 12 นิ้ว", "item_code": "P-009", "estimated_price": 35, "standard_unit": "อัน"},
        {"item_name": "ไม้บรรทัดพลาสติก 12 นิ้ว", "item_code": "P-010", "estimated_price": 15, "standard_unit": "อัน"},
        {"item_name": "กรรไกร 8 นิ้ว", "item_code": "P-011", "estimated_price": 65, "standard_unit": "เล่ม"},
        {"item_name": "คัตเตอร์ใหญ่ L-500", "item_code": "P-012", "estimated_price": 45, "standard_unit": "อัน"},
        {"item_name": "ใบมีดคัตเตอร์ใหญ่ (หลอด)", "item_code": "P-013", "estimated_price": 25, "standard_unit": "หลอด"},
        {"item_name": "เทปใส 1 นิ้ว (36 หลา)", "item_code": "P-014", "estimated_price": 25, "standard_unit": "ม้วน"},
        {"item_name": "เทปกาว 2 หน้า (บาง)", "item_code": "P-015", "estimated_price": 30, "standard_unit": "ม้วน"},
        {"item_name": "กาวแท่ง (Glue Stick) 25g", "item_code": "P-016", "estimated_price": 45, "standard_unit": "แท่ง"},
        {"item_name": "คลิปหนีบกระดาษ (No.1)", "item_code": "P-017", "estimated_price": 15, "standard_unit": "กล่อง"},
        {"item_name": "คลิปดำเบอร์ 110 (เล็ก)", "item_code": "P-018", "estimated_price": 20, "standard_unit": "กล่อง"},
        {"item_name": "คลิปดำเบอร์ 112 (ใหญ่)", "item_code": "P-019", "estimated_price": 35, "standard_unit": "กล่อง"},
        {"item_name": "เครื่องเย็บกระดาษ (Max-10)", "item_code": "P-020", "estimated_price": 120, "standard_unit": "เครื่อง"},
        {"item_name": "ลวดเย็บกระดาษ No.10", "item_code": "P-021", "estimated_price": 10, "standard_unit": "กล่อง"},
        {"item_name": "แฟ้มสันกว้าง 3 นิ้ว (F4)", "item_code": "P-022", "estimated_price": 85, "standard_unit": "แฟ้ม"},
        {"item_name": "ซองจดหมายสีขาว (แพ็ค 50)", "item_code": "P-023", "estimated_price": 55, "standard_unit": "แพ็ค"},
        {"item_name": "ซองเอกสารสีน้ำตาล A4", "item_code": "P-024", "estimated_price": 6, "standard_unit": "ซอง"},
        {"item_name": "สมุดบันทึกปกแข็ง (เล็ก)", "item_code": "P-025", "estimated_price": 45, "standard_unit": "เล่ม"},
        {"item_name": "โพสต์อิท (Post-it) 3x3", "item_code": "P-026", "estimated_price": 45, "standard_unit": "แพ็ค"},
        {"item_name": "เทปลบคำผิด (Correction Tape)", "item_code": "P-027", "estimated_price": 45, "standard_unit": "อัน"},
        {"item_name": "น้ำยาลบคำผิด (Liquid)", "item_code": "P-028", "estimated_price": 35, "standard_unit": "ด้าม"},
        {"item_name": "ปากกาเน้นข้อความ (สีเหลือง)", "item_code": "P-029", "estimated_price": 20, "standard_unit": "ด้าม"},
        {"item_name": "ปากกาไวท์บอร์ด (สีน้ำเงิน)", "item_code": "P-030", "estimated_price": 25, "standard_unit": "ด้าม"},
        {"item_name": "หมึกเติมปริ้นเตอร์ (Epson BK)", "item_code": "IT-001", "estimated_price": 290, "standard_unit": "ขวด"},
        {"item_name": "หมึกเติมปริ้นเตอร์ (Epson C)", "item_code": "IT-002", "estimated_price": 290, "standard_unit": "ขวด"},
        {"item_name": "หมึกเติมปริ้นเตอร์ (Epson M)", "item_code": "IT-003", "estimated_price": 290, "standard_unit": "ขวด"},
        {"item_name": "หมึกเติมปริ้นเตอร์ (Epson Y)", "item_code": "IT-004", "estimated_price": 290, "standard_unit": "ขวด"},
        {"item_name": "เมาส์ไร้สาย (Logitech B175)", "item_code": "IT-005", "estimated_price": 490, "standard_unit": "อัน"},
        {"item_name": "คีย์บอร์ด USB (Logitech K120)", "item_code": "IT-006", "estimated_price": 390, "standard_unit": "อัน"},
        {"item_name": "แฟลชไดรฟ์ 32GB (Sandisk)", "item_code": "IT-007", "estimated_price": 220, "standard_unit": "อัน"},
        {"item_name": "ฮาร์ดดิสก์พกพา 1TB", "item_code": "IT-008", "estimated_price": 1690, "standard_unit": "อัน"},
        {"item_name": "ปลั๊กไฟพ่วง 3 ตา 5 เมตร (Toshino)", "item_code": "IT-009", "estimated_price": 350, "standard_unit": "อัน"},
        {"item_name": "สาย LAN CAT6 (10 เมตร)", "item_code": "IT-010", "estimated_price": 250, "standard_unit": "เส้น"},
        {"item_name": "ถ่าน AA (Alkaline แพ็ค 4)", "item_code": "P-031", "estimated_price": 95, "standard_unit": "แพ็ค"},
        {"item_name": "ถ่าน AAA (Alkaline แพ็ค 4)", "item_code": "P-032", "estimated_price": 95, "standard_unit": "แพ็ค"},
        {"item_name": "กระดาษทิชชู่กล่อง (Scott)", "item_code": "CL-001", "estimated_price": 45, "standard_unit": "กล่อง"},
        {"item_name": "น้ำยาล้างจาน (ถุงเติม)", "item_code": "CL-002", "estimated_price": 55, "standard_unit": "ถุง"},
        {"item_name": "ฟองน้ำล้างจาน 3M", "item_code": "CL-003", "estimated_price": 15, "standard_unit": "อัน"},
        {"item_name": "ถุงขยะดำ 30x40 (แพ็ค)", "item_code": "CL-004", "estimated_price": 45, "standard_unit": "แพ็ค"},
        {"item_name": "ไม้กวาดดอกหญ้า", "item_code": "CL-005", "estimated_price": 80, "standard_unit": "ด้าม"},
        {"item_name": "เก้าอี้พลาสติกมีพนักพิง", "item_code": "FUR-001", "estimated_price": 350, "standard_unit": "ตัว"},
        {"item_name": "โต๊ะพับหน้าขาว 120cm", "item_code": "FUR-002", "estimated_price": 1200, "standard_unit": "ตัว"},
        {"item_name": "พัดลมตั้งโต๊ะ 16 นิ้ว (Hatari)", "item_code": "APP-001", "estimated_price": 890, "standard_unit": "เครื่อง"}
    ]

    collection = db.collection('master_items') # Using 'master_items' to match existing code
    
    print("Start seeding products...")
    batch = db.batch()
    count = 0
    for p in products:
        doc_ref = collection.document()
        p['created_at'] = firestore.SERVER_TIMESTAMP
        batch.set(doc_ref, p)
        count += 1
        if count % 400 == 0: # Batch limit is 500, safe at 400
            batch.commit()
            batch = db.batch()
    
    if count % 400 != 0:
        batch.commit()

    print(f"Seeded {len(products)} products successfully.")

if __name__ == "__main__":
    seed_products()
