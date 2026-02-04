# 🔐 Authentication System - อธิบาย Syntax ทุกบรรทัด

## ไฟล์: `api/views.py` (บรรทัด 1-65)

---

## บรรทัด 1-11: Import Libraries

```python
from django.contrib.auth.hashers import make_password, check_password
```
**อธิบาย:**
- `from ... import ...` = นำเข้า function จาก module อื่น
- `django.contrib.auth.hashers` = module ที่ Django มีให้สำหรับจัดการ password
- `make_password` = function สร้าง hash จาก password ธรรมดา
- `check_password` = function เปรียบเทียบ password กับ hash

```python
from rest_framework.views import APIView
```
**อธิบาย:**
- `rest_framework` = Django REST Framework library
- `APIView` = class พื้นฐานสำหรับสร้าง API endpoint

```python
from rest_framework.response import Response
```
**อธิบาย:**
- `Response` = class สำหรับส่ง HTTP response กลับไป

```python
from rest_framework import status
```
**อธิบาย:**
- `status` = module ที่มี HTTP status codes เช่น `status.HTTP_200_OK`, `status.HTTP_404_NOT_FOUND`

```python
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
```
**อธิบาย:**
- `IsAuthenticated` = permission ที่ต้อง login ก่อนถึงจะเข้าถึงได้
- `AllowAny` = permission ที่ใครก็เข้าถึงได้
- `BasePermission` = class พื้นฐานสำหรับสร้าง permission เอง

```python
from backend.firebase_config import db
```
**อธิบาย:**
- `backend.firebase_config` = ไฟล์ที่เราสร้างไว้
- `db` = Firestore database client ที่ export มาจากไฟล์นั้น

```python
import datetime
```
**อธิบาย:**
- `datetime` = module สำหรับจัดการวันที่และเวลา

```python
from django.shortcuts import render
```
**อธิบาย:**
- `render` = function สำหรับ render HTML template

```python
import pandas as pd
```
**อธิบาย:**
- `pandas` = library สำหรับจัดการข้อมูลตาราง
- `as pd` = ตั้งชื่อย่อเป็น `pd` เพื่อใช้งานง่าย

```python
from django_ratelimit.decorators import ratelimit
```
**อธิบาย:**
- `ratelimit` = decorator สำหรับจำกัดจำนวน request ต่อเวลา

```python
from django.utils.decorators import method_decorator
```
**อธิบาย:**
- `method_decorator` = function สำหรับใช้ decorator กับ class method

---

## บรรทัด 28-65: IsStaff Permission Class

```python
class IsStaff(BasePermission):
```
**อธิบาย:**
- `class` = ประกาศ class ใหม่
- `IsStaff` = ชื่อ class
- `(BasePermission)` = สืบทอด (inherit) จาก BasePermission

```python
    def has_permission(self, request, view):
```
**อธิบาย:**
- `def` = ประกาศ function
- `has_permission` = ชื่อ method ที่ DRF จะเรียกเพื่อตรวจสอบ permission
- `self` = reference ถึง object ตัวเอง (Python convention)
- `request` = HTTP request object
- `view` = view ที่กำลังเรียก

```python
        auth_header = request.headers.get('Authorization', '')
```
**อธิบาย:**
- `request.headers` = dictionary ของ HTTP headers
- `.get('Authorization', '')` = ดึงค่า 'Authorization' header, ถ้าไม่มีให้ return ''
- `auth_header` = เก็บผลลัพธ์ในตัวแปร

```python
        if auth_header.startswith('Bearer '):
```
**อธิบาย:**
- `if` = เงื่อนไข
- `.startswith('Bearer ')` = ตรวจสอบว่า string ขึ้นต้นด้วย 'Bearer ' หรือไม่
- `Bearer ` = รูปแบบมาตรฐานของ JWT token header

```python
            token = auth_header.split(' ')[1]
```
**อธิบาย:**
- `.split(' ')` = แยก string ด้วย space เป็น list เช่น `['Bearer', 'abc123']`
- `[1]` = เอาตัวที่ 2 (index 1) คือ token

```python
            try:
```
**อธิบาย:**
- `try:` = เริ่ม block ที่อาจเกิด error

```python
                from rest_framework_simplejwt.tokens import AccessToken
```
**อธิบาย:**
- Import AccessToken class สำหรับ decode JWT
- Import ข้างใน function เพื่อลด startup time

```python
                decoded = AccessToken(token)
```
**อธิบาย:**
- สร้าง object AccessToken จาก token string
- ถ้า token ไม่ valid จะ throw exception

```python
                user_id = decoded.get('user_id')
```
**อธิบาย:**
- `.get('user_id')` = ดึง claim 'user_id' จาก JWT payload

