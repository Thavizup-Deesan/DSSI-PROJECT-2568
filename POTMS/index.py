import os
from django.core.wsgi import get_wsgi_application

# ชี้ไปที่ settings ของคุณ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()

# ตัวแปรนี้สำคัญมาก Vercel จะมองหาตัวแปรชื่อ 'app'
app = application