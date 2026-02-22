# Technical Data Flow & Failure Analysis Guide (POTMS)

เอกสารนี้แสดงการรับส่งข้อมูลแบบละเอียด (Line-by-Line / Function-to-Function) ระหว่าง Frontend และ Backend เพื่อใช้ในการไล่โค้ดและวิเคราะห์ปัญหา

---

## 1. การสร้างใบสั่งซื้อ (Purchase Order Creation)

### ผังการไหลของข้อมูล
| ลำดับ | ส่วนงาน | ไฟล์ / ฟังก์ชัน | บรรทัดโดยประมาณ | รายละเอียดการรับส่งข้อมูล |
|:---:|:---|:---|:---|:---|
| 1 | **Frontend** | `create_order.html` <br> `submitOrder(true)` | 107-121 | รวบรวมข้อมูลจาก Form (`project_id`, `items`, `order_no`) |
| 2 | **Frontend** | `apiFetch` (POST) | 124-133 | ส่ง JSON Payload ไปยัง `/api/orders/` |
| 3 | **Backend** | `views.py` <br> `PurchaseOrderAPIView.post` | 660-683 | ตรวจสอบสิทธิ์ (is_officer/participant) และสถานะโครงการ |
| 4 | **Backend** | `views.py` | 705-709 | **Validation:** เช็ค `total > project.remaining_budget`. ถ้าจริงจะคืน Error 400 |
| 5 | **Backend** | `views.py` | 714-731 | **DB Write:** สร้าง `PurchaseOrder` และ `OrderItem` ภายใน `atomic transaction` |
| 6 | **Backend** | `views.py` <br> `update_project_budget` | 735 | เรียกฟังก์ชันคำนวณงบประมาณใหม่ เพื่อ "กั้นเงิน" (Reserved) |

### กรณีฟังก์ชันหายไปจะเกิดอะไรขึ้น? (Failure Analysis)
- **หากบรรทัด 706-709 (Check Budget) หายไป:** ผู้ใช้จะสามารถสั่งซื้อของเกินงบที่มีอยู่ได้ (Budget Overrun) ซึ่งเป็นความเสี่ยงสูงสุดทางการเงิน
- **หากบรรทัด 735 (update_project_budget) หายไป:** ใบสั่งซื้อถูกสร้างสำเร็จ แต่ยอดงบคงเหลือในโครงการจะไม่ถูกหักออก ทำให้ผู้ใช้คนอื่นยังเห็นว่างบยังมีอยู่และสั่งของซ้อนกันได้

---

## 2. การบันทึกรับของ (Partial Receive)

### ผังการไหลของข้อมูล
| ลำดับ | ส่วนงาน | ไฟล์ / ฟังก์ชัน | บรรทัดโดยประมาณ | รายละเอียดการรับส่งข้อมูล |
|:---:|:---|:---|:---|:---|
| 1 | **Frontend** | `partial_receive.html` <br> `createReceive()` | 193-247 | เตรียม `FormData` เพราะมีการแนบไฟล์ (Receipt File) และ Qty ที่รับจริง |
| 2 | **Frontend** | `fetch` (POST) | 250-256 | ส่ง `multipart/form-data` ไปยัง `/api/partial-receives/` |
| 3 | **Backend** | `views.py` <br> `PartialReceiveAPIView.post` | 1146-1180 | บันทึกไฟล์ลง Storage และสร้าง `PartialReceive` record (Status: `Pending_Inspection`) |
| 4 | **Backend** | `views.py` | 1184-1210 | วนลูปสร้าง `PartialReceiveItem` ตามรายการที่ส่งมาจากหน้าบ้าน |

### กรณีฟังก์ชันหายไปจะเกิดอะไรขึ้น?
- **หากการบันทึก File (บรรทัด 1165) ล้มเหลว:** ระบบจะไม่สามารถตรวจสอบหลักฐานใบเสร็จในภายหลังได้ (Audit Trail หาย)
- **หากไม่มีการสร้าง record ในบรรทัด 1184:** ระบบจะรู้ว่ามีการรับของ แต่ไม่รู้ว่า "รับอะไรมาบ้าง" ทำให้กรรมการตรวจรับงานไม่ได้

