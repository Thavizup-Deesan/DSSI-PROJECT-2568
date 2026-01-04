# Phase 4: ฟีเจอร์ Budget Summary Report (รายงานสรุปงบประมาณ)

> **วันที่สร้าง:** 4 มกราคม 2026

## ภาพรวม

ฟีเจอร์นี้เพิ่มหน้า **รายงานสรุปงบประมาณ** บน Staff Dashboard แสดงข้อมูล:
- งบประมาณรวมทุกโครงการ
- ยอดใช้จ่ายจริง
- ยอดจองไว้ (รออนุมัติ)
- ยอดคงเหลือ
- ตารางแสดงงบแต่ละโครงการ + Progress Bar

---

## ไฟล์ที่เกี่ยวข้อง

| ไฟล์ | หน้าที่ |
|------|---------|
| `api/views.py` | สร้าง `BudgetSummaryAPIView` API |
| `api/urls.py` | เพิ่ม URL routes |
| `api/templates/staff_reports.html` | หน้า UI รายงาน |
| `api/templates/staff_dashboard.html` | อัปเดตลิงก์ปุ่ม Reports |

---

## 1. Backend API: `BudgetSummaryAPIView`

**ไฟล์:** `api/views.py`

```python
class BudgetSummaryAPIView(APIView):
    """
    Endpoint: GET /api/budget-summary/
    
    Returns:
        JSON: {
            total_budget: float,
            total_spent: float,
            total_reserved: float,
            total_remaining: float,
            projects: [...]
        }
    """
    
    def get(self, request):
        try:
            # 1. ดึงข้อมูลโครงการทั้งหมดจาก Firestore
            projects_ref = db.collection('projects')
            projects_docs = projects_ref.stream()
            
            # 2. ตัวแปรเก็บยอดรวม
            total_budget = 0
            total_spent = 0
            total_reserved = 0
            projects_list = []
            
            # 3. วนลูปทุกโครงการ
            for doc in projects_docs:
                project = doc.to_dict()
                project_id = doc.id
                
                # ดึงค่างบประมาณ (ถ้าไม่มีให้ใช้ 0)
                budget_total = float(project.get('budget_total', 0))
                budget_spent = float(project.get('budget_spent', 0))
                budget_reserved = float(project.get('budget_reserved', 0))
                budget_remaining = budget_total - budget_spent - budget_reserved
                
                # สะสมยอดรวม
                total_budget += budget_total
                total_spent += budget_spent
                total_reserved += budget_reserved
                
                # คำนวณเปอร์เซนต์การใช้งาน
                usage_percent = 0
                if budget_total > 0:  # ป้องกันหารด้วย 0
                    usage_percent = round(((budget_spent + budget_reserved) / budget_total) * 100, 1)
                
                # เพิ่มเข้า list
                projects_list.append({
                    'project_id': project_id,
                    'project_name': project.get('project_name', '-'),
                    'budget_total': budget_total,
                    'budget_spent': budget_spent,
                    'budget_reserved': budget_reserved,
                    'budget_remaining': max(0, budget_remaining),
                    'usage_percent': usage_percent,
                    'status': project.get('status', 'Active')
                })
            
            total_remaining = total_budget - total_spent - total_reserved
            
            # 4. ส่งผลลัพธ์กลับ
            return Response({
                'total_budget': total_budget,
                'total_spent': total_spent,
                'total_reserved': total_reserved,
                'total_remaining': max(0, total_remaining),
                'projects': projects_list
            })
```

### อธิบาย Syntax:

| Syntax | ความหมาย |
|--------|----------|
| `db.collection('projects').stream()` | ดึงข้อมูลทั้งหมดจาก Collection 'projects' |
| `doc.to_dict()` | แปลง Firestore Document เป็น Python Dictionary |
| `project.get('budget_total', 0)` | ดึงค่า `budget_total` ถ้าไม่มีให้ใช้ `0` |
| `float(...)` | แปลงเป็นตัวเลขทศนิยม |
| `round(x, 1)` | ปัดเศษให้เหลือ 1 ตำแหน่ง |
| `max(0, value)` | เอาค่าที่มากกว่า (ป้องกันค่าติดลบ) |

---

## 2. URL Routing

**ไฟล์:** `api/urls.py`

```python
# เพิ่ม import
from .views import BudgetSummaryAPIView, staff_reports_view

# เพิ่ม URL patterns
urlpatterns = [
    ...
    # Reports & Budget Summary APIs
    path('budget-summary/', BudgetSummaryAPIView.as_view(), name='budget-summary'),
    path('staff/reports/', staff_reports_view, name='staff-reports'),
]
```

### URL Endpoints:

| URL | Method | หน้าที่ |
|-----|--------|---------|
| `/api/budget-summary/` | GET | API ส่ง JSON ข้อมูลงบประมาณ |
| `/api/staff/reports/` | GET | แสดงหน้า HTML รายงาน |

---

## 3. Frontend: `staff_reports.html`

### โครงสร้าง HTML:

