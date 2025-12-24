from django.contrib.auth.hashers import make_password, check_password  # เพิ่มบรรทัดนี้ด้านบนสุด
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from backend.firebase_config import db  # ดึงตัวเชื่อมต่อ DB ที่เราทำเมื่อกี้มาใช้
import datetime
from django.shortcuts import render
import pandas as pd

class ProjectAPIView(APIView):
    # ฟังก์ชันดึงข้อมูล (Read) -- เพิ่มส่วนนี้ครับ --
    def get(self, request):
        try:
            # 1. ไปที่ Collection 'projects' และดึงข้อมูลทั้งหมด (stream)
            projects_ref = db.collection('projects')
            docs = projects_ref.stream()

            # 2. วนลูปแปลงข้อมูลจาก Firestore ให้อยู่ในรูปแบบ List ที่ Django เข้าใจ
            project_list = []
            for doc in docs:
                item = doc.to_dict()
                item['id'] = doc.id  # สำคัญ! เอา ID ของเอกสารใส่เข้าไปด้วย
                project_list.append(item)

            # 3. ส่งข้อมูลกลับไป
            return Response(project_list, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
    # ฟังก์ชันสำหรับ "สร้างข้อมูลใหม่" (Create)
    def post(self, request):
        try:
            data = request.data
            new_project = {
                'project_name': data.get('project_name'),
                'budget_total': float(data.get('budget_total', 0)),
                'budget_reserved': 0.0,
                'budget_spent': 0.0,
                'status': data.get('status', 'Active'),  # รับจาก frontend หรือใช้ค่าเริ่มต้น Active
                'created_at': datetime.datetime.now()
            }

            # 3. สั่งบันทึกลง Collection ชื่อ 'projects'
            # คำสั่ง add() จะสร้าง Document ID ให้เองอัตโนมัติ
            update_time, doc_ref = db.collection('projects').add(new_project)

            # 4. ตอบกลับไปหาคนเรียก API ว่าเสร็จแล้ว พร้อมส่ง ID กลับไป
            return Response({
                'id': doc_ref.id,
                'message': 'สร้างโครงการสำเร็จแล้ว'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def project_dashboard(request):
    return render(request, 'project_list.html')

class ProjectDetailAPIView(APIView):
    # ฟังก์ชันดึงข้อมูลโครงการรายตัว (GET)
    def get(self, request, project_id):
        """ดึงข้อมูลโครงการรายบุคคล"""
        try:
            doc = db.collection('projects').document(project_id).get()
            
            if not doc.exists:
                return Response({'error': 'ไม่พบโครงการที่ระบุ'}, status=status.HTTP_404_NOT_FOUND)
            
            project_data = doc.to_dict()
            project_data['id'] = doc.id
            
            return Response(project_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # ฟังก์ชันลบข้อมูล (Delete)
    def delete(self, request, project_id):
        try:
            # สั่งลบเอกสารตาม ID ที่ส่งมา
            db.collection('projects').document(project_id).delete()

            return Response({'message': 'ลบสำเร็จ'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, project_id):
        try:
            data = request.data
            # เตรียมข้อมูลที่จะอัปเดต
            update_data = {
                'project_name': data.get('project_name'),
                'budget_total': float(data.get('budget_total', 0))
            }
            
            # ถ้ามี status ส่งมา ให้อัปเดตด้วย
            if data.get('status'):
                update_data['status'] = data.get('status')

            # สั่งอัปเดตที่ Firebase
            db.collection('projects').document(project_id).update(update_data)

            return Response({'message': 'แก้ไขสำเร็จ'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProjectImportAPIView(APIView):
    # ฟังก์ชันรับไฟล์ (POST)
    def post(self, request):
        try:
            # 1. ตรวจสอบว่ามีการส่งไฟล์มาไหม
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'กรุณาแนบไฟล์ Excel หรือ CSV'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. ใช้ Pandas อ่านไฟล์
            # ถ้าลงท้ายด้วย .csv ให้อ่านแบบ CSV, ถ้าไม่ใช่ให้อ่านแบบ Excel
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            # 3. วนลูปอ่านข้อมูลทีละแถว
            count = 0
            for index, row in df.iterrows():
                # ตรวจสอบว่าใน Excel มีหัวตารางถูกต้องไหม (project_name, budget_total)
                # เราใช้ .get() เพื่อป้องกัน Error ถ้า cell ว่าง
                p_name = row.get('project_name')
                p_budget = row.get('budget_total')

                if p_name and p_budget:
                    new_project = {
                        'project_name': str(p_name),
                        'budget_total': float(p_budget),
                        'budget_reserved': 0.0,
                        'budget_spent': 0.0,
                        'status': 'Active', # <--- เพิ่มบรรทัดนี้เช่นกัน
                        'created_at': datetime.datetime.now()
                        
                    }
                    # บันทึกลง Firebase
                    db.collection('projects').add(new_project)
                    count += 1

            return Response({'message': f'นำเข้าข้อมูลสำเร็จ {count} โครงการ'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f'เกิดข้อผิดพลาด: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class UserRegisterAPIView(APIView):
    # ฟังก์ชันสมัครสมาชิก (Register)
    def post(self, request):
        try:
            data = request.data
            username = data.get('username')
            password = data.get('password')
            role = data.get('role', 'User') # ค่าเริ่มต้นเป็น User
            department = data.get('department', '-')

            # 1. ตรวจสอบว่ามี username นี้หรือยัง
            users_ref = db.collection('users').where('username', '==', username).stream()
            if len(list(users_ref)) > 0:
                return Response({'error': 'ชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. สร้างข้อมูลผู้ใช้ใหม่ (เข้ารหัสรหัสผ่านด้วย make_password)
            new_user = {
                'username': username,
                'password': make_password(password), # Hash Password เพื่อความปลอดภัย
                'role': role,
                'department': department,
                'created_at': datetime.datetime.now()
            }

            # 3. บันทึกลง Collection 'users'
            db.collection('users').add(new_user)
            
            return Response({'message': 'ลงทะเบียนสำเร็จ'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    # ฟังก์ชันเข้าสู่ระบบ (Login)
    def post(self, request):
        try:
            data = request.data
            username = data.get('username')
            password = data.get('password')

            # 1. ค้นหา username ในระบบ
            users_ref = db.collection('users').where('username', '==', username).stream()
            
            user_found = None
            for doc in users_ref:
                user_found = doc.to_dict()
                user_found['id'] = doc.id
                break # เจอตัวแรกแล้วหยุดเลย

            # 2. ตรวจสอบรหัสผ่าน (ใช้ check_password เทียบกับค่า Hash)
            if user_found and check_password(password, user_found['password']):
                return Response({
                    'message': 'เข้าสู่ระบบสำเร็จ',
                    'user': {
                        'id': user_found['id'],
                        'username': user_found['username'],
                        'role': user_found['role'],
                        'department': user_found['department']
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def login_page(request):
    return render(request, 'login.html')

def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')

def homepage(request):
    return render(request, 'homepage.html')


def register_page(request):
    """
    ===================================================================
    register_page - แสดงหน้าสมัครสมาชิก
    ===================================================================
    
    หน้าที่:
    - Render หน้า register.html สำหรับสมัครสมาชิกใหม่
    - รองรับทั้ง User และ Staff
    
    URL: /api/register-page/
    Method: GET
    
    Returns:
        HttpResponse: หน้า HTML สำหรับสมัครสมาชิก
    ===================================================================
    """
    return render(request, 'register.html')


class StatsAPIView(APIView):
    """API สำหรับดึงสถิติแดชบอร์ด"""
    def get(self, request):
        try:
            # นับจำนวนโครงการทั้งหมด
            projects_ref = db.collection('projects').stream()
            total_projects = len(list(projects_ref))

            # ในอนาคตสามารถเพิ่มการนับสถานะต่างๆ ได้
            # ตอนนี้ใช้ค่า placeholder ก่อน (จะเปลี่ยนเมื่อมี field status ในโครงการ)
            stats = {
                'pending': 0,           # รอดำเนินการ
                'approved': 0,          # อนุมัติแล้ว
                'in_progress': 0,       # กำลังดำเนินการ
                'completed': total_projects,  # เสร็จสิ้น (นับจากจำนวนโครงการทั้งหมด)
                'total_projects': total_projects
            }

            return Response(stats, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================================================
# USER MANAGEMENT APIs - ระบบจัดการผู้ใช้งาน (CRUD)
# ==========================================================================

class UserListAPIView(APIView):
    """
    ===================================================================
    UserListAPIView - ดึงรายชื่อผู้ใช้ทั้งหมด
    ===================================================================
    
    หน้าที่:
    - ดึงข้อมูลผู้ใช้ทั้งหมดจาก Firestore (สำหรับ Admin Panel)
    - ไม่ส่ง password กลับไปเพื่อความปลอดภัย
    
    URL: /api/users/
    Method: GET
    
    Returns:
        JSON Array: รายชื่อผู้ใช้ทั้งหมด [{id, username, role, department, created_at}, ...]
    ===================================================================
    """
    def get(self, request):
        try:
            # ดึงข้อมูลจาก Collection 'users'
            users_ref = db.collection('users')
            docs = users_ref.stream()
            
            # แปลงข้อมูลเป็น List โดยไม่รวม password
            user_list = []
            for doc in docs:
                user_data = doc.to_dict()
                user_list.append({
                    'id': doc.id,
                    'username': user_data.get('username'),
                    'role': user_data.get('role'),
                    'department': user_data.get('department'),
                    'created_at': user_data.get('created_at')
                    # หมายเหตุ: ไม่ส่ง password กลับไปเพื่อความปลอดภัย
                })
            
            return Response(user_list, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPIView(APIView):
    """
    ===================================================================
    UserDetailAPIView - แก้ไข/ลบผู้ใช้ตาม ID
    ===================================================================
    
    หน้าที่:
    - GET: ดึงข้อมูลผู้ใช้รายบุคคล
    - PUT: แก้ไขข้อมูลผู้ใช้ (role, department)
    - DELETE: ลบผู้ใช้ออกจากระบบ
    
    URL: /api/users/<user_id>/
    
    ข้อควรระวัง:
    - เฉพาะ Admin เท่านั้นที่ควรเข้าถึง API นี้
    - การลบผู้ใช้เป็นการลบถาวร (Hard Delete)
    ===================================================================
    """
    
    def get(self, request, user_id):
        """
        ดึงข้อมูลผู้ใช้รายบุคคลตาม ID
        """
        try:
            # ดึงเอกสารผู้ใช้จาก Firestore
            doc = db.collection('users').document(user_id).get()
            
            if not doc.exists:
                return Response({'error': 'ไม่พบผู้ใช้ที่ระบุ'}, status=status.HTTP_404_NOT_FOUND)
            
            user_data = doc.to_dict()
            return Response({
                'id': doc.id,
                'username': user_data.get('username'),
                'role': user_data.get('role'),
                'department': user_data.get('department'),
                'created_at': user_data.get('created_at')
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, user_id):
        """
        แก้ไขข้อมูลผู้ใช้ (role, department)
        
        Body Parameters:
        - role: ประเภทผู้ใช้ (User/Staff/Admin)
        - department: แผนกที่สังกัด
        - password: (optional) รหัสผ่านใหม่
        """
        try:
            data = request.data
            
            # เตรียมข้อมูลที่จะอัปเดต
            update_data = {}
            
            # อัปเดต role ถ้ามีการส่งมา
            if data.get('role'):
                update_data['role'] = data.get('role')
            
            # อัปเดต department ถ้ามีการส่งมา
            if data.get('department'):
                update_data['department'] = data.get('department')
            
            # อัปเดต password ถ้ามีการส่งมา (ต้อง hash ก่อน)
            if data.get('password'):
                update_data['password'] = make_password(data.get('password'))
            
            # ตรวจสอบว่ามีข้อมูลที่จะอัปเดตหรือไม่
            if not update_data:
                return Response({'error': 'ไม่มีข้อมูลที่ต้องการแก้ไข'}, status=status.HTTP_400_BAD_REQUEST)
            
            # อัปเดตข้อมูลใน Firestore
            db.collection('users').document(user_id).update(update_data)
            
            return Response({'message': 'แก้ไขข้อมูลผู้ใช้สำเร็จ'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        """
        ลบผู้ใช้ออกจากระบบ (Hard Delete)
        
        ข้อควรระวัง:
        - การลบเป็นการลบถาวร ไม่สามารถกู้คืนได้
        - ควรตรวจสอบสิทธิ์ก่อนลบ (เฉพาะ Admin)
        """
        try:
            # ลบเอกสารผู้ใช้จาก Firestore
            db.collection('users').document(user_id).delete()
            
            return Response({'message': 'ลบผู้ใช้สำเร็จ'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def user_management_page(request):
    """
    ===================================================================
    user_management_page - หน้าจัดการผู้ใช้งาน (Admin Panel)
    ===================================================================
    
    หน้าที่:
    - Render หน้า user_management.html สำหรับจัดการผู้ใช้
    - แสดงรายชื่อผู้ใช้ทั้งหมด
    - รองรับการแก้ไข Role และลบผู้ใช้
    
    URL: /api/user-management/
    Method: GET
    
    สิทธิ์การเข้าถึง:
    - เฉพาะ Admin เท่านั้น (ตรวจสอบฝั่ง Frontend)
    
    Returns:
        HttpResponse: หน้า HTML สำหรับจัดการผู้ใช้
    ===================================================================
    """
    return render(request, 'user_management.html')


# ==========================================================================
# PROJECT ASSIGNMENT APIs - ระบบมอบหมายโครงการ
# ==========================================================================

class ProjectAssignmentAPIView(APIView):
    """
    ===================================================================
    ProjectAssignmentAPIView - จัดการการมอบหมายโครงการ
    ===================================================================
    
    หน้าที่:
    - GET: ดึงรายชื่อการมอบหมายทั้งหมด (หรือตาม project_id)
    - POST: เพิ่มการมอบหมายใหม่ (Staff กำหนด User ให้ดูแลโครงการ)
    
    Collection: project_assignments
    ===================================================================
    """
    
    def get(self, request):
        """
        ดึงรายชื่อการมอบหมายทั้งหมด
        Query: ?project_id=xxx (optional) - กรองตามโครงการ
        """
        try:
            project_id = request.GET.get('project_id')
            
            if project_id:
                # ดึงเฉพาะ assignment ของโครงการนั้น
                assignments_ref = db.collection('project_assignments').where('project_id', '==', project_id).stream()
            else:
                # ดึงทั้งหมด
                assignments_ref = db.collection('project_assignments').stream()
            
            assignments = []
            for doc in assignments_ref:
                assignment = doc.to_dict()
                assignment['id'] = doc.id
                assignments.append(assignment)
            
            return Response(assignments, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        """
        เพิ่มการมอบหมายใหม่
        
        Body Parameters:
        - project_id: ID โครงการ
        - user_id: ID User ที่จะรับผิดชอบ
        - assigned_by: ID Staff ที่กำหนด
        - note: หมายเหตุ (optional)
        """
        try:
            data = request.data
            
            project_id = data.get('project_id')
            user_id = data.get('user_id')
            assigned_by = data.get('assigned_by')
            note = data.get('note', '')
            
            # ตรวจสอบว่ามีการ assign ซ้ำหรือไม่
            existing = db.collection('project_assignments').where('project_id', '==', project_id).where('user_id', '==', user_id).stream()
            if len(list(existing)) > 0:
                return Response({'error': 'User นี้ถูกมอบหมายให้โครงการนี้แล้ว'}, status=status.HTTP_400_BAD_REQUEST)
            
            # สร้าง assignment ใหม่
            new_assignment = {
                'project_id': project_id,
                'user_id': user_id,
                'assigned_by': assigned_by,
                'assigned_at': datetime.datetime.now(),
                'note': note
            }
            
            update_time, doc_ref = db.collection('project_assignments').add(new_assignment)
            
            return Response({
                'id': doc_ref.id,
                'message': 'มอบหมายโครงการสำเร็จ'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProjectAssignmentDetailAPIView(APIView):
    """
    ===================================================================
    ProjectAssignmentDetailAPIView - ลบการมอบหมาย
    ===================================================================
    
    URL: /api/project-assignments/<assignment_id>/
    Method: DELETE
    ===================================================================
    """
    
    def delete(self, request, assignment_id):
        """ลบการมอบหมายออกจากระบบ"""
        try:
            db.collection('project_assignments').document(assignment_id).delete()
            return Response({'message': 'ลบการมอบหมายสำเร็จ'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def user_select_project_view(request):
    return render(request, 'user_select_project.html')


def user_dashboard(request):
    """
    ===================================================================
    user_dashboard - หน้า Dashboard สำหรับ User
    ===================================================================
    
    URL: /api/user-dashboard/
    
    แสดง:
    - โครงการที่รับผิดชอบ
    - สถิติใบขอซื้อ
    - ปุ่มเข้าสู่ระบบจัดการ
    ===================================================================
    """
    return render(request, 'user_dashboard.html')

class OrderAPIView(APIView):
    """
    API สำหรับจัดการรายการสั่งซื้อ
    
    GET: ดึงรายการสั่งซื้อทั้งหมด (หรือกรองตาม project_id, user_id)
    POST: สร้างรายการสั่งซื้อใหม่
    """
    
    def get(self, request):
        """ดึงรายการสั่งซื้อ"""
        try:
            project_id = request.GET.get('project_id')
            user_id = request.GET.get('user_id')
            
            # สร้าง query เริ่มต้น
            orders_ref = db.collection('orders')
            
            # กรองตาม project_id ถ้ามี
            if project_id:
                orders_ref = orders_ref.where('project_id', '==', project_id)
            
            # กรองตาม user_id ถ้ามี (เก็บเป็น requester_id ในฐานข้อมูล)
            if user_id:
                orders_ref = orders_ref.where('requester_id', '==', user_id)
            
            # ดึงข้อมูล
            orders = []
            for doc in orders_ref.stream():
                order = doc.to_dict()
                order['id'] = doc.id
                orders.append(order)
            
            return Response(orders, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        """สร้างรายการสั่งซื้อใหม่ (ตาม ER Diagram - MainOrder)"""
        try:
            data = request.data
            
            # สร้าง Order Number อัตโนมัติ (Format: PO-YYYYMMDD-XXX)
            today = datetime.datetime.now()
            date_str = today.strftime('%Y%m%d')
            
            # นับจำนวน orders ที่สร้างวันนี้
            start_of_day = datetime.datetime(today.year, today.month, today.day)
            end_of_day = start_of_day + datetime.timedelta(days=1)
            
            orders_today = db.collection('orders').where(
                'created_at', '>=', start_of_day
            ).where(
                'created_at', '<', end_of_day
            ).stream()
            
            count = len(list(orders_today)) + 1
            order_no = f"PO-{date_str}-{count:03d}"
            
            # สร้าง Order ใหม่ ตาม ER Diagram: MainOrder
            new_order = {
                # FK References
                'project_id': data.get('project_id'),
                'requester_id': data.get('requester_id'),  # User ผู้สั่ง
                'approver_id': None,  # Staff ผู้อนุมัติ (จะกำหนดทีหลัง)
                
                # Order Info
                'order_no': order_no,  # สร้างอัตโนมัติ: PO-YYYYMMDD-XXX
                'order_title': data.get('order_title', ''),
                'order_description': data.get('order_description', ''),
                'required_date': data.get('required_date'),
                'vendor_name': data.get('vendor_name', ''),
                
                # Items & Total
                'items': data.get('items', []),
                'total_estimated_price': data.get('total_estimated_price', 0),
                
                # Status
                'status': data.get('status', 'Draft'),
                
                # Metadata
                'inspection_committee': '',
                'staff_note': '',
                'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now()
            }
            
            # บันทึกลง Firestore
            update_time, doc_ref = db.collection('orders').add(new_order)
            
            return Response({
                'id': doc_ref.id,
                'message': 'สร้างรายการสั่งซื้อสำเร็จ'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def create_order_view(request):
    """
    ===================================================================
    create_order_view - หน้าสร้างใบสั่งซื้อ
    ===================================================================
    
    URL: /api/create-order/

    User ใช้หน้านี้เพื่อ:
    - กรอกรายการสินค้าที่ต้องการสั่งซื้อ
    - บันทึก Draft หรือส่งสั่งซื้อ
    ===================================================================
    """
    return render(request, 'create_order.html')


def my_orders_view(request):
    """
    ===================================================================
    my_orders_view - หน้ารายการสั่งซื้อของ User
    ===================================================================
    
    URL: /api/my-orders/
    
    หน้าที่:
    - แสดงรายการสั่งซื้อทั้งหมดของ User
    - กรองตามสถานะ (Draft, Ordered, etc.)
    - แก้ไข/ลบ Draft ที่ยังไม่ส่ง
    ===================================================================
    """
    return render(request, 'my_orders.html')


class OrderSubmitAPIView(APIView):
    """
    ===================================================================
    OrderSubmitAPIView - ส่งใบสั่งซื้อ (ตรวจสอบงบประมาณ)
    ===================================================================
    
    URL: /api/orders/<order_id>/submit/
    Method: POST
    
    Logic:
    1. ดึงข้อมูล Order และ Project
    2. คำนวณงบคงเหลือ
    3. ตรวจสอบว่าพอหรือไม่
    4. ถ้าพอ → ตัดงบสำรอง + อัปเดตสถานะ
    5. ถ้าไม่พอ → ส่ง error
    ===================================================================
    """
    
    def post(self, request, order_id):
        try:
            # 1. ดึงข้อมูล Order
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            order_data = order_doc.to_dict()
            
            # ตรวจสอบว่าเป็น Draft เท่านั้น
            if order_data.get('status') != 'Draft':
                return Response({'error': 'ใบสั่งซื้อนี้ถูกส่งแล้ว'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. ดึงข้อมูล Project
            project_id = order_data.get('project_id')
            project_doc = db.collection('projects').document(project_id).get()
            
            if not project_doc.exists:
                return Response({'error': 'ไม่พบโครงการ'}, status=status.HTTP_404_NOT_FOUND)
            
            project_data = project_doc.to_dict()
            
            # 3. คำนวณงบคงเหลือ
            budget_total = float(project_data.get('budget_total', 0))
            budget_reserved = float(project_data.get('budget_reserved', 0))
            budget_spent = float(project_data.get('budget_spent', 0))
            budget_remaining = budget_total - budget_reserved - budget_spent
            
            # 4. ตรวจสอบงบประมาณ
            order_total = float(order_data.get('total_estimated_price', 0))
            
            if order_total > budget_remaining:
                return Response({
                    'error': 'งบประมาณไม่เพียงพอ',
                    'budget_remaining': budget_remaining,
                    'order_total': order_total
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 5. อัปเดตสถานะ Order เป็น Pending (ยังไม่หักงบ - รอหัวหน้าอนุมัติก่อน)
            db.collection('orders').document(order_id).update({
                'status': 'Pending',
                'submitted_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now()
            })
            
            return Response({
                'message': 'ส่งใบสั่งซื้อเรียบร้อย กรุณารอการอนุมัติ',
                'order_id': order_id,
                'new_status': 'Pending'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================================================
# ORDER APPROVAL APIs - ระบบอนุมัติ/ปฏิเสธใบสั่งซื้อ (Staff)
# ==========================================================================

class OrderApproveAPIView(APIView):
    """
    ===================================================================
    OrderApproveAPIView - Staff อนุมัติใบสั่งซื้อ (ขั้นแรก)
    ===================================================================
    
    URL: POST /api/orders/{order_id}/approve/
    
    การทำงาน:
    - เปลี่ยนสถานะ Order เป็น 'WaitingBossApproval' (รอหัวหน้าอนุมัติ)
    - Staff ต้องพิมพ์ใบสั่งซื้อและให้หัวหน้าเซ็น
    - หลังจากนั้นกด "หัวหน้าอนุมัติแล้ว" เพื่อเปลี่ยนเป็น Approved
    ===================================================================
    """
    def post(self, request, order_id):
        try:
            # 1. ดึงข้อมูล Order
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            order_data = order_doc.to_dict()
            
            # 2. ตรวจสอบว่าเป็น Pending เท่านั้น
            if order_data.get('status') != 'Pending':
                return Response({'error': 'ใบสั่งซื้อนี้ไม่อยู่ในสถานะรออนุมัติ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. ดึง approver_id จาก request
            approver_id = request.data.get('approver_id', '')
            
            # 4. อัปเดตสถานะ Order เป็น WaitingBossApproval
            db.collection('orders').document(order_id).update({
                'status': 'WaitingBossApproval',
                'approver_id': approver_id,
                'updated_at': datetime.datetime.now()
            })
            
            return Response({
                'message': 'ส่งเรื่องรอหัวหน้าอนุมัติเรียบร้อย กรุณาพิมพ์ใบสั่งซื้อและเสนอหัวหน้าเซ็น',
                'order_id': order_id,
                'new_status': 'WaitingBossApproval'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderRejectAPIView(APIView):
    """
    ===================================================================
    OrderRejectAPIView - ปฏิเสธใบสั่งซื้อ
    ===================================================================
    
    URL: POST /api/orders/{order_id}/reject/
    
    Body Parameters:
    - staff_note: เหตุผลในการปฏิเสธ (required)
    - approver_id: ID ของ Staff ที่ปฏิเสธ
    
    การทำงาน:
    - เปลี่ยนสถานะ Order เป็น 'Rejected'
    - บันทึก staff_note (เหตุผล)
    - คืนงบประมาณ: budget_reserved -= order_total
    ===================================================================
    """
    def post(self, request, order_id):
        try:
            # 1. รับข้อมูลจาก request
            staff_note = request.data.get('staff_note', '')
            approver_id = request.data.get('approver_id', '')
            
            if not staff_note:
                return Response({'error': 'กรุณาระบุเหตุผลในการปฏิเสธ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. ดึงข้อมูล Order
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            order_data = order_doc.to_dict()
            
            # 3. ตรวจสอบว่าเป็น Pending เท่านั้น
            if order_data.get('status') != 'Pending':
                return Response({'error': 'ใบสั่งซื้อนี้ไม่อยู่ในสถานะรออนุมัติ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. คืนงบประมาณ
            project_id = order_data.get('project_id')
            order_total = float(order_data.get('total_estimated_price', 0))
            
            project_doc = db.collection('projects').document(project_id).get()
            if project_doc.exists:
                project_data = project_doc.to_dict()
                budget_reserved = float(project_data.get('budget_reserved', 0))
                new_reserved = max(0, budget_reserved - order_total)  # ป้องกันติดลบ
                
                db.collection('projects').document(project_id).update({
                    'budget_reserved': new_reserved
                })
            
            # 5. อัปเดตสถานะ Order
            db.collection('orders').document(order_id).update({
                'status': 'Rejected',
                'approver_id': approver_id,
                'staff_note': staff_note,
                'rejected_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now()
            })
            
            return Response({
                'message': 'ปฏิเสธใบสั่งซื้อเรียบร้อย',
                'order_id': order_id,
                'new_status': 'Rejected',
                'released_budget': order_total
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderCorrectionAPIView(APIView):
    """
    ===================================================================
    OrderCorrectionAPIView - ส่งกลับแก้ไข (Request Correction)
    ===================================================================
    
    URL: POST /api/orders/{order_id}/correction/
    
    Body Parameters:
    - staff_note: สิ่งที่ต้องแก้ไข (required)
    - approver_id: ID ของ Staff ที่ส่งกลับ
    
    การทำงาน:
    - เปลี่ยนสถานะ Order เป็น 'CorrectionNeeded'
    - บันทึก staff_note (สิ่งที่ต้องแก้ไข)
    - คืนงบประมาณ: budget_reserved -= order_total
    - User สามารถแก้ไขและส่งใหม่ได้
    ===================================================================
    """
    def post(self, request, order_id):
        try:
            # 1. รับข้อมูลจาก request
            staff_note = request.data.get('staff_note', '')
            approver_id = request.data.get('approver_id', '')
            
            if not staff_note:
                return Response({'error': 'กรุณาระบุสิ่งที่ต้องแก้ไข'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. ดึงข้อมูล Order
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            order_data = order_doc.to_dict()
            
            # 3. ตรวจสอบว่าเป็น Pending เท่านั้น
            if order_data.get('status') != 'Pending':
                return Response({'error': 'ใบสั่งซื้อนี้ไม่อยู่ในสถานะรออนุมัติ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. คืนงบประมาณ
            project_id = order_data.get('project_id')
            order_total = float(order_data.get('total_estimated_price', 0))
            
            project_doc = db.collection('projects').document(project_id).get()
            if project_doc.exists:
                project_data = project_doc.to_dict()
                budget_reserved = float(project_data.get('budget_reserved', 0))
                new_reserved = max(0, budget_reserved - order_total)  # ป้องกันติดลบ
                
                db.collection('projects').document(project_id).update({
                    'budget_reserved': new_reserved
                })
            
            # 5. อัปเดตสถานะ Order เป็น CorrectionNeeded
            db.collection('orders').document(order_id).update({
                'status': 'CorrectionNeeded',
                'approver_id': approver_id,
                'staff_note': staff_note,
                'correction_requested_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now()
            })
            
            return Response({
                'message': 'ส่งกลับแก้ไขเรียบร้อย',
                'order_id': order_id,
                'new_status': 'CorrectionNeeded',
                'released_budget': order_total
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderBossApproveAPIView(APIView):
    """
    ===================================================================
    OrderBossApproveAPIView - หัวหน้าอนุมัติใบสั่งซื้อ (ขั้นสอง)
    ===================================================================
    
    URL: POST /api/orders/{order_id}/boss-approve/
    
    การทำงาน:
    - เปลี่ยนสถานะ Order จาก 'WaitingBossApproval' เป็น 'Approved'
    - บันทึก approved_at
    - ใช้หลังจากหัวหน้าเซ็นเอกสาร
    ===================================================================
    """
    def post(self, request, order_id):
        try:
            # 1. ดึงข้อมูล Order
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            order_data = order_doc.to_dict()
            
            # 2. ตรวจสอบว่าเป็น WaitingBossApproval เท่านั้น
            if order_data.get('status') != 'WaitingBossApproval':
                return Response({'error': 'ใบสั่งซื้อนี้ไม่อยู่ในสถานะรอหัวหน้าอนุมัติ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. ตัดงบสำรอง (Reserve) - หักงบตอนหัวหน้าอนุมัติ
            project_id = order_data.get('project_id')
            order_total = float(order_data.get('total_estimated_price', 0))
            
            project_doc = db.collection('projects').document(project_id).get()
            if project_doc.exists:
                project_data = project_doc.to_dict()
                budget_reserved = float(project_data.get('budget_reserved', 0))
                new_reserved = budget_reserved + order_total
                
                db.collection('projects').document(project_id).update({
                    'budget_reserved': new_reserved
                })
            
            # 4. อัปเดตสถานะ Order เป็น Approved
            db.collection('orders').document(order_id).update({
                'status': 'Approved',
                'approved_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now()
            })
            
            return Response({
                'message': 'หัวหน้าเซ็นอนุมัติเรียบร้อย งบประมาณถูกจองแล้ว',
                'order_id': order_id,
                'new_status': 'Approved',
                'reserved_amount': order_total
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderSendToProcurementAPIView(APIView):
    """
    ===================================================================
    OrderSendToProcurementAPIView - ส่งใบสั่งซื้อให้พัสดุ
    ===================================================================
    
    URL: POST /api/orders/{order_id}/send-to-procurement/
    
    การทำงาน:
    - เปลี่ยนสถานะ Order จาก 'Approved' เป็น 'SentToProcurement'
    - บันทึก sent_to_procurement_at
    ===================================================================
    """
    def post(self, request, order_id):
        try:
            # 1. ดึงข้อมูล Order
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            order_data = order_doc.to_dict()
            
            # 2. ตรวจสอบว่าเป็น Approved เท่านั้น
            if order_data.get('status') != 'Approved':
                return Response({'error': 'ใบสั่งซื้อนี้ยังไม่ได้รับการอนุมัติ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. อัปเดตสถานะ Order เป็น SentToProcurement
            db.collection('orders').document(order_id).update({
                'status': 'SentToProcurement',
                'sent_to_procurement_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now()
            })
            
            return Response({
                'message': 'ส่งให้พัสดุเรียบร้อย',
                'order_id': order_id,
                'new_status': 'SentToProcurement'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderBossRejectAPIView(APIView):
    """
    ===================================================================
    OrderBossRejectAPIView - หัวหน้าไม่อนุมัติ (ส่งกลับแก้ไข)
    ===================================================================
    
    URL: POST /api/orders/{order_id}/boss-reject/
    
    Body Parameters:
    - boss_note: เหตุผลที่หัวหน้าไม่อนุมัติ (required)
    
    การทำงาน:
    - เปลี่ยนสถานะ Order จาก 'WaitingBossApproval' เป็น 'CorrectionNeeded'
    - บันทึก boss_note (เหตุผลที่ไม่อนุมัติ)
    - คืนงบประมาณ: budget_reserved -= order_total
    - User สามารถแก้ไขและส่งใหม่ได้
    ===================================================================
    """
    def post(self, request, order_id):
        try:
            # 1. รับข้อมูลจาก request
            boss_note = request.data.get('boss_note', '')
            
            if not boss_note:
                return Response({'error': 'กรุณาระบุเหตุผลที่หัวหน้าไม่อนุมัติ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. ดึงข้อมูล Order
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            order_data = order_doc.to_dict()
            
            # 3. ตรวจสอบว่าเป็น WaitingBossApproval เท่านั้น
            if order_data.get('status') != 'WaitingBossApproval':
                return Response({'error': 'ใบสั่งซื้อนี้ไม่อยู่ในสถานะรอหัวหน้าอนุมัติ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. คืนงบประมาณ
            project_id = order_data.get('project_id')
            order_total = float(order_data.get('total_estimated_price', 0))
            
            project_doc = db.collection('projects').document(project_id).get()
            if project_doc.exists:
                project_data = project_doc.to_dict()
                budget_reserved = float(project_data.get('budget_reserved', 0))
                new_reserved = max(0, budget_reserved - order_total)  # ป้องกันติดลบ
                
                db.collection('projects').document(project_id).update({
                    'budget_reserved': new_reserved
                })
            
            # 5. อัปเดตสถานะ Order เป็น CorrectionNeeded
            db.collection('orders').document(order_id).update({
                'status': 'CorrectionNeeded',
                'staff_note': f'หัวหน้าไม่อนุมัติ: {boss_note}',
                'boss_rejected_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now()
            })
            
            return Response({
                'message': 'ส่งกลับแก้ไขเรียบร้อย',
                'order_id': order_id,
                'new_status': 'CorrectionNeeded',
                'released_budget': order_total
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderApprovedCorrectionAPIView(APIView):
    """
    ===================================================================
    OrderApprovedCorrectionAPIView - ส่งกลับแก้ไข จากสถานะ Approved
    ===================================================================
    
    URL: POST /api/orders/{order_id}/approved-correction/
    
    Body Parameters:
    - staff_note: เหตุผลที่ต้องส่งกลับแก้ไข (required)
    
    การทำงาน:
    - เปลี่ยนสถานะ Order จาก 'Approved' เป็น 'CorrectionNeeded'
    - คืนงบประมาณ: budget_reserved -= order_total
    - User สามารถแก้ไขและส่งใหม่ได้
    ===================================================================
    """
    def post(self, request, order_id):
        try:
            # 1. รับข้อมูลจาก request
            staff_note = request.data.get('staff_note', '')
            
            if not staff_note:
                return Response({'error': 'กรุณาระบุเหตุผลที่ต้องส่งกลับแก้ไข'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. ดึงข้อมูล Order
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            order_data = order_doc.to_dict()
            
            # 3. ตรวจสอบว่าเป็น Approved เท่านั้น
            if order_data.get('status') != 'Approved':
                return Response({'error': 'ใบสั่งซื้อนี้ไม่อยู่ในสถานะหัวหน้าเซ็นอนุมัติแล้ว'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. คืนงบประมาณ
            project_id = order_data.get('project_id')
            order_total = float(order_data.get('total_estimated_price', 0))
            
            project_doc = db.collection('projects').document(project_id).get()
            if project_doc.exists:
                project_data = project_doc.to_dict()
                budget_reserved = float(project_data.get('budget_reserved', 0))
                new_reserved = max(0, budget_reserved - order_total)
                
                db.collection('projects').document(project_id).update({
                    'budget_reserved': new_reserved
                })
            
            # 5. อัปเดตสถานะ Order เป็น CorrectionNeeded
            db.collection('orders').document(order_id).update({
                'status': 'CorrectionNeeded',
                'staff_note': staff_note,
                'correction_requested_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now()
            })
            
            return Response({
                'message': 'ส่งกลับแก้ไขเรียบร้อย',
                'order_id': order_id,
                'new_status': 'CorrectionNeeded',
                'released_budget': order_total
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def print_order_view(request, order_id):
    """
    ===================================================================
    print_order_view - พิมพ์ใบขอซื้อ
    ===================================================================
    
    URL: GET /api/orders/{order_id}/print/
    
    การทำงาน:
    - ดึงข้อมูล Order, Project, และ Requester
    - Render หน้าพิมพ์ในรูปแบบ A4
    - ผู้ใช้สามารถพิมพ์หรือ Save เป็น PDF ได้
    ===================================================================
    """
    try:
        # 1. ดึงข้อมูล Order
        order_doc = db.collection('orders').document(order_id).get()
        if not order_doc.exists:
            return render(request, 'error.html', {'message': 'ไม่พบใบสั่งซื้อ'})
        
        order_data = order_doc.to_dict()
        order_data['id'] = order_id
        
        # คำนวณ total_price สำหรับแต่ละ item และ format ราคา
        items_with_total = []
        for item in order_data.get('items', []):
            item_copy = item.copy()
            qty = float(item.get('quantity_requested', 0))
            price = float(item.get('estimated_unit_price', 0))
            total = qty * price
            item_copy['total_price'] = total
            item_copy['formatted_price'] = f"{price:,.2f}"
            item_copy['formatted_total'] = f"{total:,.2f}"
            items_with_total.append(item_copy)
        order_data['items'] = items_with_total
        
        # Format dates
        if 'created_at' in order_data and order_data['created_at']:
            try:
                order_data['created_at'] = order_data['created_at'].strftime('%d/%m/%Y')
            except:
                order_data['created_at'] = str(order_data['created_at'])[:10]
        
        # 2. ดึงข้อมูล Project
        project_id = order_data.get('project_id')
        project_data = {}
        if project_id:
            project_doc = db.collection('projects').document(project_id).get()
            if project_doc.exists:
                project_data = project_doc.to_dict()
                project_data['project_id'] = project_id
        
        # 3. ดึงข้อมูล Requester
        requester_id = order_data.get('requester_id')
        requester_data = {}
        requester_name = '-'
        if requester_id:
            requester_doc = db.collection('users').document(requester_id).get()
            if requester_doc.exists:
                requester_data = requester_doc.to_dict()
                # ใช้ชื่อจาก account ของ user
                requester_name = requester_data.get('fullname') or requester_data.get('username') or '-'
        
        # 4. จัดการ vendor display
        vendor_name = order_data.get('vendor_name', '').strip()
        vendor_display = vendor_name if vendor_name else '-'
        
        # 5. จัดการ dates สำหรับ template
        created_date = order_data.get('created_at', '-')
        required_date = order_data.get('required_date', '-')
        
        # 6. Render template
        grand_total = float(order_data.get('total_estimated_price', 0))
        project_name = project_data.get('project_name', '-')
        user_department = requester_data.get('department', 'ผู้รับผิดชอบโครงการ')
        context = {
            'order': order_data,
            'project': project_data,
            'project_name': project_name,
            'requester': requester_data,
            'requester_name': requester_name,
            'user_department': user_department,
            'vendor_display': vendor_display,
            'created_date': created_date,
            'required_date': required_date,
            'grand_total': f"{grand_total:,.2f}",
        }
        
        return render(request, 'print_order.html', context)
        
    except Exception as e:
        return render(request, 'error.html', {'message': str(e)})


class OrderDetailAPIView(APIView):
    """
    ===================================================================
    OrderDetailAPIView - จัดการ Order แต่ละตัว (GET/PUT/DELETE)
    ===================================================================
    
    URL: /api/orders/<order_id>/
    Methods: GET, PUT, DELETE
    
    - GET: ดึงข้อมูล order ตัวเดียว (สำหรับดูรายละเอียด/แก้ไข)
    - PUT: อัปเดต Draft
    - DELETE: ลบ Draft
    ===================================================================
    """
    
    def get(self, request, order_id):
        """
        ดึงข้อมูล order ตัวเดียว
        """
        try:
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            order_data = order_doc.to_dict()
            order_data['id'] = order_id
            return Response(order_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, order_id):
        """
        อัปเดต Draft (ต้องเป็น Draft เท่านั้น)
        """
        try:
            # ตรวจสอบว่ามี order อยู่จริง
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            order_data = order_doc.to_dict()
        
            # ต้องเป็น Draft หรือ CorrectionNeeded เท่านั้น
            if order_data.get('status') not in ['Draft', 'CorrectionNeeded']:
                return Response({'error': 'ไม่สามารถแก้ไขใบสั่งซื้อที่ส่งแล้ว'}, status=status.HTTP_400_BAD_REQUEST)
            
            # อัปเดตข้อมูล
            update_data = request.data
            update_data['updated_at'] = datetime.datetime.now()
            
            db.collection('orders').document(order_id).update(update_data)
            
            return Response({'message': 'อัปเดตสำเร็จ', 'order_id': order_id}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, order_id):
        """
        ลบ Draft (ต้องเป็น Draft เท่านั้น)
        """
        try:
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            order_data = order_doc.to_dict()
            
            # ต้องเป็น Draft เท่านั้น
            if order_data.get('status') != 'Draft':
                return Response({'error': 'ไม่สามารถลบใบสั่งซื้อที่ส่งแล้ว'}, status=status.HTTP_400_BAD_REQUEST)
            
            # ลบ
            db.collection('orders').document(order_id).delete()
            
            return Response({'message': 'ลบสำเร็จ'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def order_detail_view(request, order_id):
    """
    ===================================================================
    order_detail_view - หน้ารายละเอียดใบสั่งซื้อ
    ===================================================================
    
    URL: /api/orders/<order_id>/detail/
    
    หน้าที่:
    - แสดงรายละเอียดใบสั่งซื้อทุกสถานะ
    - รายการสินค้า, วันที่, ร้านค้า
    - ปุ่มกลับไปหน้า My Orders
    ===================================================================
    """
    return render(request, 'order_detail.html')


def edit_order_view(request, order_id):
    """
    ===================================================================
    edit_order_view - หน้าแก้ไขใบสั่งซื้อ
    ===================================================================
    
    URL: /api/orders/<order_id>/edit/
    Parameters: order_id (from URL path)
    
    หน้าที่:
    - แสดงหน้า HTML สำหรับแก้ไขใบสั่งซื้อแบบ Draft
    - ใช้รูปแบบ Table แทน Grid
    - มีการคำนวณยอดรวมอัตโนมัติ
    ===================================================================
    """
    return render(request, 'edit_order.html', {'order_id': order_id})


class UserProjectsAPIView(APIView):
    """
    ===================================================================
    UserProjectsAPIView - ดึงโครงการที่ User รับผิดชอบ
    ===================================================================
    
    URL: GET /api/users/<user_id>/projects/
    
    Return: List of projects assigned to this user
    
    Logic:
    - Query project_assignments collection โดย user_id
    - Join กับ projects collection เพื่อดึงข้อมูลโครงการเต็ม
    ===================================================================
    """
    def get(self, request, user_id):
        try:
            # ดึง assignments ของ user นี้
            assignments = db.collection('project_assignments').where('user_id', '==', user_id).stream()
            
            # รวบรวม project_ids
            project_ids = []
            for assignment in assignments:
                assignment_data = assignment.to_dict()
                project_id = assignment_data.get('project_id')
                if project_id:
                    project_ids.append(project_id)
            
            # ดึงข้อมูลโครงการทั้งหมดที่ assign ให้ user นี้
            projects = []
            for project_id in project_ids:
                project_doc = db.collection('projects').document(project_id).get()
                if project_doc.exists:
                    project_data = project_doc.to_dict()
                    project_data['id'] = project_id
                    projects.append(project_data)
            
            return Response(projects, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StaffOrdersAPIView(APIView):
    """
    ===================================================================
    StaffOrdersAPIView - ดึงรายการใบสั่งซื้อทั้งหมด (สำหรับ Staff)
    ===================================================================
    
    URL: GET /api/staff/orders/?status=<status>
    
    Return: List of all orders (not filtered by user)
    Optional query param: status (Pending/Approved/Rejected/Draft)
    
    Staff Role Check: ต้อง login เป็น staff เท่านั้น
    ===================================================================
    """
    def get(self, request):
        try:
            #Status filter (optional)
            status_filter = request.GET.get('status', None)
            
            # Query orders
            if status_filter:
                orders_ref = db.collection('orders').where('status', '==', status_filter).stream()
            else:
                orders_ref = db.collection('orders').stream()
            
            orders = []
            for doc in orders_ref:
                order_data = doc.to_dict()
                order_data['id'] = doc.id
                orders.append(order_data)
            
            # Sort by created_at descending
            orders.sort(key=lambda x: x.get('created_at', 0), reverse=True)
            
            return Response(orders, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def staff_orders_view(request):
    """
    ===================================================================
    staff_orders_view - หน้าจัดการใบสั่งซื้อสำหรับ Staff
    ===================================================================
    
    URL: /api/staff/orders/page/
    
    Purpose:
    - แสดงรายการใบสั่งซื้อทั้งหมดในระบบ
    - กรองตามสถานะ, วันที่, เลขใบสั่งซื้อ
    - อนุมัติ/ปฏิเสธ/ส่งกลับแก้ไข
    - Export to CSV
    ===================================================================
    """
    return render(request, 'staff_orders.html')


def staff_order_detail_view(request, order_id):
    """
    ===================================================================
    staff_order_detail_view - หน้ารายละเอียดใบสั่งซื้อสำหรับ Staff
    ===================================================================
    
    URL: /api/staff/orders/<order_id>/detail/
    
    Purpose:
    - แสดงรายละเอียดใบสั่งซื้อ
    - ข้อมูลผู้สั่ง, โครงการ, รายการสินค้า
    - ปุ่มอนุมัติ/ปฏิเสธ
    ===================================================================
    """
    return render(request, 'staff_order_detail.html', {'order_id': order_id})


def staff_po_management_view(request):
    """
    ===================================================================
    staff_po_management_view - หน้าจัดการใบสั่งซื้อ (PO)
    ===================================================================
    
    URL: /api/staff/po-management/
    
    Purpose:
    - แสดงรายการใบสั่งซื้อทั้งหมด (ทุกสถานะ)
    - Filter/Search
    - Export CSV
    ===================================================================
    """
    return render(request, 'staff_po_management.html')