---

## 3. การตรวจรับพัสดุ (Inspection)

### ผังการไหลของข้อมูล
| ลำดับ | ส่วนงาน | ไฟล์ / ฟังก์ชัน | บรรทัดโดยประมาณ | รายละเอียดการรับส่งข้อมูล |
|:---:|:---|:---|:---|:---|
| 1 | **Frontend** | `order_detail.html` <br> `submitInspection()` | 289-298 | ส่ง `receive_id` และผลการตรวจ (`Pass`/`Reject`) ไปยัง `/api/inspections/` |
| 2 | **Backend** | `views.py` <br> `InspectionAPIView.post` | 1319-1330 | **Logic:** อัปเดตสถานะใบรับของเป็น `Inspected` (ถ้าผ่าน) หรือ `Rejected` (ถ้าไม่ผ่าน) |
| 3 | **Backend** | `views.py` | 1342-1364 | ตรวจสอบว่าถ้าเป็นการรับของ "งวดสุดท้าย" (ครบตาม PO) จะเปลี่ยนสถานะ PO เป็น `Completed` |

### กรณีฟังก์ชันหายไปจะเกิดอะไรขึ้น?
- **หากฟังก์ชัน Inspection หายไป:** ระบบจะไม่รู้คุณภาพของที่ได้รับ ทำให้กระบวนการ "ตั้งเบิกจ่าย" (Payment) ทำไม่ได้ เพราะระบบจะจ่ายเงินได้เฉพาะของที่ "ตรวจผ่าน" แล้วเท่านั้น

---

## 4. การตั้งเบิกจ่ายเงิน (Payment & Budget Settlement)

### ผังการไหลของข้อมูล
| ลำดับ | ส่วนงาน | ไฟล์ / ฟังก์ชัน | บรรทัดโดยประมาณ | รายละเอียดการรับส่งข้อมูล |
|:---:|:---|:---|:---|:---|
| 1 | **Frontend** | `payment.html` <br> `createPayment()` | 84-98 | ส่ง `order_id` และ `amount_paid` (ยอดเงินที่จะจ่ายรอบนี้) |
| 2 | **Backend** | `views.py` <br> `PaymentAPIView.post` | 1411-1430 | **Logic ใหม่:** คำนวณ `suggested_amount` จากยอดของที่ "ตรวจผ่านแล้ว" หักด้วย "ยอดที่เคยจ่ายไปแล้ว" |
| 3 | **Backend** | `views.py` | 1450-1460 | บันทึกรายการ `Payment` (Status: `Processing`) |
| 4 | **Backend** | `views.py` | 1464 | เรียก `update_project_budget(order.project)` เพื่อปรับปรุงยอดงบประมาณ |

### กรณีฟังก์ชันหายไปจะเกิดอะไรขึ้น?
- **หากการคำนวณ suggested_amount (บรรทัด 1411-1430) ผิดพลาด:** เจ้าหน้าที่จะเบิกเงินเกินมูลค่าของที่ได้รับจริง (ผิดระเบียบการเงิน)
- **หากลืมเรียก update_project_budget (บรรทัด 1464):** งบประมาณในโครงการจะไม่ถูกปรับปรุงยอดจอง (Reserved) ทำให้ยอดเงินคงเหลือไม่สะท้อนความเป็นจริงหลังจ่ายเงินไปแล้ว

---

## สรุปจุดเชื่อมต่อสำคัญ (The Golden Rule)
> **"จ่ายเงิน (Payment) ตามการตรวจรับ (Inspection) และคืนเงินเหลือ (Budget Release) เมื่อจบงาน (Completed)"**

- ถ้า **Inspection** ไม่ทำงาน -> **Payment** จะไม่มีข้อมูลไปจ่าย
- ถ้า **Payment** ไม่ทำงาน -> **Budget** จะถูกจอง (Reserved) ค้างไว้ตลอดกาล (เงินจม)
- ถ้า **update_project_budget** ไม่ทำงาน -> **Dashboard** จะแสดงยอดเงินผิดพลาด