```html
<!-- 4 Cards สรุปงบประมาณ -->
<div class="grid grid-cols-4 gap-4">
    <!-- Card งบประมาณรวม -->
    <div class="gradient-card card-blue">
        <p>งบประมาณรวม</p>
        <p id="totalBudget">฿0</p>
    </div>
    
    <!-- Card ใช้จ่ายแล้ว -->
    <div class="gradient-card card-green">
        <p>ใช้จ่ายแล้ว</p>
        <p id="totalSpent">฿0</p>
    </div>
    
    <!-- Card จองไว้ -->
    <div class="gradient-card card-yellow">
        <p>จองไว้</p>
        <p id="totalReserved">฿0</p>
    </div>
    
    <!-- Card คงเหลือ -->
    <div class="gradient-card card-purple">
        <p>คงเหลือ</p>
        <p id="totalRemaining">฿0</p>
    </div>
</div>

<!-- ตารางโครงการ -->
<table>
    <thead>
        <tr>
            <th>โครงการ</th>
            <th>งบทั้งหมด</th>
            <th>ใช้ไป</th>
            <th>จองไว้</th>
            <th>คงเหลือ</th>
            <th>สถานะ (Progress Bar)</th>
        </tr>
    </thead>
    <tbody id="projectsTable">
        <!-- JavaScript จะเพิ่มแถวที่นี่ -->
    </tbody>
</table>
```

### JavaScript Logic:

```javascript
async function loadBudgetData() {
    // 1. แสดง Loading
    document.getElementById('loadingState').classList.remove('hidden');
    
    try {
        // 2. เรียก API
        const response = await fetch('/api/budget-summary/');
        const data = await response.json();
        
        // 3. อัปเดตตัวเลขใน Card
        document.getElementById('totalBudget').textContent = `฿${formatNumber(data.total_budget)}`;
        document.getElementById('totalSpent').textContent = `฿${formatNumber(data.total_spent)}`;
        document.getElementById('totalReserved').textContent = `฿${formatNumber(data.total_reserved)}`;
        document.getElementById('totalRemaining').textContent = `฿${formatNumber(data.total_remaining)}`;
        
        // 4. สร้างตาราง
        const tbody = document.getElementById('projectsTable');
        data.projects.forEach(project => {
            const progressColor = getProgressColor(project.usage_percent);
            tbody.innerHTML += `
                <tr>
                    <td>${project.project_name}</td>
                    <td>฿${formatNumber(project.budget_total)}</td>
                    <td>฿${formatNumber(project.budget_spent)}</td>
                    <td>฿${formatNumber(project.budget_reserved)}</td>
                    <td>฿${formatNumber(project.budget_remaining)}</td>
                    <td>
                        <div class="progress-bar">
                            <div class="${progressColor}" style="width: ${project.usage_percent}%"></div>
                        </div>
                        <span>${project.usage_percent}%</span>
                    </td>
                </tr>
            `;
        });
        
        // 5. ซ่อน Loading, แสดง Content
        document.getElementById('loadingState').classList.add('hidden');
        document.getElementById('contentArea').classList.remove('hidden');
        
    } catch (error) {
        Swal.fire('เกิดข้อผิดพลาด', 'ไม่สามารถโหลดข้อมูลได้', 'error');
    }
}

// 6. เรียกฟังก์ชันเมื่อโหลดหน้าเสร็จ
document.addEventListener('DOMContentLoaded', loadBudgetData);
```

### อธิบาย Syntax JavaScript:

| Syntax | ความหมาย |
|--------|----------|
| `async function` | ฟังก์ชันที่รอผลลัพธ์ได้ (Asynchronous) |
| `await fetch(url)` | เรียก API และรอผลลัพธ์ |
| `response.json()` | แปลง Response เป็น JSON Object |
| `classList.add/remove('hidden')` | เพิ่ม/ลบ CSS class (ซ่อน/แสดง Element) |
| `element.textContent = 'text'` | ใส่ข้อความใน Element |
| `element.innerHTML += '...'` | เพิ่ม HTML เข้าไปใน Element |
| `DOMContentLoaded` | Event ที่เกิดเมื่อหน้าโหลดเสร็จ |
| `forEach(callback)` | วนลูปทุก element ใน Array |

---

## 4. อัปเดต Staff Dashboard

**ไฟล์:** `api/templates/staff_dashboard.html`

**เปลี่ยนจาก:**
```html
<div onclick="alertPhase(4)">
```

**เป็น:**
```html
<div onclick="window.location.href='/api/staff/reports/'">
```

---

## Flow การทำงาน

```
User คลิก "รายงานสรุป" ใน Staff Dashboard
        ↓
เปิดหน้า /api/staff/reports/ (staff_reports.html)
        ↓
JavaScript เรียก loadBudgetData()
        ↓
fetch('/api/budget-summary/') → Backend
        ↓
BudgetSummaryAPIView ดึงข้อมูลจาก Firestore
        ↓
คำนวณ: total, spent, reserved, remaining, usage_percent
        ↓
ส่ง JSON กลับ Frontend
        ↓
JavaScript อัปเดต Card และสร้าง Table
        ↓
User เห็นรายงานสรุปงบประมาณ ✅
```

---

## ตัวอย่าง API Response

```json
{
  "total_budget": 50000000,
  "total_spent": 15000000,
  "total_reserved": 5000000,
  "total_remaining": 30000000,
  "projects": [
    {
      "project_id": "abc123",
      "project_name": "โครงการสร้างคลังข้อมูล",
      "budget_total": 7200000,
      "budget_spent": 500000,
      "budget_reserved": 300000,
      "budget_remaining": 6400000,
      "usage_percent": 11.1,
      "status": "Active"
    }
  ]
}
```
