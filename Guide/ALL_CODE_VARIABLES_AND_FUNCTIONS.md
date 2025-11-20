# 🔍 ตัวแปรและหน้าที่ของโค้ด - ทั้งระบบ POTMS

---

## 📚 สารบัญ

1. [Database Layer](#1-database-layer---models)
2. [Backend API Layer](#2-backend-api-layer---views-serializers)
3. [Frontend Layer](#3-frontend-layer---html--javascript)
4. [Configuration Files](#4-configuration-files)
5. [Workflow Summary](#5-workflow-summary)

---

---

# 1. 📊 Database Layer - Models

## 1.1 Projects Model

### **ตัวแปร (Fields)**

```python
# POTMS/api/models.py

class Projects(models.Model):
    project_id = models.AutoField(primary_key=True)
    # ❓ คืออะไร: รหัสประจำตัว (ID)
    # 🔧 หน้าที่: 
    #    - ระบุโครงการแต่ละรายการ
    #    - Django สร้างอัตโนมัติ (1, 2, 3, ...)
    # 📤 ส่งไป: ViewSet สำหรับ UPDATE/DELETE
    # 📥 รับจาก: Database (auto-generated)
    
    project_code = models.CharField(max_length=50, unique=True)
    # ❓ คืออะไร: รหัสโครงการ (readable ID)
    # 🔧 หน้าที่:
    #    - ชื่อเดิมของโครงการที่ผู้คนใช้ (PRJ-001)
    #    - UNIQUE = ห้ามมีรหัสซ้ำ
    # 📤 ส่งไป: Frontend, API Response
    # 📥 รับจาก: Frontend (User Input)
    
    project_name = models.CharField(max_length=255)
    # ❓ คืออะไร: ชื่อเต็มของโครงการ
    # 🔧 หน้าที่: แสดงผลชื่อโครงการให้ผู้ใช้อ่าน
    # 📤 ส่งไป: Frontend (Display)
    # 📥 รับจาก: Frontend (User Input)
    
    budget_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    # ❓ คืออะไร: งบประมาณทั้งสิ้น
    # 🔧 หน้าที่:
    #    - เก็บจำนวนเงิน 12 ตัว โดย 2 ตัวเป็นทศนิยม
    #    - ใช้สำหรับคำนวณและรายงาน
    # 📤 ส่งไป: Frontend (Display + Format with Intl)
    # 📥 รับจาก: Frontend (User Input)
    
    status = models.CharField(max_length=50)
    # ❓ คืออะไร: สถานะของโครงการ
    # 🔧 หน้าที่:
    #    - ใช้กรองและค้นหา (ดำเนินการ, ปิด)
    #    - ใช้ Display ด้วยสี status badge
    # 📤 ส่งไป: Frontend (Display)
    # 📥 รับจาก: Frontend (User Input, Dropdown)
    
    class Meta:
        db_table = 'projects'  # ชื่อตารางใน MySQL Database
```

---

## 1.2 Vendors Model

```python
class Vendors(models.Model):
    vendor_id = models.AutoField(primary_key=True)
    # ❓ คืออะไร: รหัสประจำตัวผู้ขาย
    # 🔧 หน้าที่: ระบุผู้ขายแต่ละรายการ
    
    vendor_name = models.CharField(max_length=255)
    # ❓ คืออะไร: ชื่อบริษัท/ผู้ขาย
    # 🔧 หน้าที่: แสดงผลชื่อผู้ขาย + ค้นหา
    # 📤 ส่งไป: Frontend (Display)
    # 📥 รับจาก: Frontend (User Input)
    
    phone = models.CharField(max_length=50, blank=True, null=True)
    # ❓ คืออะไร: เบอร์โทรศัพท์
    # 🔧 หน้าที่: ติดต่อผู้ขาย
    # 📤 ส่งไป: Frontend (Display, Optional)
    # 📥 รับจาก: Frontend (User Input, Optional)
    # 🔹 blank=True, null=True = ไม่บังคับกรอก
    
    email = models.EmailField(max_length=255, blank=True, null=True)
    # ❓ คืออะไร: อีเมลติดต่อ
    # 🔧 หน้าที่: ติดต่อผู้ขาย + Validation
    # 📤 ส่งไป: Frontend (Display, Optional)
    # 📥 รับจาก: Frontend (User Input, Optional)
    
    class Meta:
        db_table = 'vendors'
```

---

## 1.3 MasterItems Model

```python
class MasterItems(models.Model):
    item_id = models.AutoField(primary_key=True)
    # ❓ คืออะไร: รหัสประจำตัวรายการ
    # 🔧 หน้าที่: ระบุรายการพัสดุแต่ละรายการ
    
    item_code = models.CharField(max_length=50, unique=True)
    # ❓ คืออะไร: รหัสพัสดุ
    # 🔧 หน้าที่:
    #    - ชื่อเดิมของรายการ (ITEM-001)
    #    - UNIQUE = ห้ามซ้ำ
    # 📤 ส่งไป: Frontend (Display)
    # 📥 รับจาก: Frontend (User Input)
    
    item_name = models.CharField(max_length=255)
    # ❓ คืออะไร: ชื่อรายการพัสดุ
    # 🔧 หน้าที่: แสดงผลชื่อรายการ
    # 📤 ส่งไป: Frontend (Display)
    # 📥 รับจาก: Frontend (User Input)
    
    standard_unit = models.CharField(max_length=50)
    # ❓ คืออะไร: หน่วยนับมาตรฐาน
    # 🔧 หน้าที่:
    #    - ระบุหน่วยนับ (ตัว, ชิ้น, กล่อง)
    #    - ใช้ Filter ใน Frontend
    # 📤 ส่งไป: Frontend (Display + Filter)
    # 📥 รับจาก: Frontend (User Input)
    
    created_at = models.DateTimeField(auto_now_add=True)
    # ❓ คืออะไร: เวลาที่สร้างรายการ
    # 🔧 หน้าที่:
    #    - บันทึกเวลาสร้าง
    #    - Django เพิ่มเวลาอัตโนมัติ
    #    - ไม่สามารถแก้ไขได้
    # 📤 ส่งไป: Frontend (Display with formatDate)
    # 📥 รับจาก: Database (auto-generated)
    
    class Meta:
        db_table = 'master_items'
```

---

---

# 2. 🐍 Backend API Layer - Views & Serializers

## 2.1 Serializers

### **ProjectSerializer**

```python
# POTMS/api/serializers.py

class ProjectSerializer(serializers.ModelSerializer):
    # ❓ คืออะไร: ตัวแปลง/ตรวจสอบข้อมูลโครงการ
    # 🔧 หน้าที่:
    #    - แปลง JSON (Request) → Python Dict
    #    - Validate ข้อมูลตามกฎของ Model
    #    - แปลง Model Instance → JSON (Response)
    
    class Meta:
        model = Projects  # เชื่อมกับ Model
        fields = '__all__'  # ใช้ทุก field: project_id, project_code, ...
```

**ขั้นตอนการใช้:**

```
Frontend (JSON)
     ↓
ProjectSerializer.is_valid()  ← Check ตามกฎ Model
     ↓ Valid
serializer.save()  ← Projects.objects.create()
     ↓
Response (JSON)
```

---

### **VendorSerializer & MasterItemSerializer**

```python
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendors
        fields = '__all__'

class MasterItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterItems
        fields = '__all__'
```

---

## 2.2 ViewSets (API Endpoints)

### **ProjectViewSet**

```python
# POTMS/api/views.py

class ProjectViewSet(viewsets.ModelViewSet):
    # ❓ คืออะไร: ตัวจัดการ API endpoint สำหรับ Projects
    # 🔧 หน้าที่:
    #    - ปรับปรุง HTTP Requests (GET, POST, PUT, DELETE)
    #    - ส่งต่อไปยัง Models/Serializers
    #    - ส่งคืน JSON Response
    
    queryset = Projects.objects.all()
    # ❓ คืออะไร: Query ทั้งหมด Projects
    # 🔧 หน้าที่: ใช้ในการ list/retrieve
    
    serializer_class = ProjectSerializer
    # ❓ คืออะไร: Serializer ที่ใช้สำหรับ Validation
    
    lookup_field = 'project_code'
    # ❓ คืออะไร: ใช้ project_code แทน project_id
    # 🔧 หน้าที่: GET /api/projects/PRJ-001/ (ไม่ใช่ /api/projects/1/)
    
    # --- Automatic Methods (from ModelViewSet) ---
    # GET    /api/projects/           → list() → ดึงทั้งหมด
    # POST   /api/projects/           → create() → สร้างใหม่
    # GET    /api/projects/PRJ-001/   → retrieve() → ดึงเฉพาะตัว
    # PUT    /api/projects/PRJ-001/   → update() → แก้ไข
    # DELETE /api/projects/PRJ-001/   → destroy() → ลบ
    
    @action(detail=False, methods=['post'], url_path='import-excel')
    def import_excel(self, request, *args, **kwargs):
        # ❓ คืออะไร: Custom action สำหรับ import Excel
        # 🔧 หน้าที่:
        #    - รับไฟล์ Excel จาก Frontend
        #    - อ่านข้อมูลด้วย pandas
        #    - Validate และ Save ลงฐานข้อมูล
        #    - ส่งคืน Response
        
        file = request.FILES.get('importFile')
        # ❓ ตัวแปร: ไฟล์ที่ upload มาจาก Frontend
        
        if not file:
            return Response(
                {'error': 'No file uploaded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            df = pd.read_excel(file)
            # ❓ ตัวแปร: DataFrame จาก Excel
            
            required_columns = ['project_code', 'project_name', 'budget_total', 'status']
            # ❓ ตัวแปร: Columns ที่จำเป็น
            
            if not all(col in df.columns for col in required_columns):
                return Response(
                    {'error': 'Missing required columns'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            for index, row in df.iterrows():
                # Loop แต่ละ row
                project_code = row['project_code']
                # ❓ ตัวแปร: รหัสโครงการจาก Excel
                
                data = {
                    'project_name': row['project_name'],
                    'budget_total': row['budget_total'],
                    'status': row['status']
                }
                # ❓ ตัวแปร: Dictionary ข้อมูล
                
                project = Projects.objects.filter(
                    project_code=project_code
                ).first()
                # ❓ ตัวแปร: ค้นหาว่ามี Project ในฐานข้อมูลหรือไม่
                
                if project:
                    # ถ้ามี = Update
                    serializer = self.get_serializer(
                        project,
                        data=data,
                        partial=True
                    )
                else:
                    # ถ้าไม่มี = Create ใหม่
                    data['project_code'] = project_code
                    serializer = self.get_serializer(data=data)
                
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(
                        {'error': f'Error at row {index + 2}: {serializer.errors}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return Response(
                {'message': f'Successfully imported/updated {len(df)} projects.'},
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
```

---

### **VendorViewSet & MasterItemViewSet**

```python
class VendorViewSet(viewsets.ModelViewSet):
    # ❓ คืออะไร: API endpoint สำหรับ Vendors
    queryset = Vendors.objects.all()
    serializer_class = VendorSerializer
    # 🔹 ไม่มี lookup_field = ใช้ vendor_id เป็นค่าเริ่มต้น
    # API: GET/POST /api/vendors/
    #      GET/PUT/DELETE /api/vendors/{vendor_id}/

class MasterItemViewSet(viewsets.ModelViewSet):
    # ❓ คืออะไร: API endpoint สำหรับ Master Items
    queryset = MasterItems.objects.all()
    serializer_class = MasterItemSerializer
    lookup_field = 'item_code'
    # 🔹 ใช้ item_code แทน item_id
    # API: GET/POST /api/master-items/
    #      GET/PUT/DELETE /api/master-items/{item_code}/
```

---

## 2.3 URL Configuration

```python
# POTMS/api/urls.py

from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, VendorViewSet, MasterItemViewSet

router = DefaultRouter()
# ❓ คืออะไร: Router ที่สร้าง URLs อัตโนมัติจาก ViewSet

router.register(r'projects', ProjectViewSet, basename='project')
# ❓ ความหมาย:
#    - Prefix: 'projects' → /api/projects/
#    - ViewSet: ProjectViewSet
#    - basename: ใช้สำหรับ reverse() และ URL naming

router.register(r'vendors', VendorViewSet)
router.register(r'master-items', MasterItemViewSet, basename='masteritem')

urlpatterns = router.urls
# ❓ URL patterns ที่สร้างขึ้น:
# GET    /api/projects/ → list
# POST   /api/projects/ → create
# GET    /api/projects/{project_code}/ → retrieve
# PUT    /api/projects/{project_code}/ → update
# DELETE /api/projects/{project_code}/ → destroy
```

---

---

# 3. 🌐 Frontend Layer - HTML & JavaScript

## 3.1 HTML Structure

### **Navbar**

```html
<div class="bg-white border-b px-6 py-4 flex justify-between items-center">
  <!-- ❓ Header ของหน้า -->
  <!-- 🔧 หน้าที่: แสดง Title และ User Profile -->
  
  <h1 class="text-2xl font-semibold">จัดการข้อมูลหลัก</h1>
  <!-- ❓ ตัวแปร: Title ของหน้า -->
  
  <div class="flex items-center gap-3">
    <!-- Profile Section -->
  </div>
</div>
```

---

### **Tabs Navigation**

```html
<div class="flex border-b px-6 pt-2">
  <button onclick="switchTab('projects')" id="tab-projects" class="tab-btn active">
    <!-- ❓ ตัวแปร: tab-projects -->
    <!-- 🔧 หน้าที่: ปุ่มเปลี่ยนแท็บ -->
    <!-- 📤 ส่งไป: switchTab('projects') function -->
    ข้อมูลโครงการ
  </button>
  
  <button onclick="switchTab('vendors')" id="tab-vendors" class="tab-btn">
    ข้อมูลผู้ขาย
  </button>
  
  <button onclick="switchTab('items')" id="tab-items" class="tab-btn">
    รายการพัสดุ
  </button>
</div>
```

---

### **Projects Table**

```html
<div id="content-projects" class="block">
  <!-- ❓ ตัวแปร: content-projects -->
  <!-- 🔧 หน้าที่: Container สำหรับแท็บ Projects -->
  
  <div class="flex gap-3">
    <button onclick="openModal('project')" class="bg-blue-600">
      <!-- 🔧 หน้าที่: ปุ่มสร้างโครงการใหม่ -->
      <!-- 📤 ส่งไป: openModal('project') -->
      เพิ่มโครงการ
    </button>
    
    <button onclick="document.getElementById('importFile').click()">
      <!-- 🔧 หน้าที่: ปุ่ม Import Excel -->
      <!-- 📤 ส่งไป: File input dialog -->
      Import/Update จากไฟล์
    </button>
    
    <input type="file" id="importFile" accept=".xlsx, .xls"
           onchange="handleImport(this)">
    <!-- ❓ ตัวแปร: importFile -->
    <!-- 🔧 หน้าที่: Input สำหรับเลือกไฟล์ -->
    <!-- 📥 รับจาก: User (File selection) -->
    <!-- 📤 ส่งไป: handleImport() function -->
  </div>
  
  <div class="text-gray-500">
    รวม <span id="project-count">0</span> โครงการ
    <!-- ❓ ตัวแปร: project-count -->
    <!-- 🔧 หน้าที่: แสดงจำนวนโครงการทั้งหมด -->
  </div>
  
  <table class="w-full">
    <thead>
      <tr>
        <th>หมายเลขโครงการ</th>
        <th>ชื่อโครงการ</th>
        <th>งบประมาณโครงการ</th>
        <th>สถานะ</th>
        <th>การกระทำ</th>
      </tr>
    </thead>
    <tbody id="project-table-body">
      <!-- ❓ ตัวแปร: project-table-body -->
      <!-- 🔧 หน้าที่: แสดงข้อมูลโครงการแต่ละแถว -->
      <!-- 📥 รับจาก: projectsData (JavaScript) -->
    </tbody>
  </table>
</div>
```

---

## 3.2 JavaScript Configuration & Variables

```javascript
// --- CONFIGURATION ---
const API_BASE_URL = "/api/";
// ❓ ตัวแปร: ที่อยู่ของ API Backend
// 🔧 หน้าที่: ใช้ใน fetchAPI() เพื่อเรียก API endpoint

let currentTab = "projects";
// ❓ ตัวแปร: แท็บปัจจุบันที่กำลังแสดง
// 🔧 หน้าที่: ติดตามว่าแท็บไหนกำลังเปิด
// 📤 ส่งไป: switchTab(), renderProjects/Vendors/Items()

let currentEditId = null;
// ❓ ตัวแปร: ID ของรายการที่กำลังแก้ไข
// 🔧 หน้าที่:
//    - null = สร้างใหม่
//    - "PRJ-001" = แก้ไข project นี้
// 📥 รับจาก: openModal() function
// 📤 ส่งไป: saveData() function

let projectsData = [];
// ❓ ตัวแปร: Array เก็บข้อมูลโครงการทั้งหมด
// 🔧 หน้าที่:
//    - เก็บ JSON response จาก API
//    - ใช้สำหรับ render table
// 📥 รับจาก: loadProjects() → fetchAPI()
// 📤 ส่งไป: renderProjects()

let vendorsData = [];
// ❓ ตัวแปร: Array เก็บข้อมูลผู้ขายทั้งหมด

let itemsData = [];
// ❓ ตัวแปร: Array เก็บข้อมูล Master Items ทั้งหมด
```

---

## 3.3 JavaScript Core Functions

### **Initialization**

```javascript
document.addEventListener("DOMContentLoaded", () => {
  // ❓ Event: เมื่อ HTML DOM โหลดเสร็จ
  // 🔧 หน้าที่: รันโค้ด initialization
  loadAllData();
  // ❓ Function: โหลดข้อมูลทั้งหมดจาก API
});
```

---

### **fetchAPI() - API Helper**

```javascript
function getCookie(name) {
  // ❓ Function: ดึง CSRF Token จาก Cookie
  // 🔧 หน้าที่: ใช้สำหรับ POST/PUT/DELETE requests
  // 📤 ส่งไป: fetchAPI() headers
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(
          cookie.substring(name.length + 1)
        );
        break;
      }
    }
  }
  return cookieValue;
}

async function fetchAPI(endpoint, method = "GET", body = null) {
  // ❓ Function: ดำเนินการ API requests
  // 🔧 หน้าที่:
  //    - สร้าง HTTP request ไปยัง Django API
  //    - Handle CSRF Token
  //    - Handle Errors
  // 📥 รับจาก: loadProjects(), saveData(), deleteData()
  
  const headers = {
    "Content-Type": "application/json",
    "X-CSRFToken": getCookie("csrftoken"),
    // ❓ CSRF Token: ป้องกัน Cross-Site Request Forgery
  };
  
  const config = { method, headers };
  if (body) config.body = JSON.stringify(body);
  // ❓ Body: ข้อมูลที่ส่งไป (JSON)
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    // ❓ fetch: ส่ง HTTP request ไปยัง API
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error || `HTTP error! status: ${response.status}`
      );
    }
    
    if (method === "DELETE") return true;
    return await response.json();
    // ❓ Return: JSON data จาก API
  } catch (error) {
    console.error("API Error:", error);
    alert("เกิดข้อผิดพลาด: " + error.message);
    return null;
  }
}
```

---

### **loadAllData() - Data Loading**

```javascript
async function loadAllData() {
  // ❓ Function: โหลดข้อมูลทั้งหมดจาก API
  // 🔧 หน้าที่: ดึงข้อมูล Projects, Vendors, Items พร้อมกัน
  
  await Promise.all([
    loadProjects(),
    loadVendors(),
    loadItems()
  ]);
  // ❓ Promise.all: รันฟังก์ชันทั้งหมดพร้อมกัน (ไม่เรียงลำดับ)
  
  // Render current tab
  if (currentTab === "projects") renderProjects();
  else if (currentTab === "vendors") renderVendors();
  else if (currentTab === "items") renderItems();
}

async function loadProjects() {
  // ❓ Function: โหลดข้อมูล Projects จาก API
  const data = await fetchAPI("projects/");
  // 📥 API Call: GET /api/projects/
  
  if (data) {
    projectsData = data.results || data;
    // ❓ ตัวแปร: เก็บข้อมูลใน projectsData
    // 🔹 รองรับ Pagination (data.results) และ Normal Array (data)
    renderProjects();
  }
}

async function loadVendors() {
  // ❓ Function: โหลดข้อมูล Vendors จาก API
  const data = await fetchAPI("vendors/");
  if (data) {
    vendorsData = data.results || data;
    renderVendors();
  }
}

async function loadItems() {
  // ❓ Function: โหลดข้อมูล Master Items จาก API
  const data = await fetchAPI("master-items/");
  if (data) {
    itemsData = data.results || data;
    renderItems();
  }
}
```

---

### **switchTab() - Tab Navigation**

```javascript
function switchTab(tab) {
  // ❓ Function: เปลี่ยนแท็บ
  // 🔧 หน้าที่:
  //    - เปลี่ยน currentTab
  //    - เปลี่ยนสไตล์ active ของ button
  //    - เปลี่ยน display ของ content
  //    - Render ข้อมูลใหม่
  
  currentTab = tab;
  // ❓ ตัวแปร: เก็บแท็บปัจจุบัน
  
  document.querySelectorAll(".tab-btn")
    .forEach((btn) => btn.classList.remove("active"));
  // ❓ Action: ลบ active class จากปุ่มทั้งหมด
  
  document.getElementById(`tab-${tab}`).classList.add("active");
  // ❓ Action: เพิ่ม active class ให้ปุ่มปัจจุบัน
  
  ["projects", "vendors", "items"].forEach((t) => {
    document.getElementById(`content-${t}`)
      .classList.toggle("hidden", t !== tab);
  });
  // ❓ Action: ซ่อนแท็บทั้งหมด ยกเว้นปัจจุบัน
  
  // Re-render
  if (tab === "projects") renderProjects();
  else if (tab === "vendors") renderVendors();
  else if (tab === "items") renderItems();
}
```

---

### **renderProjects() - Display Data**

```javascript
function renderProjects() {
  // ❓ Function: แสดงข้อมูล Projects ในตาราง
  // 🔧 หน้าที่:
  //    - ดึง DOM elements
  //    - Loop ผ่าน projectsData
  //    - สร้าง HTML rows
  //    - Insert ลง DOM
  
  const tbody = document.getElementById("project-table-body");
  // ❓ ตัวแปร: tbody element
  
  tbody.innerHTML = "";
  // ❓ Action: ล้างข้อมูลเก่า
  
  document.getElementById("project-count").innerText = projectsData.length;
  // ❓ Action: อัพเดท count
  
  if (projectsData.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center">ไม่พบข้อมูล</td></tr>`;
    return;
  }
  
  projectsData.forEach((p) => {
    // ❓ Loop: แต่ละโครงการ
    
    const statusClass = p.status === "ดำเนินการ"
      ? "bg-green-100 text-green-700"
      : "bg-gray-100 text-gray-700";
    // ❓ ตัวแปร: CSS class ตามสถานะ
    
    tbody.innerHTML += `
      <tr class="hover:bg-gray-50">
        <td class="px-6 py-4">${p.project_code}</td>
        <!-- ❓ project_code: แสดง code -->
        
        <td class="px-6 py-4">${p.project_name}</td>
        <!-- ❓ project_name: แสดง name -->
        
        <td class="px-6 py-4">${formatCurrency(p.budget_total)}</td>
        <!-- ❓ budget_total: แสดง budget (formatted) -->
        
        <td class="px-6 py-4">
          <span class="px-3 py-1 rounded-full ${statusClass}">
            ${p.status}
          </span>
        </td>
        <!-- ❓ status: แสดง status badge -->
        
        <td class="px-6 py-4 text-right">
          <button onclick="openModal('project', '${p.project_code}')">
            <!-- 🔧 Edit Button: เปิด Modal เพื่อแก้ไข -->
            แก้ไข
          </button>
          <button onclick="deleteData('projects', '${p.project_code}')">
            <!-- 🔧 Delete Button: ลบรายการ -->
            ลบ
          </button>
        </td>
      </tr>
    `;
  });
}

function renderVendors() {
  // ❓ Function: แสดงข้อมูล Vendors ในตาราง
  const tbody = document.getElementById("vendor-table-body");
  const search = document.getElementById("search-vendor").value.toLowerCase();
  // ❓ ตัวแปร: ค้นหา keyword จาก input
  
  tbody.innerHTML = "";
  
  const filtered = vendorsData.filter((v) =>
    v.vendor_name.toLowerCase().includes(search)
    // ❓ Filter: เฉพาะ vendor ที่ชื่อมี search keyword
  );
  
  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="text-center">ไม่พบข้อมูล</td></tr>`;
    return;
  }
  
  filtered.forEach((v) => {
    tbody.innerHTML += `
      <tr>
        <td class="px-6 py-4">${v.vendor_name}</td>
        <td class="px-6 py-4">${v.phone || "-"}</td>
        <td class="px-6 py-4">${v.email || "-"}</td>
        <td class="px-6 py-4 text-right">
          <button onclick="openModal('vendor', ${v.vendor_id})">แก้ไข</button>
          <button onclick="deleteData('vendors', ${v.vendor_id})">ลบ</button>
        </td>
      </tr>
    `;
  });
}

function renderItems() {
  // ❓ Function: แสดงข้อมูล Master Items ในตาราง
  const tbody = document.getElementById("item-table-body");
  const search = document.getElementById("search-item").value.toLowerCase();
  const filterUnit = document.getElementById("filter-unit").value;
  // ❓ ตัวแปร: Filter ด้วย unit
  
  tbody.innerHTML = "";
  
  const filtered = itemsData.filter((i) => {
    const matchSearch = i.item_name.toLowerCase().includes(search) ||
                       i.item_code.toLowerCase().includes(search);
    const matchUnit = filterUnit === "" || i.standard_unit === filterUnit;
    // ❓ Filter: ชื่อ + unit
    return matchSearch && matchUnit;
  });
  
  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center">ไม่พบข้อมูล</td></tr>`;
    return;
  }
  
  filtered.forEach((i) => {
    tbody.innerHTML += `
      <tr>
        <td class="px-6 py-4">${i.item_code}</td>
        <td class="px-6 py-4">${i.item_name}</td>
        <td class="px-6 py-4"><span class="bg-gray-100">${i.standard_unit}</span></td>
        <td class="px-6 py-4 text-gray-500 text-xs">${formatDate(i.created_at)}</td>
        <td class="px-6 py-4 text-right">
          <button onclick="openModal('item', '${i.item_code}')">แก้ไข</button>
          <button onclick="deleteData('master-items', '${i.item_code}')">ลบ</button>
        </td>
      </tr>
    `;
  });
}
```

---

### **openModal() - CRUD Create/Edit**

```javascript
async function openModal(type, id = null) {
  // ❓ Function: เปิด Modal สำหรับสร้างหรือแก้ไข
  // 🔧 หน้าที่:
  //    - กำหนด currentEditId
  //    - เตรียม form fields ตามประเภท
  //    - ถ้า id มี = แสดงข้อมูลเดิม (Edit Mode)
  //    - ถ้า id ไม่มี = form ว่าง (Create Mode)
  
  currentEditId = id;
  // ❓ ตัวแปร: เก็บ id ที่กำลังแก้ไข
  
  document.getElementById("modal-overlay").classList.remove("hidden");
  // ❓ Action: แสดง Modal
  
  const container = document.getElementById("modal-form-container");
  
  let data = {};
  // ❓ ตัวแปร: ข้อมูลจาก localStorage (projectsData, etc.)
  
  if (id) {
    // ❓ Condition: ถ้า id มี = Edit Mode
    if (type === "project")
      data = projectsData.find((p) => p.project_code === id);
    // ❓ Action: ค้นหาข้อมูลจาก projectsData
  }
  
  if (type === "project") {
    // ❓ Condition: สร้าง form สำหรับ Projects
    const title = document.getElementById("modal-title");
    title.innerText = id ? "แก้ไขโครงการ" : "เพิ่มโครงการใหม่";
    
    container.innerHTML = `
      <input type="text" id="inp-code" value="${data.project_code || ''}"
             ${id ? "readonly" : ""}>
      <!-- ❓ inp-code: readonly ถ้า edit (ห้ามเปลี่ยน code) -->
      
      <input type="text" id="inp-name" value="${data.project_name || ''}">
      <!-- ❓ inp-name: project_name -->
      
      <input type="number" id="inp-budget" value="${data.budget_total || ''}">
      <!-- ❓ inp-budget: budget_total -->
      
      <select id="inp-status">
        <option value="ดำเนินการ" ${data.status === "ดำเนินการ" ? "selected" : ""}>
          ดำเนินการ
        </option>
        <option value="ปิด" ${data.status === "ปิด" ? "selected" : ""}>
          ปิด
        </option>
      </select>
      <!-- ❓ inp-status: status dropdown -->
    `;
  }
  // ... similar for vendor, item
}

function closeModal() {
  // ❓ Function: ปิด Modal
  document.getElementById("modal-overlay").classList.add("hidden");
}
```

---

### **saveData() - CRUD Save (POST/PUT)**

```javascript
async function saveData() {
  // ❓ Function: บันทึกข้อมูล (สร้างหรือแก้ไข)
  // 🔧 หน้าที่:
  //    - รวบรวมข้อมูลจาก form inputs
  //    - ส่ง POST (สร้าง) หรือ PUT (แก้ไข)
  //    - Reload ข้อมูล
  //    - ปิด Modal
  
  let endpoint, body, method;
  
  if (currentTab === "projects") {
    endpoint = "projects/";
    
    body = {
      // ❓ ตัวแปร: ข้อมูลจาก form inputs
      project_code: document.getElementById("inp-code").value,
      project_name: document.getElementById("inp-name").value,
      budget_total: document.getElementById("inp-budget").value,
      status: document.getElementById("inp-status").value,
    };
    
    if (currentEditId) {
      // ❓ Condition: ถ้า currentEditId มี = PUT (Update)
      method = "PUT";
      endpoint += `${currentEditId}/`;
    } else {
      // ❓ Condition: ถ้า currentEditId ไม่มี = POST (Create)
      method = "POST";
    }
  }
  
  const result = await fetchAPI(endpoint, method, body);
  // ❓ API Call: ส่ง request ไปยัง API
  
  if (result) {
    alert("บันทึกข้อมูลสำเร็จ");
    closeModal();
    loadAllData();  // ❓ Action: โหลดข้อมูลใหม่
  }
}
```

---

### **deleteData() - CRUD Delete**

```javascript
async function deleteData(endpointType, id) {
  // ❓ Function: ลบข้อมูล
  // 🔧 หน้าที่:
  //    - ยืนยันการลบ (confirm)
  //    - ส่ง DELETE request
  //    - Reload ข้อมูล
  
  if (!confirm("ยืนยันการลบข้อมูล?")) return;
  // ❓ Action: ยืนยันก่อนลบ
  
  const result = await fetchAPI(`${endpointType}/${id}/`, "DELETE");
  // ❓ API Call: DELETE /api/{endpointType}/{id}/
  
  if (result) {
    alert("ลบข้อมูลสำเร็จ");
    loadAllData();  // ❓ Action: โหลดข้อมูลใหม่
  }
}
```

---

### **handleImport() - Import Excel**

```javascript
async function handleImport(input) {
  // ❓ Function: Import ข้อมูลจาก Excel file
  // 🔧 หน้าที่:
  //    - ดึงไฟล์จาก input
  //    - ส่ง POST request กับ FormData
  //    - Reload Projects
  
  if (!input.files || input.files.length === 0) return;
  
  const formData = new FormData();
  // ❓ ตัวแปร: FormData (ใช้สำหรับ file upload)
  
  formData.append("importFile", input.files[0]);
  // ❓ Action: เพิ่มไฟล์ลง FormData
  
  try {
    const response = await fetch(
      `${API_BASE_URL}projects/import-excel/`,
      // ❓ Endpoint: POST /api/projects/import-excel/
      {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        body: formData,
      }
    );
    
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Upload failed");
    
    alert(result.message || "Import สำเร็จ");
    loadProjects();  // ❓ Action: โหลดข้อมูลใหม่
  } catch (error) {
    alert("Error: " + error.message);
  }
  
  input.value = "";  // ❓ Action: Reset input
}
```

---

### **Utility Functions**

```javascript
function formatCurrency(amount) {
  // ❓ Function: แปลงตัวเลขเป็นสกุลเงิน
  // 🔧 หน้าที่: Display budget ด้วยรูปแบบสกุลเงินไทย
  return new Intl.NumberFormat("th-TH", {
    style: "currency",
    currency: "THB",
  }).format(amount);
  // ❓ Output: "฿1,500,000.00"
}

function formatDate(dateString) {
  // ❓ Function: แปลงวันที่เป็นรูปแบบไทย
  // 🔧 หน้าที่: Display created_at ด้วยรูปแบบไทย
  if (!dateString) return "-";
  return new Date(dateString).toLocaleDateString("th-TH", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
  // ❓ Output: "19/11/2567"
}
```

---

---

# 4. ⚙️ Configuration Files

## 4.1 settings.py - Django Configuration

```python
# POTMS/backend/settings.py

SECRET_KEY = 'django-insecure-...'
# ❓ ตัวแปร: Secret key สำหรับ encrypt
# 🔧 หน้าที่: ป้องกัน Session hijacking
# ⚠️ หมายเหตุ: ห้ามเปิดเผยใน Production

DEBUG = True
# ❓ ตัวแปร: Debug mode
# 🔧 หน้าที่: แสดง error details (เฉพาะ Development)
# ⚠️ หมายเหตุ: ต้องเป็น False ใน Production

ALLOWED_HOSTS = []
# ❓ ตัวแปร: Hosts ที่อนุญาต
# 🔧 หน้าที่: ป้องกัน Host Header Attack
# ตัวอย่าง Production: ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

INSTALLED_APPS = [
    'corsheaders',          # 🔹 ให้ Frontend เรียก API ได้
    'rest_framework',       # 🔹 Django REST Framework
    'api',                  # 🔹 แอพ API ของเรา
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ❓ CORS Middleware
    # 🔧 หน้าที่: อนุญาต Cross-Origin Requests
    # ... other middleware
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # ❓ ENGINE: MySQL database driver
        
        'NAME': 'potms',
        # ❓ NAME: ชื่อฐานข้อมูล
        
        'USER': 'root',
        # ❓ USER: ชื่อผู้ใช้ MySQL
        
        'PASSWORD': 'BookReserve2025',
        # ❓ PASSWORD: รหัสผ่าน MySQL
        
        'HOST': 'localhost',
        # ❓ HOST: ที่อยู่ MySQL server
        
        'PORT': '3306',
        # ❓ PORT: พอร์ต MySQL
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",      # ❓ Frontend dev server
    "http://127.0.0.1:5173",
]
# 🔧 หน้าที่: อนุญาต Frontend localhost requests
```

---

## 4.2 manage.py - Django CLI

```python
# POTMS/manage.py

if __name__ == '__main__':
    main()
```

**ใช้สำหรับ:**

```bash
# รัน server
python manage.py runserver

# สร้าง migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# สร้าง superuser
python manage.py createsuperuser

# Open shell
python manage.py shell

# Pop populate data
python manage.py populate_db --clear
```

---

---

# 5. 🔄 Workflow Summary

## **Complete Request-Response Flow**

```
┌─────────────────────────────────────────────────────────┐
│ 1. FRONTEND (HTML + JavaScript)                         │
│    - User clicks "เพิ่มโครงการ"                         │
│    - openModal('project') triggered                    │
└─────────────────────┬───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 2. JAVASCRIPT - PREPARE DATA                            │
│    - Form inputs collected                             │
│    - saveData() called                                 │
│    - body = {project_code, project_name, ...}          │
└─────────────────────┬───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 3. FETCH API REQUEST                                    │
│    - fetchAPI('projects/', 'POST', body)               │
│    - Headers: CSRF Token                               │
│    - Body: JSON                                        │
└─────────────────────┬───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 4. DJANGO URL ROUTER (urls.py)                          │
│    - Matches: POST /api/projects/                       │
│    - Routes to: ProjectViewSet.create()                │
└─────────────────────┬───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 5. VIEWSET - CREATE METHOD (views.py)                   │
│    - Receives request.data (JSON)                       │
│    - Calls ProjectSerializer(data=request.data)        │
└─────────────────────┬───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 6. SERIALIZER - VALIDATE & SAVE (serializers.py)        │
│    - serializer.is_valid()                             │
│    - Validates against Projects model                  │
│    - serializer.save() → ORM create()                  │
└─────────────────────┬───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 7. ORM - DATABASE (models.py)                           │
│    - Projects.objects.create(**data)                   │
│    - SQL: INSERT INTO projects ...                     │
└─────────────────────┬───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 8. MYSQL DATABASE                                       │
│    - Row inserted into projects table                  │
│    - Returns new instance with ID                      │
└─────────────────────┬───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 9. SERIALIZER - TO JSON (serializers.py)                │
│    - Model instance → serializer.data                  │
│    - Returns JSON response                             │
└─────────────────────┬───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 10. VIEWSET - RETURN RESPONSE (views.py)                │
│     - HTTP 201 Created                                  │
│     - Body: JSON (project_id, project_code, ...)        │
└─────────────────────┬───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 11. JAVASCRIPT - RECEIVE & PROCESS (S08_Master_Data.html)
│     - result = await response.json()                    │
│     - closeModal()                                      │
│     - loadAllData() → Refresh table                     │
└─────────────────────┬───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 12. RENDER - UPDATE TABLE (JavaScript)                  │
│     - renderProjects() regenerates table                │
│     - New project appears in table                      │
│     - Success message shown to user                     │
└─────────────────────────────────────────────────────────┘
```

---

## **Data Variable Mapping**

| Layer | Variable | Type | Content | Flow |
|-------|----------|------|---------|------|
| **Frontend** | form input | HTML | User enters "PRJ-001" | User Input |
| **JavaScript** | inp-code | DOM Element | "PRJ-001" | Extract |
| **JS** | body | Object | {project_code: "PRJ-001", ...} | Build |
| **API** | request.data | Dict | {project_code: "PRJ-001", ...} | Receive |
| **Serializer** | data | Dict | Validated data | Validate |
| **ORM** | Projects object | Model | Instance with values | Create |
| **Database** | projects row | SQL | INSERT statement | Execute |
| **Return** | projectsData | Array | [{id:1, code:"PRJ-001", ...}] | Store |
| **Render** | table row | HTML | `<tr><td>PRJ-001</td>...</tr>` | Display |

---

## **Key Variables Reference**

```
🔹 Frontend:
   - projectsData, vendorsData, itemsData: Arrays เก็บข้อมูล
   - currentTab: แท็บปัจจุบัน
   - currentEditId: ID ของรายการที่ edit
   - API_BASE_URL: Base URL ของ API

🔹 Backend:
   - Projects, Vendors, MasterItems: Models
   - ProjectSerializer, VendorSerializer, MasterItemSerializer: Serializers
   - ProjectViewSet, VendorViewSet, MasterItemViewSet: ViewSets

🔹 Database:
   - projects, vendors, master_items: Tables
   - project_id, project_code, project_name, budget_total, status: Columns
```

---

**🎉 ตอนนี้คุณเข้าใจโค้ดทั้งระบบแล้ว!** 🚀
