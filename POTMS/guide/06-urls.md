# 🌐 URLs.py - เส้นทาง API

## ไฟล์: `api/urls.py`

---

## โครงสร้าง URL Pattern

```python
path('endpoint/', ViewClass.as_view(), name='url-name')
```

**Syntax:**
- `path()` - กำหนด URL pattern
- `'endpoint/'` - URL ที่ต้องการ
- `ViewClass.as_view()` - แปลง class เป็น view function
- `name='...'` - ชื่อสำหรับอ้างอิง

---

## 🔐 Authentication URLs

| URL | View | ฟังก์ชัน |
|-----|------|----------|
| `/api/token/` | TokenObtainPairView | ขอ JWT token |
| `/api/token/refresh/` | TokenRefreshView | Refresh token |
| `/api/login/` | UserLoginAPIView | เข้าสู่ระบบ |
| `/api/register/` | UserRegisterAPIView | ลงทะเบียน |

---

## 📁 Project URLs

| URL | View | Method |
|-----|------|--------|
| `/api/projects/` | ProjectAPIView | GET, POST |
| `/api/projects/{id}/` | ProjectDetailAPIView | GET, PUT, DELETE |
| `/api/projects/import/` | ProjectImportAPIView | POST |
| `/api/projects/{id}/update-budget/` | ProjectUpdateBudgetAPIView | POST |

---

## 👤 User URLs

| URL | View | Method |
|-----|------|--------|
| `/api/users/` | UserListAPIView | GET |
| `/api/users/{id}/` | UserDetailAPIView | GET, PUT, DELETE |

---

## 📦 Order URLs

| URL | View | Method |
|-----|------|--------|
| `/api/orders/` | OrderListCreateAPIView | GET, POST |
| `/api/orders/{id}/` | OrderDetailAPIView | GET, PUT, DELETE |
| `/api/orders/{id}/approve/` | OrderApproveAPIView | POST |
| `/api/orders/{id}/boss-approve/` | OrderBossApproveAPIView | POST |
| `/api/orders/{id}/reject/` | OrderRejectAPIView | POST |
| `/api/orders/{id}/correction/` | OrderCorrectionAPIView | POST |
| `/api/orders/{id}/approve-fix/` | OrderApproveFixAPIView | POST |
| `/api/orders/{id}/send-to-procurement/` | SendToProcurementAPIView | POST |
| `/api/orders/{id}/receive-procurement/` | ReceiveFromProcurementAPIView | POST |
| `/api/orders/{id}/create-suborder/` | SubOrderCreateAPIView | POST |
| `/api/orders/{id}/handover/` | OrderHandoverAPIView | POST |
| `/api/orders/{id}/close/` | OrderCloseAPIView | POST |

---

## 📑 Sub-Order URLs

| URL | View | Method |
|-----|------|--------|
| `/api/suborders/{id}/` | SubOrderDetailAPIView | GET |
| `/api/suborders/{id}/inspection/` | OrderInspectionAPIView | POST |

---

## 📊 Report URLs

| URL | View | Method |
|-----|------|--------|
| `/api/stats/` | StatsAPIView | GET |
| `/api/budget-summary/` | BudgetSummaryAPIView | GET |
| `/api/orders/{id}/export-csv/` | ExportOrderCSVAPIView | GET |

---

## 🖥️ Page URLs (HTML)

| URL | View | Template |
|-----|------|----------|
| `/api/login-page/` | login_page | login.html |
| `/api/register-page/` | register_page | register.html |
| `/api/homepage/` | homepage | homepage.html |
| `/api/staff-dashboard/` | staff_dashboard | staff_dashboard.html |
| `/api/user-dashboard/` | user_dashboard | user_dashboard.html |
| `/api/project-list/` | project_dashboard | project_list.html |
| `/api/staff/orders/page/` | staff_orders_view | staff_orders.html |
| `/api/staff/orders/{id}/detail/` | staff_order_detail_view | staff_order_detail.html |
| `/api/orders/{id}/print/` | print_order_view | print_order.html |
| `/api/create-order/` | create_order_view | create_order.html |
| `/api/my-orders/` | my_orders_view | my_orders.html |
| `/api/orders/{id}/detail-view/` | order_detail_view | order_detail.html |
| `/api/user-select-project/` | user_select_project_view | user_select_project.html |

---

## URL Parameter Types

```python
path('orders/<str:order_id>/', ...)   # String parameter
path('users/<int:user_id>/', ...)      # Integer parameter
```

**Syntax:**
- `<str:name>` - String parameter
- `<int:name>` - Integer parameter
- Parameter จะถูกส่งเป็น argument ใน view function
