# 📥 วิธีการเก็บข้อมูลลง Firebase

## การเตรียม Firebase

```python
# backend/firebase_config.py
import firebase_admin
from firebase_admin import credentials, firestore

# ✅ ขั้น 1: Initialize Firebase (ทำครั้งเดียว)
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# ✅ ขั้น 2: Get Firestore client
db = firestore.client()
```

---

# 5️⃣ วิธีการเก็บข้อมูล

## ✅ วิธีที่ 1: add() - สร้างข้อมูลใหม่ (Firebase สร้าง ID)

```python
# บันทึกข้อมูล โดย Firebase สร้าง Document ID เองอัตโนมัติ

data = {
    'project_name': 'โครงการพัฒนา AI',
    'budget_total': 1500000,
    'status': 'ดำเนินการ',
    'created_at': datetime.datetime.now()
}

# ❓ add() method
update_time, doc_ref = db.collection('projects').add(data)

# 🔹 ผลลัพธ์:
#   - update_time: เวลาที่บันทึก
#   - doc_ref.id: Document ID ที่สร้างขึ้น (เช่น "AbCdEfGhIjK123")
#   - ข้อมูลถูกเก็บลง Firebase แล้ว ✅

print(f"Document created with ID: {doc_ref.id}")
```

**ตัวอย่างการใช้ในโค้ด:**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from backend.firebase_config import db
import datetime

class ProjectAPIView(APIView):
    def post(self, request):
        """สร้างโครงการใหม่"""
        try:
            data = request.data

            new_project = {
                'project_name': data.get('project_name'),
                'budget_total': float(data.get('budget_total', 0)),
                'status': data.get('status', 'ดำเนินการ'),
                'created_at': datetime.datetime.now()
            }

            # เก็บลง Firebase
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

## ✅ วิธีที่ 2: set() - เก็บข้อมูลด้วย ID ที่กำหนดเอง

```python
# บันทึกข้อมูล โดยระบุ Document ID เองเลย

data = {
    'project_code': 'PRJ-001',
    'project_name': 'โครงการ A',
    'budget_total': 1500000,
    'status': 'ดำเนินการ'
}

# ❓ set() method
db.collection('projects').document('PRJ-001').set(data)

# 🔹 ผลลัพธ์:
#   - Document ID คือ "PRJ-001" (ตามที่เราระบุ)
#   - ข้อมูลถูกเก็บลง Firebase

print("Project saved with ID: PRJ-001")

# ⚠️ ถ้า Document มีอยู่แล้ว จะถูกเขียนทับ (Overwrite)
# ❓ ถ้าอยากรวมข้อมูล ใช้: merge=True
db.collection('projects').document('PRJ-001').set(data, merge=True)
```

**ตัวอย่างการใช้:**

```python
# จาก POST request
project_code = request.data.get('project_code')
project_name = request.data.get('project_name')

db.collection('projects').document(project_code).set({
    'project_code': project_code,
    'project_name': project_name,
    'budget_total': float(request.data.get('budget_total')),
    'status': request.data.get('status')
})

return Response({'message': 'Saved'}, status=201)
```

---

## ✅ วิธีที่ 3: update() - แก้ไขข้อมูลที่มีอยู่แล้ว

```python
# อัพเดต field บางส่วน (ไม่ลบข้อมูลเดิม)

# ❓ update() method
db.collection('projects').document('PRJ-001').update({
    'project_name': 'โครงการ A (อัพเดต)',
    'budget_total': 2000000
})

# 🔹 ผลลัพธ์:
#   - เฉพาะ field ที่ระบุจึงเปลี่ยน
#   - Field อื่น ๆ คงเดิม

# ⚠️ ถ้า Document ไม่มีอยู่ → เกิด Error
```

**ตัวอย่างการใช้ (PUT request):**

