# Use Case Descriptions - POTMS

## Overview

ระบบ POTMS (Purchase Order Tracking Management System) มี Use Case ทั้งหมด 10 ตัว แบ่งเป็น 4 กลุ่ม:

| กลุ่ม | Use Cases |
|-------|-----------|
| Authentication | UC-01, UC-02, UC-03 |
| Master Data (Staff) | UC-04, UC-05 |
| Ordering System (User) | UC-06, UC-07, UC-08 |
| Approval & Inspection (Staff) | UC-09, UC-10 |

---

## UC-01: Login

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-01 |
| **Use Case Name** | Login |
| **Actor** | User, Staff |
| **Description** | ผู้ใช้เข้าสู่ระบบด้วย username และ password |
| **Preconditions** | - ผู้ใช้มีบัญชีอยู่ในระบบ<br>- ผู้ใช้ไม่ได้ login อยู่ |
| **Postconditions** | - ผู้ใช้เข้าสู่ระบบสำเร็จ<br>- ระบบเก็บ session ของผู้ใช้ |

### Main Flow (Basic Flow)
1. ผู้ใช้เข้าหน้า Login
2. ผู้ใช้กรอก Username และ Password
3. ผู้ใช้กดปุ่ม "เข้าสู่ระบบ"
4. ระบบตรวจสอบข้อมูลกับฐานข้อมูล
5. ระบบเก็บข้อมูลผู้ใช้ใน localStorage
6. ระบบ redirect ไปหน้า Dashboard ตาม role:
   - User → User Dashboard
   - Staff → Staff Dashboard

### Alternative Flow
- **AF-1**: ถ้า username/password ไม่ถูกต้อง
  - ระบบแสดง error "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
  - กลับไปขั้นตอนที่ 2

### Exception Flow
- **EF-1**: ไม่สามารถเชื่อมต่อ Server ได้
  - ระบบแสดง error "ไม่สามารถเชื่อมต่อ Server ได้"

---

## UC-02: Register

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-02 |
| **Use Case Name** | Register |
| **Actor** | User |
| **Description** | ผู้ใช้ใหม่สมัครสมาชิกเข้าสู่ระบบ |
| **Preconditions** | - ผู้ใช้ไม่มีบัญชีในระบบ |
| **Postconditions** | - สร้างบัญชีใหม่ในฐานข้อมูล<br>- ผู้ใช้สามารถ login ได้ |

### Main Flow
1. ผู้ใช้เข้าหน้า Register
2. ผู้ใช้กรอก Username, Password, Confirm Password, แผนก
3. ผู้ใช้กดปุ่ม "สมัครสมาชิก"
4. ระบบตรวจสอบว่า username ไม่ซ้ำ
5. ระบบตรวจสอบว่า password ตรงกัน
6. ระบบสร้างบัญชีใหม่ในฐานข้อมูล (role = "User")
7. ระบบแสดงข้อความ "สมัครสมาชิกสำเร็จ"
8. ระบบ redirect ไปหน้า Login

### Alternative Flow
- **AF-1**: ถ้า username ซ้ำ
  - ระบบแสดง error "ชื่อผู้ใช้นี้มีอยู่แล้ว"
- **AF-2**: ถ้า password ไม่ตรงกัน
  - ระบบแสดง error "รหัสผ่านไม่ตรงกัน"

---

## UC-03: Logout

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-03 |
| **Use Case Name** | Logout |
| **Actor** | User, Staff |
| **Description** | ผู้ใช้ออกจากระบบ |
| **Preconditions** | - ผู้ใช้ login อยู่ในระบบ |
| **Postconditions** | - ล้าง session ของผู้ใช้<br>- ผู้ใช้ถูก redirect ไปหน้า Login |

### Main Flow
1. ผู้ใช้กดปุ่ม "ออกจากระบบ"
2. ระบบล้างข้อมูลใน localStorage
3. ระบบ redirect ไปหน้า Login

---

## UC-04: Manage Projects (Create/Edit/Delete)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-04 |
| **Use Case Name** | Manage Projects |
| **Actor** | Staff |
| **Description** | Staff จัดการข้อมูลโครงการ (สร้าง, แก้ไข, ลบ) |
| **Preconditions** | - Staff login อยู่ในระบบ |
| **Postconditions** | - ข้อมูลโครงการถูกบันทึก/แก้ไข/ลบ ในฐานข้อมูล |

### Main Flow (สร้างโครงการ)
1. Staff เข้าหน้าจัดการโครงการ
2. Staff กดปุ่ม "เพิ่มโครงการใหม่"
3. ระบบแสดง Modal กรอกข้อมูล
4. Staff กรอก ชื่อโครงการ, งบประมาณ, สถานะ
5. Staff กดปุ่ม "บันทึก"
6. ระบบบันทึกข้อมูลลงฐานข้อมูล (projects collection)
7. ระบบแสดงข้อความ "บันทึกสำเร็จ"
8. ระบบ refresh ตาราง

