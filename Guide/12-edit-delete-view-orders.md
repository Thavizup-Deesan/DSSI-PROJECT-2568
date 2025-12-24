# Phase 3: ฟีเจอร์ Edit/Delete Draft และ Order Detail View

## 📋 ภาพรวม

ฟีเจอร์ 3 ตัวนี้ช่วยให้ User จัดการ Draft และดูรายละเอียดใบสั่งซื้อ:
1. **Edit Draft** - แก้ไข Draft ที่บันทึกไว้
2. **Delete Draft** - ลบ Draft ที่ไม่ต้องการ
3. **Order Detail View** - ดูรายละเอียดใบสั่งซื้อทุกสถานะ

---

## 🔧 ฟีเจอร์ 1: Edit Draft

### Logic การทำงาน:

```
User กดปุ่ม "แก้ไข" ในหน้า My Orders
        ↓
ตรวจสอบ: status === "Draft"?
        ↓
ถ้าใช่ → ไปหน้า create-order?mode=edit&order_id=xxx
        ↓
โหลดข้อมูล Draft เดิมจาก API
        ↓
แสดงในฟอร์ม
        ↓
User แก้ไข → กด "บันทึก"
        ↓
PUT /api/orders/<order_id>/ (อัปเดตข้อมูล)
```

### Backend API

#### GET `/api/orders/<order_id>/`
ดึงข้อมูล order ตัวเดียว

```python
def get(self, request, order_id):
    """
    ดึงข้อมูล order ตัวเดียว
    
    Response:
    {
        "id": "xxx",
        "project_id": "yyy",
        "order_title": "...",
        "items": [...],
        "status": "Draft",
        ...
    }
    """
    try:
        order_doc = db.collection('orders').document(order_id).get()
        if not order_doc.exists:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)
        
        order_data = order_doc.to_dict()
        order_data['id'] = order_id
        return Response(order_data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
```

#### PUT `/api/orders/<order_id>/`
อัปเดตข้อมูล Draft

```python
def put(self, request, order_id):
    """
    อัปเดต Draft เดิม
    
    Request:
    {
        "order_title": "...",
        "items": [...],
        "total_estimated_price": 1000
    }
    """
    try:
        # ตรวจสอบว่ามี order อยู่จริง
        order_doc = db.collection('orders').document(order_id).get()
        if not order_doc.exists:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)
        
        order_data = order_doc.to_dict()
        
        # ต้องเป็น Draft เท่านั้น
        if order_data.get('status') != 'Draft':
            return Response({'error': 'ไม่สามารถแก้ไขใบสั่งซื้อที่ส่งแล้ว'}, status=400)
        
        # อัปเดตข้อมูล
        update_data = request.data
        update_data['updated_at'] = datetime.datetime.now()
        
        db.collection('orders').document(order_id).update(update_data)
        
        return Response({'message': 'อัปเดตสำเร็จ', 'order_id': order_id}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
```

### Frontend (create_order.html)

#### เพิ่ม Edit Mode:

