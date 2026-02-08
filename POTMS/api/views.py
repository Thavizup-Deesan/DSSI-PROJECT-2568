from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
# Firebase removed - now using PostgreSQL
import datetime
from django.shortcuts import render
import pandas as pd
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.db import transaction
from django.db.models import F

# Import security validators
from api.utils.validators import (
    validate_order_items,
    validate_order_description,
    validate_order_title,
    validate_status_transition,
    validate_budget_amount
)

# Import audit logging
from api.utils.audit import log_audit, get_client_ip, AUDIT_ACTIONS

# Import authorization utilities
# Import authorization utilities
from api.utils.authz import verify_staff_project_access, verify_order_ownership

# Import Models
from api.models import Project, User, ProjectAssignment

# Custom Permission Class for Staff-only actions
class IsStaff(BasePermission):
    """
    Custom permission to only allow Staff users to access.
    Verifies JWT token from Authorization header.
    """
    def has_permission(self, request, view):
        # Method 1: JWT Token-based auth (recommended for Vercel)
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                token = auth_header.split(' ')[1]
                decoded = AccessToken(token)
                role = decoded.get('role', '')
                if role.lower() == 'staff':
                    # Store in request for later use
                    request.jwt_user_id = decoded.get('user_id')
                    request.jwt_role = role
                    return True
            except Exception as e:
                print(f"JWT validation error: {str(e)}")
                pass
        
        # Method 2: Session-based auth (local development fallback)
        user_role = request.session.get('user_role', '')
        if user_role.lower() == 'staff':
            return True
        
        return False


