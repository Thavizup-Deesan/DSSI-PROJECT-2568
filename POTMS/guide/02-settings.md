# 🔐 Django Settings

## ไฟล์: `backend/settings.py`

อธิบาย configuration หลักของ Django

---

## 1. การ Import และ Path Setup

```python
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
```

| Code | อธิบาย |
|------|--------|
| `Path(__file__)` | Path ของไฟล์ settings.py |
| `.resolve()` | แปลงเป็น absolute path |
| `.parent.parent` | ขึ้น 2 ระดับ (backend/ → POTMS/) |

---

## 2. Security Settings

```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'default-key')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']  # Production ควรระบุ specific hosts
```

| Setting | ความหมาย |
|---------|----------|
| `SECRET_KEY` | กุญแจเข้ารหัส (ต้องเป็นความลับ) |
| `DEBUG` | True=development, False=production |
| `ALLOWED_HOSTS` | Domain ที่อนุญาต |

---

## 3. Installed Apps

```python
INSTALLED_APPS = [
    'django.contrib.admin',        # Admin panel
    'django.contrib.auth',         # Authentication
    'django.contrib.contenttypes', # Content types
    'django.contrib.sessions',     # Sessions
    'django.contrib.messages',     # Messages
    'django.contrib.staticfiles',  # Static files
    'rest_framework',              # DRF
    'corsheaders',                 # CORS
    'django_extensions',           # Extensions
    'api',                         # Our app
]
```

---

## 4. Middleware

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',     # CORS (ต้องอยู่บนสุด)
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware', # ปิดสำหรับ API
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
```

**หมายเหตุ:** CORS middleware ต้องอยู่บนสุดเพื่อจัดการ request ก่อน

---

## 5. REST Framework Config

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}
```

---

## 6. JWT Settings

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

| Setting | ค่า | ความหมาย |
|---------|-----|----------|
| `ACCESS_TOKEN_LIFETIME` | 24 ชม. | Access token หมดอายุ |
| `REFRESH_TOKEN_LIFETIME` | 7 วัน | Refresh token หมดอายุ |
| `AUTH_HEADER_TYPES` | Bearer | รูปแบบ `Authorization: Bearer <token>` |

---

## 7. Static Files

```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

| Setting | ความหมาย |
|---------|----------|
| `STATIC_URL` | URL prefix สำหรับ static files |
| `STATIC_ROOT` | โฟลเดอร์เก็บ collected static files |
| `STATICFILES_STORAGE` | ใช้ WhiteNoise compress และ serve |

---

## 8. Rate Limiting

```python
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_VIEW = 'api.views.ratelimited_view'
```

ป้องกัน brute force โดยจำกัดจำนวน request ต่อนาที
