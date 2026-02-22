# คู่มือการติดตั้งและใช้งานระบบ POTMS ผ่าน Docker

### ขั้นตอนที่ 1: การเตรียมไฟล์โปรแกรม
ดาวน์โหลดหรือ Clone Source Code ของโครงการลงในเครื่องคอมพิวเตอร์ และเปิด Terminal (หรือ CMD/PowerShell) เข้าไปที่โฟลเดอร์ของโปรเจกต์
```bash
cd path/to/your/project/POTMS
```

### ขั้นตอนที่ 2: การสร้างและรัน Container
ใช้คำสั่ง Docker Compose เพื่อทำการ Build Image และเริ่มการทำงานของ Container ในโหมด Background (ใช้ไฟล์ dev.yml เพื่อรองรับการพัฒนาและ ngrok)
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```
*(ระบบจะทำการดาวน์โหลด Base Image, ติดตั้ง Dependencies จากไฟล์ requirements.txt และเริ่มรันเซิร์ฟเวอร์ Backend, Redis และ ngrok)*

### ขั้นตอนที่ 3: ตรวจสอบสถานะการทำงาน
ตรวจสอบว่า Container กำลังทำงานอยู่หรือไม่ด้วยคำสั่ง:
```bash
docker-compose -f docker-compose.dev.yml ps
```
*(สถานะต้องขึ้นเป็น Up หรือ Running)*

### ขั้นตอนที่ 4: การตั้งค่าฐานข้อมูลครั้งแรก (Database Initialization)
เมื่อรันระบบผ่าน Docker แล้ว จำเป็นต้องสั่งการเข้าไปภายใน Container เพื่อตั้งค่าฐานข้อมูล

**1. การสร้างตารางในฐานข้อมูล (Migrate)**
```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
```

**2. การสร้างไฟล์ Static (Collect Static)**
```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput
```

**3. การสร้างบัญชีผู้ดูแลระบบ (Create Superuser)**
```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```
*(จากนั้นกรอก Username และ Password ตามขั้นตอนที่ปรากฏ)*

### ขั้นตอนที่ 5: การเข้าใช้งานระบบ
เมื่อดำเนินการเสร็จสิ้น สามารถเข้าใช้งานระบบผ่าน Web Browser ได้ที่:
* **หน้าเว็บไซต์หลัก (Local)**: http://localhost:8000
* **หน้าเว็บไซต์หลัก (ngrok)**: [ดู URL ได้จาก ngrok dashboard]
* **หน้าผู้ดูแลระบบ**: http://localhost:8000/admin
* **ngrok Dashboard**: http://localhost:4040 (เพื่อตรวจสอบ public link)

### คำสั่งสำหรับปิดการทำงาน
เมื่อต้องการหยุดการทำงานของระบบ ให้ใช้คำสั่ง:
```bash
docker-compose -f docker-compose.dev.yml down
```
