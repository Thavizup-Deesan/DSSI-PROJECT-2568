# Use Case Descriptions - POTMS

## Overview

ระบบ POTMS (Purchase Order Tracking Management System) มี Use Case ทั้งหมด 15 ตัว แบ่งตาม Actor:

| Actor | Use Cases |
|-------|-----------|
| ทุก Role | UC-01, UC-02, UC-03 (Authentication) |
| ผู้ขอซื้อ (User) | UC-04, UC-05, UC-06, UC-07, UC-08, UC-09, UC-10, UC-12 |
| พัสดุ (Staff) | UC-11 |
| คณะกรรมการตรวจรับ | UC-13 |
| Admin | UC-14 |

### สถานะของใบขอซื้อ (Order Status)

| Status | ความหมาย | ผู้เปลี่ยนสถานะ |
|--------|----------|-----------------|
| Draft | ฉบับร่าง | User |
| รอ | รอหัวหน้าอนุมัติ | User (เมื่อส่งขออนุมัติ) |
| รอรับของ | อนุมัติแล้ว รอรับของ | Staff (หลังหัวหน้าอนุมัติ) |
| รับบางส่วน | รับของบางส่วน | User (เมื่อบันทึกรับของ) |
| รับครบ | รับของครบแล้ว | User (เมื่อรับของครบ) |
| Rejected | ไม่อนุมัติ | Staff (หลังหัวหน้าไม่อนุมัติ) |

### Role ในระบบ

| Role | สิทธิ์การใช้งาน |
|------|----------------|
| user (ผู้ขอซื้อ) | สร้าง/แก้ไขใบขอซื้อ, บันทึกการรับของ |
| staff (พัสดุ) | อัปเดตสถานะ, พิมพ์เอกสาร |
| boss (หัวหน้าภาค) | ดูข้อมูลเหมือน User (อนุมัติแบบ Offline) |
| admin | จัดการบัญชีผู้ใช้ทั้งหมด |

---

## UC-01: Login (เข้าสู่ระบบ)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-01 |
| **Use Case Name** | Login |
| **Actor** | User, Staff, Boss, Admin |
| **Description** | ผู้ใช้เข้าสู่ระบบด้วย username และ password |
| **Preconditions** | - ผู้ใช้มีบัญชีอยู่ในระบบ<br>- ผู้ใช้ไม่ได้ login อยู่ |
| **Postconditions** | - ผู้ใช้เข้าสู่ระบบสำเร็จ<br>- ระบบเก็บ JWT token ใน localStorage |

### Main Flow
1. ผู้ใช้เข้าหน้า `/api/login/`
2. ผู้ใช้กรอก Username และ Password
3. ผู้ใช้กดปุ่ม "เข้าสู่ระบบ"
4. ระบบตรวจสอบข้อมูลกับฐานข้อมูล PostgreSQL
5. ระบบสร้าง JWT token และเก็บใน localStorage
6. ระบบ redirect ตาม role:
   - Admin → `/api/admin/users/page/`
   - อื่นๆ → `/api/dashboard/`

### Alternative Flow
- **AF-1**: ถ้า username/password ไม่ถูกต้อง
  - ระบบแสดง SweetAlert error "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"

---

## UC-02: Register (ลงทะเบียน)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-02 |
| **Use Case Name** | Register |
| **Actor** | ผู้ใช้ใหม่ |
| **Description** | ผู้ใช้ใหม่สมัครสมาชิกเข้าสู่ระบบ (role เริ่มต้น = user) |
| **Preconditions** | - ผู้ใช้ไม่มีบัญชีในระบบ |
| **Postconditions** | - สร้างบัญชีใหม่ (role = user) |

### Main Flow
1. ผู้ใช้เข้าหน้า `/api/register/`
2. ผู้ใช้กรอก Username, Email, ชื่อ-สกุล, แผนก, เบอร์โทร, Password
3. ผู้ใช้กดปุ่ม "สมัครสมาชิก"
4. ระบบตรวจสอบว่า username/email ไม่ซ้ำ
5. ระบบ hash password ด้วย SHA-256
6. ระบบสร้างบัญชีใหม่ (role = "user")
7. ระบบ redirect ไปหน้า Login

---

## UC-03: Logout (ออกจากระบบ)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-03 |
| **Use Case Name** | Logout |
| **Actor** | ทุก Role |
| **Description** | ผู้ใช้ออกจากระบบ |
| **Postconditions** | - ล้าง localStorage<br>- ผู้ใช้ถูก redirect ไปหน้า Login |

### Main Flow
1. ผู้ใช้กดปุ่ม "ออกจากระบบ" ที่ Sidebar
2. ระบบแสดง Confirm Dialog (SweetAlert)
3. ผู้ใช้กด "ยืนยัน"
4. ระบบล้าง localStorage และ redirect ไปหน้า Login

---

