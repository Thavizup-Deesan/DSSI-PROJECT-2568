# 📘 Views.py - อธิบาย Class และ Function

## ไฟล์: `api/views.py`

---

## 🔐 Permission Classes

### `IsStaff`
```python
class IsStaff(BasePermission):
    def has_permission(self, request, view):
```
**Logic:** ตรวจสอบว่าผู้ใช้เป็น Staff หรือไม่
1. ดึง JWT token จาก `Authorization: Bearer <token>` header
2. Decode token แล้วตรวจ `role == 'staff'`
3. ถ้าไม่มี token ให้ fallback ไปใช้ session

---

## 📁 Project APIs

### `ProjectAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| GET | `/api/projects/` | ดึงโครงการทั้งหมดจาก Firestore แล้วแปลงเป็น list |
| POST | `/api/projects/` | สร้างโครงการใหม่พร้อมงบประมาณเริ่มต้น |

**Syntax สำคัญ:**
- `db.collection('projects').stream()` - ดึงข้อมูลทั้งหมด
- `db.collection('projects').add(data)` - เพิ่มเอกสารใหม่

---

### `ProjectDetailAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| GET | `/api/projects/{id}/` | ดึงโครงการตาม ID |
| PUT | `/api/projects/{id}/` | แก้ไขชื่อและงบประมาณ |
| DELETE | `/api/projects/{id}/` | ลบโครงการ |

**Syntax สำคัญ:**
- `db.collection('projects').document(id).get()` - ดึงเอกสารเดียว
- `db.collection('projects').document(id).update(data)` - อัพเดท
- `db.collection('projects').document(id).delete()` - ลบ

---

### `ProjectImportAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/projects/import/` | นำเข้าโครงการจากไฟล์ Excel/CSV |

**Syntax สำคัญ:**
```python
file = request.FILES.get('file')        # รับไฟล์จาก form
df = pd.read_excel(file)                  # อ่านด้วย pandas
for index, row in df.iterrows():          # วนลูปแต่ละแถว
    db.collection('projects').add(...)    # บันทึกลง Firestore
```

---

## 👤 User APIs

### `UserRegisterAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/register/` | ลงทะเบียนผู้ใช้ใหม่ |

**Logic:**
1. ตรวจสอบว่า username ซ้ำหรือไม่
2. Hash password ด้วย `make_password()`
3. บันทึกลง collection `users`

---

### `UserLoginAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/login/` | เข้าสู่ระบบ พร้อมสร้าง JWT |

**Logic:**
1. ค้นหา user ตาม username
2. ตรวจ password ด้วย `check_password()`
3. สร้าง JWT token ด้วย `RefreshToken()`
4. ส่ง access_token, refresh_token, user_info กลับ

**Rate Limit:** 5 ครั้ง/นาที

---

### `UserListAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| GET | `/api/users/` | ดึงรายชื่อผู้ใช้ทั้งหมด (ไม่รวม password) |

---

### `UserDetailAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| GET | `/api/users/{id}/` | ดูข้อมูลผู้ใช้ |
| PUT | `/api/users/{id}/` | แก้ไขข้อมูลผู้ใช้ |
| DELETE | `/api/users/{id}/` | ลบผู้ใช้ |

---

## 📦 Order APIs

### `OrderListCreateAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| GET | `/api/orders/` | ดึงใบขอซื้อทั้งหมด (filter ตาม project_id) |
| POST | `/api/orders/` | สร้างใบขอซื้อใหม่ |

**Logic การสร้าง:**
1. Validate items และ description
2. ตรวจสอบงบประมาณคงเหลือ
3. สร้าง order_no รูปแบบ `PO-YYYYMMDD-XXX`
4. ถ้า status = Pending → กันวงเงิน
5. บันทึกลง Firestore

**Syntax งบประมาณ:**
```python
available = total_budget - reserved_budget - used_budget
if total > available:
    return error
db.collection('projects').document(project_id).update({
    'reserved_budget': firestore.Increment(total)
})
```

---

### `OrderDetailAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| GET | `/api/orders/{id}/` | ดึงรายละเอียดใบขอซื้อ |
| PUT | `/api/orders/{id}/` | แก้ไขใบขอซื้อ (Draft/CorrectionNeeded) |
| DELETE | `/api/orders/{id}/` | ลบใบขอซื้อ (Draft เท่านั้น) |

---

### `OrderApproveAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/orders/{id}/approve/` | Staff อนุมัติ → เปลี่ยนเป็น WaitingBossApproval |

---

### `OrderBossApproveAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/orders/{id}/boss-approve/` | หัวหน้าอนุมัติ → เปลี่ยนเป็น Approved |

---

### `OrderRejectAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/orders/{id}/reject/` | ปฏิเสธ + คืนวงเงินที่กัน |

---

### `OrderCorrectionAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/orders/{id}/correction/` | ส่งกลับแก้ไข + คืนวงเงินที่กัน |

---

### `SendToProcurementAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/orders/{id}/send-to-procurement/` | ส่งพัสดุ → SentToProcurement |

---

### `ReceiveFromProcurementAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/orders/{id}/receive-procurement/` | รับของจากพัสดุ |

---

### `SubOrderCreateAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/orders/{id}/create-suborder/` | สร้างใบย่อยจาก items ที่เลือก |

---

### `OrderInspectionAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/suborders/{id}/inspection/` | ตรวจรับของ + อัพเดทงบจริง + สร้าง QR |

**Logic งบประมาณ:**
```python
reserved = suborder['reserved_amount']
actual = request.data.get('actual_cost')

db.collection('projects').document(project_id).update({
    'reserved_budget': firestore.Increment(-reserved),  # คืนวงเงินกัน
    'used_budget': firestore.Increment(actual)          # บันทึกค่าจริง
})
```

---

### `OrderHandoverAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/orders/{id}/handover/` | จ่ายของให้ User |

---

### `OrderCloseAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| POST | `/api/orders/{id}/close/` | ปิดใบสั่งซื้อ → Closed |

---

## 📊 Report APIs

### `StatsAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| GET | `/api/stats/` | นับจำนวน orders แยกตามสถานะ |

### `BudgetSummaryAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| GET | `/api/budget-summary/` | สรุปงบประมาณทั้งหมด |

### `ExportOrderCSVAPIView`
| Method | URL | Logic |
|--------|-----|-------|
| GET | `/api/orders/{id}/export-csv/` | Export ใบขอซื้อเป็น CSV |

---

## 🖥️ Page Views (render HTML)

| Function | URL | Template |
|----------|-----|----------|
| `login_page` | `/api/login-page/` | login.html |
| `register_page` | `/api/register-page/` | register.html |
| `homepage` | `/api/homepage/` | homepage.html |
| `staff_dashboard` | `/api/staff-dashboard/` | staff_dashboard.html |
| `user_dashboard` | `/api/user-dashboard/` | user_dashboard.html |
| `project_dashboard` | `/api/project-list/` | project_list.html |
| `staff_orders_view` | `/api/staff/orders/page/` | staff_orders.html |
| `staff_order_detail_view` | `/api/staff/orders/{id}/detail/` | staff_order_detail.html |
| `print_order_view` | `/api/orders/{id}/print/` | print_order.html |

**Syntax:**
```python
def login_page(request):
    return render(request, 'login.html')
```