```javascript
// ตรวจสอบ URL parameters
const urlParams = new URLSearchParams(window.location.search);
const mode = urlParams.get('mode'); // 'edit'
const editOrderId = urlParams.get('order_id');

// ถ้าเป็น Edit mode
if (mode === 'edit' && editOrderId) {
    loadOrderForEdit(editOrderId);
}

async function loadOrderForEdit(orderId) {
    try {
        const res = await fetch(`/api/orders/${orderId}/`);
        const order = await res.json();
        
        // ตรวจสอบว่าเป็น Draft
        if (order.status !== 'Draft') {
            Swal.fire('Error', 'ไม่สามารถแก้ไขใบสั่งซื้อที่ส่งแล้ว', 'error')
                .then(() => window.location.href = '/api/my-orders/');
            return;
        }
        
        // โหลดข้อมูลเข้าฟอร์ม
        document.getElementById('order_title').value = order.order_title;
        document.getElementById('order_description').value = order.order_description;
        document.getElementById('required_date').value = order.required_date;
        document.getElementById('vendor_name').value = order.vendor_name;
        
        // โหลดรายการสินค้า
        order.items.forEach(item => {
            addItemToTable(item);
        });
        
        // เปลี่ยนฟังก์ชัน save ให้เป็น update
        window.currentEditOrderId = orderId;
    } catch (e) {
        Swal.fire('Error', e.message, 'error');
    }
}

// แก้ไข saveDraft() ให้รองรับ edit mode
async function saveDraft() {
    const items = getItems();
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    const orderData = {
        ...
        total_estimated_price: calculateTotal()
    };
    
    try {
        let res, data;
        
        if (window.currentEditOrderId) {
            // Edit mode → PUT
            res = await fetch(`/api/orders/${window.currentEditOrderId}/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });
        } else {
            // Create mode → POST
            res = await fetch('/api/orders/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });
        }
        
        data = await res.json();
        
        if (res.ok) {
            Swal.fire('สำเร็จ', 'บันทึกเรียบร้อย', 'success')
                .then(() => window.location.href = '/api/my-orders/');
        } else {
            Swal.fire('Error', data.error, 'error');
        }
    } catch (e) {
        Swal.fire('Error', e.message, 'error');
    }
}
```

---

## 🔧 ฟีเจอร์ 2: Delete Draft

### Logic การทำงาน:

```
User กดปุ่ม "ลบ" ในหน้า My Orders
        ↓
ตรวจสอบ: status === "Draft"?
        ↓
ถ้าใช่ → แสดง Confirm Dialog
        ↓
User ยืนยัน → DELETE /api/orders/<order_id>/
        ↓
