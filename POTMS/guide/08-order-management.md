# 📦 Order Management

## ระบบจัดการใบขอซื้อ

---

## สถานะใบขอซื้อ (Order Status)

```
Draft → Pending → WaitingBossApproval → Approved → SentToProcurement 
    → ReceivedFromProcurement → WaitingInspection → Inspected → Closed
```

| สถานะ | ความหมาย |
|-------|----------|
| `Draft` | ฉบับร่าง (ยังไม่ส่ง) |
| `Pending` | รอ Staff ตรวจสอบ |
| `WaitingBossApproval` | รอหัวหน้าเซ็น |
| `Approved` | หัวหน้าอนุมัติแล้ว |
| `CorrectionNeeded` | ต้องแก้ไข |
| `Rejected` | ปฏิเสธ |
| `SentToProcurement` | ส่งพัสดุแล้ว |
| `ReceivedFromProcurement` | รับของจากพัสดุแล้ว |
| `WaitingInspection` | รอตรวจรับ |
| `Inspected` | ตรวจรับแล้ว |
| `Closed` | ปิดแล้ว |

---

## 1. สร้างใบขอซื้อ (OrderListCreateAPIView)

### POST `/api/orders/`

```python
def post(self, request):
    # ดึงข้อมูลจาก request
    project_id = request.data.get('project_id')
    items = request.data.get('items', [])
    total = float(request.data.get('total_estimated_price', 0))
    
    # Validate
    validated_items, item_error = validate_order_items(items)
    if item_error:
        return Response({'error': item_error}, status=400)
```

### Logic:

1. **รับข้อมูล** จาก request body
2. **Validate** items และ description
3. **ตรวจสอบงบ** ว่าพอหรือไม่
4. **สร้าง order_no** (PO-YYYYMMDD-XXX)
5. **กันวงเงิน** ถ้า status = Pending
6. **บันทึก** ลง Firestore

---

### สร้างเลขที่ใบขอซื้อ

```python
today = datetime.datetime.now()
date_prefix = today.strftime('%Y%m%d')  # 20260110

# หาเลข running number
orders_today = db.collection('orders') \
    .where('order_no', '>=', f'PO-{date_prefix}-') \
    .where('order_no', '<', f'PO-{date_prefix}~') \
    .stream()

count = sum(1 for _ in orders_today) + 1
order_no = f'PO-{date_prefix}-{count:03d}'  # PO-20260110-001
```

---

## 2. ตรวจสอบงบประมาณ

```python
# ดึงข้อมูลโครงการ
project_doc = db.collection('projects').document(project_id).get()
project_data = project_doc.to_dict()

total_budget = float(project_data.get('budget', 0))
reserved = float(project_data.get('reserved_budget', 0))
used = float(project_data.get('used_budget', 0))
available = total_budget - reserved - used

# ตรวจสอบว่างบพอไหม
if order_status == 'Pending' and total > available:
    return Response({
        'error': 'งบประมาณไม่เพียงพอ',
        'available': available,
        'requested': total
    }, status=400)
```

---

## 3. กันวงเงิน (Reserve Budget)

```python
if order_status == 'Pending':
    db.collection('projects').document(project_id).update({
        'reserved_budget': firestore.Increment(total)
    })
```

**`firestore.Increment()`** จะบวกค่าเข้าไป atomic (ป้องกัน race condition)

---

## 4. อนุมัติใบขอซื้อ (OrderApproveAPIView)

### POST `/api/orders/{id}/approve/`

```python
def post(self, request, order_id):
    order_doc = db.collection('orders').document(order_id).get()
    order_data = order_doc.to_dict()
    
    # ตรวจสอบสถานะ
    if order_data.get('status') != 'Pending':
        return Response({'error': 'สถานะไม่ถูกต้อง'}, status=400)
    
    # อัพเดทสถานะ
    db.collection('orders').document(order_id).update({
        'status': 'WaitingBossApproval',
        'approved_by': request.data.get('approver_id'),
        'approved_at': datetime.datetime.now()
    })
```

---

## 5. หัวหน้าอนุมัติ (OrderBossApproveAPIView)

### POST `/api/orders/{id}/boss-approve/`

```python
db.collection('orders').document(order_id).update({
    'status': 'Approved',
    'boss_approved_by': approver_id,
    'boss_approved_at': datetime.datetime.now()
})
```

---

## 6. ส่งกลับแก้ไข (OrderCorrectionAPIView)

### POST `/api/orders/{id}/correction/`

```python
def post(self, request, order_id):
    notes = request.data.get('notes', '')
    order_total = float(order_data.get('total_estimated_price', 0))
    
    # คืนวงเงินที่กันไว้
    db.collection('projects').document(project_id).update({
        'reserved_budget': firestore.Increment(-order_total)
    })
    
    # อัพเดทสถานะ
    db.collection('orders').document(order_id).update({
        'status': 'CorrectionNeeded',
        'correction_notes': notes
    })
```

---

## 7. ตรวจรับของ (OrderInspectionAPIView)

### POST `/api/suborders/{id}/inspection/`

```python
def post(self, request, suborder_id):
    actual_cost = float(request.data.get('actual_cost', 0))
    
    # คำนวณส่วนต่าง
    reserved = float(suborder_data.get('reserved_amount', 0))
    cost_difference = reserved - actual_cost
    
    # อัพเดทงบประมาณ
    db.collection('projects').document(project_id).update({
        'reserved_budget': firestore.Increment(-reserved),
        'used_budget': firestore.Increment(actual_cost)
    })
```

### Logic:
1. **ลด** reserved_budget (คืนวงเงินที่กันไว้)
2. **เพิ่ม** used_budget (บันทึกค่าจริง)
3. **สร้าง QR Code** สำหรับสินค้า

---

## 8. ปิดใบสั่งซื้อ (OrderCloseAPIView)

### POST `/api/orders/{id}/close/`

```python
db.collection('orders').document(order_id).update({
    'status': 'Closed',
    'closed_at': datetime.datetime.now()
})
```

---

## Order Document Structure

```json
{
  "id": "abc123",
  "order_no": "PO-20260110-001",
  "order_title": "ขอเบิกอุปกรณ์สำนักงาน",
  "order_description": "สำหรับโครงการ ABC",
  "project_id": "project123",
  "requester_id": "user123",
  "items": [
    {
      "item_name": "กระดาษ A4",
      "quantity_requested": 10,
      "unit": "รีม",
      "estimated_unit_price": 180
    }
  ],
  "total_estimated_price": 1800,
  "status": "Pending",
  "created_at": "2026-01-10T10:00:00Z",
  "approved_by": "staff123",
  "approved_at": "2026-01-10T11:00:00Z"
}
```
