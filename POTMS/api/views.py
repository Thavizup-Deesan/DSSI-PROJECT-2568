import json
from decimal import Decimal

from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    User, Project, ProjectParticipant,
    PurchaseOrder, OrderItem, PartialReceive,
    Inspection, Payment
)


# =================================================================
# Helper: Get current user from session
# =================================================================

def get_current_user(request):
    """ดึง User จาก session (หลัง Google Login)"""
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return None


def require_role(roles):
    """Decorator: ตรวจสอบว่า user มี role ที่กำหนด"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user = get_current_user(request)
            if not user:
                return JsonResponse({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)
            if user.role not in roles:
                return JsonResponse({'error': 'ไม่มีสิทธิ์เข้าถึง'}, status=403)
            request.current_user = user
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# =================================================================
# Page Views — Template rendering
# =================================================================

def homepage(request):
    """หน้าแรก — redirect ไป login"""
    return redirect('login_page')


def login_page(request):
    """หน้า Login ด้วย Google"""
    from django.conf import settings
    return render(request, 'login.html', {
        'google_client_id': settings.GOOGLE_CLIENT_ID,
    })


def officer_dashboard_page(request):
    """Dashboard สำหรับ Officer"""
    return render(request, 'officer_dashboard.html')


def user_dashboard_page(request):
    """Dashboard สำหรับ User"""
    return render(request, 'user_dashboard.html')


def project_list_page(request):
    """หน้ารายการโครงการ"""
    return render(request, 'project_list.html')


def participant_setup_page(request):
    """หน้าระบุผู้รับผิดชอบโครงการ"""
    return render(request, 'participant_setup.html')


def create_order_page(request):
    """หน้าสร้างใบสั่งซื้อ"""
    return render(request, 'create_order.html')


def edit_order_page(request):
    """หน้าแก้ไขใบสั่งซื้อ"""
    return render(request, 'edit_order.html')


def my_orders_page(request):
    """หน้ารายการใบสั่งซื้อของ User"""
    return render(request, 'my_orders.html')


def order_detail_page(request):
    """หน้ารายละเอียดใบสั่งซื้อ"""
    return render(request, 'order_detail.html')


def officer_orders_page(request):
    """หน้าจัดการใบสั่งซื้อ (Officer)"""
    return render(request, 'officer_orders.html')


def partial_receive_page(request):
    """หน้าบันทึกใบรับของ"""
    return render(request, 'partial_receive.html')


def inspection_page(request):
    """หน้าตรวจรับสินค้า (กรรมการ)"""
    return render(request, 'inspection.html')


def payment_page(request):
    """หน้าตั้งเบิกจ่าย"""
    return render(request, 'payment.html')


def project_closure_page(request):
    """หน้าปิดโครงการ"""
    return render(request, 'project_closure.html')


def user_management_page(request):
    """หน้าจัดการ User (Officer)"""
    return render(request, 'user_management.html')


# =================================================================
# Auth API — Google OAuth
# Activity: เข้าสู่ระบบด้วย Google
# =================================================================

class GoogleLoginAPIView(APIView):
    """
    POST /api/auth/google/
    รับ id_token จาก Google → ตรวจ @ubu.ac.th → auto-create User → login
    """

    def post(self, request):
        id_token_str = request.data.get('id_token', '')

        if not id_token_str:
            return Response(
                {'error': 'กรุณาส่ง id_token'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from google.oauth2 import id_token
            from google.auth.transport import requests as google_requests
            from django.conf import settings

            # Verify id_token with Google
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                audience=settings.GOOGLE_CLIENT_ID
            )

            email = idinfo.get('email', '')
            full_name = idinfo.get('name', '')

            # ตรวจว่า email ลงท้ายด้วย @ubu.ac.th
            if not email.endswith('@ubu.ac.th'):
                return Response(
                    {'error': 'กรุณาใช้อีเมล @ubu.ac.th เท่านั้น'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Auto-create User ถ้ายังไม่มีใน DB
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': full_name,
                    'role': 'User',
                }
            )

            # อัปเดต full_name ถ้ามีการเปลี่ยนใน Google
            if not created and user.full_name != full_name:
                user.full_name = full_name
                user.save()

            # บันทึกลง session
            request.session['user_id'] = user.user_id
            request.session['user_email'] = user.email
            request.session['user_role'] = user.role
            request.session['user_full_name'] = user.full_name

            return Response({
                'message': 'เข้าสู่ระบบสำเร็จ',
                'user': {
                    'user_id': user.user_id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                    'department': user.department,
                },
                'redirect': '/officer/dashboard/' if user.role == 'Officer' else '/user/dashboard/'
            })

        except ValueError as e:
            return Response(
                {'error': f'Token ไม่ถูกต้อง: {str(e)}'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {'error': f'เกิดข้อผิดพลาด: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =================================================================
# Google OAuth — Redirect Callback (form POST from Google)
# =================================================================

@csrf_exempt
def google_callback_view(request):
    """
    POST /api/auth/google-callback/
    Google จะ redirect กลับมาพร้อม POST form data: credential, g_csrf_token
    """
    if request.method != 'POST':
        return redirect('login_page')

    credential = request.POST.get('credential', '')
    if not credential:
        from django.conf import settings
        return render(request, 'login.html', {
            'google_client_id': settings.GOOGLE_CLIENT_ID,
            'error': 'ไม่ได้รับ credential จาก Google',
        })

    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        from django.conf import settings

        # Verify id_token with Google
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            audience=settings.GOOGLE_CLIENT_ID
        )

        email = idinfo.get('email', '')
        full_name = idinfo.get('name', '')

        # ตรวจว่า email ลงท้ายด้วย @ubu.ac.th
        if not email.endswith('@ubu.ac.th'):
            return render(request, 'login.html', {
                'google_client_id': settings.GOOGLE_CLIENT_ID,
                'error': 'กรุณาใช้อีเมล @ubu.ac.th เท่านั้น',
            })

        # Auto-create User ถ้ายังไม่มีใน DB
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'role': 'User',
            }
        )

        # อัปเดต full_name ถ้ามีการเปลี่ยนใน Google
        if not created and user.full_name != full_name:
            user.full_name = full_name
            user.save()

        # บันทึกลง session
        request.session['user_id'] = user.user_id
        request.session['user_email'] = user.email
        request.session['user_role'] = user.role
        request.session['user_full_name'] = user.full_name

        # Redirect ไป dashboard ตาม role
        if user.role == 'Officer':
            return redirect('officer_dashboard')
        else:
            return redirect('user_dashboard')

    except ValueError as e:
        from django.conf import settings
        return render(request, 'login.html', {
            'google_client_id': settings.GOOGLE_CLIENT_ID,
            'error': f'Token ไม่ถูกต้อง: {str(e)}',
        })
    except Exception as e:
        from django.conf import settings
        return render(request, 'login.html', {
            'google_client_id': settings.GOOGLE_CLIENT_ID,
            'error': f'เกิดข้อผิดพลาด: {str(e)}',
        })


class LogoutAPIView(APIView):
    """POST /api/auth/logout/ — ออกจากระบบ"""

    def post(self, request):
        request.session.flush()
        return Response({'message': 'ออกจากระบบสำเร็จ'})


class CurrentUserAPIView(APIView):
    """GET /api/auth/me/ — ดึงข้อมูล user ปัจจุบัน"""

    def get(self, request):
        user = get_current_user(request)
        if not user:
            return Response(
                {'error': 'ไม่ได้เข้าสู่ระบบ'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response({
            'user_id': user.user_id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'department': user.department,
        })


# =================================================================
# Project APIs
# Activity: นำเข้าโครงการ → ตรวจสอบ → ระบุผู้เข้าร่วม → เริ่ม PRJ
# UI State: S1 (Project Draft) → S2 (Participant Setup) → ProjectActive
# =================================================================

class ProjectAPIView(APIView):
    """
    GET  /api/projects/     — รายการโครงการ (ตาม role)
    POST /api/projects/     — สร้างโครงการ (Officer only)
    """

    def get(self, request):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        if user.role == 'Officer':
            # Officer เห็นทุกโครงการ
            projects = Project.objects.all().order_by('-created_at')
        else:
            # User เห็นเฉพาะโครงการที่ถูกเพิ่มเป็น Participant
            project_ids = ProjectParticipant.objects.filter(
                user=user
            ).values_list('project_id', flat=True)
            projects = Project.objects.filter(
                project_id__in=project_ids
            ).order_by('-created_at')

        data = [{
            'project_id': p.project_id,
            'project_name': p.project_name,
            'total_budget': str(p.total_budget),
            'reserved_budget': str(p.reserved_budget),
            'remaining_budget': str(p.remaining_budget),
            'status': p.status,
            'start_date': str(p.start_date) if p.start_date else None,
            'end_date': str(p.end_date) if p.end_date else None,
            'created_at': p.created_at.isoformat(),
        } for p in projects]

        return Response(data)

    def post(self, request):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        data = request.data
        project = Project.objects.create(
            created_by=user,
            project_name=data.get('project_name', ''),
            total_budget=Decimal(str(data.get('total_budget', 0))),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            status='Draft',
        )

        return Response({
            'message': 'สร้างโครงการสำเร็จ',
            'project_id': project.project_id,
        }, status=201)


class ProjectDetailAPIView(APIView):
    """
    GET    /api/projects/<id>/  — รายละเอียดโครงการ
    PUT    /api/projects/<id>/  — แก้ไขโครงการ (Officer)
    DELETE /api/projects/<id>/  — ลบโครงการ (Officer)
    """

    def get(self, request, project_id):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'ไม่พบโครงการ'}, status=404)

        # Check access: Officer เห็นทุกโครงการ, User ต้องเป็น Participant
        if user.role != 'Officer':
            if not ProjectParticipant.objects.filter(
                project=project, user=user
            ).exists():
                return Response({'error': 'ไม่มีสิทธิ์เข้าถึงโครงการนี้'}, status=403)

        participants = ProjectParticipant.objects.filter(
            project=project
        ).select_related('user')

        return Response({
            'project_id': project.project_id,
            'project_name': project.project_name,
            'total_budget': str(project.total_budget),
            'reserved_budget': str(project.reserved_budget),
            'remaining_budget': str(project.remaining_budget),
            'status': project.status,
            'start_date': str(project.start_date) if project.start_date else None,
            'end_date': str(project.end_date) if project.end_date else None,
            'created_at': project.created_at.isoformat(),
            'participants': [{
                'user_id': pp.user.user_id,
                'email': pp.user.email,
                'full_name': pp.user.full_name,
                'role_in_project': pp.role_in_project,
            } for pp in participants],
        })

    def put(self, request, project_id):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'ไม่พบโครงการ'}, status=404)

        data = request.data
        if 'project_name' in data:
            project.project_name = data['project_name']
        if 'total_budget' in data:
            project.total_budget = Decimal(str(data['total_budget']))
        if 'start_date' in data:
            project.start_date = data['start_date']
        if 'end_date' in data:
            project.end_date = data['end_date']

        project.save()
        return Response({'message': 'แก้ไขโครงการสำเร็จ'})

    def delete(self, request, project_id):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'ไม่พบโครงการ'}, status=404)

        if project.status != 'Draft':
            return Response({'error': 'ลบได้เฉพาะโครงการที่ยังเป็น Draft'}, status=400)

        project.delete()
        return Response({'message': 'ลบโครงการสำเร็จ'})


class ProjectStartAPIView(APIView):
    """
    POST /api/projects/<id>/start/
    Activity: กดเริ่มกระบวนการสั่งซื้อ (Start PRJ)
    UI State: S2 → ProjectActive
    """

    def post(self, request, project_id):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'ไม่พบโครงการ'}, status=404)

        if project.status != 'Draft':
            return Response({'error': 'เริ่มได้เฉพาะโครงการ Draft'}, status=400)

        # ตรวจว่ามี Participant อย่างน้อย 1 คน
        if not ProjectParticipant.objects.filter(project=project).exists():
            return Response(
                {'error': 'กรุณาเพิ่มผู้เข้าร่วมโครงการก่อนเริ่ม'},
                status=400
            )

        project.status = 'Active'
        project.save()

        return Response({'message': 'เริ่มโครงการสำเร็จ — พร้อมสร้างใบสั่งซื้อ'})


# =================================================================
# Participant APIs
# Activity: ระบุผู้เข้าร่วมโครงการ
# UI State: S2 (Participant Setup)
# =================================================================

class ProjectParticipantAPIView(APIView):
    """
    GET  /api/projects/<id>/participants/  — รายชื่อผู้เข้าร่วม
    POST /api/projects/<id>/participants/  — เพิ่มผู้เข้าร่วม (Officer)
    """

    def get(self, request, project_id):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        participants = ProjectParticipant.objects.filter(
            project_id=project_id
        ).select_related('user')

        data = [{
            'user_id': pp.user.user_id,
            'email': pp.user.email,
            'full_name': pp.user.full_name,
            'role_in_project': pp.role_in_project,
        } for pp in participants]

        return Response(data)

    def post(self, request, project_id):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        data = request.data
        email = data.get('email', '')
        role_in_project = data.get('role_in_project', 'Requester')

        # หา User จาก email
        try:
            target_user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': f'ไม่พบผู้ใช้ {email} ในระบบ กรุณาให้ผู้ใช้ login ด้วย Google ก่อน'},
                status=404
            )

        # ตรวจว่าไม่ซ้ำ
        if ProjectParticipant.objects.filter(
            project_id=project_id, user=target_user
        ).exists():
            return Response({'error': 'ผู้ใช้นี้อยู่ในโครงการแล้ว'}, status=400)

        ProjectParticipant.objects.create(
            project_id=project_id,
            user=target_user,
            role_in_project=role_in_project,
        )

        return Response({
            'message': f'เพิ่ม {target_user.full_name} เข้าโครงการสำเร็จ',
        }, status=201)


class ParticipantDeleteAPIView(APIView):
    """DELETE /api/projects/<id>/participants/<user_id>/ — ลบผู้เข้าร่วม"""

    def delete(self, request, project_id, user_id):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            pp = ProjectParticipant.objects.get(
                project_id=project_id, user_id=user_id
            )
        except ProjectParticipant.DoesNotExist:
            return Response({'error': 'ไม่พบผู้เข้าร่วม'}, status=404)

        pp.delete()
        return Response({'message': 'ลบผู้เข้าร่วมสำเร็จ'})


# =================================================================
# Purchase Order APIs
# Activity: สร้างใบสั่งซื้อ → ตรวจสอบ → Check Budget → Reserve
# UI State: S3 (Order Entry) → S4 (Budget Validation) → S5 (Budget Reserved)
# =================================================================

class PurchaseOrderAPIView(APIView):
    """
    GET  /api/orders/?project_id=X  — รายการใบสั่งซื้อ
    POST /api/orders/               — สร้างใบสั่งซื้อ (User)
    """

    def get(self, request):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        project_id = request.query_params.get('project_id')

        if user.role == 'Officer':
            orders = PurchaseOrder.objects.all()
        else:
            # User เห็นเฉพาะ order ของตัวเอง
            orders = PurchaseOrder.objects.filter(requester=user)

        if project_id:
            orders = orders.filter(project_id=project_id)

        orders = orders.select_related('project', 'requester').order_by('-created_at')

        data = [{
            'order_id': o.order_id,
            'order_no': o.order_no,
            'project_name': o.project.project_name,
            'project_id': o.project_id,
            'requester_name': o.requester.full_name,
            'total_amount': str(o.total_amount),
            'status': o.status,
            'created_at': o.created_at.isoformat(),
            'items_count': o.items.count(),
        } for o in orders]

        return Response(data)

    def post(self, request):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        data = request.data
        project_id = data.get('project_id')
        items = data.get('items', [])

        # ตรวจว่า user เป็น Participant ของโครงการ
        if user.role != 'Officer':
            if not ProjectParticipant.objects.filter(
                project_id=project_id, user=user
            ).exists():
                return Response({'error': 'คุณไม่ได้เป็นผู้เข้าร่วมโครงการนี้'}, status=403)

        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'ไม่พบโครงการ'}, status=404)

        if project.status != 'Active':
            return Response({'error': 'โครงการยังไม่เปิดใช้งาน'}, status=400)

        # สร้าง order_no อัตโนมัติ
        count = PurchaseOrder.objects.filter(project=project).count() + 1
        order_no = f"PO-{project.project_id:04d}-{count:04d}"

        order = PurchaseOrder.objects.create(
            project=project,
            requester=user,
            order_no=order_no,
            reason=data.get('reason', ''),
            status='Draft',
        )

        # สร้าง items
        total = Decimal('0')
        for item_data in items:
            qty = int(item_data.get('quantity', 1))
            unit_price = Decimal(str(item_data.get('unit_price', 0)))
            item = OrderItem.objects.create(
                order=order,
                material_name=item_data.get('material_name', ''),
                quantity=qty,
                unit=item_data.get('unit', 'ชิ้น'),
                unit_price=unit_price,
            )
            total += item.total_price

        order.total_amount = total
        order.save()

        return Response({
            'message': 'สร้างใบสั่งซื้อสำเร็จ',
            'order_id': order.order_id,
            'order_no': order.order_no,
        }, status=201)


class PurchaseOrderDetailAPIView(APIView):
    """
    GET /api/orders/<id>/   — รายละเอียดใบสั่งซื้อ + items
    PUT /api/orders/<id>/   — แก้ไขใบสั่งซื้อ (Draft only)
    """

    def get(self, request, order_id):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        try:
            order = PurchaseOrder.objects.select_related(
                'project', 'requester', 'approver'
            ).get(order_id=order_id)
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        items = OrderItem.objects.filter(order=order)
        partial_receives = PartialReceive.objects.filter(order=order)

        return Response({
            'order_id': order.order_id,
            'order_no': order.order_no,
            'project_id': order.project_id,
            'project_name': order.project.project_name,
            'requester': {
                'user_id': order.requester.user_id,
                'full_name': order.requester.full_name,
                'email': order.requester.email,
            },
            'approver': {
                'user_id': order.approver.user_id,
                'full_name': order.approver.full_name,
            } if order.approver else None,
            'total_amount': str(order.total_amount),
            'reason': order.reason,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'items': [{
                'item_id': i.item_id,
                'material_name': i.material_name,
                'quantity': i.quantity,
                'unit': i.unit,
                'unit_price': str(i.unit_price),
                'total_price': str(i.total_price),
            } for i in items],
            'partial_receives': [{
                'receive_id': pr.receive_id,
                'receipt_no': pr.receipt_no,
                'received_date': pr.received_date.isoformat(),
                'status': pr.status,
            } for pr in partial_receives],
        })

    def put(self, request, order_id):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        try:
            order = PurchaseOrder.objects.get(order_id=order_id)
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        if order.status not in ['Draft', 'Rejected']:
            return Response({'error': 'แก้ไขได้เฉพาะ Draft หรือถูกปฏิเสธ'}, status=400)

        data = request.data

        if 'reason' in data:
            order.reason = data['reason']

        # อัปเดต items ถ้ามี
        if 'items' in data:
            order.items.all().delete()
            total = Decimal('0')
            for item_data in data['items']:
                qty = int(item_data.get('quantity', 1))
                unit_price = Decimal(str(item_data.get('unit_price', 0)))
                item = OrderItem.objects.create(
                    order=order,
                    material_name=item_data.get('material_name', ''),
                    quantity=qty,
                    unit=item_data.get('unit', 'ชิ้น'),
                    unit_price=unit_price,
                )
                total += item.total_price
            order.total_amount = total

        order.save()
        return Response({'message': 'แก้ไขใบสั่งซื้อสำเร็จ'})


class OrderSubmitAPIView(APIView):
    """
    POST /api/orders/<id>/submit/
    Activity: ตรวจสอบวงเงินคงเหลือ → กันวงเงิน
    UI State: S3 → S4 (Budget Validation) → S5 (Budget Reserved)
    """

    def post(self, request, order_id):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        try:
            order = PurchaseOrder.objects.select_related('project').get(
                order_id=order_id
            )
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        if order.status not in ['Draft', 'Rejected']:
            return Response({'error': 'ส่งได้เฉพาะ Draft หรือถูกปฏิเสธ'}, status=400)

        project = order.project

        # S4: ตรวจสอบวงเงินคงเหลือ (Check Budget)
        if order.total_amount > project.remaining_budget:
            return Response({
                'error': 'งบประมาณไม่เพียงพอ',
                'required': str(order.total_amount),
                'remaining': str(project.remaining_budget),
            }, status=400)

        # กันวงเงิน (Reserve Budget)
        project.reserved_budget += order.total_amount
        project.save()  # triggers auto-calculate remaining_budget

        # อัปเดตสถานะ
        order.status = 'Reserved'
        order.save()

        return Response({
            'message': 'กันวงเงินสำเร็จ',
            'reserved_amount': str(order.total_amount),
            'remaining_budget': str(project.remaining_budget),
        })


# =================================================================
# Export & Approval APIs
# Activity: Export .xlsx → ระบุกรรมการ → หัวหน้าพิจารณา (Offline)
# UI State: S5 (Budget Reserved) → S6 (Approval Pending) → Approved
# =================================================================

class OrderExportAPIView(APIView):
    """
    POST /api/orders/<id>/export/
    Activity: Export file .xlsx + ระบุกรรมการตรวจรับ → ส่งรออนุมัติ
    UI State: S5 → S6
    """

    def post(self, request, order_id):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            order = PurchaseOrder.objects.get(order_id=order_id)
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        if order.status != 'Reserved':
            return Response({'error': 'Export ได้เฉพาะใบสั่งซื้อที่กันวงเงินแล้ว'}, status=400)

        # อัปเดตสถานะเป็น Pending_Approval
        order.status = 'Pending_Approval'
        order.save()

        return Response({
            'message': 'ส่งรออนุมัติสำเร็จ — นำเอกสารไปให้หัวหน้าภาคเซ็นอนุมัติ',
            'order_no': order.order_no,
        })


class OrderApprovalRecordAPIView(APIView):
    """
    POST /api/orders/<id>/approve/
    Activity: บันทึกผลอนุมัติจากหัวหน้าภาค (Offline process)
    UI State: S6 → Approved หรือ S6 → S3 (Request Modification)
    """

    def post(self, request, order_id):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            order = PurchaseOrder.objects.select_related('project').get(
                order_id=order_id
            )
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        if order.status != 'Pending_Approval':
            return Response({'error': 'ใบสั่งซื้อไม่ได้อยู่ในสถานะรออนุมัติ'}, status=400)

        action = request.data.get('action')  # 'approve' or 'reject'

        if action == 'approve':
            order.status = 'Approved'
            order.save()
            return Response({
                'message': 'อนุมัติสำเร็จ — พร้อมดำเนินการจัดซื้อ',
            })

        elif action == 'reject':
            # คืนวงเงินที่กัน
            project = order.project
            project.reserved_budget -= order.total_amount
            project.save()

            order.status = 'Rejected'
            order.save()

            return Response({
                'message': 'ส่งกลับแก้ไข — คืนวงเงินแล้ว',
                'remaining_budget': str(project.remaining_budget),
            })

        return Response({'error': 'กรุณาระบุ action: approve หรือ reject'}, status=400)


# =================================================================
# Partial Receive APIs
# Activity: สร้างใบสั่งซื้อย่อย พร้อมแนบใบเสร็จ (.pdf/.jpg)
# UI State: S7 (Partial Receive Entry)
# =================================================================

class PartialReceiveAPIView(APIView):
    """
    GET  /api/partial-receives/?order_id=X  — รายการใบรับของ
    POST /api/partial-receives/             — สร้างใบรับของ (Officer)
    """

    def get(self, request):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        order_id = request.query_params.get('order_id')
        receives = PartialReceive.objects.all()

        if order_id:
            receives = receives.filter(order_id=order_id)

        receives = receives.select_related('order', 'recorded_by').order_by('-received_date')

        data = [{
            'receive_id': r.receive_id,
            'order_no': r.order.order_no,
            'order_id': r.order_id,
            'receipt_no': r.receipt_no,
            'receipt_file_path': r.receipt_file_path,
            'recorded_by': r.recorded_by.full_name,
            'received_date': r.received_date.isoformat(),
            'status': r.status,
        } for r in receives]

        return Response(data)

    def post(self, request):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        data = request.data
        order_id = data.get('order_id')

        try:
            order = PurchaseOrder.objects.get(order_id=order_id)
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        if order.status != 'Approved':
            return Response({'error': 'สร้างได้เฉพาะใบสั่งซื้อที่อนุมัติแล้ว'}, status=400)

        receive = PartialReceive.objects.create(
            order=order,
            recorded_by=user,
            receipt_no=data.get('receipt_no', ''),
            receipt_file_path=data.get('receipt_file_path', ''),
            status='Pending_Inspection',
        )

        return Response({
            'message': 'สร้างใบรับของสำเร็จ — รอกรรมการตรวจรับ',
            'receive_id': receive.receive_id,
        }, status=201)


# =================================================================
# Inspection APIs
# Activity: กก.ตรวจรับ: ตรวจนับจำนวน/คุณภาพ → ยืนยัน/ปฏิเสธ
# UI State: S8 (Inspection Process) → CheckComplete
# =================================================================

class InspectionAPIView(APIView):
    """
    GET  /api/inspections/?order_id=X  — รายการตรวจรับ
    POST /api/inspections/             — บันทึกผลตรวจรับ (Committee)
    """

    def get(self, request):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        order_id = request.query_params.get('order_id')
        inspections = Inspection.objects.all()

        if order_id:
            inspections = inspections.filter(
                partial_receive__order_id=order_id
            )

        inspections = inspections.select_related(
            'partial_receive', 'committee'
        ).order_by('-inspection_date')

        data = [{
            'inspection_id': insp.inspection_id,
            'receive_id': insp.partial_receive.receive_id,
            'receipt_no': insp.partial_receive.receipt_no,
            'committee_name': insp.committee.full_name,
            'inspection_date': insp.inspection_date.isoformat(),
            'result': insp.result,
            'comment': insp.comment,
        } for insp in inspections]

        return Response(data)

    def post(self, request):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        data = request.data
        receive_id = data.get('receive_id')
        result = data.get('result')  # 'Pass' or 'Reject'

        if result not in ['Pass', 'Reject']:
            return Response({'error': 'กรุณาระบุ result: Pass หรือ Reject'}, status=400)

        try:
            receive = PartialReceive.objects.select_related('order').get(
                receive_id=receive_id
            )
        except PartialReceive.DoesNotExist:
            return Response({'error': 'ไม่พบใบรับของ'}, status=404)

        if receive.status != 'Pending_Inspection':
            return Response({'error': 'ใบรับของนี้ถูกตรวจรับแล้ว'}, status=400)

        # สร้างผลตรวจรับ
        inspection = Inspection.objects.create(
            partial_receive=receive,
            committee=user,
            result=result,
            comment=data.get('comment', ''),
        )

        # อัปเดตสถานะ PartialReceive
        receive.status = 'Inspected'
        receive.save()

        if result == 'Reject':
            return Response({
                'message': 'ปฏิเสธรับของ — แจ้งผู้ขายแก้ไข',
                'result': 'Reject',
            })

        # ตรวจว่ารายการสั่งซื้อครบถ้วนหรือไม่
        order = receive.order
        all_receives = PartialReceive.objects.filter(order=order)
        all_inspected = all_receives.filter(status='Inspected').count()
        all_passed = Inspection.objects.filter(
            partial_receive__order=order, result='Pass'
        ).count()

        return Response({
            'message': 'ยืนยันการตรวจรับสำเร็จ',
            'result': 'Pass',
            'total_receives': all_receives.count(),
            'total_passed': all_passed,
        })


# =================================================================
# Payment APIs
# Activity: คำนวณงบประมาณ → ตั้งเบิกจ่ายเงิน
# UI State: S9 (Payment Processing)
# =================================================================

class PaymentAPIView(APIView):
    """
    GET  /api/payments/?project_id=X  — รายการเบิกจ่าย
    POST /api/payments/               — ตั้งเบิกจ่าย (Officer)
    """

    def get(self, request):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        project_id = request.query_params.get('project_id')
        payments = Payment.objects.all()

        if project_id:
            payments = payments.filter(project_id=project_id)

        payments = payments.select_related(
            'project', 'related_order'
        ).order_by('-payment_date')

        data = [{
            'payment_id': p.payment_id,
            'project_name': p.project.project_name,
            'order_no': p.related_order.order_no,
            'amount_paid': str(p.amount_paid),
            'payment_date': p.payment_date.isoformat(),
            'status': p.status,
        } for p in payments]

        return Response(data)

    def post(self, request):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        data = request.data
        order_id = data.get('order_id')

        try:
            order = PurchaseOrder.objects.select_related('project').get(
                order_id=order_id
            )
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        if order.status != 'Approved':
            return Response({'error': 'ตั้งเบิกได้เฉพาะใบสั่งซื้อที่อนุมัติแล้ว'}, status=400)

        # คำนวณยอดจ่ายจริง
        amount = order.total_amount

        payment = Payment.objects.create(
            project=order.project,
            related_order=order,
            amount_paid=amount,
            status='Processing',
        )

        # อัปเดตสถานะ order เป็น Completed
        order.status = 'Completed'
        order.save()

        return Response({
            'message': 'ตั้งเบิกจ่ายสำเร็จ',
            'payment_id': payment.payment_id,
            'amount_paid': str(amount),
        }, status=201)


# =================================================================
# Project Closure API
# Activity: สรุปโครงการและปิดโครงการ
# UI State: S10 (Project Closure)
# =================================================================

class ProjectCloseAPIView(APIView):
    """
    POST /api/projects/<id>/close/
    Activity: สรุปโครงการและปิดโครงการ
    """

    def post(self, request, project_id):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'ไม่พบโครงการ'}, status=404)

        if project.status != 'Active':
            return Response({'error': 'ปิดได้เฉพาะโครงการ Active'}, status=400)

        # สรุปข้อมูล
        total_orders = PurchaseOrder.objects.filter(project=project).count()
        completed_orders = PurchaseOrder.objects.filter(
            project=project, status='Completed'
        ).count()
        total_payments = Payment.objects.filter(
            project=project
        ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')

        project.status = 'Closed'
        project.save()

        return Response({
            'message': 'ปิดโครงการสำเร็จ',
            'summary': {
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'total_payments': str(total_payments),
                'total_budget': str(project.total_budget),
                'reserved_budget': str(project.reserved_budget),
                'remaining_budget': str(project.remaining_budget),
            }
        })


# =================================================================
# User Management APIs (Officer only)
# =================================================================

class UserListAPIView(APIView):
    """GET /api/users/ — รายชื่อ User ทั้งหมด (Officer only)"""

    def get(self, request):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        users = User.objects.all().order_by('full_name')
        data = [{
            'user_id': u.user_id,
            'email': u.email,
            'full_name': u.full_name,
            'role': u.role,
            'department': u.department,
        } for u in users]

        return Response(data)


class UserDetailAPIView(APIView):
    """
    PUT /api/users/<id>/ — แก้ไข role/department ของ User (Officer only)
    """

    def put(self, request, user_id):
        user = get_current_user(request)
        if not user or user.role != 'Officer':
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            target_user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'ไม่พบผู้ใช้'}, status=404)

        data = request.data
        if 'role' in data:
            target_user.role = data['role']
        if 'department' in data:
            target_user.department = data['department']
        if 'full_name' in data:
            target_user.full_name = data['full_name']

        target_user.save()
        return Response({'message': 'แก้ไขข้อมูลผู้ใช้สำเร็จ'})


# =================================================================
# Dashboard Stats API
# =================================================================

class StatsAPIView(APIView):
    """GET /api/stats/ — สถิติสำหรับ Dashboard"""

    def get(self, request):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        if user.role == 'Officer':
            data = {
                'total_projects': Project.objects.count(),
                'active_projects': Project.objects.filter(status='Active').count(),
                'total_orders': PurchaseOrder.objects.count(),
                'pending_orders': PurchaseOrder.objects.filter(
                    status='Pending_Approval'
                ).count(),
                'total_users': User.objects.count(),
            }
        else:
            # User stats — เฉพาะโครงการที่เป็น Participant
            my_project_ids = ProjectParticipant.objects.filter(
                user=user
            ).values_list('project_id', flat=True)

            data = {
                'my_projects': len(my_project_ids),
                'my_orders': PurchaseOrder.objects.filter(requester=user).count(),
                'pending_inspection': PartialReceive.objects.filter(
                    order__project_id__in=my_project_ids,
                    status='Pending_Inspection'
                ).count(),
            }

        return Response(data)
