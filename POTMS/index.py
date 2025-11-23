import os
import sys
from django.core.wsgi import get_wsgi_application

# เพิ่ม path ปัจจุบันเพื่อให้หา backend เจอ
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ชี้ไปที่ settings ของคุณ (โฟลเดอร์ backend)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = get_wsgi_application()