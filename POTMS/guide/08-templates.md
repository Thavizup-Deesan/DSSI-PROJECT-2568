# 🖥️ HTML Templates - อธิบาย Syntax

## ไฟล์ใน: `api/templates/`

---

## โครงสร้างพื้นฐาน

```html
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>ชื่อหน้า - POTMS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
</head>
<body>
    <!-- เนื้อหา -->
    <script>
        // JavaScript
    </script>
</body>
</html>
```

---

## Libraries ที่ใช้

| Library | URL | การใช้งาน |
|---------|-----|----------|
| TailwindCSS | cdn.tailwindcss.com | CSS styling |
| SweetAlert2 | cdn.jsdelivr.net/npm/sweetalert2@11 | Popup/Alert |
| SheetJS | cdn.sheetjs.com/xlsx | อ่าน Excel |
| Google Fonts | fonts.googleapis.com | Font Prompt |

---

## JavaScript Patterns

### 1. localStorage - เก็บข้อมูล User

```javascript
// เก็บข้อมูลหลัง login
localStorage.setItem('user', JSON.stringify(data.user));
localStorage.setItem('access_token', data.access_token);

// อ่านข้อมูล
const user = JSON.parse(localStorage.getItem('user'));
const token = localStorage.getItem('access_token');

// ลบข้อมูล (logout)
localStorage.clear();
```

---

### 2. fetch API - เรียก Backend

```javascript
// GET request
const response = await fetch('/api/orders/');
const data = await response.json();

// POST request พร้อม JWT
const response = await fetch('/api/orders/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ name: 'test' })
});
```

---

### 3. SweetAlert2 - แสดง Popup

```javascript
// Success
Swal.fire({
    icon: 'success',
    title: 'สำเร็จ',
    text: 'บันทึกข้อมูลเรียบร้อย',
    timer: 2000
});

// Confirm
const result = await Swal.fire({
    title: 'ยืนยันการลบ?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'ลบ',
    cancelButtonText: 'ยกเลิก'
});
if (result.isConfirmed) {
    // ทำการลบ
}

// Loading
Swal.fire({
    title: 'กำลังโหลด...',
    allowOutsideClick: false,
    didOpen: () => Swal.showLoading()
});
```

---

### 4. Dynamic HTML - สร้าง Element

```javascript
const container = document.getElementById('items-container');

// เพิ่ม element
const div = document.createElement('div');
div.className = 'bg-white p-4';
div.innerHTML = `
    <p>ชื่อ: ${item.name}</p>
    <button onclick="deleteItem('${item.id}')">ลบ</button>
`;
container.appendChild(div);

// ลบ element
div.remove();
```

---

## รายการ Templates

### 🔐 Authentication

| ไฟล์ | หน้าที่ | JavaScript หลัก |
|------|--------|----------------|
| `login.html` | หน้า Login | POST /api/login/, เก็บ token |
| `register.html` | หน้าสมัครสมาชิก | POST /api/register/ |

---

### 👤 User Pages

| ไฟล์ | หน้าที่ |
|------|--------|
| `user_dashboard.html` | Dashboard user |
| `user_select_project.html` | เลือกโครงการ |
| `create_order.html` | สร้างใบขอซื้อ |
| `edit_order.html` | แก้ไขใบขอซื้อ |
| `my_orders.html` | รายการใบขอซื้อของฉัน |
| `order_detail.html` | รายละเอียดใบขอซื้อ |

---

### 👨‍💼 Staff Pages

| ไฟล์ | หน้าที่ |
|------|--------|
| `staff_dashboard.html` | Dashboard staff |
| `staff_orders.html` | รายการใบขอซื้อทั้งหมด |
| `staff_order_detail.html` | ตรวจสอบและอนุมัติ |
| `staff_po_management.html` | จัดการพัสดุ |
| `staff_po_detail.html` | รายละเอียดพัสดุ |
| `staff_reports.html` | รายงานสรุป |
| `user_management.html` | จัดการผู้ใช้ |

---

### 📄 Other Pages

| ไฟล์ | หน้าที่ |
|------|--------|
| `homepage.html` | หน้าแรก |
| `project_list.html` | รายการโครงการ |
| `print_order.html` | พิมพ์ใบขอซื้อ |
| `scan_suborder.html` | สแกน QR Code |

---

## Django Template Syntax

```html
<!-- ตัวแปร -->
{{ order.order_no }}
{{ order.total|default:"-" }}

<!-- เงื่อนไข -->
{% if order.status == 'Pending' %}
    <span>รออนุมัติ</span>
{% else %}
    <span>{{ order.status }}</span>
{% endif %}

<!-- วนลูป -->
{% for item in order.items %}
    <tr>
        <td>{{ forloop.counter }}</td>
        <td>{{ item.name }}</td>
    </tr>
{% endfor %}
```

---

## TailwindCSS Classes ที่ใช้บ่อย

| Class | ความหมาย |
|-------|----------|
| `bg-blue-500` | พื้นหลังสีฟ้า |
| `text-white` | ตัวอักษรสีขาว |
| `p-4` | padding 1rem |
| `rounded-lg` | มุมโค้ง |
| `flex` | display flex |
| `grid` | display grid |
| `hover:bg-blue-600` | เปลี่ยนสีเมื่อ hover |
| `hidden` | ซ่อน element |
