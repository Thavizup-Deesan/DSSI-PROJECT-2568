# 🎨 อธิบาย HTML Templates

## 📍 ไฟล์ Templates อยู่ที่ไหน?

```
POTMS/api/templates/
├── homepage.html           # หน้าแรก
├── login.html              # หน้า Login
├── register.html           # หน้าสมัครสมาชิก
├── project_list.html       # รายการโครงการ (User)
├── staff_dashboard.html    # แดชบอร์ด Staff
└── user_management.html    # จัดการผู้ใช้ (Admin)
```

---

## 🛠️ เทคโนโลยีที่ใช้ใน Templates

| เทคโนโลยี | หน้าที่ | CDN Link |
|-----------|---------|----------|
| **TailwindCSS** | Styling (CSS) | `cdn.tailwindcss.com` |
| **SweetAlert2** | Popup แจ้งเตือน | `cdn.jsdelivr.net/npm/sweetalert2@11` |
| **Google Fonts** | ฟอนต์ภาษาไทย | `fonts.googleapis.com` |

---

## 📄 โครงสร้างพื้นฐานของ HTML

```html
<!DOCTYPE html>
<html lang="th">

<head>
    <!-- 1. Meta Tags -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ชื่อหน้า - POTMS</title>
    
    <!-- 2. CDN Links -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link href="https://fonts.googleapis.com/css2?family=Prompt&display=swap" rel="stylesheet">
    
    <!-- 3. Custom Styles -->
    <style>
        body { font-family: 'Prompt', sans-serif; }
    </style>
</head>

<body class="bg-gray-50">
    <!-- 4. เนื้อหาหน้าเว็บ -->
    
    <!-- 5. JavaScript -->
    <script>
        // โค้ด JavaScript
    </script>
</body>

</html>
```

---

## 🎯 อธิบาย login.html

### โครงสร้างหลัก

```html
<body class="bg-gradient-to-r from-blue-500 to-indigo-600 h-screen flex items-center justify-center">
    <!-- Container หลัก -->
    <div class="bg-white p-6 rounded-xl shadow-2xl w-80">
        
        <!-- หัวข้อ -->
        <h1 class="text-xl font-bold text-center">ยินดีต้อนรับ</h1>
        
        <!-- Form Login -->
        <form onsubmit="handleLogin(event)">
            <!-- Input Username -->
            <input type="text" id="username" required>
            
            <!-- Input Password -->
            <input type="password" id="password" required>
            
            <!-- ปุ่ม Submit -->
            <button type="submit">เข้าสู่ระบบ</button>
        </form>
        
        <!-- ลิงก์สมัครสมาชิก -->
        <a href="/api/register-page/">สมัครสมาชิกใหม่</a>
    </div>
</body>
```

### อธิบาย TailwindCSS Classes

| Class | ความหมาย |
|-------|----------|
| `bg-gradient-to-r` | พื้นหลังไล่สีจากซ้ายไปขวา |
| `from-blue-500 to-indigo-600` | ไล่จากน้ำเงินไปม่วง |
| `h-screen` | ความสูง = เต็มหน้าจอ |
| `flex items-center justify-center` | จัดให้อยู่ตรงกลาง |
| `bg-white` | พื้นหลังสีขาว |
| `p-6` | padding รอบด้าน 1.5rem |
| `rounded-xl` | มุมโค้ง |
| `shadow-2xl` | เงาหนัก |
| `w-80` | ความกว้าง 20rem |

### JavaScript: handleLogin()

```javascript
async function handleLogin(event) {
    event.preventDefault();  // ป้องกันหน้ารีเฟรช

    // 1. ดึงค่าจาก Input
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        // 2. ส่งข้อมูลไปที่ API
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            // 3. Login สำเร็จ: บันทึกลง LocalStorage
            localStorage.setItem('user', JSON.stringify(data.user));

            // 4. แสดง Popup และ Redirect
            Swal.fire({
                icon: 'success',
                title: 'สำเร็จ',
                text: 'กำลังเข้าสู่ระบบ...',
                timer: 1500,
                showConfirmButton: false
            }).then(() => {
                // Redirect ตาม Role
                const role = data.user.role;
                if (role === 'Staff' || role === 'Admin') {
                    window.location.href = '/api/staff-dashboard/';
                } else {
                    window.location.href = '/api/dashboard/';
                }
            });
        } else {
            // 5. Login ผิดพลาด
            Swal.fire('ข้อผิดพลาด', data.error, 'error');
        }
    } catch (error) {
        Swal.fire('Error', 'ไม่สามารถเชื่อมต่อ Server ได้', 'error');
    }
}
```

**อธิบาย Flow:**

```
User กดปุ่ม Login
        │
        ▼
┌─────────────────────────┐
│ event.preventDefault()  │  ← ป้องกันหน้ารีเฟรช
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ fetch('/api/login/')    │  ← เรียก API
│ POST { username, pass } │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ if (response.ok)        │  ← เช็คผลลัพธ์
└───────────┬─────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
 สำเร็จ           ผิดพลาด
    │               │
    ▼               ▼
localStorage    Swal.fire
.setItem()      ('error')
    │
    ▼
Redirect
```

