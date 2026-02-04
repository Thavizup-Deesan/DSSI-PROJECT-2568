from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import User, Project, Order, OrderItem, OrderImage, Vendor, MasterItem, DeliveryRecord, DeliveryItem

import datetime
import uuid
import pandas as pd
import jwt
from django.conf import settings
import json
import csv
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

# ===================================================================
# Helper Functions
# ===================================================================

def get_user_from_token(request):
    """
    Helper to check JWT token from Authorization header.
    Returns user_data dict or None.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except Exception as e:
        return None

def generate_jwt(user_data):
    """
    Generate a simple JWT for the user.
    """
    payload = {
        'uid': user_data.get('uid'),
        'email': user_data.get('email'),
        'role': user_data.get('role', 'ผู้ขอซื้อ'),
        'name': user_data.get('name'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

# ===================================================================
# Order Status Constants (New Workflow)
# ===================================================================
ORDER_STATUS = {
    'DRAFT': 'Draft',
    'PENDING': 'รอ',
    'AWAITING_DELIVERY': 'รอรับของ',
    'PARTIAL': 'รับบางส่วน',
    'COMPLETED': 'รับครบ'
}

# Role Constants
ROLES = {
    'REQUESTER': 'ผู้ขอซื้อ',
    'COMMITTEE': 'คณะกรรมการตรวจรับ',
    'BOSS': 'หัวหน้าภาควิชา',
    'ADMIN': 'Admin'
}

# ===================================================================
# Frontend Page Views
# ===================================================================

def homepage(request):
    return redirect('page-login')

def login_page(request):
    return render(request, 'login.html')

def register_page(request):
    return render(request, 'register.html')

def requester_dashboard(request):
    return render(request, 'requester_dashboard.html')

def project_list_view(request):
    return render(request, 'project_list.html')

def select_project_view(request):
    return render(request, 'select_project.html')

def create_order_view(request):
    return render(request, 'create_order.html')

def my_orders_view(request):
    return render(request, 'my_orders.html')

def order_detail_view(request, order_id):
    return render(request, 'order_detail.html', {'order_id': order_id})

def edit_order_view(request, order_id):
    return render(request, 'edit_order.html', {'order_id': order_id})

def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')

def order_qr_view(request, order_id):
    """Display QR Code for order inspection"""
    return render(request, 'order_qr.html', {'order_id': order_id})

def receive_items_view(request, order_id):
    """Form for receiving items (partial or full)"""
    return render(request, 'receive_items.html', {'order_id': order_id})

def order_history_view(request):
    """View order history"""
    return render(request, 'order_history.html')

# ===================================================================
# Equipment (ครุภัณฑ์) Frontend Page Views - Uses temp2 templates
# ===================================================================

def equipment_select_project_view(request):
    return render(request, 'temp2/select_project.html')

def equipment_project_list_view(request):
    return render(request, 'temp2/project_list.html')

def equipment_my_orders_view(request):
    return render(request, 'temp2/my_orders.html')

def equipment_create_order_view(request):
    return render(request, 'temp2/create_order.html')

def equipment_order_detail_view(request, order_id):
    return render(request, 'temp2/order_detail.html', {'order_id': order_id})

def equipment_edit_order_view(request, order_id):
    return render(request, 'temp2/edit_order.html', {'order_id': order_id})

def print_order_view(request, order_id):
    """Render printable order document"""
    try:
        order = get_object_or_404(Order, id=order_id)
        items = order.items.all()
        
        total = sum(item.subtotal for item in items)
        
        # Format items
        items_list = []
        for item in items:
            items_list.append({
                'item_name': item.item_name,
                'quantity': item.quantity,
                'quantity_requested': item.quantity,
                'unit': item.unit,
                'estimated_unit_price': item.estimated_unit_price,
                'formatted_price': "{:,.2f}".format(item.estimated_unit_price),
                'formatted_total': "{:,.2f}".format(item.subtotal)
            })
        
        context = {
            'order': order,
            'items': items_list,
            'order_no': order.order_no,
            'requester_name': order.requester_name or (order.requester.full_name if order.requester else '-'),
            'requester_position': 'เจ้าหน้าที่',
            'requester_phone': '-',
            'project_name': order.project_name or '-',
            'project_code': order.project_code or '-',
            'created_date': order.created_at.strftime('%d/%m/%Y') if order.created_at else '',
            'required_date': str(order.required_date) if order.required_date else '-',
            'vendor_display': order.vendor_name or '-',
            'grand_total': "{:,.2f}".format(total)
        }
        return render(request, 'print_order.html', context)
    except Exception as e:
        print(e)
        return HttpResponse("Error loading order", status=404)

def print_equipment_request_view(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        items = order.items.all()
        
        total = sum(item.subtotal for item in items)
        
        items_list = []
        for item in items:
            items_list.append({
                'item_name': item.item_name,
                'quantity': item.quantity,
                'quantity_requested': item.quantity,
                'unit': item.unit,
                'estimated_unit_price': item.estimated_unit_price,
                'formatted_price': "{:,.2f}".format(item.estimated_unit_price),
                'formatted_total': "{:,.2f}".format(item.subtotal)
            })
        
        context = {
            'order': order,
            'items': items_list,
            'requester_name': order.requester_name or '-',
            'requester_position': 'เจ้าหน้าที่',
            'requester_phone': '-',
            'project_name': order.project_name or '-',
            'project_code': order.project_code or '-',
            'grand_total': "{:,.2f}".format(total)
        }
        return render(request, 'print_equipment_request.html', context)
    except Exception as e:
        print(e)
        return HttpResponse("Error loading order", status=404)

def scan_order_view(request, order_id):
    return render(request, 'scan_order.html', {'order_id': order_id})

# ===================================================================
# Authentication APIs
# ===================================================================

@method_decorator(ratelimit(key='ip', rate='3/m', block=True), name='dispatch')
class UserRegisterAPIView(APIView):
    def post(self, request):
        import hashlib
        data = request.data
        email = data.get('email')
        username = data.get('username')
        password = data.get('password', '')
        name = data.get('name')
        role = data.get('role', 'user')
        
        try:
            # Validate username
            if not username:
                return Response({'error': 'Username is required'}, status=400)
            
            # Check existing email
            if User.objects.filter(email=email).exists():
                return Response({'error': 'Email already exists'}, status=400)
            
            # Check existing username (uid)
            if User.objects.filter(uid=username).exists():
                return Response({'error': 'Username already exists'}, status=400)
            
            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest() if password else ''
            
            user = User.objects.create(
                uid=username,  # Use username as uid
                email=email,
                full_name=name,
                password=password_hash,
                role=role
            )
            
            return Response({'message': 'User registered successfully', 'uid': username}, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='dispatch')
class UserLoginAPIView(APIView):
    def post(self, request):
        import hashlib
        data = request.data
        username = data.get('username')
        password = data.get('password', '')
        
        try:
            # Find user by uid, email or full_name
            user = User.objects.filter(
                Q(uid=username) | Q(email=username) | Q(full_name=username)
            ).first()
            
            if not user:
                return Response({'error': 'Invalid credentials'}, status=401)
            
            # Check password (hash with sha256)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user.password and user.password != password_hash:
                return Response({'error': 'Invalid credentials'}, status=401)
            
            user_data = {
                'uid': user.uid,
                'email': user.email,
                'name': user.full_name,
                'role': user.role
            }
            
            token = generate_jwt(user_data)
            
            return Response({
                'token': token,
                'user': user_data
            }, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class UserDetailAPIView(APIView):
    def get(self, request, user_id):
        try:
            user = get_object_or_404(User, uid=user_id)
            return Response({
                'uid': user.uid,
                'email': user.email,
                'name': user.full_name,
                'role': user.role,
                'department': user.department
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class UserListAPIView(APIView):
    def get(self, request):
        try:
            users = User.objects.all()
            user_list = [{
                'uid': u.uid,
                'email': u.email,
                'name': u.full_name,
                'role': u.role
            } for u in users]
            return Response(user_list)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ===================================================================
# Project APIs
# ===================================================================

class ProjectAPIView(APIView):
    def get(self, request):
        try:
            projects = Project.objects.all().order_by('-created_at')
            
            # Filter by project type if key provided
            project_type = request.GET.get('type')
            if project_type:
                projects = projects.filter(project_type=project_type)

            project_list = []
            for p in projects:
                project_list.append({
                    'id': p.id,
                    'project_code': p.project_code,
                    'project_name': p.project_name,
                    'project_type': p.project_type,  # Added project_type
                    'budget_total': float(p.budget_total),
                    'budget_used': float(p.budget_used),
                    'budget_remaining': float(p.budget_remaining),
                    'status': p.status
                })
            return Response(project_list)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def post(self, request):
        data = request.data
        try:
            project = Project.objects.create(
                project_code=data.get('project_code'),
                project_name=data.get('project_name'),
                project_type=data.get('project_type', 'พัสดุ'),  # Added project_type with default
                budget_total=data.get('budget_total', 0),
                status=data.get('status', 'Active')
            )
            return Response({
                'message': 'Project created',
                'project_id': project.id
            }, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class ProjectDetailAPIView(APIView):
    def get(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id)
            return Response({
                'id': project.id,
                'project_code': project.project_code,
                'project_name': project.project_name,
                'budget_total': float(project.budget_total),
                'budget_used': float(project.budget_used),
                'budget_remaining': float(project.budget_remaining),
                'status': project.status
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def put(self, request, project_id):
        data = request.data
        try:
            project = get_object_or_404(Project, id=project_id)
            project.project_name = data.get('project_name', project.project_name)
            project.budget_total = data.get('budget_total', project.budget_total)
            project.status = data.get('status', project.status)
            project.save()
            return Response({'message': 'Project updated'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def delete(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id)
            project.delete()
            return Response({'message': 'Project deleted'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ===================================================================
# Order APIs
# ===================================================================

class OrderAPIView(APIView):
    def get(self, request):
        user_id_param = request.GET.get('user_id')
        
        try:
            orders = Order.objects.all()
            
            # Filter by user_id if provided
            if user_id_param and user_id_param not in ['undefined', 'null', '']:
                orders = orders.filter(requester_id=user_id_param)

            # Filter by project type (e.g. ?type=พัสดุ)
            project_type = request.GET.get('type')
            if project_type:
               orders = orders.filter(project__project_type=project_type)
            
            orders = orders.order_by('-created_at')[:100]
            
            order_list = []
            for o in orders:
                order_list.append({
                    'id': o.id,
                    'order_no': o.order_no,
                    'order_title': o.order_title,
                    'status': o.status,
                    'created_at': o.created_at.isoformat() if o.created_at else None,
                    'total_estimated_price': float(o.total_estimated_price),
                    'project_code': o.project_code,
                    'project_name': o.project_name,
                    'project_type': o.project.project_type if o.project else 'พัสดุ',
                    'requester_name': o.requester_name,
                    'requester_id': o.requester_id if o.requester else None,
                    'item_count': o.items.count()
                })
            
            return Response(order_list)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def post(self, request):
        data = request.data
        try:
            # Generate Order No
            ts = int(datetime.datetime.now().timestamp())
            order_no = f"PO-{ts}"
            
            # Get or create project
            project = None
            project_id = data.get('project_id')
            if project_id:
                project = Project.objects.filter(id=project_id).first()
            
            # Get requester
            requester = None
            requester_id = data.get('requester_id')
            if requester_id:
                requester = User.objects.filter(uid=requester_id).first()
            
            initial_status = 'Draft'
            if data.get('action') == 'submit':
                initial_status = 'Pending'
            
            order = Order.objects.create(
                order_no=order_no,
                order_title=data.get('order_title'),
                project=project,
                requester=requester,
                requester_name=data.get('requester_name', ''),
                vendor_name=data.get('vendor_name', ''),
                status=initial_status,
                total_estimated_price=data.get('total_estimated_price', 0),
                required_date=data.get('required_date'),
                order_description=data.get('order_description', ''),
                submitted_at=timezone.now() if initial_status != 'Draft' else None
            )
            
            # Create order items
            items = data.get('items', [])
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    item_name=item.get('item_name'),
                    quantity=item.get('quantity', 1),
                    unit=item.get('unit', ''),
                    estimated_unit_price=item.get('estimated_unit_price', 0)
                )
            
            return Response({
                'message': 'Order created',
                'order_id': order.id,
                'order_no': order_no
            }, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class OrderDetailAPIView(APIView):
    def get(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id)
            
            items = [{
                'id': item.id,
                'item_name': item.item_name,
                'quantity': item.quantity,
                'unit': item.unit,
                'estimated_unit_price': float(item.estimated_unit_price),
                'quantity_received': item.quantity_received,
                'quantity_pending': item.remaining_quantity,
                'subtotal': float(item.subtotal)
            } for item in order.items.all()]
            
            # Get images
            images = [{
                'id': img.id,
                'url': img.image.url if img.image else None,
                'description': img.description,
                'uploaded_at': img.uploaded_at.isoformat() if img.uploaded_at else None
            } for img in order.images.all()]
            
            return Response({
                'id': order.id,
                'order_no': order.order_no,
                'order_title': order.order_title,
                'project_id': order.project_id,
                'project_name': order.project_name,
                'project_code': order.project_code,
                'requester_id': order.requester_id if order.requester else None,
                'requester_name': order.requester_name,
                'vendor_name': order.vendor_name,
                'status': order.status,
                'total_estimated_price': float(order.total_estimated_price),
                'required_date': str(order.required_date) if order.required_date else None,
                'order_description': order.order_description,
                'staff_note': order.staff_note,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'updated_at': order.updated_at.isoformat() if order.updated_at else None,
                'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
                'items': items,
                'images': images
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def put(self, request, order_id):
        data = request.data
        try:
            order = get_object_or_404(Order, id=order_id)
            
            if order.status not in ['Draft', 'CorrectionNeeded']:
                return Response({'error': 'Cannot edit order in this status'}, status=400)
            
            order.order_title = data.get('order_title', order.order_title)
            order.vendor_name = data.get('vendor_name', order.vendor_name)
            order.total_estimated_price = data.get('total_estimated_price', order.total_estimated_price)
            order.required_date = data.get('required_date', order.required_date)
            order.order_description = data.get('order_description', order.order_description)
            
            if data.get('action') == 'submit':
                order.status = 'Pending'
                order.submitted_at = timezone.now()
            
            order.save()
            
            # Update items
            if 'items' in data:
                order.items.all().delete()
                for item in data['items']:
                    OrderItem.objects.create(
                        order=order,
                        item_name=item.get('item_name'),
                        quantity=item.get('quantity', 1),
                        unit=item.get('unit', ''),
                        estimated_unit_price=item.get('estimated_unit_price', 0)
                    )
            
            return Response({'message': 'Order updated'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
            
    def delete(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id)
            
            if order.status != 'Draft':
                return Response({'error': 'Can only delete Draft orders'}, status=400)
            
            order.delete()
            return Response({'message': 'Order deleted'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class OrderSubmitAPIView(APIView):
    def post(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id)
            order.status = 'Pending'
            order.submitted_at = timezone.now()
            order.save()
            return Response({'message': 'Order submitted'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class OrderStatusUpdateAPIView(APIView):
    def post(self, request, order_id):
        status_val = request.data.get('status')
        try:
            order = get_object_or_404(Order, id=order_id)
            order.status = status_val
            order.save()
            return Response({'message': 'Status updated'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class ExportOrderCSVAPIView(APIView):
    def get(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id)
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="order_{order.order_no}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['ลำดับ', 'รายการ', 'จำนวน', 'หน่วย', 'ราคา/หน่วย', 'รวม'])
            
            for idx, item in enumerate(order.items.all(), 1):
                writer.writerow([
                    idx,
                    item.item_name,
                    item.quantity,
                    item.unit,
                    float(item.estimated_unit_price),
                    float(item.subtotal)
                ])
            
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ===================================================================
# Delivery APIs
# ===================================================================

class DeliveryRecordAPIView(APIView):
    def get(self, request, order_id):
        try:
            deliveries = DeliveryRecord.objects.filter(order_id=order_id).order_by('-delivered_at')
            delivery_list = [{
                'id': d.id,
                'delivered_at': d.delivered_at.isoformat() if d.delivered_at else None,
                'notes': d.notes,
                'items': [{
                    'order_item_id': di.order_item_id,
                    'quantity_received': di.quantity_received
                } for di in d.items.all()]
            } for d in deliveries]
            return Response(delivery_list)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def post(self, request, order_id):
        data = request.data
        try:
            order = get_object_or_404(Order, id=order_id)
            
            delivery = DeliveryRecord.objects.create(
                order=order,
                notes=data.get('notes', '')
            )
            
            return Response({'message': 'Delivery recorded', 'delivery_id': delivery.id})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ===================================================================
# Scan APIs
# ===================================================================

class ScanOrderDataAPIView(APIView):
    def get(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id)
            
            items = [{
                'item_name': item.item_name,
                'quantity': item.quantity,
                'unit': item.unit,
                'quantity_received': item.quantity_received
            } for item in order.items.all()]
            
            return Response({
                'order_no': order.order_no,
                'status': order.status,
                'requester': order.requester_name,
                'project_type': order.project.project_type if order.project else 'พัสดุ',
                'items': items
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ===================================================================
# Staff Order Actions
# ===================================================================

def staff_order_detail_view(request, order_id):
    return render(request, 'staff_order_detail.html', {'order_id': order_id})

class OrderApproveAPIView(APIView):
    def post(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id)
            order.status = 'Approved'
            order.staff_note = request.data.get('note', '')
            order.save()
            return Response({'message': 'Order approved'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class OrderRejectAPIView(APIView):
    def post(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id)
            order.status = 'Rejected'
            order.staff_note = request.data.get('note', '')
            order.save()
            return Response({'message': 'Order rejected'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class OrderCorrectionAPIView(APIView):
    def post(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id)
            order.status = 'CorrectionNeeded'
            order.staff_note = request.data.get('note', '')
            order.save()
            return Response({'message': 'Correction requested'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ===================================================================
# QR Code & Item Receiving APIs (New Workflow)
# ===================================================================

class GenerateQRCodeAPIView(APIView):
    """Generate QR Code URL for order inspection"""
    def get(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id)
            
            base_url = request.build_absolute_uri('/').rstrip('/')
            qr_url = f"{base_url}/api/orders/{order_id}/receive/"
            
            return Response({
                'order_id': order_id,
                'qr_url': qr_url,
                'order_no': order.order_no
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class ItemReceivingAPIView(APIView):
    """API for recording item receiving (partial or full)"""
    def get(self, request, order_id):
        """Get order items with receiving status"""
        try:
            order = get_object_or_404(Order, id=order_id)
            
            items = []
            for item in order.items.all():
                items.append({
                    'id': item.id,
                    'item_index': item.id,
                    'item_name': item.item_name,
                    'quantity': item.quantity,
                    'quantity_total': item.quantity,
                    'quantity_received': item.quantity_received,
                    'quantity_pending': item.remaining_quantity,
                    'unit': item.unit
                })
            
            return Response({
                'order': {
                    'id': order.id,
                    'order_no': order.order_no,
                    'status': order.status
                },
                'items': items,
                'status': order.status
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def post(self, request, order_id):
        """Record item receiving"""
        try:
            data = request.data
            received_items = data.get('items', [])
            is_final = data.get('is_final', False)
            
            order = get_object_or_404(Order, id=order_id)
            
            # Update each item's received quantity
            for recv in received_items:
                item_id = recv.get('item_id') or recv.get('item_index')
                qty_this_round = float(recv.get('quantity_received', 0))
                
                if item_id:
                    try:
                        order_item = order.items.get(id=item_id)
                        order_item.quantity_received += qty_this_round
                        order_item.save()
                    except OrderItem.DoesNotExist:
                        pass
            
            # Check if all items are complete
            all_complete = all(
                item.quantity_received >= item.quantity 
                for item in order.items.all()
            )
            
            if is_final or all_complete:
                new_status = ORDER_STATUS['COMPLETED']
            else:
                new_status = ORDER_STATUS['PARTIAL']
            
            order.status = new_status
            order.save()
            
            return Response({
                'message': 'Items received successfully',
                'new_status': new_status,
                'all_complete': all_complete
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class OrderHistoryAPIView(APIView):
    """Get completed orders history"""
    def get(self, request):
        try:
            user = get_user_from_token(request)
            
            orders = Order.objects.filter(status=ORDER_STATUS['COMPLETED'])
            
            if user and user.get('role') not in [ROLES['ADMIN'], ROLES['COMMITTEE']]:
                orders = orders.filter(requester_id=user.get('uid'))
            
            orders = orders.order_by('-updated_at')[:100]
            
            order_list = [{
                'id': o.id,
                'order_no': o.order_no,
                'order_title': o.order_title,
                'status': o.status,
                'project_name': o.project_name,
                'requester_name': o.requester_name,
                'created_at': o.created_at.isoformat() if o.created_at else None,
                'updated_at': o.updated_at.isoformat() if o.updated_at else None
            } for o in orders]
            
            return Response(order_list)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class UpdateOrderStatusAPIView(APIView):
    """Update order status to new workflow statuses"""
    def post(self, request, order_id):
        try:
            new_status = request.data.get('status')
            valid_statuses = list(ORDER_STATUS.values())
            
            if new_status not in valid_statuses:
                return Response({'error': f'Invalid status. Must be one of: {valid_statuses}'}, status=400)
            
            order = get_object_or_404(Order, id=order_id)
            order.status = new_status
            order.save()
            
            return Response({'message': f'Status updated to {new_status}'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ===================================================================
# Image Upload APIs (NEW FEATURE)
# ===================================================================

class OrderImageUploadAPIView(APIView):
    """Upload image for an order"""
    parser_classes = (MultiPartParser, FormParser)
    
    def get(self, request, order_id):
        """Get all images for an order"""
        try:
            order = get_object_or_404(Order, id=order_id)
            images = [{
                'id': img.id,
                'url': img.image.url if img.image else None,
                'description': img.description,
                'uploaded_at': img.uploaded_at.isoformat() if img.uploaded_at else None
            } for img in order.images.all()]
            return Response({'images': images})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def post(self, request, order_id):
        """Upload a new image"""
        try:
            order = get_object_or_404(Order, id=order_id)
            image_file = request.FILES.get('image')
            
            if not image_file:
                return Response({'error': 'No image file provided'}, status=400)
            
            description = request.data.get('description', '')
            
            order_image = OrderImage.objects.create(
                order=order,
                image=image_file,
                description=description
            )
            
            return Response({
                'message': 'Image uploaded successfully',
                'image_id': order_image.id,
                'url': order_image.image.url
            }, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def delete(self, request, order_id):
        """Delete an image"""
        try:
            image_id = request.data.get('image_id')
            image = get_object_or_404(OrderImage, id=image_id, order_id=order_id)
            image.image.delete()
            image.delete()
            return Response({'message': 'Image deleted'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ===================================================================
# MasterItem APIs
# ===================================================================

class MasterItemAPIView(APIView):
    def get(self, request):
        try:
            items = MasterItem.objects.all()
            search = request.GET.get('search', '')
            
            if search:
                items = items.filter(
                    Q(item_name__icontains=search) | Q(item_code__icontains=search)
                )
            
            item_list = [{
                'id': i.id,
                'item_code': i.item_code,
                'item_name': i.item_name,
                'standard_unit': i.standard_unit,
                'category': i.category
            } for i in items[:50]]
            
            return Response(item_list)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ===================================================================
# Vendor APIs
# ===================================================================

class VendorAPIView(APIView):
    def get(self, request):
        try:
            vendors = Vendor.objects.all()
            vendor_list = [{
                'id': v.id,
                'vendor_name': v.vendor_name,
                'phone': v.phone,
                'email': v.email
            } for v in vendors]
            return Response(vendor_list)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def post(self, request):
        data = request.data
        try:
            vendor = Vendor.objects.create(
                vendor_name=data.get('vendor_name'),
                phone=data.get('phone', ''),
                email=data.get('email', '')
            )
            return Response({
                'message': 'Vendor created',
                'vendor_id': vendor.id
            }, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ===================================================================
# Admin User Management
# ===================================================================

def admin_users_view(request):
    return render(request, 'admin_users.html')

class AdminUserAPIView(APIView):
    def get(self, request, uid=None):
        # 1. Check Admin Permission
        user_data = get_user_from_token(request)
        if not user_data or user_data.get('role') != 'admin':
            return Response({'error': 'Unauthorized'}, status=403)

        # 2. Get Single User
        if uid:
            user = get_object_or_404(User, uid=uid)
            return Response({
                'uid': user.uid,
                'email': user.email,
                'full_name': user.full_name,
                'department': user.department,
                'phone': user.phone,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at
            })

        # 3. List All Users
        users = User.objects.all().order_by('-created_at')
        data = [{
            'uid': u.uid,
            'email': u.email,
            'full_name': u.full_name,
            'department': u.department,
            'phone': u.phone,
            'role': u.role,
            'is_active': u.is_active,
            'created_at': u.created_at
        } for u in users]
        return Response(data)

    def post(self, request):
        # 1. Check Admin Permission
        user_data = get_user_from_token(request)
        if not user_data or user_data.get('role') != 'admin':
            return Response({'error': 'Unauthorized'}, status=403)

        data = request.data
        try:
            # Check unique UID/Email
            if User.objects.filter(uid=data.get('uid')).exists():
                return Response({'error': 'UID already exists'}, status=400)
            if User.objects.filter(email=data.get('email')).exists():
                return Response({'error': 'Email already exists'}, status=400)

            user = User.objects.create(
                uid=data.get('uid'),
                email=data.get('email'),
                full_name=data.get('full_name'),
                department=data.get('department', ''),
                phone=data.get('phone', ''),
                role=data.get('role', 'user'),
                is_active=data.get('is_active', True)
            )
            return Response({'message': 'User created', 'uid': user.uid}, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def put(self, request, uid):
        # 1. Check Admin Permission
        user_data = get_user_from_token(request)
        if not user_data or user_data.get('role') != 'admin':
            return Response({'error': 'Unauthorized'}, status=403)

        data = request.data
        try:
            user = get_object_or_404(User, uid=uid)
            
            # Check email uniqueness if changed
            new_email = data.get('email')
            if new_email and new_email != user.email:
                if User.objects.filter(email=new_email).exclude(uid=uid).exists():
                    return Response({'error': 'Email already exists'}, status=400)
                user.email = new_email

            user.full_name = data.get('full_name', user.full_name)
            user.department = data.get('department', user.department)
            user.phone = data.get('phone', user.phone)
            user.role = data.get('role', user.role)
            user.is_active = data.get('is_active', user.is_active)
            user.save()
            
            return Response({'message': 'User updated'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def delete(self, request, uid):
        # 1. Check Admin Permission
        user_data = get_user_from_token(request)
        if not user_data or user_data.get('role') != 'admin':
            return Response({'error': 'Unauthorized'}, status=403)

        try:
            user = get_object_or_404(User, uid=uid)
            user.delete()
            return Response({'message': 'User deleted'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class ResetPasswordAPIView(APIView):
    def post(self, request, uid):
        import hashlib
        # 1. Check Admin Permission
        user_data = get_user_from_token(request)
        if not user_data or user_data.get('role') != 'admin':
            return Response({'error': 'Unauthorized'}, status=403)

        data = request.data
        new_password = data.get('new_password')
        
        if not new_password or len(new_password) < 4:
            return Response({'error': 'Password must be at least 4 characters'}, status=400)

        try:
            user = get_object_or_404(User, uid=uid)
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            user.password = password_hash
            user.save()
            return Response({'message': 'Password reset successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
