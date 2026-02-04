# 🛠️ Utilities - อธิบาย Syntax

## ไฟล์ใน: `api/utils/`

---

## 1. validators.py - ตรวจสอบข้อมูล

### `validate_order_items(items)`
```python
def validate_order_items(items):
    """ตรวจสอบรายการสินค้า"""
    if not items or len(items) == 0:
        return None, "กรุณาเพิ่มรายการสินค้า"
    
    for item in items:
        if not item.get('item_name'):
            return None, "ชื่อสินค้าต้องไม่ว่าง"
        if float(item.get('quantity_requested', 0)) <= 0:
            return None, "จำนวนต้องมากกว่า 0"
    
    return items, None  # (validated_items, error)
```

**Logic:** ตรวจสอบว่า items มีข้อมูลครบถ้วน

---

### `validate_order_description(description)`
```python
def validate_order_description(description):
    """ตรวจสอบ description ว่าปลอดภัย"""
    if not description:
        return "", None
    
    # ตัด HTML tags ออก
    import re
    clean = re.sub(r'<[^>]+>', '', description)
    return clean[:1000], None  # จำกัด 1000 ตัวอักษร
```

**Logic:** Sanitize input ป้องกัน XSS

---

### `validate_status_transition(current, new)`
```python
VALID_TRANSITIONS = {
    'Draft': ['Pending'],
    'Pending': ['WaitingBossApproval', 'CorrectionNeeded', 'Rejected'],
    'WaitingBossApproval': ['Approved', 'CorrectionNeeded', 'Rejected'],
    # ...
}

def validate_status_transition(current, new):
    allowed = VALID_TRANSITIONS.get(current, [])
    if new not in allowed:
        return False, f"ไม่สามารถเปลี่ยนจาก {current} เป็น {new}"
    return True, None
```

**Logic:** ตรวจสอบว่าเปลี่ยนสถานะได้หรือไม่

---

## 2. audit.py - บันทึก Log

### `log_audit(action, user_id, details, request)`
```python
AUDIT_ACTIONS = {
    'LOGIN': 'login',
    'LOGOUT': 'logout',
    'CREATE_ORDER': 'create_order',
    'APPROVE_ORDER': 'approve_order',
    # ...
}

def log_audit(action, user_id, details=None, request=None):
    """บันทึก audit log ลง Firestore"""
    log_data = {
        'action': action,
        'user_id': user_id,
        'details': details or {},
        'ip_address': get_client_ip(request) if request else None,
        'timestamp': datetime.datetime.now()
    }
    db.collection('audit_logs').add(log_data)
```

**Logic:** บันทึกทุกการกระทำสำคัญ

---

### `get_client_ip(request)`
```python
def get_client_ip(request):
    """ดึง IP address ของผู้ใช้"""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR')
```

**Logic:** รองรับ reverse proxy

---

## 3. authz.py - Authorization

### `verify_staff_project_access(user_id, project_id)`
```python
def verify_staff_project_access(user_id, project_id):
    """ตรวจสอบว่า staff มีสิทธิ์เข้าถึงโครงการนี้หรือไม่"""
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        return False
    
    user_data = user_doc.to_dict()
    
    # Staff เข้าถึงได้ทุกโครงการ
    if user_data.get('role', '').lower() == 'staff':
        return True
    
    return False
```

---

### `verify_order_ownership(user_id, order_id)`
```python
def verify_order_ownership(user_id, order_id):
    """ตรวจสอบว่า user เป็นเจ้าของ order นี้หรือไม่"""
    order_doc = db.collection('orders').document(order_id).get()
    if not order_doc.exists:
        return False
    
    order_data = order_doc.to_dict()
    return order_data.get('requester_id') == user_id
```

---

## การใช้งานใน views.py

```python
from api.utils.validators import validate_order_items
from api.utils.audit import log_audit, AUDIT_ACTIONS

class OrderCreateAPIView(APIView):
    def post(self, request):
        items = request.data.get('items', [])
        
        # Validate
        validated, error = validate_order_items(items)
        if error:
            return Response({'error': error}, status=400)
        
        # Create order...
        
        # Log
        log_audit(
            AUDIT_ACTIONS['CREATE_ORDER'],
            request.user_id,
            {'order_id': order_id},
            request
        )
```