refresh ตาราง
```

### Backend API

#### DELETE `/api/orders/<order_id>/`

```python
def delete(self, request, order_id):
    """
    ลบ Draft
    
    - ตรวจสอบว่าเป็น Draft เท่านั้น
    - ลบออกจาก Firestore
    """
    try:
        order_doc = db.collection('orders').document(order_id).get()
        if not order_doc.exists:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)
        
        order_data = order_doc.to_dict()
        
        # ต้องเป็น Draft เท่านั้น
        if order_data.get('status') != 'Draft':
            return Response({'error': 'ไม่สามารถลบใบสั่งซื้อที่ส่งแล้ว'}, status=400)
        
        # ลบ
        db.collection('orders').document(order_id).delete()
        
        return Response({'message': 'ลบสำเร็จ'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
```

### Frontend (my_orders.html)

```javascript
async function deleteOrder(orderId) {
    const result = await Swal.fire({
        title: 'ยืนยันการลบ?',
        text: 'ข้อมูลจะถูกลบถาวร',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        confirmButtonText: 'ลบเลย',
        cancelButtonText: 'ยกเลิก'
    });

    if (!result.isConfirmed) return;

    try {
        const res = await fetch(`/api/orders/${orderId}/`, {
            method: 'DELETE'
        });
        const data = await res.json();

        if (res.ok) {
            Swal.fire('สำเร็จ', 'ลบเรียบร้อย', 'success');
            loadOrders(); // refresh
        } else {
            Swal.fire('Error', data.error, 'error');
        }
    } catch (e) {
        Swal.fire('Error', e.message, 'error');
    }
}
```

---

## 🔧 ฟีเจอร์ 3: Order Detail View

### Logic การทำงาน:

```
User กดปุ่ม "ดูรายละเอียด" ในหน้า My Orders
        ↓
ไปหน้า /api/orders/<order_id>/detail/
        ↓
ดึงข้อมูล: GET /api/orders/<order_id>/
        ↓
แสดงรายละเอียดครบ:
- ข้อมูลหลัก (เรื่อง, วันที่, ร้านค้า)
- รายการสินค้า (table)
- สถานะ
- ปุ่มกลับ
```

### Backend

ใช้ API GET `/api/orders/<order_id>/` เดิม

### Frontend (order_detail.html)

หน้าใหม่สำหรับแสดงรายละเอียด

```html
<!DOCTYPE html>
<html lang="th">
<head>
    <title>รายละเอียดใบสั่งซื้อ - POTMS</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <main>
        <div class="bg-white p-6">
            <h2 id="orderTitle" class="text-2xl font-bold">กำลังโหลด...</h2>
            <p id="orderNo" class="text-gray-500">เลขที่: -</p>
            
            <!-- ข้อมูลหลัก -->
            <div class="grid grid-cols-2 gap-4 mt-4">
                <div>
                    <label>วันที่ต้องการใช้งาน:</label>
                    <p id="requiredDate">-</p>
                </div>
                <div>
                    <label>ร้านค้า/บริษัท:</label>
                    <p id="vendorName">-</p>
                </div>
            </div>
            
            <!-- รายการสินค้า -->
            <table id="itemsTable" class="w-full mt-6">
                <thead>
                    <tr>
                        <th>ลำดับ</th>
                        <th>ชื่อสินค้า</th>
                        <th>จำนวน</th>
                        <th>หน่วย</th>
                        <th>ราคา/หน่วย</th>
                        <th>รวม</th>
                    </tr>
                </thead>
                <tbody id="itemsBody"></tbody>
            </table>
            
            <div class="mt-4">
                <p class="text-xl font-bold">
                    ยอดรวม: <span id="totalPrice">฿0</span>
                </p>
            </div>
            
            <button onclick="window.location.href='/api/my-orders/'" 
                class="mt-6 px-4 py-2 bg-gray-500 text-white rounded">
                กลับ
            </button>
        </div>
    </main>
    
    <script>
        const orderId = new URLSearchParams(window.location.search).get('id');
        
        async function loadOrderDetail() {
            const res = await fetch(`/api/orders/${orderId}/`);
            const order = await res.json();
            
            document.getElementById('orderTitle').textContent = order.order_title;
            document.getElementById('orderNo').textContent = `เลขที่: ${order.order_no || orderId}`;
            document.getElementById('requiredDate').textContent = order.required_date || '-';
            document.getElementById('vendorName').textContent = order.vendor_name || '-';
            
            // แสดงรายการสินค้า
            const tbody = document.getElementById('itemsBody');
            order.items.forEach((item, i) => {
                const total = item.quantity_requested * item.estimated_unit_price;
                tbody.innerHTML += `
                    <tr>
                        <td>${i + 1}</td>
                        <td>${item.item_name}</td>
                        <td>${item.quantity_requested}</td>
                        <td>${item.unit}</td>
                        <td>฿${item.estimated_unit_price.toLocaleString()}</td>
                        <td>฿${total.toLocaleString()}</td>
                    </tr>
                `;
            });
            
            document.getElementById('totalPrice').textContent = 
                `฿${order.total_estimated_price.toLocaleString()}`;
        }
        
        loadOrderDetail();
    </script>
</body>
</html>
```

---

## 📁 ไฟล์ที่ต้องสร้าง/แก้ไข

| ไฟล์ | สิ่งที่เพิ่ม |
|------|-------------|
| `api/views.py` | เพิ่ม `OrderDetailAPIView` (GET, PUT, DELETE) |
| `api/views.py` | เพิ่ม `order_detail_view` function |
| `api/urls.py` | เพิ่ม URL `/orders/<id>/` และ `/orders/<id>/detail/` |
| `api/templates/my_orders.html` | ทำให้ปุ่ม Edit/Delete ทำงานจริง |
| `api/templates/create_order.html` | รองรับ Edit mode |
| `api/templates/order_detail.html` | สร้างหน้าใหม่ |

---

## 🔄 Flow รวม

### Edit Draft:
```
My Orders → กด "แก้ไข" → Create Order (edit mode) → บันทึก → My Orders
```

### Delete Draft:
```
My Orders → กด "ลบ" → ยืนยัน → ลบ → refresh ตาราง
```

### View Detail:
```
My Orders → กด "ดูรายละเอียด" → Order Detail → กลับ → My Orders
```