---

## 🎯 อธิบาย staff_dashboard.html

### 1. Header แสดงข้อมูล User

```html
<header class="bg-white shadow-sm">
    <div class="flex justify-between items-center">
        <!-- Logo และชื่อระบบ -->
        <div class="flex items-center gap-3">
            <div class="bg-cyan-500 p-2 rounded-lg text-white">
                <!-- SVG Icon -->
            </div>
            <h1>ระบบจัดการติดตามการสั่งซื้อของโครงการ</h1>
        </div>
        
        <!-- ข้อมูล User และปุ่ม Logout -->
        <div class="flex items-center gap-4">
            <p id="user-name">Loading...</p>
            <p id="user-role">Loading...</p>
            <button onclick="logout()">ออกจากระบบ</button>
        </div>
    </div>
</header>
```

### 2. การ์ดเมนู

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    
    <!-- การ์ด 1 -->
    <div class="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition cursor-pointer"
         onclick="alertPhase(3)">
        
        <!-- Icon -->
        <div class="h-12 w-12 bg-red-100 text-red-500 rounded-lg">
            <!-- SVG -->
        </div>
        
        <!-- ชื่อเมนู -->
        <h3>รายการขอซื้อรออนุมัติ</h3>
        <p>ตรวจสอบและอนุมัติรายการขอซื้อ</p>
    </div>
    
    <!-- การ์ด 2, 3, ... -->
</div>
```

### 3. ตรวจสอบสิทธิ์การเข้าถึง

```javascript
// ดึงข้อมูล User จาก LocalStorage
const userStr = localStorage.getItem('user');

if (!userStr) {
    // ไม่มีข้อมูล User = ยังไม่ Login
    window.location.href = '/api/login-page/';
} else {
    const user = JSON.parse(userStr);
    
    // แสดงชื่อและ Role
    document.getElementById('user-name').innerText = user.username;
    document.getElementById('user-role').innerText = `${user.role} (${user.department})`;
    
    // เช็คสิทธิ์
    if (user.role !== 'Staff' && user.role !== 'Admin') {
        Swal.fire('Warning', 'Access Denied', 'error')
            .then(() => window.location.href = '/api/login-page/');
    }
    
    // แสดง Card Admin เฉพาะ Admin
    if (user.role === 'Admin') {
        document.getElementById('admin-only-card').classList.remove('hidden');
    }
}
```

### 4. ฟังก์ชัน Logout

```javascript
function logout() {
    localStorage.removeItem('user');  // ลบข้อมูล User
    window.location.href = '/api/login-page/';  // กลับหน้า Login
}
```

---

## 📊 LocalStorage

LocalStorage ใช้เก็บข้อมูลในเบราว์เซอร์

```javascript
// บันทึกข้อมูล
localStorage.setItem('user', JSON.stringify({
    id: 'abc123',
    username: 'john',
    role: 'Admin',
    department: 'IT'
}));

// อ่านข้อมูล
const user = JSON.parse(localStorage.getItem('user'));
console.log(user.username);  // "john"

// ลบข้อมูล
localStorage.removeItem('user');

// ลบทั้งหมด
localStorage.clear();
```

---

## 🍬 SweetAlert2 (Popup)

### แจ้งเตือนสำเร็จ
```javascript
Swal.fire({
    icon: 'success',
    title: 'สำเร็จ',
    text: 'บันทึกข้อมูลเรียบร้อย',
    timer: 1500,
    showConfirmButton: false
});
```

### แจ้งเตือน Error
```javascript
Swal.fire('ข้อผิดพลาด', 'ไม่สามารถบันทึกได้', 'error');
```

### ยืนยันก่อนลบ
```javascript
Swal.fire({
    title: 'ยืนยันการลบ?',
    text: 'ข้อมูลจะถูกลบถาวร!',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    confirmButtonText: 'ลบ',
    cancelButtonText: 'ยกเลิก'
}).then((result) => {
    if (result.isConfirmed) {
        // ทำการลบ
    }
});
```

---

## 🔄 การเรียก API ด้วย fetch()

```javascript
// GET Request
const response = await fetch('/api/projects/');
const data = await response.json();

// POST Request
const response = await fetch('/api/projects/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        project_name: 'โครงการใหม่',
        budget_total: 1000000
    })
});

// DELETE Request
await fetch(`/api/projects/${projectId}/`, {
    method: 'DELETE'
});

// PUT Request
await fetch(`/api/projects/${projectId}/`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        project_name: 'ชื่อใหม่',
        budget_total: 2000000
    })
});
```

---

## 📄 ไฟล์ถัดไป

→ [07-api-reference.md](./07-api-reference.md) - API Reference