## UC-04: Select Project (เลือกโครงการ)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-04 |
| **Use Case Name** | Select Project |
| **Actor** | ผู้ขอซื้อ (User) |
| **Description** | User เลือกประเภท (พัสดุ/ครุภัณฑ์) และโครงการก่อนสร้างใบขอซื้อ |
| **Postconditions** | - ระบบ redirect ไปหน้าสร้างใบขอซื้อพร้อม project_id |

### Main Flow
1. User เข้าหน้า Dashboard
2. User กดเลือก "พัสดุ" หรือ "ครุภัณฑ์"
3. ระบบ redirect ไป `/api/projects/select/?type=พัสดุ|ครุภัณฑ์`
4. ระบบแสดงรายการโครงการพร้อมงบประมาณคงเหลือ
5. User กดเลือกโครงการ
6. ระบบ redirect ไป `/api/orders/create/?project_id=...&type=...`

---

## UC-05: Create Order (สร้างใบขอซื้อ)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-05 |
| **Use Case Name** | Create Order |
| **Actor** | ผู้ขอซื้อ (User) |
| **Description** | User สร้างใบขอซื้อใหม่พร้อมรายการสินค้า |
| **Postconditions** | - ใบขอซื้อถูกบันทึก (status = Draft) |

### Main Flow
1. ระบบแสดงฟอร์มสร้างใบขอซื้อ พร้อมข้อมูลโครงการ
2. ระบบสร้างเลขที่เอกสารอัตโนมัติ (PQ-YYYYMMDD-XXXX หรือ EQ-YYYYMMDD-XXXX)
3. User กรอกข้อมูล:
   - เรื่อง (order_title)
   - ชื่อร้านค้า (vendor_name)
   - วันที่ต้องการใช้งาน (required_date)
   - รายละเอียด (order_description)
4. User เพิ่มรายการสินค้า:
   - ชื่อสินค้า, จำนวน, หน่วย, ราคาประมาณการ
5. ระบบคำนวณยอดรวมอัตโนมัติ
6. User กดปุ่ม "บันทึกร่าง" → status = "Draft"

---

## UC-06: View My Orders (ดูรายการใบขอซื้อ)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-06 |
| **Use Case Name** | View My Orders |
| **Actor** | ผู้ขอซื้อ (User) |
| **Description** | User ดูรายการใบขอซื้อทั้งหมดของตัวเอง |

### Main Flow
1. User เข้าหน้า `/api/orders/my/?type=พัสดุ|ครุภัณฑ์`
2. ระบบแสดงตารางรายการใบขอซื้อ:
   - เลขที่เอกสาร, โครงการ, ร้านค้า, ยอดรวม, วันที่สร้าง, สถานะ
3. User กรองตามสถานะ (Tabs: ทั้งหมด, Draft, รอ, รอรับของ, รับครบ)
4. User กดปุ่ม "ดู" เพื่อดูรายละเอียด

---

## UC-07: Edit Order (แก้ไขใบขอซื้อ)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-07 |
| **Use Case Name** | Edit Order |
| **Actor** | ผู้ขอซื้อ (User) |
| **Description** | User แก้ไขใบขอซื้อที่ยังเป็น Draft |
| **Preconditions** | - status = "Draft" เท่านั้น |

### Main Flow
1. User เข้าหน้ารายละเอียดใบขอซื้อ
2. User กดปุ่ม "แก้ไข"
3. ระบบ redirect ไปหน้า `/api/orders/edit/{order_id}/`
4. User แก้ไขข้อมูลและรายการสินค้า
5. User กดปุ่ม "บันทึก"

---

## UC-08: Submit Order (ส่งขออนุมัติ)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-08 |
| **Use Case Name** | Submit Order |
| **Actor** | ผู้ขอซื้อ (User) |
| **Description** | User ส่งใบขอซื้อเพื่อขออนุมัติจากหัวหน้าภาค |
| **Postconditions** | - status = "รอ"<br>- ระบบสร้าง QR Code อัตโนมัติ |

### Main Flow
1. User เข้าหน้าสร้าง/แก้ไขใบขอซื้อ
2. User กดปุ่ม "ส่งขออนุมัติ"
3. ระบบแสดง Confirm Dialog
4. ระบบบันทึก submitted_at = now()
5. ระบบเปลี่ยน status เป็น "รอ"
6. ระบบสร้าง QR Code สำหรับสแกนดูรายการ

---

## UC-09: Record Receiving (บันทึกการรับของ)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-09 |
| **Use Case Name** | Record Receiving |
| **Actor** | ผู้ขอซื้อ (User) |
| **Description** | User บันทึกจำนวนสินค้าที่รับ (หลังคณะกรรมการตรวจรับแบบ Offline) |
| **Preconditions** | - status = "รอรับของ" หรือ "รับบางส่วน" |