```python
class ProjectDetailAPIView(APIView):
    def put(self, request, project_code):
        """แก้ไขโครงการ"""
        try:
            update_data = {
                'project_name': request.data.get('project_name'),
                'budget_total': float(request.data.get('budget_total'))
            }

            # อัพเดต Firebase
            db.collection('projects').document(project_code).update(update_data)

            return Response({'message': 'Updated'}, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=400)
```

---

## ✅ วิธีที่ 4: Batch Write - บันทึกหลายเอกสารพร้อมกัน

```python
# เก็บ/แก้ไข หลาย Document ในครั้งเดียว

batch = db.batch()

# เพิ่ม Project 1
project1_ref = db.collection('projects').document('PRJ-001')
batch.set(project1_ref, {
    'project_name': 'โครงการ A',
    'budget_total': 1500000
})

# เพิ่ม Project 2
project2_ref = db.collection('projects').document('PRJ-002')
batch.set(project2_ref, {
    'project_name': 'โครงการ B',
    'budget_total': 2000000
})

# อัพเดต Project 3
project3_ref = db.collection('projects').document('PRJ-003')
batch.update(project3_ref, {'status': 'ปิด'})

# ❓ commit() ทำการบันทึกทั้งหมด
batch.commit()

# 🔹 ผลลัพธ์:
#   - ทั้ง 3 operation บันทึกลง Firebase พร้อมกัน
#   - ถ้าเกิด Error ใด operation ใด → ทั้งหมดจะไม่บันทึก (Transaction)
```

**ตัวอย่างการใช้ (Import Excel):**

```python
def import_excel(self, request):
    """Import หลาย project จาก Excel"""
    file = request.FILES.get('importFile')
    df = pd.read_excel(file)

    batch = db.batch()

    for index, row in df.iterrows():
        project_code = row['project_code']

        project_ref = db.collection('projects').document(project_code)
        batch.set(project_ref, {
            'project_code': project_code,
            'project_name': row['project_name'],
            'budget_total': float(row['budget_total']),
            'status': row['status']
        })

    # บันทึกทั้งหมดพร้อมกัน
    batch.commit()

    return Response(
        {'message': f'Imported {len(df)} projects'},
        status=201
    )
```

---

## ✅ วิธีที่ 5: Transaction - บันทึกพร้อมเงื่อนไข

```python
# บันทึกข้อมูล โดยตรวจสอบเงื่อนไขก่อน

def transfer_budget(project_from, project_to, amount):
    """โอนงบประมาณระหว่าง Project"""

    transaction = db.transaction()

    @transaction.transactional
    def transfer_in_transaction(transaction):
        # ✅ ขั้น 1: ดึงข้อมูล
        from_ref = db.collection('projects').document(project_from)
        to_ref = db.collection('projects').document(project_to)

        from_doc = from_ref.get(transaction=transaction)
        to_doc = to_ref.get(transaction=transaction)

        # ✅ ขั้น 2: ตรวจสอบเงื่อนไข
        if from_doc.get('budget_total') < amount:
            raise Exception('Insufficient budget')

        # ✅ ขั้น 3: อัพเดต
        new_from_budget = from_doc.get('budget_total') - amount
        new_to_budget = to_doc.get('budget_total') + amount

        transaction.update(from_ref, {
            'budget_total': new_from_budget
        })
        transaction.update(to_ref, {
            'budget_total': new_to_budget
        })

    # ❓ execute() ทำการ transaction
    transfer_in_transaction(transaction)

    # 🔹 ผลลัพธ์:
    #   - ถ้าเงื่อนไขเป็นจริง → บันทึก
    #   - ถ้าเงื่อนไขเป็นเท็จ → ไม่บันทึก + Error

try:
    transfer_budget('PRJ-001', 'PRJ-002', 500000)
    print("Transfer successful")
except Exception as e:
    print(f"Transfer failed: {e}")
```

---

# 📊 เปรียบเทียบวิธีการ

