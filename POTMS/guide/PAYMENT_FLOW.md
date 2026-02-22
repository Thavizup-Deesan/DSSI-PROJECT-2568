# กระบวนการตั้งเบิกจ่าย (Payment Disbursement Flow)

> UC-12: คำนวณยอดและตั้งเบิกจ่าย — ตามมูลค่าที่ตรวจรับจริง

## หลักการ

ระบบคำนวณยอดเบิกจ่ายจาก **จำนวนสินค้าที่กรรมการตรวจรับผ่าน (Inspection Pass)** คูณ **ราคาต่อหน่วยในใบสั่งซื้อ (PO)**  
ถ้าของยังรับไม่ครบ ก็จะเบิกจ่ายได้แค่ส่วนที่ตรวจรับผ่านจริงเท่านั้น

```
ยอดเบิกจ่าย = Σ (จำนวนที่ตรวจรับผ่าน × ราคาต่อหน่วยตาม PO) - ยอดที่เบิกไปแล้ว
```

---

## Data Flow: Frontend → Backend

### 1. โหลดรายการใบสั่งซื้อ

**Frontend** — [payment.html](file:///e:/P1/DSSI-PROJECT-2568/POTMS/api/templates/payment.html)

```javascript
// payment.html: loadOrders() (บรรทัด 49-67)
async function loadOrders() {
    const orders = await apiFetch('/api/orders/');    // ← GET /api/orders/
    // กรองเฉพาะ status: Approved, Processing, Partially_Paid, Completed
    // แต่ละ order มี suggested_payment_amount ที่ backend คำนวณมาให้
}
```

**Backend** — [views.py](file:///e:/P1/DSSI-PROJECT-2568/POTMS/api/views.py) → `PurchaseOrderAPIView.get()` (บรรทัด 601-614)

```python
# คำนวณ suggested_payment_amount ในแต่ละ order
for item in o.items.all():
    passed_qty = item.received_records.filter(
        partial_receive__inspection__result='Pass'      # เฉพาะที่ตรวจรับผ่าน
    ).aggregate(total=Sum('quantity'))['total'] or 0
    delivered_value += (Decimal(passed_qty) * item.unit_price)

already_paid = Payment.objects.filter(related_order=o)
    .aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')

suggested = delivered_value - already_paid   # ยอดที่เบิกได้อีก
```

---

### 2. เลือก Order และแสดงยอดแนะนำ

**Frontend** — `onOrderSelectChange()` (บรรทัด 69-87)

```javascript
function onOrderSelectChange() {
    // ดึง suggested_payment_amount จาก data attribute
    let amount = option.getAttribute('data-amount');   // ยอดจากตรวจรับจริง
    document.getElementById('paymentAmount').value = amount;
}
```

- ถ้า `suggested_payment_amount > 0` → ใส่ยอดให้อัตโนมัติ
- ถ้า `= 0` → option จะถูก **disable** พร้อมข้อความ `[ยังไม่มียอดตรวจรับผ่าน]`

---

### 3. กดปุ่ม "ตั้งเบิกจ่าย"

**Frontend** — `createPayment()` (บรรทัด 84-109)

```javascript
async function createPayment() {
    const res = await apiFetch('/api/payments/', {
        method: 'POST',
        body: JSON.stringify({
            order_id: orderId,       // ID ใบสั่งซื้อ
            amount_paid: amount      // จำนวนเงินที่ต้องการเบิก
        })
    });
}
```

**Backend** — `PaymentAPIView.post()` (บรรทัด 1411-1503)

```
รับ order_id, amount_paid
        │
        ▼
┌─ ตรวจสอบสถานะ Order ────────────────────────────┐
│  ต้องเป็น Approved / Processing / Partially_Paid │
│  ❌ ถ้าไม่ใช่ → return error                      │
└──────────────────────────────────────────────────┘
        │ ✅
        ▼
┌─ คำนวณ delivered_value ─────────────────────────┐
│  วนลูปทุก item:                                  │
│    passed_qty = จำนวนที่ตรวจรับผ่าน (Pass)        │
│    delivered_value += passed_qty × unit_price     │
│  ❌ ถ้า = 0 → "ยังไม่มีรายการตรวจรับผ่าน"          │
└──────────────────────────────────────────────────┘
        │ ✅
        ▼
┌─ คำนวณ suggested_amount ────────────────────────┐
│  suggested = delivered_value - already_paid       │
│  ❌ ถ้า ≤ 0 → "ไม่มียอดคงเหลือที่เบิกได้"          │
└──────────────────────────────────────────────────┘
        │ ✅
        ▼
┌─ ตรวจยอดที่ขอเบิก ──────────────────────────────┐
│  ❌ amount > suggested → "เกินยอดตรวจรับ"          │
│  ❌ amount ≤ 0 → "ต้องมากกว่า 0"                   │
└──────────────────────────────────────────────────┘
        │ ✅
        ▼
┌─ สร้าง Payment record ──────────────────────────┐
│  Payment.objects.create(                          │
│      project=order.project,                       │
│      related_order=order,                         │
│      amount_paid=amount,                          │
│      status='Processing'                          │
│  )                                                │
└──────────────────────────────────────────────────┘
        │
        ▼
┌─ อัปเดตงบโครงการ ───────────────────────────────┐
│  update_project_budget(project):                  │
│    - Order ที่ Completed → กันแค่ยอดจ่ายจริง        │
│    - Order ที่ยังไม่ Completed → กันเต็มจำนวน PO    │
│    reserved_budget = ผลรวม                        │
│    remaining_budget = total - reserved             │
└──────────────────────────────────────────────────┘
        │
        ▼
┌─ อัปเดตสถานะ Order ─────────────────────────────┐
│  ถ้า จ่ายครบ + ของครบ → status = 'Completed'       │
│  ถ้า จ่ายบางส่วน → status = 'Partially_Paid'       │
└──────────────────────────────────────────────────┘
        │
        ▼
   Response กลับ Frontend → แสดง toast "สำเร็จ"
```

**โค้ด Backend ที่สำคัญ:**

```python
# views.py: PaymentAPIView.post() (บรรทัด 1429-1503)

# 1. คำนวณ delivered_value
delivered_value = Decimal('0')
for item in order.items.all():
    passed_qty = PartialReceiveItem.objects.filter(
        order_item=item,
        partial_receive__inspection__result='Pass'
    ).aggregate(total=Sum('quantity'))['total'] or 0
    delivered_value += (Decimal(passed_qty) * item.unit_price)

# 2. ยอดที่เบิกไปแล้ว
already_paid = Payment.objects.filter(related_order=order)
    .aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')

# 3. ยอดที่เบิกได้
suggested_amount = delivered_value - already_paid

# 4. Block ถ้าไม่มียอด
if delivered_value <= 0:
    return error("ยังไม่มีรายการตรวจรับผ่าน")
if suggested_amount <= 0:
    return error("ไม่มียอดคงเหลือที่เบิกได้")
if amount > suggested_amount:
    return error("เกินยอดตรวจรับ")

# 5. สร้าง Payment
payment = Payment.objects.create(...)

# 6. อัปเดตงบ
update_project_budget(order.project)

# 7. อัปเดตสถานะ Order
if total_paid >= delivered_value and delivered_value >= order.total_amount:
    order.status = 'Completed'      # ของครบ + จ่ายครบ
elif total_paid > 0:
    order.status = 'Partially_Paid' # จ่ายบางส่วน
```

---

## Models ที่เกี่ยวข้อง

| Model | ตาราง | หน้าที่ |
|-------|-------|---------|
| `PurchaseOrder` | `purchase_orders` | ใบสั่งซื้อหลัก (มี `total_amount`, `status`) |
| `OrderItem` | `order_items` | รายการวัสดุ (มี `quantity`, `unit_price`) |
| `PartialReceive` | `partial_receives` | ใบรับของ (แนบใบเสร็จ) |
| `PartialReceiveItem` | `partial_receive_items` | รายการที่รับ (มี `quantity` ที่รับจริง) |
| `Inspection` | `inspections` | ผลตรวจรับ (`Pass` / `Reject`) |
| `Payment` | `payments` | การเบิกจ่าย (มี `amount_paid`, `status`) |
| `Project` | `projects` | โครงการ (มี `total_budget`, `reserved_budget`, `remaining_budget`) |

---

## ความสัมพันธ์ของข้อมูล

```
Project (โครงการ)
  └─ PurchaseOrder (ใบสั่งซื้อหลัก)
       ├─ OrderItem (รายการวัสดุ)
       │    └─ PartialReceiveItem (จำนวนที่รับจริง)
       ├─ PartialReceive (ใบรับของ + ใบเสร็จ)
       │    ├─ PartialReceiveItem (รายการที่รับ)
       │    └─ Inspection (ผลตรวจรับ: Pass/Reject)
       └─ Payment (การเบิกจ่าย)
```

---

## Guard Rails (การป้องกัน)

1. **ไม่มี inspection ผ่าน** → ❌ เบิกจ่ายไม่ได้
2. **เบิกครบแล้ว** → ❌ เบิกซ้ำไม่ได้
3. **ยอดเบิก > ยอดตรวจรับ** → ❌ เบิกเกินไม่ได้
4. **ยอดเบิก ≤ 0** → ❌ ต้องมากกว่า 0
5. **Order status ไม่ใช่ Approved/Processing** → ❌ เบิกไม่ได้