### Main Flow
1. User เข้าหน้ารายละเอียดใบขอซื้อ
2. User กดปุ่ม "บันทึกรับของ"
3. ระบบแสดง Modal ให้กรอกจำนวนที่รับในแต่ละรายการ
4. User กรอกจำนวนและหมายเหตุ
5. User กดปุ่ม "บันทึก"
6. ระบบสร้าง DeliveryRecord และ DeliveryItem
7. ระบบอัปเดต quantity_received ใน OrderItem
8. ถ้ารับครบทุกรายการ: status = "รับครบ"
9. ถ้ารับบางส่วน: status = "รับบางส่วน"

---

## UC-10: Order History (ประวัติใบขอซื้อ)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-10 |
| **Use Case Name** | Order History |
| **Actor** | ผู้ขอซื้อ (User) |
| **Description** | User ค้นหาและกรองประวัติใบขอซื้อ |

### Main Flow
1. User เข้าหน้า `/api/orders/history/`
2. User ค้นหาด้วยเลขที่เอกสาร, โครงการ, วันที่
3. User กรองตามสถานะ
4. User ดูรายละเอียดใบขอซื้อ

---

## UC-11: Update Approval Status (อัปเดตสถานะอนุมัติ)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-11 |
| **Use Case Name** | Update Approval Status |
| **Actor** | พัสดุ (Staff) |
| **Description** | Staff อัปเดตสถานะใบขอซื้อหลังหัวหน้าอนุมัติ (Offline Process) |

### Main Flow
1. Staff เข้าหน้า `/api/staff/dashboard/`
2. Staff เลือกใบขอซื้อที่ต้องการอัปเดต
3. Staff กดเลือกสถานะใหม่:
   - "รอรับของ" (หัวหน้าอนุมัติ)
   - "Rejected" (หัวหน้าไม่อนุมัติ พร้อมเหตุผล)
4. ระบบบันทึกสถานะใหม่

---

## UC-12: Upload Order Images (อัปโหลดรูปภาพประกอบ)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-12 |
| **Use Case Name** | Upload Order Images |
| **Actor** | ผู้ขอซื้อ (User) |
| **Description** | User อัปโหลดรูปภาพประกอบใบขอซื้อ (เช่น ใบเสร็จ, รูปสินค้า) |

### Main Flow
1. User เข้าหน้ารายละเอียดใบขอซื้อ
2. User กดปุ่ม "อัปโหลดรูปภาพ"
3. User เลือกไฟล์รูปภาพ (jpg, png)
4. User กรอกคำอธิบาย (optional)
5. User กดปุ่ม "บันทึก"
6. ระบบสร้าง OrderImage record
7. ระบบแสดงรูปภาพที่อัปโหลดในหน้ารายละเอียด

---

## UC-13: Scan QR View Items (สแกน QR ดูรายการ)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-13 |
| **Use Case Name** | Scan QR View Items |
| **Actor** | คณะกรรมการตรวจรับ |
| **Description** | คณะกรรมการสแกน QR Code เพื่อดูรายการสินค้า (อ่านอย่างเดียว) |

### Main Flow
1. คณะกรรมการใช้มือถือสแกน QR Code บนเอกสาร
2. ระบบ redirect ไป `/api/orders/scan/{order_id}/`
3. ระบบแสดงรายการสินค้าในใบขอซื้อ
4. คณะกรรมการตรวจนับของจริง (Offline)
5. คณะกรรมการลงนามบนเอกสาร (Offline)

---

## UC-14: Manage Users (จัดการบัญชีผู้ใช้)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-15 |
| **Use Case Name** | Manage Users |
| **Actor** | Admin |
| **Description** | Admin จัดการบัญชีผู้ใช้ทั้งหมดในระบบ |

### Main Flow (ดูรายการ)
1. Admin เข้าหน้า `/api/admin/users/page/`
2. ระบบแสดงตารางผู้ใช้ทั้งหมด
3. Admin ค้นหา/กรองตาม Role

### Alternative Flow (เพิ่มผู้ใช้)
1. Admin กดปุ่ม "เพิ่มผู้ใช้ใหม่"
2. Admin กรอกข้อมูลและเลือก Role
3. Admin กดปุ่ม "บันทึก"

### Alternative Flow (แก้ไข Role)
1. Admin กดปุ่ม "แก้ไข" ที่ผู้ใช้ที่ต้องการ
2. Admin เปลี่ยน Role (user, staff, boss, admin)
3. Admin กดปุ่ม "บันทึก"

### Alternative Flow (รีเซ็ตรหัสผ่าน)
1. Admin กดปุ่ม "รีเซ็ตรหัสผ่าน"
2. Admin กรอกรหัสผ่านใหม่
3. Admin กดปุ่ม "บันทึก"

### Alternative Flow (ลบผู้ใช้)
1. Admin กดปุ่ม "ลบ" ที่ผู้ใช้ที่ต้องการ
2. ระบบแสดง Confirm Dialog
3. Admin กด "ยืนยัน"
4. ระบบลบผู้ใช้จากฐานข้อมูล
