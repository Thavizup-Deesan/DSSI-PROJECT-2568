import requests
import json

# URL ของ API ที่เราเพิ่งสร้าง
url = 'http://127.0.0.1:8000/api/projects/'

# ข้อมูลที่จะส่งไป (จำลองว่ากรอกมาจากหน้าเว็บ)
data = {
    'project_name': 'โครงการพัฒนา AI ตรวจจับแมว',
    'budget_total': 50000
}

# ยิงข้อมูล (POST)
try:
    response = requests.post(url, json=data)

    print(f"Status Code: {response.status_code}")
    print("Response:", response.json())

    if response.status_code == 201:
        print("✅ สำเร็จ! ข้อมูลถูกส่งไป Firebase แล้ว")
    else:
        print("❌ เกิดข้อผิดพลาด")
except Exception as e:
    print(f"Error: {e}")
    print("อย่าลืม pip install requests นะครับ")