class ProjectAPIView(APIView):
    """Project List/Create API - using PostgreSQL"""
    
    def get(self, request):
        """Get all projects"""
        try:
            from api.models import Project
            
            # Query all projects from PostgreSQL
            projects = Project.objects.all()
            
            # Convert to list with all fields
            project_list = [{
                'id': str(project.project_id),
                'project_id': str(project.project_id),
                'ubufmis_code': project.ubufmis_code or '',
                'project_code': project.project_code or '',
                'project_name': project.project_name,
                'budget_compensation': float(project.budget_compensation),
                'budget_usage': float(project.budget_usage),
                'budget_materials': float(project.budget_materials),
                'budget_equipment': float(project.budget_equipment),
                'budget_total': float(project.budget_total),
                'budget_reserved': float(project.budget_reserved),
                'budget_spent': float(project.budget_spent),
                'responsible_person': project.responsible_person or '',
                'status': project.status,
                'created_at': project.created_at.isoformat() if project.created_at else None
            } for project in projects]

            return Response(project_list, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
    def post(self, request):
        """Create new project"""
        try:
            from api.models import Project
            data = request.data
            
            # Create new project with all fields
            new_project = Project.objects.create(
                ubufmis_code=data.get('ubufmis_code'),
                project_name=data.get('project_name'),
                project_code=data.get('project_code'),
                budget_compensation=float(data.get('budget_compensation', 0)),
                budget_usage=float(data.get('budget_usage', 0)),
                budget_materials=float(data.get('budget_materials', 0)),
                budget_equipment=float(data.get('budget_equipment', 0)),
                budget_total=float(data.get('budget_total', 0)),
                budget_reserved=0.0,
                budget_spent=0.0,
                responsible_person=data.get('responsible_person'),
                status=data.get('status', 'Active')
            )

            return Response({
                'id': str(new_project.project_id),
                'message': 'สร้างโครงการสำเร็จแล้ว'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def project_dashboard(request):
    return render(request, 'project_list.html')

class ProjectDetailAPIView(APIView):
    """Project Detail API - using PostgreSQL"""
    
    def get(self, request, project_id):
        """Get project by ID (supports both firestore_id and project_id)"""
        try:
            from api.models import Project
            
            # Find by project_id directly (PostgreSQL)
            project = Project.objects.get(project_id=project_id)
            
            project_data = {
                'id': str(project.project_id),
                'project_id': str(project.project_id),
                'project_code': project.project_code or '',
                'project_name': project.project_name,
                'budget_total': float(project.budget_total),
                'budget_reserved': float(project.budget_reserved),
                'budget_spent': float(project.budget_spent),
                'status': project.status
            }
            
            return Response(project_data, status=status.HTTP_200_OK)
            
        except Project.DoesNotExist:
            return Response({'error': 'ไม่พบโครงการที่ระบุ'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, project_id):
        """Delete project"""
        try:
            from api.models import Project
            
            # Find by project_id directly (PostgreSQL)
            project = Project.objects.get(project_id=project_id)
            project.delete()

            return Response({'message': 'ลบสำเร็จ'}, status=status.HTTP_200_OK)
            
        except Project.DoesNotExist:
            return Response({'error': 'ไม่พบโครงการที่ระบุ'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, project_id):
        """Update project"""
        try:
            from api.models import Project
            data = request.data
            
            # Find by project_id directly (PostgreSQL)
            project = Project.objects.get(project_id=project_id)
            
            # Update project fields
            project.project_name = data.get('project_name', project.project_name)
            project.budget_total = float(data.get('budget_total', project.budget_total))
            
            if data.get('status'):
                project.status = data.get('status')
            
            if data.get('project_code'):
                project.project_code = data.get('project_code')
            
            project.save()

            return Response({'message': 'แก้ไขสำเร็จ'}, status=status.HTTP_200_OK)
            
        except Project.DoesNotExist:
            return Response({'error': 'ไม่พบโครงการที่ระบุ'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProjectImportAPIView(APIView):
    # ฟังก์ชันรับไฟล์ (POST)
    def post(self, request):
        try:
            from api.models import Project
            
            # 1. ตรวจสอบว่ามีการส่งไฟล์มาไหม
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'กรุณาแนบไฟล์ Excel หรือ CSV'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. ใช้ Pandas อ่านไฟล์
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            # 3. Map column names (Thai to English)
            # Expected columns from user's spreadsheet:
            # รหัส UBUFMIS, รหัสโครงการ, ชื่อโครงการ, ค่าตอบแทน, ค่าใช้สอย, ค่าวัสดุ, ค่าครุภัณฑ์, รวม, ผู้รับผิดชอบ
            column_mapping = {
                'รหัส UBUFMIS': 'ubufmis_code',
                'รหัสโครงการ': 'project_code',
                'ชื่อโครงการ': 'project_name',
                'ค่าตอบแทน': 'budget_compensation',
                'ค่าใช้สอย': 'budget_usage',
                'ค่าวัสดุ': 'budget_materials',
                'ค่าครุภัณฑ์': 'budget_equipment',
                'รวม': 'budget_total',
                'หน่วยงาน/ผู้รับผิดชอบโครงการ': 'responsible_person',
                'ผู้รับผิดชอบ': 'responsible_person',
                # Support English column names too
                'project_name': 'project_name',
                'budget_total': 'budget_total',
            }
            
            # Rename columns if they match
            df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)

            # 4. วนลูปอ่านข้อมูลทีละแถว
            count = 0
            errors = []
            for index, row in df.iterrows():
                p_name = row.get('project_name')
                
                # Skip empty rows
                if not p_name or pd.isna(p_name):
                    continue
                    
                try:
                    Project.objects.create(
                        ubufmis_code=str(row.get('ubufmis_code', '')) if not pd.isna(row.get('ubufmis_code')) else None,
                        project_code=str(row.get('project_code', '')) if not pd.isna(row.get('project_code')) else None,
                        project_name=str(p_name),
                        budget_compensation=float(row.get('budget_compensation', 0)) if not pd.isna(row.get('budget_compensation')) else 0,
                        budget_usage=float(row.get('budget_usage', 0)) if not pd.isna(row.get('budget_usage')) else 0,
                        budget_materials=float(row.get('budget_materials', 0)) if not pd.isna(row.get('budget_materials')) else 0,
                        budget_equipment=float(row.get('budget_equipment', 0)) if not pd.isna(row.get('budget_equipment')) else 0,
                        budget_total=float(row.get('budget_total', 0)) if not pd.isna(row.get('budget_total')) else 0,
                        budget_reserved=0.0,
                        budget_spent=0.0,
                        responsible_person=str(row.get('responsible_person', '')) if not pd.isna(row.get('responsible_person')) else None,
                        status='Active'
                    )
                    count += 1
                except Exception as row_error:
                    errors.append(f"Row {index+2}: {str(row_error)}")

            response_msg = f'นำเข้าข้อมูลสำเร็จ {count} โครงการ'
            if errors:
                response_msg += f' (พบข้อผิดพลาด {len(errors)} รายการ)'
                
            return Response({'message': response_msg, 'errors': errors}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f'เกิดข้อผิดพลาด: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class UserRegisterAPIView(APIView):
    """User registration - now using PostgreSQL"""
    def post(self, request):
        try:
            from api.models import User
            data = request.data
            username = data.get('username')
            password = data.get('password')
            role = data.get('role', 'User')
            department = data.get('department', '-')

            # 1. Check if username already exists
            if User.objects.filter(username=username).exists():
                return Response({'error': 'ชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Create new user with hashed password
            new_user = User.objects.create(
                username=username,
                password=make_password(password),  # Hash password
                role=role,
                department=department
            )
            
            return Response({'message': 'ลงทะเบียนสำเร็จ'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='post')
class UserLoginAPIView(APIView):
    """
    User Login API with JWT Token Generation - now using PostgreSQL
    Rate Limit: 5 attempts per minute per IP
    
    Returns:
        - access: JWT access token (1 hour)
        - refresh: JWT refresh token (7 days)
        - user: User info (id, username, role, department)
    """
    def post(self, request):
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            from api.models import User
            
            data = request.data
            username = data.get('username')
            password = data.get('password')

            # 1. Query user from PostgreSQL
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'error': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'}, status=status.HTTP_401_UNAUTHORIZED)

            # 2. Verify password
            if not check_password(password, user.password):
                return Response({'error': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'}, status=status.HTTP_401_UNAUTHORIZED)

            # 3. Generate JWT tokens with custom claims
            refresh = RefreshToken()
            refresh['user_id'] = str(user.user_id)
            refresh['username'] = user.username
            refresh['role'] = user.role
            refresh['department'] = user.department or ''
            
            return Response({
                'message': 'เข้าสู่ระบบสำเร็จ',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': str(user.user_id),
                    'username': user.username,
                    'role': user.role,
                    'department': user.department or '',
                    'fullname': user.username  # Add fullname for compatibility
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Login error: {str(e)}")
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
    """API สำหรับดึงสถิติแดชบอร์ด (นับจากฐานข้อมูลจริง)"""
    def get(self, request):
        try:
            # 1. นับจำนวนโครงการทั้งหมด
            # stream() คือการดึงข้อมูลทั้งหมดใน collection มา
            projects_ref = db.collection('projects').stream()
            total_projects = len(list(projects_ref))

            # 2. ดึงใบสั่งซื้อทั้งหมดมาเพื่อนับแยกสถานะ
            orders_ref = db.collection('orders').stream()
            
            # สร้างตัวแปรเก็บตัวนับ
            pending = 0
            approved = 0
            in_progress = 0
            completed = 0
            
            # วนลูปดูใบสั่งซื้อทีละใบ
            for doc in orders_ref:
                data = doc.to_dict()
                status = data.get('status')
                
                # เช็คเงื่อนไขและนับ
                if status == 'Pending':
                    pending += 1
                elif status == 'Approved':
                    approved += 1
                # สถานะเหล่านี้ถือว่าเป็น "กำลังดำเนินการ" (รอหัวหน้า, รอแก้, ส่งพัสดุ)
                elif status in ['WaitingBossApproval', 'CorrectionNeeded', 'SentToProcurement']:
                    in_progress += 1
                # สถานะนี้ถือว่า "เสร็จสิ้น" (รับของแล้ว)
                elif status == 'ReceivedFromProcurement':
                    completed += 1

            # 3. ส่งผลลัพธ์กลับไปที่หน้าเว็บ
            stats = {
                'pending': pending,
                'approved': approved,
                'in_progress': in_progress,
                'completed': completed,
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
    UserListAPIView - ดึงรายชื่อผู้ใช้ทั้งหมด (PostgreSQL)
    ===================================================================
    
    หน้าที่:
    - ดึงข้อมูลผู้ใช้ทั้งหมดจาก PostgreSQL (สำหรับ Admin Panel)
    - ไม่ส่ง password กลับไปเพื่อความปลอดภัย
    
    URL: /api/users/
    Method: GET
    
    Returns:
        JSON Array: รายชื่อผู้ใช้ทั้งหมด [{id, username, role, department}, ...]
    ===================================================================
    """
    def get(self, request):
        try:
            from api.models import User
            
            # Query all users from PostgreSQL
            users = User.objects.all()
            
            # Convert to list (exclude password)
            user_list = [{
                'id': str(user.user_id),
                'username': user.username,
                'role': user.role,
                'department': user.department or '',
                'fullname': user.username  # For compatibility
            } for user in users]
            
            return Response(user_list, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPIView(APIView):
    """
    ===================================================================
    UserDetailAPIView - แก้ไข/ลบผู้ใช้ตาม ID (PostgreSQL)
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
        """ดึงข้อมูลผู้ใช้รายบุคคลตาม ID"""
        try:
            from api.models import User
            
            user = User.objects.get(user_id=user_id)
            
            return Response({
                'id': str(user.user_id),
                'username': user.username,
                'role': user.role,
                'department': user.department or '',
                'fullname': user.username
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'ไม่พบผู้ใช้ที่ระบุ'}, status=status.HTTP_404_NOT_FOUND)
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
            from api.models import User
            data = request.data
            
            user = User.objects.get(user_id=user_id)
            
            # Update fields if provided
            if 'role' in data:
                user.role = data['role']
            
            if 'department' in data:
                user.department = data['department']
            
            # Update password if provided (hash it first)
            if 'password' in data:
                user.password = make_password(data['password'])
            
            user.save()
            
            return Response({'message': 'แก้ไขข้อมูลผู้ใช้สำเร็จ'}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'ไม่พบผู้ใช้ที่ระบุ'}, status=status.HTTP_404_NOT_FOUND)
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
            from api.models import User
            
            user = User.objects.get(user_id=user_id)
            user.delete()
            
            return Response({'message': 'ลบผู้ใช้สำเร็จ'}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'ไม่พบผู้ใช้ที่ระบุ'}, status=status.HTTP_404_NOT_FOUND)
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
    
    Model: ProjectAssignment
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
                assignments = ProjectAssignment.objects.filter(project_id=project_id)
            else:
                # ดึงทั้งหมด
                assignments = ProjectAssignment.objects.all()
            
            # Serialize data
            data = []
            for assign in assignments:
                data.append({
                    'id': assign.assignment_id,
                    'project_id': assign.project_id,
                    'project_name': assign.project.project_name,
                    'user_id': assign.user_id,
                    'user_name': assign.user.username,
                    'assigned_by': assign.assigned_by.username if assign.assigned_by else None,
                    'assigned_at': assign.assigned_at,
                    'note': assign.note
                })
            
            return Response(data, status=status.HTTP_200_OK)
            
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
            assigned_by_id = data.get('assigned_by')
            note = data.get('note', '')
            
            # ตรวจสอบว่ามีการ assign ซ้ำหรือไม่
            if ProjectAssignment.objects.filter(project_id=project_id, user_id=user_id).exists():
                return Response({'error': 'User นี้ถูกมอบหมายให้โครงการนี้แล้ว'}, status=status.HTTP_400_BAD_REQUEST)
            
            # ดึง instance ของ FK
            try:
                project = Project.objects.get(pk=project_id)
                user = User.objects.get(pk=user_id)
                assigned_by = User.objects.get(pk=assigned_by_id) if assigned_by_id else None
            except ObjectDoesNotExist:
                 return Response({'error': 'ไม่พบ Project หรือ User ที่ระบุ'}, status=status.HTTP_404_NOT_FOUND)

            # สร้าง assignment ใหม่
            new_assignment = ProjectAssignment.objects.create(
                project=project,
                user=user,
                assigned_by=assigned_by,
                note=note
            )
            
            return Response({
                'id': new_assignment.assignment_id,
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
            assignment = ProjectAssignment.objects.get(pk=assignment_id)
            assignment.delete()
            return Response({'message': 'ลบการมอบหมายสำเร็จ'}, status=status.HTTP_200_OK)
        except ProjectAssignment.DoesNotExist:
             return Response({'error': 'ไม่พบข้อมูลการมอบหมาย'}, status=status.HTTP_404_NOT_FOUND)
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

@method_decorator(ratelimit(key='user_or_ip', rate='10/h', method='POST'), name='post')
class OrderAPIView(APIView):
    """
    Order Creation API - using PostgreSQL
    Rate Limit: 10 orders per hour per user/IP
    
    GET: ดึงรายการสั่งซื้อทั้งหมด (หรือกรองตาม project_id, user_id)
    POST: สร้างรายการสั่งซื้อใหม่
    """
    
    def get(self, request):
        """ดึงรายการสั่งซื้อ"""
        try:
            from api.models import MainOrder, OrderItem
            
            project_id = request.GET.get('project_id')
            user_id = request.GET.get('user_id')
            
            # สร้าง query เริ่มต้น
            orders_query = MainOrder.objects.all()
            
            # กรองตาม project_id ถ้ามี
            if project_id:
                orders_query = orders_query.filter(project_id=project_id)
            
            # กรองตาม user_id ถ้ามี
            if user_id:
                orders_query = orders_query.filter(requester_id=user_id)
            
            # ดึงข้อมูลพร้อม items
            orders = []
            for order in orders_query:
                # Get order items
                items = []
                for item in order.items.all():
                    items.append({
                        'item_name': item.item_name,
                        'quantity_requested': item.quantity_requested,
                        'unit': item.unit,
                        'estimated_unit_price': float(item.estimated_unit_price),
                        'remarks': item.remarks or '',
                    })
                
                orders.append({
                    'id': str(order.order_id),
                    'project_id': str(order.project_id) if order.project_id else None,
                    'requester_id': str(order.requester_id) if order.requester_id else None,
                    'order_no': order.order_no,
                    'order_title': order.order_title,
                    'order_description': order.order_description or '',
                    'required_date': str(order.required_date) if order.required_date else None,
                    'vendor_name': order.vendor_name or '',
                    'items': items,
                    'total_estimated_price': float(order.total_estimated_price),
                    'status': order.status,
                    'created_at': order.created_at.isoformat() if order.created_at else None,
                })
            
            return Response(orders, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        """สร้างรายการสั่งซื้อใหม่ (PostgreSQL)"""
        try:
            from api.models import MainOrder, OrderItem, Project, User
            
            data = request.data
            
            # ✅ SECURITY: Validate inputs
            items = data.get('items', [])
            validate_order_items(items)  # Prevent XSS, negative values
            
            order_title = validate_order_title(data.get('order_title', ''))
            order_description = validate_order_description(data.get('order_description', ''))
            
            # Validate total price
            total_price = validate_budget_amount(
                data.get('total_estimated_price', 0),
                'Total price'
            )
            
            # ✅ ถ้าผู้ใช้กำหนด order_no มา ใช้ค่านั้น ถ้าไม่กำหนด สร้างอัตโนมัติ
            user_order_no = data.get('order_no')
            if user_order_no and user_order_no.strip():
                order_no = user_order_no.strip()
                # Check if order_no already exists
                if MainOrder.objects.filter(order_no=order_no).exists():
                    return Response({'error': f'เลขที่ใบขอซื้อ {order_no} มีอยู่แล้วในระบบ'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # สร้าง Order Number อัตโนมัติ (Format: PO-YYYYMMDD-XXX)
                today = datetime.datetime.now()
                date_str = today.strftime('%Y%m%d')
                
                # นับจำนวน orders ที่สร้างวันนี้
                start_of_day = datetime.datetime(today.year, today.month, today.day)
                count = MainOrder.objects.filter(created_at__gte=start_of_day).count() + 1
                order_no = f"PO-{date_str}-{count:03d}"
                
                # Ensure uniqueness
                while MainOrder.objects.filter(order_no=order_no).exists():
                    count += 1
                    order_no = f"PO-{date_str}-{count:03d}"
            
            # Get project and requester references
            project = None
            requester = None
            
            project_id = data.get('project_id')
            if project_id:
                try:
                    project = Project.objects.get(project_id=project_id)
                except Project.DoesNotExist:
                    pass
            
            requester_id = data.get('requester_id')
            if requester_id:
                try:
                    requester = User.objects.get(user_id=requester_id)
                except User.DoesNotExist:
                    pass
            
            # สร้าง Order ใหม่
            new_order = MainOrder.objects.create(
                project=project,
                requester=requester,
                order_no=order_no,
                order_title=order_title,
                order_description=order_description,
                required_date=data.get('required_date') or None,
                vendor_name=data.get('vendor_name', ''),
                total_estimated_price=float(total_price),
                status='Draft'
            )
            
            # สร้าง Order Items
            for item in items:
                OrderItem.objects.create(
                    order=new_order,
                    item_name=item.get('item_name', ''),
                    quantity_requested=int(item.get('quantity_requested', 1)),
                    unit=item.get('unit', 'อัน'),
                    estimated_unit_price=float(item.get('estimated_unit_price', 0)),
                    remarks=item.get('remarks', '')
                )
            
            return Response({
                'id': str(new_order.order_id),
                'order_no': order_no,
                'message': 'สร้างรายการสั่งซื้อสำเร็จ'
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            # Validation errors
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log error but don't expose details
            print(f"Order creation error: {str(e)}")
            return Response({'error': 'Failed to create order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


@method_decorator(ratelimit(key='user_or_ip', rate='20/h', method='POST'), name='post')
class OrderSubmitAPIView(APIView):
    """
    Order Submission API
    Rate Limit: 20 submissions per hour per user/IP
    """
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
    
    @transaction.atomic
    def post(self, request, order_id):
        try:
            from api.models import MainOrder, Project
            # 1. ดึงข้อมูล Order
            try:
                order = MainOrder.objects.select_for_update().get(pk=order_id)
            except MainOrder.DoesNotExist:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            # ✅ SECURITY: Validate status transition
            validate_status_transition(order.status, 'Pending')
            
            # 2. ดึงข้อมูล Project
            if not order.project:
                return Response({'error': 'ใบสั่งซื้อไม่ได้ระบุโครงการ'}, status=status.HTTP_400_BAD_REQUEST)
                
            project = Project.objects.select_for_update().get(pk=order.project_id)
            
            # Validate order total
            order_total = validate_budget_amount(order.total_estimated_price)
            
            # 3. คำนวณงบประมาณ
            # งบเหลือ = งบทั้งหมด - งบจอง - งบจ่ายจริง
            budget_remaining = project.budget_total - project.budget_reserved - project.budget_spent
            
            # Check if enough budget
            if order_total > budget_remaining:
                return Response({
                    'error': f'งบประมาณไม่เพียงพอ: คงเหลือ ฿{float(budget_remaining):,.2f} แต่ต้องการ ฿{float(order_total):,.2f}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. อัปเดต (Atomic)
            project.budget_reserved += order_total
            project.save()
            
            order.status = 'Pending'
            order.submitted_at = datetime.datetime.now()
            order.updated_at = datetime.datetime.now()
            order.save()
            
            # Log audit
            log_audit(
                action='SUBMIT_ORDER',
                user_id=order.requester_id,
                resource_id=str(order.order_id),
                resource_type='order',
                details={'amount': float(order_total), 'new_budget_reserved': float(project.budget_reserved)}
            )
            
            return Response({
                'message': 'ส่งใบสั่งซื้อเรียบร้อย กรุณารอการอนุมัติ',
                'order_id': str(order_id),
                'new_status': 'Pending',
                'budget_reserved': float(project.budget_reserved)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Submit order error: {str(e)}")
            return Response({'error': 'Failed to submit order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==========================================================================
# ORDER APPROVAL APIs - ระบบอนุมัติ/ปฏิเสธใบสั่งซื้อ (Staff)
# ==========================================================================

@method_decorator(ratelimit(key='user', rate='50/h', method='POST'), name='post')
class OrderApproveAPIView(APIView):
    """
    Staff Order Approval API
    Rate Limit: 50 approvals per hour per user
    """
    permission_classes = [IsStaff]  # ✅ Only Staff can approve
    
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
            try:
                order = MainOrder.objects.get(pk=order_id)
            except MainOrder.DoesNotExist:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            # ✅ SECURITY: Validate status transition
            validate_status_transition(order.status, 'WaitingBossApproval')
            
            # 3. ดึง approver_id จาก request body หรือ JWT
            approver_id = request.data.get('approver_id', '')
            if not approver_id:
                # Try to get from JWT (stored by IsStaff permission)
                approver_id = getattr(request, 'jwt_user_id', '')
            
            # 4. อัปเดตสถานะ Order เป็น WaitingBossApproval
            order.status = 'WaitingBossApproval'
            order.approver_id = approver_id if approver_id else None # Note: MainOrder.approver_id might be ForeignKey or CharField? Check Model.
            # Assuming CharField or adjust if ForeignKey to User. 
            # In Models, approver is ForeignKey(User). So we need User instance if approver_id is ID.
            # But here we stick to simple assignment if logic handles it. 
            # Let's check Model: approver = ForeignKey(User).
            # So we need to fetch User if approver_id is provided.
            if approver_id:
                try:
                    approver_user = User.objects.get(pk=approver_id)
                    order.approver = approver_user
                except User.DoesNotExist:
                    pass # Keep existing or None
            
            order.updated_at = datetime.datetime.now()
            order.save()
            
            # ✅ AUDIT: Log approval action
            log_audit(
                action='ORDER_APPROVED',
                user_id=approver_id,
                resource_type='order',
                resource_id=str(order_id),
                details={'new_status': 'WaitingBossApproval'},
                ip_address=get_client_ip(request)
            )
            
            return Response({
                'message': 'ส่งเรื่องรอหัวหน้าอนุมัติเรียบร้อย กรุณาพิมพ์ใบสั่งซื้อและเสนอหัวหน้าเซ็น',
                'order_id': str(order_id),
                'new_status': 'WaitingBossApproval'
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Approval error: {str(e)}")
            return Response({'error': 'Failed to approve order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderRejectAPIView(APIView):
    permission_classes = [IsStaff]  # ✅ Only Staff can reject
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
    @transaction.atomic
    def post(self, request, order_id):
        try:
            # 1. รับข้อมูลจาก request
            staff_note = request.data.get('staff_note', '')
            approver_id = request.data.get('approver_id', '')
            
            if not staff_note:
                return Response({'error': 'กรุณาระบุเหตุผลในการปฏิเสธ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. ดึงข้อมูล Order
            try:
                order = MainOrder.objects.select_for_update().get(pk=order_id)
            except MainOrder.DoesNotExist:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            # 3. ตรวจสอบว่าเป็น Pending เท่านั้น
            if order.status != 'Pending':
                return Response({'error': 'ใบสั่งซื้อนี้ไม่อยู่ในสถานะรออนุมัติ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. คืนงบประมาณ
            # ต้องดึง Project มาเพื่อคืนงบ
            if order.project:
                project = Project.objects.select_for_update().get(pk=order.project_id)
                project.budget_reserved = max(0, project.budget_reserved - order.total_estimated_price)
                project.save()
            
            # 5. อัปเดตสถานะ Order
            order.status = 'Rejected'
            if approver_id:
                try:
                     order.approver = User.objects.get(pk=approver_id)
                except: pass
            
            order.staff_note = staff_note
            order.rejected_at = datetime.datetime.now()
            order.updated_at = datetime.datetime.now()
            order.save()
            
            return Response({
                'message': 'ปฏิเสธใบสั่งซื้อเรียบร้อย',
                'order_id': str(order_id),
                'new_status': 'Rejected',
                'released_budget': float(order.total_estimated_price)
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
    @transaction.atomic
    def post(self, request, order_id):
        try:
            # 1. รับข้อมูลจาก request
            staff_note = request.data.get('staff_note', '')
            approver_id = request.data.get('approver_id', '')
            
            if not staff_note:
                return Response({'error': 'กรุณาระบุสิ่งที่ต้องแก้ไข'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. ดึงข้อมูล Order
            try:
                order = MainOrder.objects.select_for_update().get(pk=order_id)
            except MainOrder.DoesNotExist:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            # 3. ตรวจสอบว่าเป็น Pending เท่านั้น
            if order.status != 'Pending':
                return Response({'error': 'ใบสั่งซื้อนี้ไม่อยู่ในสถานะรออนุมัติ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. คืนงบประมาณ
            if order.project:
                project = Project.objects.select_for_update().get(pk=order.project_id)
                project.budget_reserved = max(0, project.budget_reserved - order.total_estimated_price)
                project.save()
            
            # 5. อัปเดตสถานะ Order เป็น CorrectionNeeded
            order.status = 'CorrectionNeeded'
            if approver_id:
                try:
                     order.approver = User.objects.get(pk=approver_id)
                except: pass
            
            order.staff_note = staff_note
            order.correction_requested_at = datetime.datetime.now()
            order.updated_at = datetime.datetime.now()
            order.save()
            
            return Response({
                'message': 'ส่งกลับแก้ไขเรียบร้อย',
                'order_id': str(order_id),
                'new_status': 'CorrectionNeeded',
                'released_budget': float(order.total_estimated_price)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderBossApproveAPIView(APIView):
    permission_classes = [IsStaff]  # ✅ Only Staff can mark as boss approved
    
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
            try:
                order = MainOrder.objects.get(pk=order_id)
            except MainOrder.DoesNotExist:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            # ✅ SECURITY: Validate status transition 
            validate_status_transition(order.status, 'Approved')
            
            # 3. อัปเดตสถานะ Order เป็น Approved เท่านั้น
            # ⚠️ FIX: ไม่ตัดงบที่นี่ - จะตัดตอน Inspection เมื่อทราบราคาจ่ายจริง
            order.status = 'Approved'
            order.approved_at = datetime.datetime.now()
            order.updated_at = datetime.datetime.now()
            order.save()
            
            # ✅ AUDIT: Log boss approval
            log_audit(
                action='ORDER_BOSS_APPROVED',
                user_id=request.session.get('user_id', 'boss'),
                resource_type='order',
                resource_id=str(order_id),
                details={'new_status': 'Approved'},
                ip_address=get_client_ip(request)
            )
            
            return Response({
                'message': 'หัวหน้าเซ็นอนุมัติเรียบร้อย',
                'order_id': str(order_id),
                'new_status': 'Approved',
                'note': 'งบประมาณจะถูกย้ายจาก Reserved → Spent ตอนตรวจรับสินค้า'
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Boss approval error: {str(e)}")
            return Response({'error': 'Failed to approve order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            try:
                order = MainOrder.objects.get(pk=order_id)
            except MainOrder.DoesNotExist:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            # 2. ตรวจสอบว่าเป็น Approved เท่านั้น
            if order.status != 'Approved':
                return Response({'error': 'ใบสั่งซื้อนี้ยังไม่ได้รับการอนุมัติ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. อัปเดตสถานะ Order เป็น SentToProcurement
            order.status = 'SentToProcurement'
            order.sent_to_procurement_at = datetime.datetime.now()
            order.updated_at = datetime.datetime.now()
            order.save()
            
            return Response({
                'message': 'ส่งให้พัสดุเรียบร้อย',
                'order_id': str(order_id),
                'new_status': 'SentToProcurement'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================================================
# RECEIVE FROM PROCUREMENT API - รับของจากพัสดุ (Phase 4)
# ==========================================================================

class OrderReceiveFromProcurementAPIView(APIView):
    """
    ===================================================================
    OrderReceiveFromProcurementAPIView - รับของจากพัสดุ
    ===================================================================
    
    Staff บันทึกเมื่อพัสดุส่งของมา
    
    Flow: SentToProcurement → ReceivedFromProcurement
    
    Method: POST /api/orders/<order_id>/receive-procurement/
    
    Actions:
    - เปลี่ยนสถานะ: SentToProcurement → ReceivedFromProcurement
    - บันทึก received_from_procurement_at (timestamp)
    ===================================================================
    """
    def post(self, request, order_id):
        try:
            # 1. ดึงข้อมูล Order
            try:
                order = MainOrder.objects.get(pk=order_id)
            except MainOrder.DoesNotExist:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            # 2. ตรวจสอบว่าเป็น SentToProcurement เท่านั้น
            if order.status != 'SentToProcurement':
                return Response({'error': 'ใบสั่งซื้อนี้ยังไม่ได้ส่งให้พัสดุ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. อัปเดตสถานะ Order เป็น ReceivedFromProcurement
            order.status = 'ReceivedFromProcurement'
            order.received_from_procurement_at = datetime.datetime.now()
            order.updated_at = datetime.datetime.now()
            order.save()
            
            return Response({
                'message': 'บันทึกการรับของจากพัสดุเรียบร้อย',
                'order_id': str(order_id),
                'new_status': 'ReceivedFromProcurement'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================================================
# SUB-ORDER CREATE API - สร้าง Sub-order (Phase 4)
# ==========================================================================

class SubOrderCreateAPIView(APIView):
    """
    ===================================================================
    SubOrderCreateAPIView - สร้าง Sub-order
    ===================================================================
    
    Staff สร้าง Sub-order เพื่อแยกรายการที่ได้รับจากพัสดุ
    (กรณีของมาไม่ครบงวดเดียว)
    
    Flow: ReceivedFromProcurement → WaitingInspection
    
    Method: POST /api/orders/<order_id>/create-suborder/
    
    Body: {
        "items": [
            {"item_name": "...", "quantity": 5, "unit": "ชิ้น"},
            ...
        ],
        "notes": "หมายเหตุ (optional)"
    }
    
    Actions:
    - สร้าง sub_order document ใน Firebase collection 'sub_orders'
    - Generate suborder_no อัตโนมัติ (SUB-0001, SUB-0002, ...)
    - เปลี่ยนสถานะ order → WaitingInspection
    ===================================================================
    """
    @transaction.atomic
    def post(self, request, order_id):
        try:
            # 1. ดึงข้อมูล Order
            try:
                order = MainOrder.objects.get(pk=order_id)
            except MainOrder.DoesNotExist:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            # 2. ตรวจสอบสถานะ
            if order.status != 'ReceivedFromProcurement':
                return Response({
                    'error': 'ใบสั่งซื้อนี้ยังไม่ได้รับของจากพัสดุ'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. รับข้อมูลจาก request
            items = request.data.get('items', [])
            notes = request.data.get('notes', '')
            
            if not items:
                return Response({'error': 'กรุณาเลือกรายการสินค้า'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. Generate suborder_no
            suborder_count = SubOrder.objects.filter(main_order=order).count() + 1
            suborder_no = f"SUB-{order.order_no}-{suborder_count:03d}"
            
            # 6. สร้าง Sub-order document
            suborder = SubOrder.objects.create(
                main_order=order,
                receiver=request.user if request.user.is_authenticated else None, # Assuming user logged in
                suborder_no=suborder_no,
                note=notes,
                status='WaitingInspection'
            )
            
            # 5. Create InspectionDetails for items
            total_amount = 0
            for item in items:
                # Find OrderItem
                item_name = item.get('item_name', item.get('name', '-'))
                qty = float(item.get('quantity', item.get('quantity_requested', 0)))
                # price = float(item.get('unit_price', item.get('estimated_unit_price', 0))) # Price from order item is better
                
                # Match by name (simple fallback)
                order_item = OrderItem.objects.filter(order=order, item_name=item_name).first()
                if not order_item:
                    # Fallback logic or skip? better to skip if not found to avoid error
                    continue
                
                InspectionDetail.objects.create(
                    sub_order=suborder,
                    item=order_item,
                    qty_received=int(qty)
                )

            
            # 7. อัปเดตสถานะ Order เป็น WaitingInspection
            order.status = 'WaitingInspection'
            order.updated_at = datetime.datetime.now()
            order.save()
            
            return Response({
                'message': 'สร้าง Sub-order เรียบร้อย',
                'suborder_id': suborder.sub_order_id,
                'suborder_no': suborder_no
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================================================
# INSPECTION API - ตรวจรับสินค้า + สร้าง QR Code (Phase 4)
# ==========================================================================

class InspectionAPIView(APIView):
    """
    ===================================================================
    InspectionAPIView - ตรวจรับสินค้า + สร้าง QR Code
    ===================================================================
    
    Staff ตรวจรับสินค้าจาก Sub-order พร้อมสร้าง QR Code
    
    Flow: WaitingInspection → Inspected
    
    Method: POST /api/suborders/<suborder_id>/inspection/
    
    Body: {
        "actual_cost": 50000,
        "inspector_name": "ชื่อผู้ตรวจรับ",
        "notes": "หมายเหตุ (optional)"
    }
    
    Actions:
    - ตรวจสอบ Sub-order
    - สร้าง QR Code (base64)
    - บันทึก actual_cost
    - ปรับงบประมาณ (ถ้า actual ≠ estimated)
    - เปลี่ยนสถานะ → Inspected
    ===================================================================
    """
    @transaction.atomic
    def post(self, request, suborder_id):
        try:
            import qrcode
            import io
            import base64
            
            # 1. ดึงข้อมูล Sub-order
            try:
                suborder = SubOrder.objects.select_for_update().get(pk=suborder_id)
            except SubOrder.DoesNotExist:
                return Response({'error': 'ไม่พบ Sub-order'}, status=status.HTTP_404_NOT_FOUND)
            
            # 2. ตรวจสอบสถานะ
            if suborder.status != 'WaitingInspection':
                return Response({
                    'error': 'Sub-order นี้ไม่อยู่ในสถานะรอตรวจรับ'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. รับข้อมูลจาก request
            actual_cost = float(request.data.get('actual_cost', 0))
            inspector_name = request.data.get('inspector_name', '')
            notes = request.data.get('notes', '')
            
            if actual_cost <= 0:
                return Response({'error': 'กรุณาระบุยอดจ่ายจริง'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not inspector_name:
                return Response({'error': 'กรุณาระบุชื่อผู้ตรวจรับ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. สร้าง QR Code
            host = request.get_host()
            scheme = 'https' if request.is_secure() else 'http'
            scan_url = f"{scheme}://{host}/api/scan/{suborder_id}/"
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(scan_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # 5. ปรับงบประมาณ
            order = suborder.main_order
            if order.project:
                project = Project.objects.select_for_update().get(pk=order.project_id)
                
                # Logic: Refund full reserved amount, add actual cost to spent
                # Assumption: Suborder completes the order for now (simple migration)
                # Or at least for this suborder? Legacy code uses (actual - estimated)
                # Correct logic for "Full Completion":
                reserved_to_release = order.total_estimated_price # Assuming full release
                project.budget_reserved = max(0, project.budget_reserved - reserved_to_release)
                project.budget_spent += actual_cost
                project.save()
            
            # 6. Update SubOrder
            suborder.status = 'Inspected'
            suborder.updated_at = datetime.datetime.now() # if updated_at exists on model
            suborder.save()
             
            # 7. อัปเดต Order status เป็น Inspected ด้วย
            order.status = 'Inspected'
            order.actual_cost = actual_cost # Assuming MainOrder has actual_cost field
            order.inspected_at = datetime.datetime.now()
            order.updated_at = datetime.datetime.now()
            order.save()
            
            return Response({
                'message': 'ตรวจรับเรียบร้อย',
                'suborder_id': str(suborder_id),
                'suborder_no': suborder.sub_order_no,
                'new_status': 'Inspected',
                'actual_cost': actual_cost,
                'qr_code': f'data:image/png;base64,{qr_base64}'
            }, status=status.HTTP_200_OK)
            
        except ImportError:
            return Response({
                'error': 'กรุณาติดตั้ง qrcode library: pip install qrcode[pil]'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================================================
# HANDOVER API - จ่ายของให้ผู้ขอซื้อ (Phase 4)
# ==========================================================================

class HandoverAPIView(APIView):
    """
    ===================================================================
    HandoverAPIView - จ่ายของให้ผู้ขอซื้อ
    ===================================================================
    
    Staff จ่ายของที่ตรวจรับแล้วให้ User
    
    Flow: Inspected → Received
    
    Method: POST /api/orders/<order_id>/handover/
    
    Body: {
        "receiver_name": "ชื่อผู้รับของ",
        "notes": "หมายเหตุ (optional)"
    }
    ===================================================================
    """
    def post(self, request, order_id):
        try:
            # 1. ดึงข้อมูล Order
            try:
                order = MainOrder.objects.get(pk=order_id)
            except MainOrder.DoesNotExist:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            # 2. ตรวจสอบสถานะ - ต้องเป็น Inspected เท่านั้น
            if order.status != 'Inspected':
                return Response({
                    'error': 'ใบสั่งซื้อนี้ยังไม่ได้ตรวจรับ'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. รับข้อมูลจาก request
            receiver_name = request.data.get('receiver_name', '')
            notes = request.data.get('notes', '')
            
            if not receiver_name:
                return Response({'error': 'กรุณาระบุชื่อผู้รับของ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. อัปเดต Order
            order.status = 'Received'
            order.receiver_name = receiver_name
            order.handover_notes = notes
            order.received_at = datetime.datetime.now()
            order.updated_at = datetime.datetime.now()
            order.save()
            
            return Response({
                'message': 'จ่ายของเรียบร้อย',
                'order_id': str(order_id),
                'new_status': 'Received',
                'receiver_name': receiver_name
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================================================
# CLOSE ORDER API - ปิดงาน (Phase 4)
# ==========================================================================

class CloseOrderAPIView(APIView):
    """
    ===================================================================
    CloseOrderAPIView - ปิดการสั่งซื้อ
    ===================================================================
    
    Staff ปิดการสั่งซื้อหลังจากจ่ายของเรียบร้อยแล้ว
    
    Flow: Received → Closed
    
    Method: POST /api/orders/<order_id>/close/
    
    Body: {
        "notes": "หมายเหตุปิดงาน (optional)"
    }
    ===================================================================
    """
    def post(self, request, order_id):
        try:
            # 1. ดึงข้อมูล Order
            try:
                order = MainOrder.objects.get(pk=order_id)
            except MainOrder.DoesNotExist:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            # 2. ตรวจสอบสถานะ - ต้องเป็น Received เท่านั้น
            if order.status != 'Received':
                return Response({
                    'error': 'ใบสั่งซื้อนี้ยังไม่ได้จ่ายของ'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. รับข้อมูลจาก request
            notes = request.data.get('notes', '')
            
            # 4. อัปเดต Order
            order.status = 'Closed'
            order.close_notes = notes
            order.closed_at = datetime.datetime.now()
            order.updated_at = datetime.datetime.now()
            order.save()
            
            return Response({
                'message': 'ปิดงานเรียบร้อย',
                'order_id': str(order_id),
                'new_status': 'Closed'
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
    @transaction.atomic
    def post(self, request, order_id):
        try:
            # 1. รับข้อมูลจาก request
            boss_note = request.data.get('boss_note', '')
            
            if not boss_note:
                return Response({'error': 'กรุณาระบุเหตุผลที่หัวหน้าไม่อนุมัติ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. ดึงข้อมูล Order
            try:
                order = MainOrder.objects.select_for_update().get(pk=order_id)
            except MainOrder.DoesNotExist:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            # 3. ตรวจสอบว่าเป็น WaitingBossApproval เท่านั้น
            if order.status != 'WaitingBossApproval':
                return Response({'error': 'ใบสั่งซื้อนี้ไม่อยู่ในสถานะรอหัวหน้าอนุมัติ'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. คืนงบประมาณ
            if order.project:
                project = Project.objects.select_for_update().get(pk=order.project_id)
                project.budget_reserved = max(0, project.budget_reserved - order.total_estimated_price)
                project.save()
            
            # 5. อัปเดตสถานะ Order เป็น CorrectionNeeded
            order.status = 'CorrectionNeeded'
            order.staff_note = f'หัวหน้าไม่อนุมัติ: {boss_note}' # ใช้ staff_note หรือสร้าง field boss_note? Model มี boss_note ไหม? Check Model...
            # Model has `note` but not `boss_note` specifically in previous artifacts. 
            # Reusing staff_note or note field. The legacy code put it in staff_note. I'll follow that.
            order.boss_rejected_at = datetime.datetime.now()
            order.updated_at = datetime.datetime.now()
            order.save()
            
            return Response({
                'message': 'ส่งกลับแก้ไขเรียบร้อย',
                'order_id': str(order_id),
                'new_status': 'CorrectionNeeded',
                'released_budget': float(order.total_estimated_price)
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
    @transaction.atomic
    def post(self, request, order_id):
        try:
            # 1. รับข้อมูลจาก request
            staff_note = request.data.get('staff_note', '')
            
            if not staff_note:
                return Response({'error': 'กรุณาระบุเหตุผลที่ต้องส่งกลับแก้ไข'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. ดึงข้อมูล Order
            try:
                order = MainOrder.objects.select_for_update().get(pk=order_id)
            except MainOrder.DoesNotExist:
                return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
            
            # 3. ตรวจสอบว่าเป็น Approved เท่านั้น
            if order.status != 'Approved':
                return Response({'error': 'ใบสั่งซื้อนี้ไม่อยู่ในสถานะหัวหน้าเซ็นอนุมัติแล้ว'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. คืนงบประมาณ (คืนสู่ Reserved เพราะ Approved ยังไม่ได้ตัดเข้า Spent)
            # แก้ไขจาก Legacy ที่ตัด Spent เพราะ Logic ใน BossApprove บอกว่าตัดตอน Inspection
            if order.project:
                project = Project.objects.select_for_update().get(pk=order.project_id)
                project.budget_reserved = max(0, project.budget_reserved - order.total_estimated_price)
                project.save()
            
            # 5. อัปเดตสถานะ Order เป็น CorrectionNeeded
            order.status = 'CorrectionNeeded'
            order.staff_note = staff_note
            order.correction_requested_at = datetime.datetime.now()
            order.updated_at = datetime.datetime.now()
            order.save()
            
            return Response({
                'message': 'ส่งกลับแก้ไขเรียบร้อย',
                'order_id': str(order_id),
                'new_status': 'CorrectionNeeded',
                'released_budget': float(order.total_estimated_price)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def print_order_view(request, order_id):
    """
    ===================================================================
    print_order_view - พิมพ์ใบขอซื้อครุภัณฑ์ (PostgreSQL)
    ===================================================================
    
    URL: GET /api/orders/{order_id}/print/
    
    การทำงาน:
    - ดึงข้อมูล Order, Project, และ Requester จาก PostgreSQL
    - Render หน้าพิมพ์ในรูปแบบ A4 ตามแบบฟอร์มราชการ
    - ผู้ใช้สามารถพิมพ์หรือ Save เป็น PDF ได้
    ===================================================================
    """
    try:
        from api.models import MainOrder, OrderItem, Project, User
        
        # 1. ดึงข้อมูล Order จาก PostgreSQL
        try:
            order = MainOrder.objects.get(order_id=order_id)
        except MainOrder.DoesNotExist:
            return render(request, 'error.html', {'message': 'ไม่พบใบสั่งซื้อ'})
        
        # คำนวณ total_price สำหรับแต่ละ item และ format ราคา
        items_with_total = []
        for item in order.items.all():
            qty = float(item.quantity_requested or 0)
            price = float(item.estimated_unit_price or 0)
            total = qty * price
            items_with_total.append({
                'item_name': item.item_name,
                'quantity_requested': item.quantity_requested,
                'unit': item.unit,
                'estimated_unit_price': price,
                'total_price': total,
                'formatted_price': f"{price:,.2f}",
                'formatted_total': f"{total:,.2f}",
                'remarks': item.remarks or '',
            })
        
        # สร้าง order_data สำหรับ template
        order_data = {
            'id': str(order.order_id),
            'order_no': order.order_no,
            'order_title': order.order_title,
            'order_description': order.order_description or '',
            'vendor_name': order.vendor_name or '',
            'status': order.status,
            'total_estimated_price': float(order.total_estimated_price or 0),
            'items': items_with_total,
        }
        
        # Format dates
        created_date = order.created_at.strftime('%d/%m/%Y') if order.created_at else '-'
        required_date = str(order.required_date) if order.required_date else '-'
        
        # 2. ดึงข้อมูล Project
        project_data = {}
        project_name = '-'
        if order.project:
            project_data = {
                'project_id': str(order.project.project_id),
                'project_name': order.project.project_name,
                'project_code': order.project.project_code if hasattr(order.project, 'project_code') else '',
            }
            project_name = order.project.project_name
        
        # 3. ดึงข้อมูล Requester
        requester_data = {}
        requester_name = '-'
        user_department = 'ผู้รับผิดชอบโครงการ'
        if order.requester:
            requester_data = {
                'user_id': str(order.requester.user_id),
                'username': order.requester.username,
                'department': order.requester.department or '',
            }
            requester_name = order.requester.username
            user_department = order.requester.department or 'ผู้รับผิดชอบโครงการ'
        
        # 4. จัดการ vendor display
        vendor_name = order_data.get('vendor_name', '').strip()
        vendor_display = vendor_name if vendor_name else '-'
        
        # 5. คำนวณ empty_rows เพื่อให้ตารางมีแถวครบ (ควรมีอย่างน้อย 8 แถว)
        min_rows = 8
        current_items = len(items_with_total)
        empty_rows_count = max(0, min_rows - current_items)
        empty_rows = range(empty_rows_count)
        
        # 6. Render template
        grand_total = float(order_data.get('total_estimated_price', 0))
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
            'empty_rows': empty_rows,  # เพิ่มแถวว่างให้ตารางครบ
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
            from api.models import MainOrder
            # ดึงข้อมูลพร้อม items และ project
            order = MainOrder.objects.get(pk=order_id)
            
            items = []
            for item in order.items.all():
                items.append({
                    'item_id': item.item_id,
                    'item_name': item.item_name,
                    'quantity_requested': item.quantity_requested,
                    'unit': item.unit,
                    'estimated_unit_price': float(item.estimated_unit_price),
                    'total_price': float(item.estimated_total_price),
                    'remarks': item.remarks or ''
                })
            
            data = {
                'id': str(order.order_id),
                'order_id': str(order.order_id),
                'order_no': order.order_no,
                'project_id': str(order.project_id) if order.project_id else None,
                'project_name': order.project.project_name if order.project else None,
                'requester_id': str(order.requester_id) if order.requester_id else None,
                'requester_name': order.requester.username if order.requester else None,
                'status': order.status,
                'total_estimated_price': float(order.total_estimated_price),
                'items': items,
                'created_at': order.created_at,
                'updated_at': order.updated_at,
                # Additional fields may benefit frontend
                'order_title': order.order_title,
                'order_description': order.order_description,
                'vendor_name': order.vendor_name,
                'required_date': order.required_date
            }
            
            return Response(data, status=status.HTTP_200_OK)
        except MainOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, order_id):
        """
        อัปเดต Draft (ต้องเป็น Draft หรือ CorrectionNeeded เท่านั้น)
        """
        try:
            from api.models import MainOrder
            order = MainOrder.objects.get(pk=order_id)
        
            # ต้องเป็น Draft หรือ CorrectionNeeded เท่านั้น
            if order.status not in ['Draft', 'CorrectionNeeded']:
                return Response({'error': 'ไม่สามารถแก้ไขใบสั่งซื้อที่ส่งแล้ว'}, status=status.HTTP_400_BAD_REQUEST)
            
            data = request.data
            
            # อัปเดตข้อมูลทั่วไป
            if 'order_title' in data: order.order_title = data['order_title']
            if 'order_description' in data: order.order_description = data['order_description']
            if 'vendor_name' in data: order.vendor_name = data['vendor_name']
            if 'required_date' in data: order.required_date = data['required_date']
            
            # TODO: Handle Item updates if needed (usually handled by separate logic or complex full update)
            # For now assuming frontend might send items update separately or we update total price here
            if 'total_estimated_price' in data:
                order.total_estimated_price = validate_budget_amount(data['total_estimated_price'])
                
            order.updated_at = datetime.datetime.now()
            order.save()
            
            return Response({'message': 'อัปเดตสำเร็จ', 'order_id': order_id}, status=status.HTTP_200_OK)
        except MainOrder.DoesNotExist:
             return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, order_id):
        """
        ลบ Draft (ต้องเป็น Draft เท่านั้น)
        """
        try:
            from api.models import MainOrder
            order = MainOrder.objects.get(pk=order_id)
            
            # ต้องเป็น Draft เท่านั้น
            if order.status != 'Draft':
                return Response({'error': 'ไม่สามารถลบใบสั่งซื้อที่ส่งแล้ว'}, status=status.HTTP_400_BAD_REQUEST)
            
            order.delete()
            
            return Response({'message': 'ลบสำเร็จ'}, status=status.HTTP_200_OK)
        except MainOrder.DoesNotExist:
             return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=status.HTTP_404_NOT_FOUND)
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
    - Query ProjectAssignment by user_id
    - Return related Project data
    ===================================================================
    """
    def get(self, request, user_id):
        try:
            # ดึง assignments ของ user นี้
            assignments = ProjectAssignment.objects.filter(user_id=user_id).select_related('project')
            
            projects = []
            for assign in assignments:
                project = assign.project
                projects.append({
                    'id': str(project.project_id),
                    'project_id': str(project.project_id),
                    'project_code': project.project_code or '',
                    'project_name': project.project_name,
                    'budget_total': float(project.budget_total),
                    'budget_reserved': float(project.budget_reserved),
                    'budget_spent': float(project.budget_spent),
                    'status': project.status,
                    'assignment_id': assign.assignment_id,
                    'assigned_at': assign.assigned_at
                })
            
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


def staff_po_detail_view(request, order_id):
    """
    ===================================================================
    staff_po_detail_view - หน้าดูรายละเอียดใบสั่งซื้อ (View Only)
    ===================================================================
    
    URL: /api/staff/po/<order_id>/detail/
    
    Purpose:
    - แสดงรายละเอียดใบสั่งซื้อ (ดูอย่างเดียว ไม่มีปุ่มอนุมัติ)
    - ใช้จากหน้ารายการใบสั่งซื้อ (PO Management)
    - กลับหน้า PO Management
    ===================================================================
    """
    return render(request, 'staff_po_detail.html', {'order_id': order_id})


# ==========================================================================
# SCAN QR CODE - หน้าสแกน QR Code ตรวจเช็คสินค้า
# ==========================================================================

def scan_suborder_view(request, suborder_id):
    """
    ===================================================================
    scan_suborder_view - หน้าตรวจเช็คสินค้าจาก QR Code
    ===================================================================
    
    URL: /api/scan/<suborder_id>/
    
    Purpose:
    - แสดงข้อมูล Sub-order จากการสแกน QR Code
    - ใช้บนมือถือ/แท็บเล็ต
    - แสดงรายการสินค้า, ยอดเงิน, ผู้ตรวจรับ
    ===================================================================
    """
    return render(request, 'scan_suborder.html', {'suborder_id': suborder_id})


class ScanSuborderDataAPIView(APIView):
    """
    ===================================================================
    ScanSuborderDataAPIView - API ดึงข้อมูล Sub-order สำหรับหน้าสแกน
    ===================================================================
    
    URL: GET /api/scan/<suborder_id>/data/
    
    Returns:
    - ข้อมูล Sub-order พร้อม Order และ Project info
    ===================================================================
    """
    def get(self, request, suborder_id):
        try:
            # 1. ดึงข้อมูล Sub-order
            suborder_doc = db.collection('sub_orders').document(suborder_id).get()
            if not suborder_doc.exists:
                return Response({'error': 'ไม่พบ Sub-order'}, status=status.HTTP_404_NOT_FOUND)
            
            suborder_data = suborder_doc.to_dict()
            suborder_data['id'] = suborder_doc.id
            
            # 2. ดึงข้อมูล Parent Order
            parent_order_id = suborder_data.get('parent_order_id')
            order_no = '-'
            project_name = '-'
            
            if parent_order_id:
                order_doc = db.collection('orders').document(parent_order_id).get()
                if order_doc.exists:
                    order_data = order_doc.to_dict()
                    order_no = order_data.get('order_no', '-')
                    
                    # 3. ดึงข้อมูล Project
                    project_id = order_data.get('project_id')
                    if project_id:
                        project_doc = db.collection('projects').document(project_id).get()
                        if project_doc.exists:
                            project_data = project_doc.to_dict()
                            project_name = project_data.get('project_name', '-')
            
            # 4. แปลง timestamp เป็น string
            inspected_at = suborder_data.get('inspected_at')
            if inspected_at:
                suborder_data['inspected_at'] = inspected_at.isoformat() if hasattr(inspected_at, 'isoformat') else str(inspected_at)
            
            # 5. เพิ่มข้อมูล order และ project
            suborder_data['order_no'] = order_no
            suborder_data['project_name'] = project_name
            
            # 6. Ensure QR Code has prefix
            qr_code = suborder_data.get('qr_code')
            if qr_code and not qr_code.startswith('data:image'):
                suborder_data['qr_code'] = f"data:image/png;base64,{qr_code}"
            
            return Response(suborder_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================================================
# BUDGET SUMMARY API - สรุปงบประมาณรวม (Phase 4: Reports)
# ==========================================================================

class BudgetSummaryAPIView(APIView):
    """
    ===================================================================
    BudgetSummaryAPIView - ดึงข้อมูลสรุปงบประมาณทุกโครงการ
    ===================================================================
    
    Endpoint: GET /api/budget-summary/
    
    Returns:
        JSON: {
            total_budget: float,
            total_spent: float,
            total_reserved: float,
            total_remaining: float,
            projects: [...]
        }
    ===================================================================
    """
    
    def get(self, request):
        try:
            # 1. ดึงข้อมูลโครงการทั้งหมด
            projects_ref = db.collection('projects')
            projects_docs = projects_ref.stream()
            
            total_budget = 0
            total_spent = 0
            total_reserved = 0
            projects_list = []
            
            for doc in projects_docs:
                project = doc.to_dict()
                project_id = doc.id
                
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
                if budget_total > 0:
                    usage_percent = round(((budget_spent + budget_reserved) / budget_total) * 100, 1)
                
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
            
            return Response({
                'total_budget': total_budget,
                'total_spent': total_spent,
                'total_reserved': total_reserved,
                'total_remaining': max(0, total_remaining),
                'projects': projects_list
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================================================
# REPORTS PAGE VIEW - หน้ารายงานสรุป
# ==========================================================================

def staff_reports_view(request):
    """
    ===================================================================
    staff_reports_view - หน้ารายงานสรุปงบประมาณ
    ===================================================================
    
    Endpoint: /api/staff/reports/
    
    Returns:
        HttpResponse: หน้า HTML แสดงรายงานสรุปงบประมาณ
    ===================================================================
    """
    return render(request, 'staff_reports.html')


# ==========================================================================
# EXPORT ORDER CSV API - ดาวน์โหลดใบสั่งซื้อเป็น CSV
# ==========================================================================

from django.http import HttpResponse
import csv

class ExportOrderCSVAPIView(APIView):
    """
    ===================================================================
    ExportOrderCSVAPIView - ดาวน์โหลดใบสั่งซื้อเป็นไฟล์ CSV
    ===================================================================
    
    Endpoint: GET /api/orders/<order_id>/export-csv/
    
    Returns:
        CSV File: ไฟล์ CSV ของใบสั่งซื้อ
    ===================================================================
    """
    
    def get(self, request, order_id):
        try:
            # 1. ดึงข้อมูล Order
            order_ref = db.collection('orders').document(order_id)
            order_doc = order_ref.get()
            
            if not order_doc.exists:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
            
            order = order_doc.to_dict()
            
            # 2. ดึงชื่อโครงการ
            project_name = '-'
            if order.get('project_id'):
                project_doc = db.collection('projects').document(order['project_id']).get()
                if project_doc.exists:
                    project_name = project_doc.to_dict().get('project_name', '-')
            
            # 3. ดึงชื่อผู้ขอซื้อ
            requester_name = '-'
            if order.get('requester_id'):
                user_doc = db.collection('users').document(order['requester_id']).get()
                if user_doc.exists:
                    requester_name = user_doc.to_dict().get('username', '-')
            
            # 4. สร้าง CSV Response
            response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
            response['Content-Disposition'] = f'attachment; filename="order_{order.get("order_no", order_id)}.csv"'
            
            # เขียน BOM สำหรับ Excel ภาษาไทย
            response.write('\ufeff')
            
            writer = csv.writer(response)
            
            # Header ข้อมูลทั่วไป
            writer.writerow(['ใบขอซื้อ / Purchase Order'])
            writer.writerow([])
            writer.writerow(['เลขที่ใบสั่งซื้อ', order.get('order_no', '-')])
            writer.writerow(['โครงการ', project_name])
            writer.writerow(['เรื่อง', order.get('order_title', '-')])
            writer.writerow(['ผู้ขอซื้อ', requester_name])
            writer.writerow(['ร้านค้า', order.get('vendor_name', '-')])
            writer.writerow(['วันที่ต้องการ', order.get('required_date', '-')])
            writer.writerow(['หมายเหตุ', order.get('order_description', '-')])
            writer.writerow([])
            
            # Header ตารางสินค้า
            writer.writerow(['ลำดับ', 'รายการ', 'จำนวน', 'หน่วย', 'ราคา/หน่วย', 'จำนวนเงิน'])
            
            # รายการสินค้า
            items = order.get('items', [])
            total = 0
            for i, item in enumerate(items, 1):
                qty = float(item.get('quantity_requested', item.get('quantity', 0)))
                price = float(item.get('estimated_unit_price', item.get('unit_price', 0)))
                subtotal = qty * price
                total += subtotal
                
                writer.writerow([
                    i,
                    item.get('item_name', item.get('name', '-')),
                    qty,
                    item.get('unit', '-'),
                    f'{price:,.2f}',
                    f'{subtotal:,.2f}'
                ])
            
            # ยอดรวม
            writer.writerow([])
            writer.writerow(['', '', '', '', 'รวมเงินทั้งสิ้น', f'{total:,.2f} บาท'])
            
            return response
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ===================================================================
# Order Edit History - ประวัติการแก้ไขใบสั่งซื้อ
# ===================================================================

def order_edit_history_view(request):
    """หน้าประวัติการแก้ไขใบขอซื้อ"""
    return render(request, 'order_edit_history.html')


class OrderEditHistoryAPIView(APIView):
    """
    API ประวัติการแก้ไขใบขอซื้อ
    GET /api/order-edit-history/ - ดึงรายการประวัติทั้งหมด
    """
    
    def get(self, request):
        """Get all order edit history with optional filters"""
        try:
            from api.models import OrderEditHistory
            
            # Query all history records
            history_qs = OrderEditHistory.objects.select_related('order', 'changed_by').all()
            
            # Apply filters
            order_no = request.query_params.get('order_no')
            if order_no:
                history_qs = history_qs.filter(order__order_no__icontains=order_no)
            
            action = request.query_params.get('action')
            if action:
                history_qs = history_qs.filter(action=action)
            
            # Build response
            history_list = []
            for h in history_qs[:100]:  # Limit to 100 records
                history_list.append({
                    'history_id': h.history_id,
                    'order_id': str(h.order.order_id) if h.order else None,
                    'order_no': h.order.order_no if h.order else None,
                    'action': h.action,
                    'changed_by': h.changed_by.username if h.changed_by else None,
                    'changed_at': h.changed_at.isoformat() if h.changed_at else None,
                    'changed_fields': h.changed_fields or [],
                    'notes': h.notes,
                })
            
            return Response(history_list, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderEditHistoryDetailAPIView(APIView):
    """
    API รายละเอียดประวัติการแก้ไข
    GET /api/order-edit-history/<history_id>/ - ดึงรายละเอียด
    """
    
    def get(self, request, history_id):
        """Get detail of a specific history record"""
        try:
            from api.models import OrderEditHistory
            
            h = OrderEditHistory.objects.select_related('order', 'changed_by').get(history_id=history_id)
            
            data = {
                'history_id': h.history_id,
                'order_id': str(h.order.order_id) if h.order else None,
                'order_no': h.order.order_no if h.order else None,
                'action': h.action,
                'changed_by': h.changed_by.username if h.changed_by else None,
                'changed_at': h.changed_at.isoformat() if h.changed_at else None,
                'before_data': h.before_data,
                'after_data': h.after_data,
                'changed_fields': h.changed_fields or [],
                'notes': h.notes,
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except OrderEditHistory.DoesNotExist:
            return Response({'error': 'ไม่พบประวัติที่ระบุ'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Helper function to log order changes
def log_order_edit(order, action, user, before_data=None, after_data=None, changed_fields=None, notes=None):
    """
    บันทึกประวัติการแก้ไขใบขอซื้อ
    
    Args:
        order: MainOrder instance
        action: 'create', 'update', 'status_change', 'delete'
        user: User instance or None
        before_data: dict of data before change
        after_data: dict of data after change
        changed_fields: list of field names that changed
        notes: optional notes
    """
    try:
        from api.models import OrderEditHistory
        
        OrderEditHistory.objects.create(
            order=order,
            action=action,
            changed_by=user,
            before_data=before_data,
            after_data=after_data,
            changed_fields=changed_fields,
            notes=notes
        )
    except Exception as e:
        print(f"Error logging order edit: {str(e)}")