| วิธี            | ฟังก์ชัน                      | ใช้เมื่อ             | Example                                                       |
| --------------- | ----------------------------- | -------------------- | ------------------------------------------------------------- |
| **add()**       | สร้างใหม่ (Firebase สร้าง ID) | เก็บข้อมูลใหม่       | `db.collection('projects').add(data)`                         |
| **set()**       | สร้างด้วย ID เอง              | เก็บด้วย ID ที่กำหนด | `db.collection('projects').document('PRJ-001').set(data)`     |
| **update()**    | แก้ไขข้อมูลเดิม               | อัพเดต field บางส่วน | `db.collection('projects').document('PRJ-001').update({...})` |
| **batch**       | หลาย operation                | Import หลาย record   | `batch.set(), batch.update(), batch.commit()`                 |
| **transaction** | conditional write             | Transfer กับตรวจสอบ  | `@transaction.transactional`                                  |

---

# 🔍 ตัวอย่างที่เสร็จสมบูรณ์

## Django View + Firebase

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from backend.firebase_config import db
import datetime
import pandas as pd

class ProjectAPIView(APIView):
    """API สำหรับจัดการ Projects ใน Firebase"""

    # ===== READ =====
    def get(self, request):
        """ดึงข้อมูล projects ทั้งหมด"""
        try:
            docs = db.collection('projects').stream()

            projects = []
            for doc in docs:
                item = doc.to_dict()
                item['id'] = doc.id
                projects.append(item)

            return Response(projects, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    # ===== CREATE (วิธีที่ 1: add) =====
    def post(self, request):
        """สร้าง project ใหม่"""
        try:
            new_project = {
                'project_name': request.data.get('project_name'),
                'budget_total': float(request.data.get('budget_total', 0)),
                'status': request.data.get('status', 'ดำเนินการ'),
                'created_at': datetime.datetime.now()
            }

            update_time, doc_ref = db.collection('projects').add(new_project)

            return Response({
                'id': doc_ref.id,
                **new_project
            }, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class ProjectDetailAPIView(APIView):
    """API สำหรับแก้ไข/ลบ Project เดียว"""

    # ===== UPDATE (วิธีที่ 3: update) =====
    def put(self, request, project_id):
        """แก้ไข project"""
        try:
            update_data = {
                'project_name': request.data.get('project_name'),
                'budget_total': float(request.data.get('budget_total')),
                'status': request.data.get('status'),
                'updated_at': datetime.datetime.now()
            }

            db.collection('projects').document(project_id).update(update_data)

            return Response({'message': 'Updated'}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    # ===== DELETE =====
    def delete(self, request, project_id):
        """ลบ project"""
        try:
            db.collection('projects').document(project_id).delete()

            return Response({'message': 'Deleted'}, status=204)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class ImportAPIView(APIView):
    """API สำหรับ import Excel (วิธีที่ 4: batch)"""

    def post(self, request):
        """import projects จาก Excel"""
        try:
            file = request.FILES.get('importFile')
            df = pd.read_excel(file)

            batch = db.batch()

            for index, row in df.iterrows():
                project_code = row['project_code']

                batch.set(
                    db.collection('projects').document(project_code),
                    {
                        'project_code': project_code,
                        'project_name': row['project_name'],
                        'budget_total': float(row['budget_total']),
                        'status': row['status'],
                        'created_at': datetime.datetime.now()
                    }
                )

            batch.commit()

            return Response(
                {'message': f'Imported {len(df)} projects'},
                status=201
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)
```

---

# 💾 สรุป

## ขั้นตอนเก็บข้อมูล Firebase

```
1. ✅ Initialize Firebase
   └─ import db จาก firebase_config.py

2. ✅ เตรียมข้อมูล
   └─ data = {'field': 'value', ...}

3. ✅ เลือกวิธี:
   ├─ add() → สร้างใหม่ (Firebase สร้าง ID)
   ├─ set() → เก็บด้วย ID เองเลย
   ├─ update() → แก้ไขเดิม
   ├─ batch → หลายเอกสารพร้อม
   └─ transaction → เงื่อนไข

4. ✅ ส่ง Response
   └─ return Response(data, status=201)
```

**ที่ใช้มากที่สุด:** `add()` และ `update()` ✅
