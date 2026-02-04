# 💰 Budget System - ระบบงบประมาณ

## Logic การจัดการงบประมาณ

---

## โครงสร้างข้อมูลโครงการ

```json
{
  "project_name": "โครงการ ABC",
  "budget": 1000000,          // งบประมาณทั้งหมด
  "reserved_budget": 50000,   // งบที่กันไว้ (รอดำเนินการ)
  "used_budget": 30000,       // งบที่ใช้จริงแล้ว
  "status": "Active"
}
```

**สูตรคำนวณ:**
```
งบคงเหลือ = budget - reserved_budget - used_budget
```

---

## 1. กันวงเงิน (Reserve Budget)

**เมื่อไหร่:** User submit ใบขอซื้อ (status = Pending)

```python
# OrderListCreateAPIView.post()
if order_status == 'Pending':
    db.collection('projects').document(project_id).update({
        'reserved_budget': firestore.Increment(total)
    })
```

**Logic:**
1. User สร้างใบขอซื้อ ยอดรวม 10,000
2. ระบบตรวจสอบว่างบพอหรือไม่
3. ถ้าพอ → เพิ่ม reserved_budget += 10,000
4. งบคงเหลือลดลงทันที

---

## 2. คืนวงเงิน (Release Budget)

**เมื่อไหร่:** 
- ปฏิเสธใบขอซื้อ (Reject)
- ส่งกลับแก้ไข (Correction)

```python
# OrderRejectAPIView.post()
order_total = float(order_data.get('total_estimated_price', 0))
db.collection('projects').document(project_id).update({
    'reserved_budget': firestore.Increment(-order_total)
})
```

**Logic:**
1. ใบขอซื้อถูกปฏิเสธ
2. ระบบคืน reserved_budget -= 10,000
3. งบคงเหลือเพิ่มขึ้น

---

## 3. บันทึกค่าจริง (Record Actual Cost)

**เมื่อไหร่:** ตรวจรับของ (Inspection)

```python
# OrderInspectionAPIView.post()
reserved = float(suborder_data.get('reserved_amount', 0))
actual_cost = float(request.data.get('actual_cost', 0))

db.collection('projects').document(project_id).update({
    'reserved_budget': firestore.Increment(-reserved),  # คืนวงเงินกัน
    'used_budget': firestore.Increment(actual_cost)     # บันทึกค่าจริง
})
```

**Logic:**
1. Staff ตรวจรับของ ระบุราคาจริง = 9,500
2. ระบบคืน reserved_budget -= 10,000 (ที่กันไว้)
3. ระบบเพิ่ม used_budget += 9,500 (ค่าจริง)
4. ส่วนต่าง 500 กลับเข้างบคงเหลือ

---

## 4. ตรวจสอบงบก่อนสั่งซื้อ

```python
# OrderListCreateAPIView.post()
project_doc = db.collection('projects').document(project_id).get()
project_data = project_doc.to_dict()

total_budget = float(project_data.get('budget', 0))
reserved = float(project_data.get('reserved_budget', 0))
used = float(project_data.get('used_budget', 0))
available = total_budget - reserved - used

if order_status == 'Pending' and total > available:
    return Response({
        'error': 'งบประมาณไม่เพียงพอ',
        'available': available,
        'requested': total
    }, status=400)
```

---

## Firestore Increment

```python
from google.cloud.firestore_v1 import Increment

db.collection('projects').document(id).update({
    'reserved_budget': firestore.Increment(1000)   # เพิ่ม
    'reserved_budget': firestore.Increment(-1000)  # ลด
})
```

**ข้อดี:**
- Atomic operation (ป้องกัน race condition)
- ไม่ต้องอ่านค่าเดิมก่อน
- หลาย request พร้อมกันก็ไม่มีปัญหา

---

## สรุป Flow งบประมาณ

```
สร้างใบขอซื้อ → กันวงเงิน (reserved_budget ↑)
    │
    ├── อนุมัติ → ดำเนินการ → ตรวจรับ → บันทึกค่าจริง (used_budget ↑, reserved_budget ↓)
    │
    ├── ปฏิเสธ → คืนวงเงิน (reserved_budget ↓)
    │
    └── ส่งกลับแก้ไข → คืนวงเงิน (reserved_budget ↓) → แก้ไข → กันวงเงินใหม่
```