```python
                user_doc = db.collection('users').document(user_id).get()
```
**อธิบาย:**
- `db.collection('users')` = เข้าถึง collection 'users' ใน Firestore
- `.document(user_id)` = เข้าถึง document ที่มี ID = user_id
- `.get()` = ดึงข้อมูล document

```python
                if user_doc.exists:
```
**อธิบาย:**
- `.exists` = property ที่บอกว่า document มีอยู่จริงหรือไม่

```python
                    user_data = user_doc.to_dict()
```
**อธิบาย:**
- `.to_dict()` = แปลง document เป็น Python dictionary

```python
                    if user_data.get('role', '').lower() == 'staff':
```
**อธิบาย:**
- `.get('role', '')` = ดึง role, ถ้าไม่มีให้ return ''
- `.lower()` = แปลงเป็นตัวพิมพ์เล็ก
- `== 'staff'` = เปรียบเทียบว่าเท่ากับ 'staff' หรือไม่

```python
                        request.user_id = user_id
                        request.user_role = 'Staff'
```
**อธิบาย:**
- แนบข้อมูล user ไปกับ request object
- เพื่อให้ view ใช้งานได้

```python
                        return True
```
**อธิบาย:**
- `return True` = อนุญาตให้เข้าถึง

```python
            except Exception as e:
                pass
```
**อธิบาย:**
- `except` = จับ error ที่เกิดขึ้นใน try block
- `Exception as e` = จับทุกประเภท error, เก็บไว้ในตัวแปร e
- `pass` = ไม่ทำอะไร (ละเลย error)

```python
        return False
```
**อธิบาย:**
- `return False` = ไม่อนุญาต (ถ้าไม่ผ่านเงื่อนไขด้านบน)

---

## บรรทัด 242-280: UserLoginAPIView

```python
class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
```
**อธิบาย:**
- สร้าง API view สำหรับ login
- `permission_classes = [AllowAny]` = ใครก็เรียกได้โดยไม่ต้อง login

```python
    @method_decorator(ratelimit(key='ip', rate='5/m', block=True))
```
**อธิบาย:**
- `@` = decorator syntax
- `method_decorator()` = ทำให้ decorator ใช้กับ method ได้
- `ratelimit()` = จำกัด request
- `key='ip'` = นับตาม IP address
- `rate='5/m'` = 5 ครั้งต่อนาที
- `block=True` = ถ้าเกิน จะ block request

```python
    def post(self, request):
```
**อธิบาย:**
- Handle HTTP POST request

```python
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
```
**อธิบาย:**
- `request.data` = body ของ request (JSON ที่ส่งมา)
- `.get('username', '')` = ดึง username, default = ''
- `.strip()` = ตัด whitespace หัวท้ายออก

```python
        if not username or not password:
            return Response({'error': 'กรุณากรอกข้อมูลให้ครบ'}, status=status.HTTP_400_BAD_REQUEST)
```
**อธิบาย:**
- `if not username` = ถ้า username เป็น '' หรือ None
- `or` = หรือ
- `Response({...}, status=...)` = ส่ง response กลับ
- `status.HTTP_400_BAD_REQUEST` = 400 Bad Request

```python
        users = db.collection('users').where('username', '==', username).limit(1).stream()
```
**อธิบาย:**
- `.where('username', '==', username)` = filter เฉพาะที่ username ตรง
- `.limit(1)` = เอาแค่ 1 record
- `.stream()` = return generator สำหรับวนลูป

```python
        user_doc = next(users, None)
```
**อธิบาย:**
- `next(iterator, default)` = ดึงค่าถัดไปจาก iterator
- ถ้าไม่มี จะ return `None`

```python
        if not check_password(password, user_data.get('password')):
            return Response({'error': 'รหัสผ่านไม่ถูกต้อง'}, status=status.HTTP_401_UNAUTHORIZED)
```
**อธิบาย:**
- `check_password(plain, hashed)` = เปรียบเทียบ password
- `HTTP_401_UNAUTHORIZED` = 401 Unauthorized

```python
        from rest_framework_simplejwt.tokens import RefreshToken
        
        class FakeUser:
            def __init__(self, user_id):
                self.id = user_id
        
        fake_user = FakeUser(user_doc.id)
        refresh = RefreshToken.for_user(fake_user)
```
**อธิบาย:**
- สร้าง class FakeUser เพราะ RefreshToken.for_user() ต้องการ object ที่มี .id
- `user_doc.id` = document ID ของ user ใน Firestore
- `RefreshToken.for_user(user)` = สร้าง refresh token

```python
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
```
**อธิบาย:**
- `.access_token` = ดึง access token จาก refresh token object
- `str()` = แปลงเป็น string

```python
        return Response({
            'message': 'เข้าสู่ระบบสำเร็จ',
            'user': { ... },
            'access_token': access_token,
            'refresh_token': refresh_token
        })
```
**อธิบาย:**
- ส่ง response กลับพร้อมข้อมูล user และ tokens
- Default status = 200 OK
