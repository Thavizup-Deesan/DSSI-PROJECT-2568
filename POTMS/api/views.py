import json
from decimal import Decimal
from django.core.files.storage import FileSystemStorage

from django.db import transaction, connection
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    User, Project, ProjectParticipant,
    PurchaseOrder, OrderItem, PartialReceive, PartialReceiveItem,
    Inspection, Payment
)
from .serializers import PurchaseOrderSerializer


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


def require_flags(*flags):
    """Decorator: ตรวจสอบว่า user มี flag ที่กำหนด (is_admin, is_officer, is_committee)"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user = get_current_user(request)
            if not user:
                return JsonResponse({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)
            if not any(getattr(user, f, False) for f in flags):
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
    """หน้า Login ด้วย Google OAuth 2.0 (allauth)"""
    if request.user.is_authenticated:
        api_user = get_current_user(request)
        if api_user:
            if api_user.is_officer:
                return redirect('officer_dashboard')
            elif api_user.role == 'Inspector':
                return redirect('inspection')
            return redirect('user_dashboard')
    return render(request, 'login.html')


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


def inspector_landing_page(request):
    return render(request, 'inspector_landing.html')


# =================================================================
# Auth API — Google OAuth
# Activity: เข้าสู่ระบบด้วย Google
# =================================================================

def allauth_post_login_view(request):
    """
    Bridge view: หลัง allauth login สำเร็จ → sync api.models.User → set session → redirect
    allauth จะ redirect มาที่นี่หลัง Google OAuth เสร็จ (LOGIN_REDIRECT_URL)
    """
    if not request.user.is_authenticated:
        return redirect('login_page')

    django_user = request.user

    # ดึงชื่อจาก social account
    full_name = f"{django_user.first_name} {django_user.last_name}".strip()
    try:
        social_account = django_user.socialaccount_set.filter(provider='google').first()
        if social_account:
            full_name = social_account.extra_data.get('name', full_name)
    except Exception:
        pass

    # Sync ไปยัง api.models.User (ตรวจสอบสิทธิ์การเข้าใช้งาน)
    try:
        api_user = User.objects.get(email__iexact=django_user.email)
        created = False
    except User.DoesNotExist:
        # ไม่อนุญาตให้ล็อกอินถ้ายังไม่ได้ถูกเพิ่มในระบบ (Whitelist only)
        from django.contrib.auth import logout as auth_logout
        auth_logout(request)
        return render(request, 'login.html', {
            'error': 'คุณไม่มีสิทธิ์เข้าใช้งานระบบ (กรุณาติดต่อเจ้าหน้าที่พัสดุหรือผู้ดูแลระบบ)'
        })

    if not created and api_user.full_name != full_name and full_name:
        api_user.full_name = full_name
        api_user.save(update_fields=['full_name'])

    # Set session variables
    request.session['user_id'] = api_user.user_id
    request.session['user_email'] = api_user.email
    request.session['user_full_name'] = api_user.full_name

    # Redirect ตาม flags
    if api_user.is_admin:
        return redirect('admin_management')
    elif api_user.is_officer:
        return redirect('officer_dashboard')
    elif api_user.role == 'Inspector':
        return redirect('inspection')
    else:
        return redirect('user_dashboard')


class LogoutAPIView(APIView):
    """POST /api/auth/logout/ — ออกจากระบบ"""

    def post(self, request):
        from django.contrib.auth import logout as auth_logout
        auth_logout(request)
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
            'is_admin': user.is_admin,
            'is_officer': user.is_officer,
            'is_head': user.is_head,
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

        if user.is_officer:
            # Officer เห็นทุกโครงการ
            projects = Project.objects.all().order_by('-created_at')
        else:
            # User เห็นเฉพาะโครงการที่ถูกเพิ่มเป็น Participant หรือเป็น Committee
            project_ids = set(ProjectParticipant.objects.filter(
                user=user
            ).values_list('project_id', flat=True))

            committee_project_ids = set(PartialReceive.objects.filter(
                committee=user
            ).values_list('order__project_id', flat=True)) | set(PurchaseOrder.objects.filter(
                inspection_committee=user
            ).values_list('project_id', flat=True))
            
            all_project_ids = project_ids | committee_project_ids

            projects = Project.objects.filter(
                project_id__in=all_project_ids
            ).order_by('-created_at')

        data = [{
            'project_id': p.project_id,
            'project_name': p.project_name,
            'ubufmis_code': p.ubufmis_code,
            'project_code': p.project_code,
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
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        data = request.data
        
        project = Project.objects.create(
            created_by=user,
            project_name=data.get('project_name', ''),
            ubufmis_code=data.get('ubufmis_code', ''),
            project_code=data.get('project_code', ''),
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

        # Check access: Officer เห็นทุกโครงการ, User ต้องเป็น Participant หรือ Committee
        if not user.is_officer:
            is_participant = ProjectParticipant.objects.filter(project=project, user=user).exists()
            is_committee = PartialReceive.objects.filter(order__project=project, committee=user).exists()
            
            if not is_participant and not is_committee:
                return Response({'error': 'ไม่มีสิทธิ์เข้าถึงโครงการนี้'}, status=403)

        participants = ProjectParticipant.objects.filter(
            project=project
        ).select_related('user')

        return Response({
            'project_id': project.project_id,
            'project_name': project.project_name,
            'ubufmis_code': project.ubufmis_code,
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
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'ไม่พบโครงการ'}, status=404)

        data = request.data
        if 'project_name' in data:
            project.project_name = data['project_name']
        if 'ubufmis_code' in data:
            project.ubufmis_code = data['ubufmis_code']

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
        if not user or not user.is_officer:
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
        if not user or not user.is_officer:
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
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        data = request.data
        email = data.get('email', '')
        role_in_project = data.get('role_in_project', 'Requester')

        # Restrict 'Inspector' role in Participant Setup
        if role_in_project == 'Inspector':
             return Response({'error': 'บทบาทกรรมการตรวจรับต้องระบุในขั้นตอน Export ใบสั่งซื้อเท่านั้น'}, status=400)

        # หา User จาก email หรือสร้างใหม่ (Placeholder)
        try:
            target_user, created = User.objects.get_or_create(email=email)
            if created:
                target_user.full_name = email.split('@')[0]
                target_user.role = 'Requester'
                target_user.save()
        except Exception as e:
            return Response({'error': f'Invalid Email: {str(e)}'}, status=400)

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
        if not user or not user.is_officer:
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

def update_project_budget(project):
    """
    Recalculate reserved_budget from scratch.
    Reserved = Sum(Orders in Reserved/Pending/Approved/Processing) + Sum(Paid amount for Paid orders)
    """
    total_reserved = Decimal('0')
    
    # 1. Active Orders (excluding Draft, Rejected, Cancelled)
    # Note: Closed/Completed orders eventually become Paid.
    # While 'Completed' (waiting for payment), they count as Order Total.
    # Once 'Paid', they should use actual Payment amount.
    
    orders = PurchaseOrder.objects.filter(
        project=project
    ).exclude(status__in=['Draft', 'Cancelled'])
    
    for order in orders:
        # Check for payments (Authorized/Paid/Processing)
        # Sum all payments related to this order
        payment_sum = Payment.objects.filter(related_order=order).aggregate(
            total=Sum('amount_paid')
        )['total'] or Decimal('0')
        
        # Logic Update:
        # 1. If Completed (Closed job), use actual payment sum (release leftover budget).
        # 2. If Not Completed (Active/Partial), keep full order amount reserved.
        
        if order.status == 'Completed':
             total_reserved += payment_sum
        else:
             # Reserve full amount until the job is done
             total_reserved += order.total_amount
            
    project.reserved_budget = total_reserved
    project.save() # Triggers remaining_budget calculation

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

        if user.is_officer:
            orders = PurchaseOrder.objects.all()
        else:
            # User เห็นเฉพาะ order ของตัวเอง หรือที่เป็น Committee
            orders = PurchaseOrder.objects.filter(
                Q(requester=user) | Q(inspection_committee=user)
            )

        if project_id:
            orders = orders.filter(project_id=project_id)

        orders = orders.select_related('project', 'requester').prefetch_related(
            'items',
            'items__received_records',
            'items__received_records__partial_receive',
            'items__received_records__partial_receive__inspection'
        ).order_by('-created_at')

        data = []
        for o in orders:
            # 1. Calculate Suggested Payment Amount (Passed Inspections - Paid)
            delivered_value = Decimal('0')
            for item in o.items.all():
                passed_qty = item.received_records.filter(
                    partial_receive__inspection__result='Pass'
                ).aggregate(total=Sum('quantity'))['total'] or 0
                delivered_value += (Decimal(passed_qty) * item.unit_price)

            already_paid = Payment.objects.filter(related_order=o).aggregate(
                total=Sum('amount_paid')
            )['total'] or Decimal('0')

            suggested = delivered_value - already_paid
            if suggested < 0: suggested = Decimal('0')

            # Check if order is fully received (all items received >= ordered)
            is_fully_received = True
            if o.items.count() == 0:
                is_fully_received = False # Empty order is not "received"
            
            for item in o.items.all():
                received_qty = 0
                for record in item.received_records.all():
                    # Check if rejected
                    is_rejected = False
                    # Reverse relation one-to-one 'inspection' logic
                    # If inspection exists and result is Reject
                    try:
                        if hasattr(record.partial_receive, 'inspection'):
                            if record.partial_receive.inspection.result == 'Reject':
                                is_rejected = True
                    except:
                        pass
                    
                    if not is_rejected:
                        received_qty += record.quantity
                
                if received_qty < item.quantity:
                    is_fully_received = False
                    break

            data.append({
                'order_id': o.order_id,
                'order_no': o.order_no,
                'project_name': o.project.project_name,
                'project_code': o.project.project_code,   # Added
                'ubufmis_code': o.project.ubufmis_code,   # Added
                'project_id': o.project_id,
                'requester_name': o.requester.full_name,
                'total_amount': str(o.total_amount),
                'suggested_payment_amount': str(suggested),
                'status': o.status,
                'created_at': o.created_at.isoformat(),
                'items_count': o.items.count(),
                'is_fully_received': is_fully_received,
            })

        return Response(data)

    def post(self, request):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        data = request.data
        project_id = data.get('project_id')
        items = data.get('items', [])
        is_submitting = data.get('submit', False)  # New flag

        # ตรวจว่า user เป็น Participant ของโครงการ
        if not user.is_officer:
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

        # รับเลขที่ใบสั่งซื้อ (ถ้ามีกรอกมา)
        order_no = data.get('order_no', '').strip() or None

        # 1. คำนวณยอดรวม (Calculate Total)
        total = Decimal('0')
        order_items = []
        for item_data in items:
            qty = int(item_data.get('quantity', 1))
            unit_price = Decimal(str(item_data.get('unit_price', 0)))
            total_price = qty * unit_price
            total += total_price
            order_items.append({
                'material_name': item_data.get('material_name', ''),
                'quantity': qty,
                'unit': item_data.get('unit', 'ชิ้น'),
                'unit_price': unit_price,
                'total_price': total_price
            })

        # 2. ตรวจสอบวงเงิน (Check Budget) - Only if submitting
        final_status = 'Reserved' if is_submitting else 'Draft'
        if is_submitting and total > project.remaining_budget:
             return Response({
                'error': f'งบประมาณไม่เพียงพอ (ต้องการ {total:,}, คงเหลือ {project.remaining_budget:,})',
            }, status=400)

        try:
            with transaction.atomic():
                # 3. สร้าง Order
                order = PurchaseOrder.objects.create(
                    project=project,
                    requester=user,
                    order_no=order_no,
                    reason=data.get('reason', ''),
                    total_amount=total,
                    status=final_status,
                )

                # 4. สร้าง Items
                for item in order_items:
                    OrderItem.objects.create(
                        order=order,
                        material_name=item['material_name'],
                        quantity=item['quantity'],
                        unit=item['unit'],
                        unit_price=item['unit_price'],
                    )
                
                # 5. Update Budget (Centralized) - Only if status is not Draft
                if final_status != 'Draft':
                    update_project_budget(project)
        except Exception as e:
            return Response({'error': f'เกิดข้อผิดพลาดในการบันทึก: {str(e)}'}, status=500)
            
        return Response({
            'message': 'สร้างใบสั่งซื้อและกันวงเงินเรียบร้อยแล้ว',
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
                'project', 'requester', 'inspection_committee'
            ).prefetch_related(
                'items', 
                'partial_receives__recorded_by',
                'partial_receives__receive_items__order_item'
            ).get(order_id=order_id)
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)
        except Exception as e:
            print(f"DEBUG: Error fetching order: {e}")
            return Response({'error': f'เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}'}, status=500)
        # Permission Check
        if not (user.is_officer or user.is_admin):
            # 1. Is Requester?
            is_requester = (order.requester == user)
            
            # 2. Is Participant in Project?
            is_participant = ProjectParticipant.objects.filter(project=order.project, user=user).exists()
            
            # 3. Is Committee for this Order? (Direct or via PartialReceive)
            is_committee = (order.inspection_committee == user) or PartialReceive.objects.filter(order=order, committee=user).exists()
            
            if not (is_requester or is_participant or is_committee):
                 return Response({'error': 'ไม่มีสิทธิ์เข้าถึงใบสั่งซื้อนี้ (เฉพาะผู้ที่เกี่ยวข้องเท่านั้น)'}, status=403)

        serializer = PurchaseOrderSerializer(order)
        return Response(serializer.data)

    def delete(self, request, order_id):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        try:
            order = PurchaseOrder.objects.get(order_id=order_id)
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        if order.status != 'Draft':
            return Response({'error': 'ลบได้เฉพาะใบสั่งซื้อที่อยู่ในสถานะ Draft เท่านั้น'}, status=400)

        if order.requester != user:
            return Response({'error': 'เฉพาะผู้ขอซื้อที่สร้างใบสั่งซื้อเท่านั้นที่สามารถลบได้'}, status=403)

        project = order.project
        order.delete()
        
        # Recalculate budget (just in case, though Draft shouldn't reserve anything)
        update_project_budget(project)

        return Response({'message': 'ลบใบสั่งซื้อสำเร็จ'}, status=200)

    def put(self, request, order_id):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        try:
            order = PurchaseOrder.objects.get(order_id=order_id)
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        if order.status not in ['Draft', 'Rejected', 'Revising']:
            return Response({'error': 'แก้ไขได้เฉพาะ Draft หรือถูกปฏิเสธ'}, status=400)

        if order.requester != user:
            return Response({'error': 'เฉพาะผู้ขอซื้อเท่านั้นที่สามารถแก้ไขได้'}, status=403)

        data = request.data
        
        try:
            with transaction.atomic():
                if 'reason' in data:
                    order.reason = data['reason']

                # อัปเดต items ถ้ามี
                if 'items' in data:
                    order.items.all().delete()
                    total = Decimal('0')
                    for item_data in data['items']:
                        qty = int(item_data.get('quantity') or 1)
                        unit_price = Decimal(str(item_data.get('unit_price') or 0))
                        item = OrderItem.objects.create(
                            order=order,
                            material_name=item_data.get('material_name', ''),
                            quantity=qty,
                            unit=item_data.get('unit', 'ชิ้น'),
                            unit_price=unit_price,
                        )
                        total += item.total_price

                    order.total_amount = total

                # If it was Rejected, change to Revising (not Draft)
                if order.status == 'Rejected':
                    order.status = 'Revising'

                order.save()
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': 'เกิดข้อผิดพลาดในการบันทึก: ' + str(e)}, status=500)

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

        if order.status not in ['Draft', 'Rejected', 'Revising']:
            return Response({'error': 'ส่งได้เฉพาะ Draft, ส่งกลับแก้ไข, หรือกำลังแก้ไข'}, status=400)

        if order.requester != user:
             return Response({'error': 'เฉพาะผู้ขอซื้อเท่านั้นที่สามารถยืนยันคำสั่งซื้อได้'}, status=403)

        project = order.project

        # S4: ตรวจสอบวงเงินคงเหลือ (Check Budget)
        # S4: ตรวจสอบวงเงินคงเหลือ (Check Budget)
        # ถ้าเป็น Rejected (เคยกันวงเงินแล้ว) ไม่ต้องเช็คเต็มจำนวน เช็คแค่สถานะ
        if order.total_amount > project.remaining_budget:
             return Response({
                'error': 'งบประมาณไม่เพียงพอ',
                'required': str(order.total_amount),
                'remaining': str(project.remaining_budget),
            }, status=400)
             
        # อัปเดตสถานะและกันวงเงิน
        order.status = 'Reserved'
        order.save()
        
        # Recalculate Budget (Handles both Draft->Reserved and Rejected->Reserved)
        update_project_budget(project)

        # ถ้าเป็น Rejected งบถูกกันไว้แล้ว (และปรับปรุงตอน Edit แล้ว)
        # ไม่ต้องทำอะไรกับ project.reserved_budget

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
        from api.utils.export_helper import generate_po_excel
        from django.http import HttpResponse

        user = get_current_user(request)
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            order = PurchaseOrder.objects.get(order_id=order_id)
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        if order.status != 'Reserved':
             # Allow re-export if already pending? Maybe not.
             if order.status != 'Pending_Approval':
                return Response({'error': 'Export ได้เฉพาะใบสั่งซื้อที่กันวงเงินแล้ว'}, status=400)

        # 1. Update Committee (Email + Name -> User)
        committee_email = request.data.get('committee_email', '').strip()
        committee_name = request.data.get('committee_name', '').strip()
        
        if not committee_email:
             return Response({'error': 'กรุณาระบุอีเมลกรรมการตรวจรับ'}, status=400)
        
        try:
            # Create or Get User
            committee_user, created = User.objects.get_or_create(email=committee_email)
            if created or not committee_user.full_name:
                committee_user.full_name = committee_name if committee_name else committee_email.split('@')[0]
            elif committee_name:
                committee_user.full_name = committee_name
            
            # Always ensure Inspector role (แม้ user มีอยู่แล้ว ต้องได้ role Inspector)
            if committee_user.role not in ['Admin', 'Officer']:
                committee_user.role = 'Inspector'
            committee_user.save()
            
            # Assign to Order
            order.inspection_committee = committee_user
            order.inspection_committee_name = committee_user.full_name
            
        except Exception as e:
            return Response({'error': f'เกิดข้อผิดพลาดในการเพิ่มกรรมการ: {str(e)}'}, status=400)

        # 2. Update Status
        if order.status == 'Reserved':
            order.status = 'Pending_Approval'
        
        order.save()

        # 3. Generate Excel
        excel_file = generate_po_excel(order)
        
        # 4. Return File
        response = HttpResponse(
            excel_file.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="PO-{order.order_no}.xlsx"'
        return response


class OrderApprovalRecordAPIView(APIView):
    """
    POST /api/orders/<id>/approve/
    Activity: บันทึกผลอนุมัติจากหัวหน้าภาค (Offline process)
    UI State: S6 → Approved หรือ S6 → S3 (Request Modification)
    """

    def post(self, request, order_id):
        user = get_current_user(request)
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            order = PurchaseOrder.objects.select_related('project').get(
                order_id=order_id
            )
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        action = request.data.get('action')  # 'approve' or 'reject'

        if order.status != 'Pending_Approval':
            # Allow re-rejecting (updating note) if already rejected
            if not (order.status == 'Rejected' and action == 'reject'):
                return Response({'error': 'ใบสั่งซื้อไม่ได้อยู่ในสถานะรออนุมัติ'}, status=400)

        if action == 'approve':
            order.status = 'Approved'
            order.save()
            return Response({
                'message': 'อนุมัติสำเร็จ — พร้อมดำเนินการจัดซื้อ',
            })

        elif action == 'reject':
            note = request.data.get('note', '').strip()
            if not note:
                return Response({'error': 'กรุณาระบุเหตุผลที่ปฏิเสธ/แก้ไข'}, status=400)

            # Reject: คืนวงเงินเพื่อให้ User แก้ไข (If needed)
            # ในระบบนี้ Rejected หมายถึงต้องส่งกลับไปแก้ -> คืนงบชั่วคราวเพื่อให้งบแสดงผลถูกต้อง
            # หรือถ้าไม่คืน ต้องระวังเรื่องงบซ้อนตอน User แก้ไขแล้วส่งใหม่
            
            project = order.project
            with transaction.atomic():
                if order.status != 'Rejected': 
                     # Only update status, budget helper handles calculation
                     pass

                order.status = 'Rejected'
                order.rejection_reason = note
                order.save()
                
                # Update Budget (Release funds)
                update_project_budget(project)

            return Response({
                'message': 'ส่งกลับแก้ไข — วงเงินยังถูกจองไว้รอแก้ไขและส่งใหม่',
                'remaining_budget': str(project.remaining_budget),
            })

        elif action == 'cancel':
            note = request.data.get('note', '').strip()
            if not note:
                return Response({'error': 'กรุณาระบุเหตุผลที่ไม่อนุมัติ'}, status=400)

            project = order.project
            with transaction.atomic():
                order.status = 'Cancelled'
                order.rejection_reason = note
                order.save()

                # คืนวงเงินให้โครงการ (Cancelled ถูก exclude จาก budget calculation)
                update_project_budget(project)

            return Response({
                'message': 'ไม่อนุมัติ — ยกเลิกใบสั่งซื้อและคืนวงเงินให้โครงการแล้ว',
                'remaining_budget': str(project.remaining_budget),
            })

        return Response({'error': 'กรุณาระบุ action: approve, reject หรือ cancel'}, status=400)

class OrderProcessAPIView(APIView):
    """
    POST /api/orders/<id>/process/
    Activity: ส่งใบสั่งซื้อให้งานพัสดุ (Officer)
    UI State: Approved -> Processing
    """

    def post(self, request, order_id):
        user = get_current_user(request)
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            order = PurchaseOrder.objects.get(order_id=order_id)
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        if order.status != 'Approved':
            return Response({'error': 'ใบสั่งซื้อไม่ได้อยู่ในสถานะอนุมัติ'}, status=400)

        order.status = 'Processing'
        order.save()

        return Response({'message': 'ส่งใบสั่งซื้อให้งานพัสดุแล้ว — สถานะ Processing'})

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
        receive_id = request.query_params.get('receive_id')

        receives = PartialReceive.objects.all()

        if order_id:
            receives = receives.filter(order_id=order_id)
        if receive_id:
            receives = receives.filter(receive_id=receive_id)
        
        # Filter visibility for Committee (Non-Officer/Admin)
        if not user.is_officer and not user.is_admin:
             # Show only if assigned as committee
             receives = receives.filter(committee=user)

        receives = receives.select_related('order', 'recorded_by', 'committee').prefetch_related('receive_items__order_item').order_by('-received_date')

        data = [{
            'receive_id': r.receive_id,
            'order_id': r.order_id,
            'order_no': r.order.order_no,
            'project_name': r.order.project.project_name,
            'project_code': r.order.project.project_code,
            'ubufmis_code': r.order.project.ubufmis_code,
            'project_id': r.order.project_id,
            'requester': r.order.requester.user_id,
            'requester_name': r.order.requester.full_name,
            'receipt_no': r.receipt_no,
            'receipt_file_path': r.receipt_file_path,
            'recorded_by': r.recorded_by.full_name,
            'committee_email': r.committee.email if r.committee else '-',
            'received_date': r.received_date.isoformat(),
            'status': r.status,
            'items': [{
                'material_name': i.order_item.material_name,
                'quantity': i.quantity,
                'unit': i.order_item.unit,
            } for i in r.receive_items.all()]
        } for r in receives]

        return Response(data)

    def post(self, request):
        user = get_current_user(request)
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        data = request.POST # FormData
        order_id = data.get('order_id')

        try:
            order = PurchaseOrder.objects.get(order_id=order_id)
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'ไม่พบใบสั่งซื้อ'}, status=404)

        if order.status not in ['Approved', 'Processing', 'Partially_Paid']:
            return Response({'error': 'สร้างได้เฉพาะใบสั่งซื้อที่อนุมัติแล้ว หรือกำลังดำเนินการ (Processing)'}, status=400)

        # 1. Use Committee from Order (Inherited from PO Export assignment)
        committee_user = order.inspection_committee
        
        if not committee_user:
             return Response({'error': 'กรุณาระบุกรรมการตรวจรับที่ขั้นตอน Export ใบสั่งซื้อก่อน'}, status=400)
        
        # Handle Receipt File
        receipt_file = request.FILES.get('receipt_file')
        file_path = ''
        if receipt_file:
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            file_name = f"receipts/{order.order_no}_{receipt_file.name}"
            file_path = default_storage.save(file_name, ContentFile(receipt_file.read()))
            file_path = f"/media/{file_path}" # Assuming media url setup
        
        # Receive creation moved to atomic block below

        # Validate Items & Quantities
        import json
        from django.db import transaction
        from .models import OrderItem, PartialReceiveItem

        try:
            items_json = data.get('items', '[]')
            items_data = json.loads(items_json)
            
            validated_items = []
            
            for item in items_data:
                item_id = item.get('item_id')
                quantity = int(item.get('quantity', 0))
                
                if quantity > 0:
                    try:
                         order_item = OrderItem.objects.get(item_id=item_id, order=order)
                    except OrderItem.DoesNotExist:
                         return Response({'error': f'Item ID {item_id} ไม่พบในใบสั่งซื้อนี้'}, status=400)

                    # Calculate Remaining (Excluding Rejected)
                    received_so_far = sum(
                        r.quantity for r in order_item.received_records.exclude(
                            partial_receive__inspection__result='Reject'
                        )
                    )
                    remaining = order_item.quantity - received_so_far
                    
                    if quantity > remaining:
                        return Response({
                            'error': f'รายการ {order_item.material_name} ระบุจำนวนเกิน (เหลือ {remaining}, ระบุ {quantity})'
                        }, status=400)
                    
                    validated_items.append({
                        'order_item': order_item,
                        'quantity': quantity
                    })

            if not validated_items:
                 return Response({'error': 'กรุณาระบุจำนวนสินค้าที่รับอย่างน้อย 1 รายการ'}, status=400)

            # Atomic Creation
            with transaction.atomic():
                receive = PartialReceive.objects.create(
                    order=order,
                    recorded_by=user,
                    committee=committee_user,
                    receipt_no=data.get('receipt_no', ''),
                    receipt_file_path=file_path,
                    status='Pending_Inspection',
                )
                
                for v_item in validated_items:
                    PartialReceiveItem.objects.create(
                        partial_receive=receive,
                        order_item=v_item['order_item'],
                        quantity=v_item['quantity']
                    )

        except json.JSONDecodeError:
            return Response({'error': 'Invalid items JSON'}, status=400)
        except Exception as e:
            return Response({'error': f'Failed to process receive: {str(e)}'}, status=400)

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
            return Response({'error': 'ใบรับของนี้ถูกตรวจรับแล้วหรือยังไม่พร้อมตรวจ'}, status=400)

        # Permission Check: Officer or Admin only (Committee can only view)
        if not (user.is_officer or user.is_admin):
             return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้นที่สามารถยืนยันผลตรวจรับได้'}, status=403)

        # สร้างผลตรวจรับ
        inspection = Inspection.objects.create(
            partial_receive=receive,
            committee=user,
            result=result,
            comment=data.get('comment', ''),
        )

        # อัปเดตสถานะ PartialReceive (Force Update)
        PartialReceive.objects.filter(pk=receive.receive_id).update(status='Inspected')
        # receive.save() # Bypass save() to ensure DB update

        if result == 'Reject':
            return Response({
                'message': 'ปฏิเสธรับของ — แจ้งผู้ขายแก้ไข',
                'result': 'Reject',
            })

        # ตรวจว่ารายการสั่งซื้อครบถ้วนหรือไม่ (Quantity Check)
        order = receive.order
        all_items = order.items.all()
        
        # ค้นหาจำนวนที่ผ่านการตรวจรับทั้งหมด (Pass เท่านั้น)
        is_order_complete = True
        progress_data = []

        for item in all_items:
            # Sum quantity from PartialReceiveItem where Inspection Result is 'Pass'
            passed_qty = PartialReceiveItem.objects.filter(
                order_item=item,
                partial_receive__inspection__result='Pass'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            progress_data.append({
                'material_name': item.material_name,
                'ordered': item.quantity,
                'passed': passed_qty
            })

            if passed_qty < item.quantity:
                is_order_complete = False

        if is_order_complete:
            order.status = 'Completed'
            order.save()

        return Response({
            'message': 'ยืนยันการตรวจรับสำเร็จ' + (' (รายการสั่งซื้อครบถ้วน)' if is_order_complete else ''),
            'result': 'Pass',
            'is_complete': is_order_complete,
            'progress': progress_data
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
            'project', 'related_order', 'related_receive'
        ).order_by('-payment_date')

        payment_data = [{
            'payment_id': p.payment_id,
            'project_name': p.project.project_name,
            'order_id': p.related_order.order_id,
            'order_no': p.related_order.order_no,
            'receive_id': p.related_receive_id,
            'receive_no': p.related_receive.receipt_no if p.related_receive else '',
            'amount_paid': str(p.amount_paid),
            'payment_date': p.payment_date.isoformat(),
            'status': p.status,
        } for p in payments]

        # Also return list of payable receives (inspected Pass, not yet paid)
        # Filter out None to avoid SQL NOT IN (NULL) bug which excludes everything
        paid_receive_ids = list(
            Payment.objects.exclude(related_receive__isnull=True)
            .values_list('related_receive_id', flat=True)
        )
        payable_receives = PartialReceive.objects.filter(
            inspection__result='Pass',
        ).exclude(
            receive_id__in=paid_receive_ids
        ).select_related('order', 'order__project').order_by('-received_date')

        receives_data = []
        for r in payable_receives:
            # Calculate value of this receipt
            receive_value = Decimal('0')
            for ri in r.receive_items.select_related('order_item'):
                receive_value += Decimal(ri.quantity) * ri.order_item.unit_price
            
            receives_data.append({
                'receive_id': r.receive_id,
                'receipt_no': r.receipt_no or f'PR-{r.receive_id}',
                'order_id': r.order.order_id,
                'order_no': r.order.order_no,
                'project_name': r.order.project.project_name,
                'received_date': r.received_date.isoformat(),
                'value': str(receive_value),
            })

        return Response({
            'payments': payment_data,
            'payable_receives': receives_data,
        })

    def post(self, request):
        user = get_current_user(request)
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        data = request.data
        receive_id = data.get('receive_id')

        if not receive_id:
            return Response({'error': 'กรุณาเลือกใบรับของ'}, status=400)

        try:
            receive = PartialReceive.objects.select_related(
                'order', 'order__project', 'inspection'
            ).get(receive_id=receive_id)
        except PartialReceive.DoesNotExist:
            return Response({'error': 'ไม่พบใบรับของ'}, status=404)

        # Check inspection passed
        if not hasattr(receive, 'inspection') or receive.inspection.result != 'Pass':
            return Response({'error': 'ใบรับของนี้ยังไม่ผ่านการตรวจรับ'}, status=400)

        # Check not already paid
        if Payment.objects.filter(related_receive=receive).exists():
            return Response({'error': 'ใบรับของนี้ถูกตั้งเบิกจ่ายแล้ว'}, status=400)

        # Calculate value of this receipt
        receive_value = Decimal('0')
        for ri in receive.receive_items.select_related('order_item'):
            receive_value += Decimal(ri.quantity) * ri.order_item.unit_price

        if receive_value <= 0:
            return Response({'error': 'ใบรับของนี้ไม่มีมูลค่า'}, status=400)

        # Determine amount (use receipt value as default, allow override)
        try:
            amount = Decimal(str(data.get('amount_paid', receive_value)))
        except:
            amount = receive_value

        if amount > receive_value:
            return Response({
                'error': f'จำนวนเงินที่เบิก ({amount:,.2f}) เกินกว่ามูลค่าใบรับของ ({receive_value:,.2f} บาท)'
            }, status=400)

        if amount <= 0:
            return Response({'error': 'จำนวนเงินต้องมากกว่า 0'}, status=400)

        order = receive.order
        project = order.project

        payment = Payment.objects.create(
            project=project,
            related_order=order,
            related_receive=receive,
            amount_paid=amount,
            status='Processing',
        )

        # Update Budget
        update_project_budget(project)

        # Update Order Status
        total_delivered = Decimal('0')
        for item in order.items.all():
            passed_qty = PartialReceiveItem.objects.filter(
                order_item=item,
                partial_receive__inspection__result='Pass'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            total_delivered += Decimal(passed_qty) * item.unit_price

        total_paid = Payment.objects.filter(related_order=order).aggregate(
            total=Sum('amount_paid')
        )['total'] or Decimal('0')

        if total_paid >= total_delivered and total_delivered >= order.total_amount:
            order.status = 'Completed'
        elif total_paid > 0:
            order.status = 'Partially_Paid'
        order.save()

        return Response({
            'message': f'ตั้งเบิกจ่ายสำเร็จ — ใบรับของ {receive.receipt_no or "PR-" + str(receive.receive_id)} ({amount:,.2f} บาท)',
            'payment_id': payment.payment_id,
            'amount_paid': str(amount),
        }, status=201)


class PaymentConfirmAPIView(APIView):
    """
    POST /api/payments/<id>/confirm/
    Activity: ยืนยันการเบิกจ่าย (Processing -> Paid)
    """
    def post(self, request, payment_id):
        user = get_current_user(request)
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            payment = Payment.objects.get(payment_id=payment_id)
        except Payment.DoesNotExist:
            return Response({'error': 'ไม่พบรายการเบิกจ่าย'}, status=404)

        if payment.status == 'Paid':
             return Response({'message': 'รายการนี้เบิกจ่ายเสร็จสิ้นแล้ว'})

        payment.status = 'Paid'
        # payment.payment_date = timezone.now() # Optional: update date to confirm date?
        payment.save()
        
        # Update Budget (Confirm Paid amount)
        update_project_budget(payment.project)

        return Response({'message': 'ยืนยันการเบิกจ่ายเสร็จสิ้น (Paid)'})

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

    def get(self, request, project_id):
        user = get_current_user(request)
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'ไม่พบโครงการ'}, status=404)

        # สรุปข้อมูล
        total_orders = PurchaseOrder.objects.filter(project=project).count()
        completed_orders = PurchaseOrder.objects.filter(
            project=project, status='Completed'
        ).count()
        total_payments = Payment.objects.filter(
            project=project
        ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')

        return Response({
            'project_id': project.project_id,
            'project_name': project.project_name,
            'summary': {
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'total_payments': str(total_payments),
                'total_budget': str(project.total_budget),
                'reserved_budget': str(project.reserved_budget),
                'remaining_budget': str(project.remaining_budget),
            }
        })

    def post(self, request, project_id):
        user = get_current_user(request)
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'ไม่พบโครงการ'}, status=404)

        if project.status != 'Active':
            return Response({'error': 'ปิดได้เฉพาะโครงการ Active'}, status=400)

        # สรุปข้อมูล (re-calculate for confirmation/logging if needed, or just close)
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
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        users = User.objects.all().order_by('full_name')
        data = [{
            'user_id': u.user_id,
            'email': u.email,
            'full_name': u.full_name,
            'is_admin': u.is_admin,
            'is_officer': u.is_officer,
            'is_head': u.is_head,
            'department': u.department,
            'role': 'Admin' if u.is_admin else ('Head' if u.is_head else ('Officer' if u.is_officer else 'User')),
        } for u in users]

        return Response(data)


class UserDetailAPIView(APIView):
    """
    PUT /api/users/<id>/ — แก้ไข role/department ของ User (Officer only)
    """

    def put(self, request, user_id):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'Unauthorized'}, status=401)

        try:
            # Ensure user_id is integer from URL
            target_user = User.objects.get(user_id=int(user_id))
        except (User.DoesNotExist, ValueError):
            return Response({'error': 'ไม่พบผู้ใช้'}, status=404)

        is_admin = user.is_admin
        is_self = str(user.user_id) == str(target_user.user_id)
        
        # Permission Check
        if not is_admin:
            if not (user.is_officer and is_self):
                return Response({'error': 'คุณไม่มีสิทธิ์แก้ไขข้อมูลผู้ใช้นี้'}, status=403)

        data = request.data
        
        # Admin can edit everything
        if is_admin:
            if 'full_name' in data: target_user.full_name = data['full_name']
            if 'department' in data: target_user.department = data['department']
            
            # Update role flags AND the role field itself to stay in sync
            if 'is_officer' in data: target_user.is_officer = data['is_officer']
            if 'is_head' in data: target_user.is_head = data['is_head']
            if 'is_admin' in data: target_user.is_admin = data['is_admin']
            
            # Sync role string from flags so model.save() doesn't overwrite them
            if target_user.is_admin: target_user.role = 'Admin'
            elif target_user.is_head: target_user.role = 'Head'
            elif target_user.is_officer: target_user.role = 'Officer'
            else: target_user.role = 'Requester'

        # Officer can only edit their own name and department
        elif user.is_officer and is_self:
            # Check if attempting to change forbidden role fields
            role_flags = ['is_officer', 'is_head', 'is_admin']
            for flag in role_flags:
                if flag in data and data[flag] != getattr(target_user, flag):
                    return Response({'error': 'เจ้าหน้าที่สามารถแก้ไขได้เฉพาะชื่อและภาควิชาของตนเองเท่านั้น'}, status=403)
            
            if 'full_name' in data:
                target_user.full_name = data['full_name']
            if 'department' in data:
                target_user.department = data['department']

        target_user.save()
        return Response({'message': 'แก้ไขข้อมูลสำเร็จ'})


# =================================================================
# Admin Management APIs (Officer only)
# =================================================================

class AdminListAPIView(APIView):
    """
    GET  /api/admins/  — รายชื่อ admin (Officer) ทั้งหมด
    POST /api/admins/  — เพิ่ม admin ใหม่ด้วย email @ubu.ac.th
    """

    def get(self, request):
        user = get_current_user(request)
        if not user or not user.is_admin:
            return Response({'error': 'เฉพาะ admin เท่านั้น'}, status=403)

        admins = User.objects.filter(Q(is_admin=True) | Q(is_officer=True)).order_by('full_name')
        data = [{
            'user_id': u.user_id,
            'email': u.email,
            'full_name': u.full_name,
            'department': u.department,
            'role': u.role,
            'is_admin': u.is_admin,
            'is_officer': u.is_officer,
            'created_at': u.created_at.isoformat(),
        } for u in admins]

        return Response(data)

    def post(self, request):
        user = get_current_user(request)
        if not user or not user.is_admin:
            return Response({'error': 'เฉพาะ admin เท่านั้น'}, status=403)

        email = request.data.get('email', '').strip().lower()
        role = request.data.get('role', 'Admin').strip() # 'Admin' or 'Officer'

        if not email:
            return Response({'error': 'กรุณาระบุอีเมล'}, status=400)

        if not email.endswith('@ubu.ac.th'):
            return Response(
                {'error': 'อนุญาตเฉพาะอีเมล @ubu.ac.th เท่านั้น'},
                status=400
            )

        # ถ้ามี user อยู่แล้ว → ตั้งเป็นสิทธิ์ใหม่
        try:
            target_user = User.objects.get(email=email)
            target_user.role = role
            # User model save() will handle is_admin/is_officer sync
            target_user.save()
            return Response({
                'message': f'อัปเดตสิทธิ์ของ {target_user.full_name} เป็น {role} สำเร็จ',
                'user_id': target_user.user_id,
            })
        except User.DoesNotExist:
            pass

        # ถ้ายังไม่มี user → สร้างใหม่พร้อมกำหนดสิทธิ์
        new_user = User.objects.create(
            email=email,
            full_name=request.data.get('full_name', '').strip() or email.split('@')[0].replace('.', ' ').title(),
            role=role,
        )

        return Response({
            'message': f'เพิ่ม {role} {email} สำเร็จ',
            'user_id': new_user.user_id,
        }, status=201)


class AdminRemoveAPIView(APIView):
    """DELETE /api/admins/<user_id>/ — ถอดสิทธิ์ (เปลี่ยนเป็น User)"""

    def delete(self, request, user_id):
        user = get_current_user(request)
        if not user or not user.is_admin:
            return Response({'error': 'เฉพาะ admin เท่านั้น'}, status=403)

        if str(user.user_id) == str(user_id):
            return Response(
                {'error': 'ไม่สามารถถอดสิทธิ์ตัวเองได้'},
                status=400
            )

        try:
            target_user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'ไม่พบผู้ใช้'}, status=404)

        target_user.role = 'Requester'
        target_user.save()

        return Response({
            'message': f'ถอดสิทธิ์ของ {target_user.full_name} ออกเรียบร้อยแล้ว'
        })


def admin_management_page(request):
    """หน้าจัดการ Admin (Officer only)"""
    return render(request, 'admin_management.html')


# =================================================================
# Dashboard Stats API
# =================================================================

class StatsAPIView(APIView):
    """GET /api/stats/ — สถิติสำหรับ Dashboard"""

    def get(self, request):
        user = get_current_user(request)
        if not user:
            return Response({'error': 'กรุณาเข้าสู่ระบบ'}, status=401)

        if user.is_officer or user.is_admin:
            data = {
                'total_projects': Project.objects.count(),
                'active_projects': Project.objects.filter(status='Active').count(),
                'total_orders': PurchaseOrder.objects.count(),
                'pending_orders': PurchaseOrder.objects.filter(
                    status='Pending_Approval'
                ).count(),
                'total_users': User.objects.count(),
                'total_payments': Payment.objects.filter(
                    status='Paid'
                ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0'),
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
                'total_payments': Payment.objects.filter(
                    related_order__requester=user,
                    status='Paid'
                ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0'),
            }

        return Response(data)


def partial_receive_page(request):
    """หน้าใบรับของ (Officer)"""
    return render(request, 'partial_receive.html')


class PartialReceiveDetailAPIView(APIView):
    """
    DELETE /api/partial-receives/<id>/ — ลบใบรับของ (Officer only)
    Condition: Status must be Pending_Inspection or Inspected (Reject only)
    """

    def delete(self, request, receive_id):
        user = get_current_user(request)
        if not user or not user.is_officer:
            return Response({'error': 'เฉพาะเจ้าหน้าที่พัสดุเท่านั้น'}, status=403)

        try:
            receive = PartialReceive.objects.select_related('order').get(
                receive_id=receive_id
            )
        except PartialReceive.DoesNotExist:
            return Response({'error': 'ไม่พบใบรับของ'}, status=404)

        # Condition Check
        if receive.status == 'Inspected':
            # Check Inspection Result
            # Reverse relation: inspection
            try:
                if receive.inspection.result != 'Reject':
                    return Response({'error': 'ไม่สามารถลบรายการที่ผ่านการตรวจรับแล้วได้'}, status=400)
            except Inspection.DoesNotExist:
                # Should not happen if status is Inspected, but good for safety
                pass
        elif receive.status != 'Pending_Inspection':
             return Response({'error': 'ลบได้เฉพาะรายการที่รอตรวจรับ หรือถูกปฏิเสธเท่านั้น'}, status=400)

        # Perform Delete
        receive.delete()

        return Response({'message': 'ลบรายการรับของเรียบร้อยแล้ว'})

# =================================================================
# System Utilities
# =================================================================

def run_migrations(request):
    """
    Force run migrations via HTTP request.
    Use this when build script fails to run migrations on Vercel.
    """
    from django.core.management import call_command
    from django.http import HttpResponse
    from django.contrib.sites.models import Site
    from allauth.socialaccount.models import SocialApp
    import io
    import traceback
    from contextlib import redirect_stdout, redirect_stderr
    import os
    
    if not request.user.is_superuser:
        pass

    f = io.StringIO()
    try:
        with redirect_stdout(f), redirect_stderr(f):
            # 1. Run Migrations
            print("--- Running Migrations ---")
            call_command('migrate', interactive=False)
            
            # 2. Fix Site ID = 1
            print("\n--- Fix Site Configuration ---")
            current_domain = request.get_host()
            site, created = Site.objects.update_or_create(
                id=1,
                defaults={
                    'domain': current_domain,
                    'name': 'POTMS Production'
                }
            )
            print(f"Site ID=1 configured: {site.domain}")

            # 3. Setup Google SocialApp
            google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
            google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
            if google_client_id and google_client_secret:
                print("\n--- Setup Google SocialApp ---")
                app, app_created = SocialApp.objects.update_or_create(
                    provider='google',
                    defaults={
                        'name': 'Google OAuth',
                        'client_id': google_client_id,
                        'secret': google_client_secret,
                    }
                )
                app.sites.add(site)
                print(f"Google SocialApp configured for {site.domain}")

        output = f.getvalue()
        return HttpResponse(f"<h1>Migration & Setup Success</h1><pre>{output}</pre>")
    except Exception:
        error_msg = traceback.format_exc()
        return HttpResponse(f"<h1>Migration Failed</h1><pre>{error_msg}</pre><hr><pre>{f.getvalue()}</pre>", status=500)
