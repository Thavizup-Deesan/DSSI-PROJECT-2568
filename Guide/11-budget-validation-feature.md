# Phase 3: ฟีเจอร์ Budget Validation (ตรวจสอบงบประมาณ)

## 📋 ภาพรวม

ฟีเจอร์นี้ช่วยให้ระบบตรวจสอบงบประมาณก่อนอนุญาตให้ User สั่งซื้อ:
- ตรวจสอบว่างบประมาณคงเหลือเพียงพอหรือไม่
- ถ้าพอ → ตัดงบสำรอง (Reserve) และอัปเดตสถานะเป็น "Ordered"
- ถ้าไม่พอ → แจ้งเตือน User

---

## 🗃️ Fields ที่ใช้ (จาก ER Diagram)

### Project Collection:
| Field | Type | ความหมาย |
|-------|------|----------|
| `budget_total` | DECIMAL | งบประมาณทั้งหมด |
| `budget_reserved` | DECIMAL | งบที่ถูกจอง (รอดำเนินการ) |
| `budget_spent` | DECIMAL | งบที่จ่ายจริงแล้ว |

### คำนวณงบคงเหลือ:
```
budget_remaining = budget_total - budget_reserved - budget_spent
```

---

## 🔧 Backend API

### PUT `/api/orders/<order_id>/submit/`

ส่งใบสั่งซื้อ พร้อมตรวจสอบงบประมาณ

**Request:**
```json
{
  "order_id": "xxx"
}
```

**Response (สำเร็จ):**
```json
{
  "message": "สั่งซื้อสำเร็จ",
  "order_id": "xxx",
  "new_status": "Ordered"
}
```

**Response (งบไม่พอ):**
```json
{
  "error": "งบประมาณไม่เพียงพอ",
  "budget_remaining": 5000,
  "order_total": 10000
}
```

---

## 🧠 Logic การทำงาน

### ขั้นตอนที่ 1: ดึงข้อมูล Order
```python
order_doc = db.collection('orders').document(order_id).get()
order_data = order_doc.to_dict()
```

### ขั้นตอนที่ 2: ดึงข้อมูล Project
```python
project_id = order_data['project_id']
project_doc = db.collection('projects').document(project_id).get()
project_data = project_doc.to_dict()
```

### ขั้นตอนที่ 3: คำนวณงบคงเหลือ
```python
budget_total = float(project_data.get('budget_total', 0))
budget_reserved = float(project_data.get('budget_reserved', 0))
budget_spent = float(project_data.get('budget_spent', 0))
budget_remaining = budget_total - budget_reserved - budget_spent
```

### ขั้นตอนที่ 4: ตรวจสอบงบประมาณ
```python
order_total = float(order_data.get('total_estimated_price', 0))

if order_total > budget_remaining:
    # งบไม่พอ → ส่ง error
    return Response({
        'error': 'งบประมาณไม่เพียงพอ',
        'budget_remaining': budget_remaining,
        'order_total': order_total
    }, status=400)
```

### ขั้นตอนที่ 5: ตัดงบสำรอง (Reserve)
```python
new_reserved = budget_reserved + order_total
db.collection('projects').document(project_id).update({
    'budget_reserved': new_reserved
})
```

### ขั้นตอนที่ 6: อัปเดตสถานะ Order
```python
db.collection('orders').document(order_id).update({
    'status': 'Ordered',
    'updated_at': datetime.now()
})
```

---

## 📝 Code เต็ม (views.py)