### Alternative Flow (แก้ไขโครงการ)
1. Staff กดปุ่ม "แก้ไข" ที่โครงการที่ต้องการ
2. ระบบแสดง Modal พร้อมข้อมูลเดิม
3. Staff แก้ไขข้อมูล
4. Staff กดปุ่ม "บันทึก"
5. ระบบอัปเดตข้อมูลในฐานข้อมูล

### Alternative Flow (ลบโครงการ)
1. Staff กดปุ่ม "ลบ" ที่โครงการที่ต้องการ
2. ระบบแสดง Confirm Dialog
3. Staff กด "ยืนยัน"
4. ระบบลบข้อมูลจากฐานข้อมูล

---

## UC-05: Import Project Data (Excel/CSV)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-05 |
| **Use Case Name** | Import Project Data |
| **Actor** | Staff |
| **Description** | Staff นำเข้าข้อมูลโครงการจากไฟล์ Excel หรือ CSV |
| **Preconditions** | - Staff login อยู่ในระบบ<br>- มีไฟล์ Excel/CSV ที่มีรูปแบบถูกต้อง |
| **Postconditions** | - ข้อมูลโครงการถูกบันทึกลงฐานข้อมูล |

### Main Flow
1. Staff เข้าหน้าจัดการโครงการ
2. Staff กดปุ่ม "นำเข้าข้อมูล"
3. ระบบแสดง Modal สำหรับ upload ไฟล์
4. Staff เลือกไฟล์ Excel/CSV
5. Staff กดปุ่ม "นำเข้า"
6. ระบบอ่านข้อมูลจากไฟล์
7. ระบบบันทึกข้อมูลทีละรายการลงฐานข้อมูล
8. ระบบแสดงผลลัพธ์ (สำเร็จ X รายการ, ล้มเหลว X รายการ)

### Exception Flow
- **EF-1**: รูปแบบไฟล์ไม่ถูกต้อง
  - ระบบแสดง error "รูปแบบไฟล์ไม่ถูกต้อง"

---

## UC-06: Select Project

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-06 |
| **Use Case Name** | Select Project |
| **Actor** | User |
| **Description** | User เลือกโครงการที่ต้องการสั่งซื้อ |
| **Preconditions** | - User login อยู่ในระบบ<br>- User ถูก assign โครงการแล้ว |
| **Postconditions** | - User เลือกโครงการสำเร็จ<br>- ระบบ redirect ไปหน้าสร้างใบสั่งซื้อ |

### Main Flow
1. User เข้าหน้าเลือกโครงการ
2. ระบบแสดงรายการโครงการที่ User ถูก assign
3. User กรองหรือค้นหาโครงการ (optional)
4. User กดปุ่ม "เลือกโครงการ"
5. ระบบเก็บ project_id ไว้
6. ระบบ redirect ไปหน้าสร้างใบสั่งซื้อ พร้อม project_id

### Alternative Flow
- **AF-1**: ไม่มีโครงการที่ถูก assign
  - ระบบแสดงข้อความ "ยังไม่มีโครงการที่รับผิดชอบ"

---

## UC-07: Create Order (Create/Edit Draft)

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-07 |
| **Use Case Name** | Create Order |
| **Actor** | User |
| **Description** | User สร้างใบสั่งซื้อใหม่หรือแก้ไข Draft |
| **Preconditions** | - User login อยู่ในระบบ<br>- User เลือกโครงการแล้ว |
| **Postconditions** | - ใบสั่งซื้อถูกบันทึก (Draft หรือ Ordered) |

### Main Flow (สร้างใบสั่งซื้อ)
1. ระบบแสดงหน้าสร้างใบสั่งซื้อ พร้อมข้อมูลโครงการ
2. User กรอกข้อมูล:
   - เรื่อง (order_title)
   - รายละเอียด (order_description)
   - วันที่ต้องการใช้งาน (required_date)
   - ชื่อร้านค้า (vendor_name)
3. User เพิ่มรายการพัสดุ:
   - ชื่อสินค้า (item_name)
   - จำนวน (quantity_requested)
   - หน่วย (unit)
   - ราคาต่อหน่วย (estimated_unit_price)
4. ระบบคำนวณยอดรวมอัตโนมัติ
5. User กดปุ่ม "บันทึกฉบับร่าง"
6. ระบบบันทึกข้อมูลลง orders collection (status = "Draft")
7. ระบบแสดงข้อความ "บันทึกสำเร็จ"

