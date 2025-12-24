# 📘 คำอธิบายโค้ดทั้งหมด - POTMS Project

**ชื่อโปรเจค:** Project & Operations Task Management System  
**เวลาอัพเดต:** December 16, 2025  
**ภาษา:** Django + Firebase + JavaScript/HTML

---

# 📚 สารบัญ

1. [Architecture Overview](#1-architecture-overview)
2. [Backend Structure](#2-backend-structure)
3. [Database Layer (Firebase/MySQL)](#3-database-layer)
4. [API ViewSets & Views](#4-api-viewsets--views)
5. [Serializers (Data Validation)](#5-serializers-data-validation)
6. [Frontend Layer](#6-frontend-layer)
7. [Complete Request-Response Flow](#7-complete-request-response-flow)
8. [Utilities & Helpers](#8-utilities--helpers)

---

---

# 1. 🏗️ Architecture Overview

## System Architecture (3-Tier)

```
┌─────────────────────────────────────────────────────┐
│            FRONTEND LAYER (UI)                       │
│  HTML + Tailwind CSS + JavaScript + Fetch API       │
│                                                     │
│  File: api/templates/S08_Master_Data.html          │
│  Port: http://localhost:8000/                       │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ HTTP Request (JSON)
                   ↓
┌─────────────────────────────────────────────────────┐
│          BACKEND LAYER (Business Logic)              │
│  Django + Django REST Framework                     │
│                                                     │
│  Files: views.py, serializers.py, urls.py          │
│  Port: http://localhost:8000/api/                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ ORM/Queries
                   ↓
┌─────────────────────────────────────────────────────┐
│       DATABASE LAYER (Data Persistence)              │
│  Firebase Firestore + MySQL (MySQL in production)   │
│                                                     │
│  Models: Projects, Vendors, MasterItems             │
│  Database: potms (MySQL) or Firestore              │
└─────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer               | Technology                      | Version | Purpose        |
| ------------------- | ------------------------------- | ------- | -------------- |
| **Frontend**        | HTML5, Tailwind CSS, JavaScript | ES6+    | User Interface |
| **Backend**         | Django                          | 5.2.6   | Web Framework  |
| **API**             | Django REST Framework           | 3.16.1  | RESTful API    |
| **Database**        | Firebase / MySQL                | -       | Data Storage   |
| **Data Processing** | Pandas                          | 2.3.3   | Excel Import   |
| **Environment**     | Python                          | 3.9+    | Runtime        |

---

---

# 2. 🔧 Backend Structure

## Folder Layout

```
POTMS/
├── manage.py                    # Django CLI entry point
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables (development)
│
├── api/                        # Django App
│   ├── models.py               # ORM Models (Projects, Vendors, MasterItems)
│   ├── serializers.py          # Data validation & transformation
│   ├── views.py                # API endpoints & business logic
│   ├── urls.py                 # URL routing
│   ├── admin.py                # Django admin configuration
│   ├── apps.py                 # App configuration
│   ├── tests.py                # Unit tests
│   │
│   ├── migrations/             # Database migrations
│   │   ├── __init__.py
│   │   ├── 0001_initial.py     # Create initial models
│   │   └── 0002_*.py           # Schema changes
│   │
│   └── templates/              # HTML templates
│       └── S08_Master_Data.html # Main UI page
│
├── backend/                    # Django Project Settings
│   ├── settings.py             # Django configuration
│   ├── urls.py                 # Main URL router
│   ├── wsgi.py                 # WSGI application
│   ├── asgi.py                 # ASGI application
│   └── firebase_config.py      # Firebase initialization
│
└── vercel.json                 # Vercel deployment config
```

---

---

# 3. 🗄️ Database Layer

## 3.1 Models Definition (models.py)

### **Projects Model**

```python
class Projects(models.Model):
    project_id = models.AutoField(primary_key=True)
    # ❓ ตัวแปร: project_id
    # 🔧 หน้าที่: Primary key สำหรับระบุโครงการ
    # 📊 Type: Integer (auto-increment)
    # 🔹 ตัวอย่าง: 1, 2, 3, ...

    project_code = models.CharField(max_length=50, unique=True)
    # ❓ ตัวแปร: project_code
    # 🔧 หน้าที่: Unique identifier สำหรับโครงการ
    # 📊 Type: String, max 50 characters
    # 🔹 ตัวอย่าง: "PRJ-001", "PRJ-AI-2025"
    # ⚠️ Unique constraint: ไม่สามารถซ้ำได้

    project_name = models.CharField(max_length=255)
    # ❓ ตัวแปร: project_name
    # 🔧 หน้าที่: ชื่อของโครงการ
    # 📊 Type: String, max 255 characters
    # 🔹 ตัวอย่าง: "โครงการพัฒนา AI", "Project X"

    budget_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    # ❓ ตัวแปร: budget_total
    # 🔧 หน้าที่: งบประมาณรวมของโครงการ
    # 📊 Type: Decimal (ที่มี 2 ตำแหน่งทศนิยม)
    # 💰 ตัวอย่าง: 1500000.00, 5000000.50
    # 📏 Max: 999999999999.99 (12 digits)

    status = models.CharField(max_length=50)
    # ❓ ตัวแปร: status
    # 🔧 หน้าที่: สถานะของโครงการ
    # 📊 Type: String
    # 🔹 ค่าที่เป็นไปได้: "ดำเนินการ", "ปิด", "รอการอนุมัติ"

    class Meta:
        db_table = 'projects'

    def __str__(self):
        return f"{self.project_code} - {self.project_name}"
```

**SQL Equivalent (MySQL):**

```sql
CREATE TABLE projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    project_code VARCHAR(50) UNIQUE NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    budget_total DECIMAL(12,2) DEFAULT 0.00,
    status VARCHAR(50) NOT NULL
);
```

---

### **Vendors Model**

```python
class Vendors(models.Model):
    vendor_id = models.AutoField(primary_key=True)
    # Primary key สำหรับผู้จัดจำหน่าย

    vendor_name = models.CharField(max_length=255)
    # ชื่อของผู้จัดจำหน่าย
    # 🔹 เช่น: "บริษัท ABC จำกัด", "Supplier XYZ"

    phone = models.CharField(max_length=50, blank=True, null=True)
    # เบอร์โทรศัพท์ (optional)
    # blank=True: ฟอร์มหลังบ้านให้ว่างเปล่าได้
    # null=True: ฐานข้อมูลเก็บ NULL ได้

    email = models.EmailField(max_length=255, blank=True, null=True)
    # อีเมล (optional)
    # EmailField: Django ตรวจสอบรูปแบบอีเมล

    class Meta:
        db_table = 'vendors'
```

---

### **MasterItems Model**

```python
class MasterItems(models.Model):
    item_id = models.AutoField(primary_key=True)
    # Primary key

    item_code = models.CharField(max_length=50, unique=True)
    # รหัสสินค้า เดียวกัน (Unique)
    # 🔹 เช่น: "ITEM-001", "ITEM-LAPTOP"

    item_name = models.CharField(max_length=255)
    # ชื่อสินค้า

    standard_unit = models.CharField(max_length=50)
    # หน่วยมาตรฐาน
    # 🔹 เช่น: "ชิ้น", "กล่อง", "ตัน"

    created_at = models.DateTimeField(auto_now_add=True)
    # วันที่สร้าง (auto-generated)
    # auto_now_add=True: Django ใส่ timestamp เองตอนสร้าง

    class Meta:
        db_table = 'master_items'
```

---

## 3.2 Database Connection (settings.py)

```python
# Development (MySQL - Local)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'potms',              # Database name
        'USER': 'root',               # MySQL user
        'PASSWORD': 'BookReserve2025', # Password
        'HOST': 'localhost',          # Server address
        'PORT': '3306',               # MySQL port
    }
}

# Production (PostgreSQL - Vercel)
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ['DATABASE_URL'],
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
```

---

## 3.3 Firebase Integration (Optional)

```python
# backend/firebase_config.py
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# Get Firestore DB
db = firestore.client()
```

---

---

# 4. 🔌 API ViewSets & Views

## 4.1 ProjectAPIView (APIView)

**ไฟล์:** `api/views.py`  
**Type:** APIView (Function-like API endpoint)

```python
class ProjectAPIView(APIView):
    """
    API endpoint สำหรับจัดการข้อมูล Projects

    Methods:
        GET     - ดึงรายการ projects ทั้งหมด
        POST    - สร้าง project ใหม่
    """

    def get(self, request):
        """
        ❓ Method: GET /api/projects/
        🔧 หน้าที่: ดึงข้อมูล projects ทั้งหมดจากฐานข้อมูล

        Response:
            Status: 200 OK
            Body: [
                {
                    "project_id": 1,
                    "project_code": "PRJ-001",
                    "project_name": "โครงการ A",
                    "budget_total": 1500000.00,
                    "status": "ดำเนินการ"
                },
                ...
            ]
        """
        try:
            # Firebase version
            projects_ref = db.collection('projects')
            docs = projects_ref.stream()

            project_list = []
            for doc in docs:
                item = doc.to_dict()
                item['id'] = doc.id
                project_list.append(item)

            return Response(project_list, status=status.HTTP_200_OK)

        # MySQL ORM version (alternative)
        # projects = Projects.objects.all()
        # serializer = ProjectSerializer(projects, many=True)
        # return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        """
        ❓ Method: POST /api/projects/
        🔧 หน้าที่: สร้าง project ใหม่

        Request Body:
        {
            "project_name": "โครงการใหม่",
            "budget_total": 2000000,
            "status": "ดำเนินการ"
        }

        Response:
            Status: 201 Created
            Body: {
                "id": "doc_id_from_firebase",
                "project_name": "โครงการใหม่",
                ...
            }
        """
        try:
            data = request.data

            new_project = {
                'project_name': data.get('project_name'),
                'budget_total': float(data.get('budget_total', 0)),
                'budget_reserved': 0.0,
                'budget_spent': 0.0,
                'status': data.get('status', 'Active'),
                'created_at': datetime.datetime.now()
            }

            # Firebase save
            update_time, doc_ref = db.collection('projects').add(new_project)

            return Response({
                'id': doc_ref.id,
                **new_project
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
```

---

## 4.2 ProjectViewSet (ModelViewSet)

```python
# Alternative: Using Django ORM (not Firebase)
from rest_framework import viewsets

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint สำหรับ Projects (ใช้ Django ORM)

    Auto-generated endpoints:
        GET    /api/projects/              - list()
        POST   /api/projects/              - create()
        GET    /api/projects/{id}/         - retrieve()
        PUT    /api/projects/{id}/         - update()
        DELETE /api/projects/{id}/         - destroy()
    """

    queryset = Projects.objects.all()
    # ❓ queryset: ดึงข้อมูล projects ทั้งหมดจาก MySQL

    serializer_class = ProjectSerializer
    # ❓ serializer_class: ใช้ ProjectSerializer สำหรับ validation

    lookup_field = 'project_code'
    # ❓ lookup_field: ใช้ project_code แทน project_id ใน URL
    # 🔹 เช่น: /api/projects/PRJ-001/ (ไม่ใช่ /api/projects/1/)
```

---

## 4.3 Custom Actions

```python
@action(detail=False, methods=['post'], url_path='import-excel')
def import_excel(self, request, *args, **kwargs):
    """
    ❓ Custom Action: POST /api/projects/import-excel/
    🔧 หน้าที่: Import/Update projects จาก Excel file

    Request:
        Content-Type: multipart/form-data
        Body: importFile (Excel file)

    Response:
        Status: 201 Created
        Body: {'message': 'Successfully imported X projects.'}
    """

    file = request.FILES.get('importFile')

    if not file:
        return Response(
            {'error': 'No file uploaded'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Read Excel
        df = pd.read_excel(file)

        # Validate columns
        required_columns = ['project_code', 'project_name', 'budget_total', 'status']
        if not all(col in df.columns for col in required_columns):
            return Response(
                {'error': 'Missing required columns'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process each row
        for index, row in df.iterrows():
            project_code = row['project_code']

            # Check if exists
            project = Projects.objects.filter(project_code=project_code).first()

            data = {
                'project_name': row['project_name'],
                'budget_total': row['budget_total'],
                'status': row['status']
            }

            if project:
                # UPDATE
                serializer = self.get_serializer(project, data=data, partial=True)
            else:
                # CREATE
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
            {'message': f'Successfully imported {len(df)} projects.'},
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
```

---

---

# 5. 🔍 Serializers (Data Validation)

**ไฟล์:** `api/serializers.py`

```python
from rest_framework import serializers
from .models import Projects, Vendors, MasterItems

class ProjectSerializer(serializers.ModelSerializer):
    """
    ❓ Serializer: ProjectSerializer
    🔧 หน้าที่:
        1. Validate incoming JSON data
        2. Transform data (Python ↔ JSON)
        3. Create/Update database records
    """

    class Meta:
        model = Projects
        # ❓ model: บอก serializer ว่าต้องดูแล Projects model

        fields = '__all__'
        # ❓ fields: ใส่ทุก field ของ Projects model
        # Alternative: fields = ['project_id', 'project_code', 'project_name', ...]

    # Optional: Custom validation
    def validate_budget_total(self, value):
        """Custom validator สำหรับ budget_total"""
        if value < 0:
            raise serializers.ValidationError("Budget cannot be negative")
        return value

    # Optional: Custom create
    def create(self, validated_data):
        """Custom create method"""
        instance = Projects.objects.create(**validated_data)
        return instance

    # Optional: Custom update
    def update(self, instance, validated_data):
        """Custom update method"""
        instance.project_name = validated_data.get('project_name', instance.project_name)
        instance.budget_total = validated_data.get('budget_total', instance.budget_total)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

class VendorSerializer(serializers.ModelSerializer):
    """Serializer for Vendors model"""
    class Meta:
        model = Vendors
        fields = '__all__'

class MasterItemSerializer(serializers.ModelSerializer):
    """Serializer for MasterItems model"""
    class Meta:
        model = MasterItems
        fields = '__all__'
```

---

## Serializer Validation Flow

```
User Input (JSON)
    ↓
Serializer.is_valid() → Check:
    ├─ Field types correct?
    ├─ Required fields present?
    ├─ Field length limits?
    ├─ Unique constraints?
    └─ Custom validators?
    ↓
If ✅ valid:
    └─ serializer.save() → ORM create/update()

If ❌ invalid:
    └─ serializer.errors → Return error response
```

---

---

# 6. 🌐 Frontend Layer

**ไฟล์:** `api/templates/S08_Master_Data.html`

## 6.1 HTML Structure

```html
<!DOCTYPE html>
<html>
  <head>
    <title>POTMS - Project Management</title>
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body>
    <!-- Navigation Bar -->
    <nav class="bg-blue-600 text-white">
      <h1>Project & Operations Task Management System</h1>
    </nav>

    <!-- Main Content -->
    <div class="container mx-auto p-6">
      <!-- Tabs Navigation -->
      <div class="flex gap-4 mb-6">
        <button onclick="showTab('projects')" class="px-4 py-2 bg-blue-500">
          Projects
        </button>
        <button onclick="showTab('vendors')" class="px-4 py-2 bg-gray-500">
          Vendors
        </button>
        <button onclick="showTab('items')" class="px-4 py-2 bg-gray-500">
          Master Items
        </button>
      </div>

      <!-- Projects Tab -->
      <div id="projects" class="tab">
        <div class="mb-4">
          <button onclick="openModal('project')" class="px-4 py-2 bg-green-500">
            Add Project
          </button>
          <input type="file" id="importFile" accept=".xlsx" />
          <button onclick="handleImport()" class="px-4 py-2 bg-blue-500">
            Import Excel
          </button>
        </div>

        <table id="projectsTable" class="w-full border">
          <thead>
            <tr>
              <th>Code</th>
              <th>Name</th>
              <th>Budget</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>

      <!-- Add/Edit Modal -->
      <div id="modal" class="hidden fixed inset-0 bg-black bg-opacity-50">
        <div class="bg-white p-6 rounded-lg">
          <h2 id="modalTitle">Add Project</h2>

          <form id="modalForm">
            <input type="text" id="inp-code" placeholder="Code" />
            <input type="text" id="inp-name" placeholder="Name" />
            <input type="number" id="inp-budget" placeholder="Budget" />
            <select id="inp-status">
              <option>ดำเนินการ</option>
              <option>ปิด</option>
              <option>รอการอนุมัติ</option>
            </select>

            <button type="submit" class="bg-blue-500">Save</button>
            <button type="button" onclick="closeModal()" class="bg-gray-500">
              Cancel
            </button>
          </form>
        </div>
      </div>
    </div>
  </body>
</html>
```

---

## 6.2 JavaScript Functions

```javascript
// ===== LOAD DATA =====

async function loadAllData() {
  /**
   * ❓ Function: loadAllData
   * 🔧 หน้าที่: Load ข้อมูลทั้งหมดจาก backend
   */
  await loadProjects();
  await loadVendors();
  await loadItems();
}

async function loadProjects() {
  /**
   * ❓ Function: loadProjects
   * 🔧 หน้าที่: Fetch GET /api/projects/ → Display in table
   */
  try {
    const response = await fetch("/api/projects/");
    const projects = await response.json();
    renderProjects(projects);
  } catch (error) {
    console.error("Error loading projects:", error);
    alert("Failed to load projects");
  }
}

async function renderProjects(projects) {
  /**
   * ❓ Function: renderProjects
   * 🔧 หน้าที่: Render projects data to HTML table
   */
  const tbody = document.querySelector("#projectsTable tbody");
  tbody.innerHTML = "";

  projects.forEach((project) => {
    const row = document.createElement("tr");
    row.innerHTML = `
            <td>${project.project_code}</td>
            <td>${project.project_name}</td>
            <td>${project.budget_total}</td>
            <td>${project.status}</td>
            <td>
                <button onclick="openModal('project', '${project.project_code}')">Edit</button>
                <button onclick="deleteData('projects', '${project.project_code}')">Delete</button>
            </td>
        `;
    tbody.appendChild(row);
  });
}

// ===== CREATE/UPDATE DATA =====

async function saveData(type = "project") {
  /**
   * ❓ Function: saveData
   * 🔧 หน้าที่: Save form data (POST new or PUT update)
   */
  const code = document.getElementById("inp-code").value;
  const name = document.getElementById("inp-name").value;
  const budget = document.getElementById("inp-budget").value;
  const status = document.getElementById("inp-status").value;

  // Validation
  if (!code || !name || !budget) {
    alert("Please fill all fields");
    return;
  }

  const body = {
    project_code: code,
    project_name: name,
    budget_total: parseFloat(budget),
    status: status,
  };

  try {
    // Check if create or update
    const isUpdate = currentEditId !== null;
    const method = isUpdate ? "PUT" : "POST";
    const url = isUpdate ? `/api/projects/${currentEditId}/` : `/api/projects/`;

    const response = await fetch(url, {
      method: method,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify(body),
    });

    if (response.ok) {
      alert("Saved successfully");
      closeModal();
      loadProjects();
    } else {
      const error = await response.json();
      alert("Error: " + JSON.stringify(error));
    }
  } catch (error) {
    console.error("Error saving:", error);
    alert("Failed to save");
  }
}

// ===== DELETE DATA =====

async function deleteData(type, id) {
  /**
   * ❓ Function: deleteData
   * 🔧 หน้าที่: Delete record with DELETE request
   */
  if (!confirm("Are you sure?")) return;

  try {
    const url =
      type === "projects" ? `/api/projects/${id}/` : `/api/vendors/${id}/`;

    const response = await fetch(url, {
      method: "DELETE",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    });

    if (response.ok) {
      alert("Deleted successfully");
      loadAllData();
    }
  } catch (error) {
    console.error("Error deleting:", error);
  }
}

// ===== IMPORT EXCEL =====

async function handleImport() {
  /**
   * ❓ Function: handleImport
   * 🔧 หน้าที่: Upload Excel file → POST /api/projects/import-excel/
   */
  const fileInput = document.getElementById("importFile");
  const file = fileInput.files[0];

  if (!file) {
    alert("Please select a file");
    return;
  }

  const formData = new FormData();
  formData.append("importFile", file);

  try {
    const response = await fetch("/api/projects/import-excel/", {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: formData,
    });

    const result = await response.json();

    if (response.ok) {
      alert(result.message);
      fileInput.value = "";
      loadProjects();
    } else {
      alert("Error: " + result.error);
    }
  } catch (error) {
    console.error("Error importing:", error);
  }
}

// ===== MODAL FUNCTIONS =====

function openModal(type, id = null) {
  /**
   * ❓ Function: openModal
   * 🔧 หน้าที่: Open modal for add/edit
   */
  const modal = document.getElementById("modal");
  document.getElementById("modalTitle").textContent = id
    ? "Edit Project"
    : "Add Project";

  if (id) {
    // Load data for edit
    const projects = JSON.parse(localStorage.getItem("projects"));
    const project = projects.find((p) => p.project_code === id);

    document.getElementById("inp-code").value = project.project_code;
    document.getElementById("inp-name").value = project.project_name;
    document.getElementById("inp-budget").value = project.budget_total;
    document.getElementById("inp-status").value = project.status;

    currentEditId = id;
  } else {
    document.getElementById("modalForm").reset();
    currentEditId = null;
  }

  modal.classList.remove("hidden");
}

function closeModal() {
  /**
   * ❓ Function: closeModal
   * 🔧 หน้าที่: Close modal and reset form
   */
  document.getElementById("modal").classList.add("hidden");
  document.getElementById("modalForm").reset();
}

// ===== UTILITIES =====

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Initialize
document.addEventListener("DOMContentLoaded", loadAllData);
```

---

---

# 7. 🔄 Complete Request-Response Flow

## Full Cycle: Create Project

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: USER INTERACTION (Frontend - S08_Master_Data.html)           │
│                                                                     │
│ User fills form:                                                    │
│   - inp-code: "PRJ-NEW"                                             │
│   - inp-name: "โครงการใหม่"                                         │
│   - inp-budget: 5000000                                             │
│   - inp-status: "ดำเนินการ"                                         │
│                                                                     │
│ User clicks "Save" button → onclick="saveData('project')"          │
└──────────────────────────┬──────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 2: JAVASCRIPT - PREPARE & SEND REQUEST                          │
│                                                                      │
│ Function: saveData()                                                 │
│                                                                      │
│ // Collect form data                                                 │
│ const body = {                                                       │
│     project_code: "PRJ-NEW",                                         │
│     project_name: "โครงการใหม่",                                    │
│     budget_total: 5000000,                                           │
│     status: "ดำเนินการ"                                              │
│ }                                                                    │
│                                                                      │
│ // Send HTTP request                                                │
│ fetch('/api/projects/', {                                            │
│     method: 'POST',                                                  │
│     headers: {                                                       │
│         'Content-Type': 'application/json',                          │
│         'X-CSRFToken': csrftoken                                     │
│     },                                                               │
│     body: JSON.stringify(body)                                       │
│ })                                                                   │
└──────────────────────────┬───────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 3: HTTP REQUEST (Network)                                       │
│                                                                      │
│ POST /api/projects/ HTTP/1.1                                        │
│ Host: localhost:8000                                                 │
│ Content-Type: application/json                                       │
│ X-CSRFToken: xxxxxxxx                                                │
│                                                                      │
│ {                                                                    │
│     "project_code": "PRJ-NEW",                                       │
│     "project_name": "โครงการใหม่",                                  │
│     "budget_total": 5000000,                                         │
│     "status": "ดำเนินการ"                                            │
│ }                                                                    │
└──────────────────────────┬───────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 4: DJANGO URL ROUTER (backend/urls.py)                         │
│                                                                      │
│ URL Patterns:                                                        │
│   - /api/ → router.urls                                              │
│   - DefaultRouter auto-registers ProjectViewSet                     │
│   - Matches: POST /api/projects/                                     │
│   - Routes to: ProjectViewSet.create()                              │
└──────────────────────────┬───────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 5: VIEWSET - CREATE METHOD (api/views.py)                      │
│                                                                      │
│ Class: ProjectViewSet(viewsets.ModelViewSet)                        │
│ Method: create() (auto-generated by ModelViewSet)                   │
│                                                                      │
│ 1. request.data = {project_code, project_name, ...}                │
│ 2. serializer = ProjectSerializer(data=request.data)                │
│ 3. Call serializer.is_valid()                                       │
└──────────────────────────┬───────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 6: SERIALIZER - VALIDATION (api/serializers.py)                │
│                                                                      │
│ Class: ProjectSerializer(serializers.ModelSerializer)               │
│                                                                      │
│ Validation Checks:                                                   │
│   ✓ project_code: CharField, max_length=50, unique=True             │
│     - Check: ไม่เกิน 50 ตัว ✓                                       │
│     - Check: ไม่ซ้ำในฐานข้อมูล ✓                                    │
│                                                                      │
│   ✓ project_name: CharField, max_length=255                         │
│     - Check: ไม่เกิน 255 ตัว ✓                                      │
│                                                                      │
│   ✓ budget_total: DecimalField(max_digits=12, decimal_places=2)    │
│     - Check: เป็นตัวเลข ✓                                            │
│     - Check: ไม่เกิน 999999999999.99 ✓                               │
│                                                                      │
│   ✓ status: CharField                                                │
│     - Check: มีค่า ✓                                                 │
│                                                                      │
│ Result: is_valid() = True → serializer.save()                       │
└──────────────────────────┬───────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 7: ORM - DATABASE SAVE (api/models.py)                         │
│                                                                      │
│ serializer.save() calls:                                             │
│   Projects.objects.create(**validated_data)                         │
│                                                                      │
│ Django ORM converts to SQL:                                          │
│   INSERT INTO projects                                               │
│   (project_code, project_name, budget_total, status)                │
│   VALUES                                                             │
│   ('PRJ-NEW', 'โครงการใหม่', 5000000.00, 'ดำเนินการ')              │
│                                                                      │
│ Database executes SQL → New row inserted                            │
│ Django assigns auto-increment project_id = 5                        │
└──────────────────────────┬───────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 8: RESPONSE SERIALIZATION (api/serializers.py)                │
│                                                                      │
│ serializer.data = {                                                  │
│     'project_id': 5,                                                 │
│     'project_code': 'PRJ-NEW',                                       │
│     'project_name': 'โครงการใหม่',                                  │
│     'budget_total': '5000000.00',                                    │
│     'status': 'ดำเนินการ'                                            │
│ }                                                                    │
│                                                                      │
│ JSONRenderer converts to JSON:                                       │
│   application/json format                                            │
└──────────────────────────┬───────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 9: HTTP RESPONSE (Network)                                      │
│                                                                      │
│ HTTP/1.1 201 Created                                                │
│ Content-Type: application/json                                       │
│                                                                      │
│ {                                                                    │
│     "project_id": 5,                                                 │
│     "project_code": "PRJ-NEW",                                       │
│     "project_name": "โครงการใหม่",                                  │
│     "budget_total": "5000000.00",                                    │
│     "status": "ดำเนินการ"                                            │
│ }                                                                    │
└──────────────────────────┬───────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 10: JAVASCRIPT - HANDLE RESPONSE (Frontend)                     │
│                                                                      │
│ if (response.ok) {                                                   │
│     const result = await response.json()                            │
│     alert('Saved successfully')                                      │
│     closeModal()                                                     │
│     loadProjects()  // Refresh table                                 │
│ } else {                                                             │
│     const error = await response.json()                              │
│     alert('Error: ' + JSON.stringify(error))                        │
│ }                                                                    │
└──────────────────────────┬───────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 11: PAGE REFRESH - RENDER TABLE (Frontend)                     │
│                                                                      │
│ Function: loadProjects()                                             │
│   → fetch('/api/projects/')                                         │
│   → renderProjects(projects)                                        │
│                                                                      │
│ Table HTML updated with new project:                                │
│   <tr>                                                               │
│     <td>PRJ-NEW</td>                                                 │
│     <td>โครงการใหม่</td>                                            │
│     <td>5000000.00</td>                                              │
│     <td>ดำเนินการ</td>                                               │
│     <td><button>Edit</button><button>Delete</button></td>           │
│   </tr>                                                              │
│                                                                      │
│ User sees new project in table ✅                                    │
└──────────────────────────────────────────────────────────────────────┘
```

---

---

# 8. 🛠️ Utilities & Helpers

## 8.1 Management Commands

**ไฟล์:** `api/management/commands/populate_db.py`

```python
from django.core.management.base import BaseCommand
from api.models import Projects, Vendors, MasterItems

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        """
        ❓ Command: python manage.py populate_db
        🔧 หน้าที่: สร้าง sample data สำหรับ development
        """

        # Create Projects
        projects = [
            {
                'project_code': 'PRJ-001',
                'project_name': 'โครงการพัฒนา AI',
                'budget_total': 1500000.00,
                'status': 'ดำเนินการ'
            },
            {
                'project_code': 'PRJ-002',
                'project_name': 'โครงการปรับปรุง Infrastructure',
                'budget_total': 2000000.00,
                'status': 'ดำเนินการ'
            }
        ]

        for project_data in projects:
            Projects.objects.get_or_create(**project_data)

        # Create Vendors
        vendors = [
            {
                'vendor_name': 'บริษัท ABC จำกัด',
                'phone': '02-123-4567',
                'email': 'abc@company.com'
            }
        ]

        for vendor_data in vendors:
            Vendors.objects.get_or_create(**vendor_data)

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database')
        )
```

**Run:**

```bash
python manage.py populate_db
```

---

## 8.2 Django Shell Usage

```bash
# Open Django Shell
python manage.py shell

# Import models
>>> from api.models import Projects, Vendors, MasterItems

# CREATE - สร้างข้อมูลใหม่
>>> project = Projects.objects.create(
...     project_code='PRJ-003',
...     project_name='โครงการใหม่',
...     budget_total=3000000.00,
...     status='ดำเนินการ'
... )

# READ - ดึงข้อมูล
>>> projects = Projects.objects.all()
>>> for p in projects:
...     print(f"{p.project_code}: {p.project_name}")

# UPDATE - แก้ไขข้อมูล
>>> project = Projects.objects.get(project_code='PRJ-001')
>>> project.project_name = 'โครงการพัฒนา AI ขั้น 2'
>>> project.save()

# DELETE - ลบข้อมูล
>>> project = Projects.objects.get(project_code='PRJ-003')
>>> project.delete()

# FILTER - ค้นหา
>>> active_projects = Projects.objects.filter(status='ดำเนินการ')
>>> for p in active_projects:
...     print(p.project_name)
```

---

## 8.3 Testing

**ไฟล์:** `api/tests.py`

```python
from django.test import TestCase
from api.models import Projects

class ProjectsTestCase(TestCase):
    """Unit tests for Projects model"""

    def setUp(self):
        """Setup test data"""
        self.project = Projects.objects.create(
            project_code='PRJ-TEST',
            project_name='Test Project',
            budget_total=1000000.00,
            status='ดำเนินการ'
        )

    def test_project_creation(self):
        """Test if project is created correctly"""
        self.assertEqual(self.project.project_code, 'PRJ-TEST')
        self.assertEqual(self.project.project_name, 'Test Project')

    def test_project_unique_code(self):
        """Test unique constraint on project_code"""
        with self.assertRaises(Exception):
            Projects.objects.create(
                project_code='PRJ-TEST',  # Duplicate
                project_name='Another Project',
                budget_total=500000.00,
                status='ดำเนินการ'
            )
```

**Run tests:**

```bash
python manage.py test
```

---

## 8.4 Environment Variables (.env)

```bash
# .env (Development)
DEBUG=True
DJANGO_SECRET_KEY=django-insecure-xxxxx
DATABASE_URL=mysql://root:password@localhost:3306/potms
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# .env.production.local (Production/Vercel)
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host:5432/potms
ALLOWED_HOSTS=yourapp.vercel.app,www.yourapp.vercel.app
CORS_ALLOWED_ORIGINS=https://yourapp.vercel.app
```

---

---

# 9. 📊 Summary & Quick Reference

## Project Components

| Component       | Location              | Purpose         | Tech Stack          |
| --------------- | --------------------- | --------------- | ------------------- |
| **Models**      | `api/models.py`       | Database schema | Django ORM          |
| **Serializers** | `api/serializers.py`  | Data validation | DRF Serializer      |
| **Views**       | `api/views.py`        | API endpoints   | DRF ViewSet/APIView |
| **URLs**        | `api/urls.py`         | Route mapping   | Django URLs         |
| **Templates**   | `api/templates/`      | HTML UI         | Tailwind CSS        |
| **Static**      | `api/static/`         | JS, CSS, Images | Vanilla JS          |
| **Settings**    | `backend/settings.py` | Configuration   | Environment vars    |
| **Database**    | MySQL/Firebase        | Data storage    | MySQL/Firestore     |

---

## Common Operations

### Create Project

```bash
POST /api/projects/
{
    "project_code": "PRJ-001",
    "project_name": "โครงการใหม่",
    "budget_total": 5000000,
    "status": "ดำเนินการ"
}
```

### Read Projects

```bash
GET /api/projects/
GET /api/projects/PRJ-001/
```

### Update Project

```bash
PUT /api/projects/PRJ-001/
{
    "project_name": "โครงการอัพเดต",
    "budget_total": 6000000
}
```

### Delete Project

```bash
DELETE /api/projects/PRJ-001/
```

### Import from Excel

```bash
POST /api/projects/import-excel/
Content-Type: multipart/form-data
File: projects.xlsx
```

---

## Troubleshooting

| Error                        | Cause                       | Solution                          |
| ---------------------------- | --------------------------- | --------------------------------- |
| **ModuleNotFoundError**      | Missing dependency          | `pip install -r requirements.txt` |
| **No database tables**       | Migrations not applied      | `python manage.py migrate`        |
| **CORS error**               | Frontend domain not allowed | Update `CORS_ALLOWED_ORIGINS`     |
| **Static files not loading** | Collectstatic not run       | `python manage.py collectstatic`  |
| **DisallowedHost**           | Domain not in ALLOWED_HOSTS | Add domain to settings            |

---

**Complete! ทุกส่วนของโปรเจคได้รับการอธิบายแล้ว** 🎉