```python
class OrderSubmitAPIView(APIView):
    """
    ===================================================================
    OrderSubmitAPIView - ส่งใบสั่งซื้อ (ตรวจสอบงบประมาณ)
    ===================================================================
    
    URL: /api/orders/<order_id>/submit/
    Method: POST
    
    Logic:
    1. ดึงข้อมูล Order และ Project
    2. คำนวณงบคงเหลือ
    3. ตรวจสอบว่าพอหรือไม่
    4. ถ้าพอ → ตัดงบสำรอง + อัปเดตสถานะ
    5. ถ้าไม่พอ → ส่ง error
    ===================================================================
    """
    
    def post(self, request, order_id):
        try:
            # 1. ดึงข้อมูล Order
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)
            
            order_data = order_doc.to_dict()
            
            # ตรวจสอบว่าเป็น Draft เท่านั้น
            if order_data.get('status') != 'Draft':
                return Response({'error': 'ใบสั่งซื้อนี้ถูกส่งแล้ว'}, status=400)
            
            # 2. ดึงข้อมูล Project
            project_id = order_data.get('project_id')
            project_doc = db.collection('projects').document(project_id).get()
            
            if not project_doc.exists:
                return Response({'error': 'ไม่พบโครงการ'}, status=404)
            
            project_data = project_doc.to_dict()
            
            # 3. คำนวณงบคงเหลือ
            budget_total = float(project_data.get('budget_total', 0))
            budget_reserved = float(project_data.get('budget_reserved', 0))
            budget_spent = float(project_data.get('budget_spent', 0))
            budget_remaining = budget_total - budget_reserved - budget_spent
            
            # 4. ตรวจสอบงบประมาณ
            order_total = float(order_data.get('total_estimated_price', 0))
            
            if order_total > budget_remaining:
                return Response({
                    'error': 'งบประมาณไม่เพียงพอ',
                    'budget_remaining': budget_remaining,
                    'order_total': order_total
                }, status=400)
            
            # 5. ตัดงบสำรอง (Reserve)
            new_reserved = budget_reserved + order_total
            db.collection('projects').document(project_id).update({
                'budget_reserved': new_reserved
            })
            
            # 6. อัปเดตสถานะ Order
            db.collection('orders').document(order_id).update({
                'status': 'Ordered',
                'updated_at': datetime.datetime.now()
            })
            
            return Response({
                'message': 'สั่งซื้อสำเร็จ',
                'order_id': order_id,
                'new_status': 'Ordered',
                'reserved_amount': order_total
            }, status=200)
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)
```

---

## 📝 Code (urls.py)

```python
# เพิ่ม import
from .views import OrderSubmitAPIView

# เพิ่ม URL pattern
urlpatterns = [
    ...
    path('orders/<str:order_id>/submit/', OrderSubmitAPIView.as_view(), name='order-submit'),
]
```

---

## 📝 Frontend (create_order.html)

### Function submitOrder():
```javascript
async function submitOrder() {
    // Validation
    const items = getItems();
    if (items.length === 0) {
        Swal.fire('Warning', 'กรุณาเพิ่มรายการพัสดุ', 'warning');
        return;
    }
    
    // ถ้าเป็น Draft ใหม่ → บันทึกก่อน แล้วค่อย submit
    // ถ้าเป็น Draft ที่บันทึกแล้ว → submit ได้เลย
    
    // ยืนยันก่อนส่ง
    const result = await Swal.fire({
        title: 'ยืนยันการสั่งซื้อ?',
        text: 'เมื่อส่งแล้วระบบจะตัดงบสำรองอัตโนมัติ',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'ยืนยัน',
        cancelButtonText: 'ยกเลิก'
    });
    
    if (!result.isConfirmed) return;
    
    try {
        // เรียก API submit
        const res = await fetch(`/api/orders/${orderId}/submit/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await res.json();
        
        if (res.ok) {
            Swal.fire('สำเร็จ', 'สั่งซื้อเรียบร้อย ระบบตัดงบสำรองแล้ว', 'success')
                .then(() => window.location.href = '/api/my-orders/');
        } else {
            // แสดง error (งบไม่พอ)
            Swal.fire({
                icon: 'error',
                title: 'งบประมาณไม่เพียงพอ',
                html: `
                    <p>งบคงเหลือ: ฿${data.budget_remaining?.toLocaleString()}</p>
                    <p>ยอดสั่งซื้อ: ฿${data.order_total?.toLocaleString()}</p>
                `
            });
        }
    } catch (e) {
        Swal.fire('Error', e.message, 'error');
    }
}
```

---

## 🔄 Flow Diagram

```
User กดปุ่ม "ส่งเพื่อขออนุมัติ"
        │
        ▼
ระบบดึงข้อมูล Order (total_estimated_price)
        │
        ▼
ระบบดึงข้อมูล Project (budget_total, budget_reserved, budget_spent)
        │
        ▼
คำนวณ: budget_remaining = total - reserved - spent
        │
        ▼
┌───────────────────────────────────┐
│   order_total > budget_remaining? │
└───────────────┬───────────────────┘
                │
        ┌───────┴───────┐
        │               │
       ใช่             ไม่ใช่
        │               │
        ▼               ▼
   แจ้งเตือน        ตัดงบสำรอง
   งบไม่พอ         budget_reserved += order_total
                        │
                        ▼
                  อัปเดต status = 'Ordered'
                        │
                        ▼
                  แจ้งผลสำเร็จ
```

---

## 📁 ไฟล์ที่ต้องแก้ไข

| ไฟล์ | สิ่งที่เพิ่ม |
|------|-------------|
| `api/views.py` | เพิ่ม `OrderSubmitAPIView` class |
| `api/urls.py` | เพิ่ม URL `/orders/<order_id>/submit/` |
| `api/templates/create_order.html` | แก้ไข `submitOrder()` function |