### Alternative Flow (ส่งสั่งซื้อ)
1. User กดปุ่ม "ส่งเพื่อขออนุมัติ"
2. ระบบตรวจสอบงบประมาณคงเหลือ
3. ถ้างบประมาณพอ: status = "Ordered"
4. ระบบแจ้งเตือน Staff

### Exception Flow
- **EF-1**: งบประมาณไม่พอ
  - ระบบแสดง error "งบประมาณไม่เพียงพอ"

---

## UC-08: View My Orders

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-08 |
| **Use Case Name** | View My Orders |
| **Actor** | User |
| **Description** | User ดูรายการสั่งซื้อทั้งหมดของตัวเอง |
| **Preconditions** | - User login อยู่ในระบบ |
| **Postconditions** | - แสดงรายการสั่งซื้อของ User |

### Main Flow
1. User เข้าหน้ารายการใบขอซื้อ
2. ระบบดึงข้อมูล orders ที่ requester_id = user.id
3. ระบบแสดงตารางรายการ:
   - เลขที่ใบขอซื้อ (order_no)
   - วันที่ (created_at)
   - เรื่อง (order_title)
   - หมายเลขโครงการ (project_id)
   - สถานะ (status)
4. User กรองตามสถานะหรือวันที่ (optional)
5. User กดปุ่ม "ดูรายละเอียด" เพื่อดูรายละเอียด

### Alternative Flow
- **AF-1**: ไม่มีรายการ
  - ระบบแสดงข้อความ "ยังไม่มีรายการใบขอซื้อ"

---

## UC-09: Review & Approve Order

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-09 |
| **Use Case Name** | Review & Approve Order |
| **Actor** | Staff |
| **Description** | Staff ตรวจสอบและอนุมัติใบสั่งซื้อ |
| **Preconditions** | - Staff login อยู่ในระบบ<br>- มีใบสั่งซื้อ status = "Ordered" |
| **Postconditions** | - status = "Approved" หรือ "CorrectionNeeded" |

### Main Flow (อนุมัติ)
1. Staff เข้าหน้าตรวจสอบใบสั่งซื้อ
2. ระบบแสดงรายการใบสั่งซื้อที่รออนุมัติ
3. Staff กดปุ่ม "ดูรายละเอียด"
4. ระบบแสดงรายละเอียดใบสั่งซื้อ
5. Staff ตรวจสอบข้อมูล
6. Staff กดปุ่ม "อนุมัติ"
7. ระบบอัปเดต status = "Approved"
8. ระบบอัปเดต approver_id = staff.id
9. ระบบแจ้งเตือน User

### Alternative Flow (ส่งกลับแก้ไข)
1. Staff กดปุ่ม "ส่งกลับแก้ไข"
2. Staff กรอก staff_note
3. ระบบอัปเดต status = "CorrectionNeeded"
4. ระบบแจ้งเตือน User

---

## UC-10: Inspect & Receive Items

| รายการ | รายละเอียด |
|--------|------------|
| **Use Case ID** | UC-10 |
| **Use Case Name** | Inspect & Receive Items |
| **Actor** | Staff |
| **Description** | Staff ตรวจรับพัสดุและบันทึกการรับของ |
| **Preconditions** | - Staff login อยู่ในระบบ<br>- มีใบสั่งซื้อ status = "Approved"<br>- สินค้าถูกจัดส่งแล้ว |
| **Postconditions** | - สร้าง SubOrder และ InspectionDetail<br>- อัปเดตสถานะรายการสินค้า |

### Main Flow
1. Staff เข้าหน้าตรวจรับพัสดุ
2. ระบบแสดงรายการใบสั่งซื้อที่รอตรวจรับ
3. Staff เลือกใบสั่งซื้อที่ต้องการตรวจรับ
4. ระบบแสดงรายการสินค้าในใบสั่งซื้อ
5. Staff กรอกข้อมูลการรับ:
   - จำนวนที่รับ (qty_received)
   - ราคาจริงต่อหน่วย (actual_unit_price)
6. Staff กดปุ่ม "บันทึกการตรวจรับ"
7. ระบบสร้าง SubOrder และ InspectionDetail
8. ระบบอัปเดต item status = "Received"
9. ถ้าสินค้าครบ: อัปเดต order status = "Closed"

---

## Status Flow Summary

```
Draft → Ordered → Approved → SentToProcurement → Closed
                ↓
         CorrectionNeeded → Draft (แก้ไขและส่งใหม่)
```

| Status | ความหมาย | ใครเป็นคนเปลี่ยน |
|--------|----------|-----------------|
| Draft | ฉบับร่าง | User |
| Ordered | รออนุมัติ | User |
| Approved | อนุมัติแล้ว | Staff |
| CorrectionNeeded | ต้องแก้ไข | Staff |
| SentToProcurement | จัดส่งแล้ว | Staff |
| Closed | ปิดแล้ว | Staff |
