from django.urls import path
from .views import (
    # Auth APIs
    UserRegisterAPIView, UserLoginAPIView, UserDetailAPIView, UserListAPIView, AdminUserAPIView, admin_users_view, ResetPasswordAPIView,
    
    # Project APIs
    ProjectAPIView, ProjectDetailAPIView,

    # Master Item APIs
    MasterItemAPIView,

    # Order APIs
    OrderAPIView, OrderDetailAPIView, OrderSubmitAPIView, OrderStatusUpdateAPIView,
    
    # Delivery APIs
    DeliveryRecordAPIView,

    # Export & Scan APIs
    ExportOrderCSVAPIView, ScanOrderDataAPIView,

    # Page Views (Frontend)
    homepage, login_page, register_page, requester_dashboard,
    project_list_view, select_project_view, create_order_view,
    my_orders_view, order_detail_view, edit_order_view, staff_dashboard, staff_order_detail_view,
    order_qr_view, receive_items_view, order_history_view,
    
    # Equipment Page Views
    equipment_select_project_view, equipment_project_list_view, equipment_my_orders_view,
    equipment_create_order_view, equipment_order_detail_view, equipment_edit_order_view,
    
    # Print Views
    print_order_view, print_equipment_request_view,

    # Scan Views
    scan_order_view,
    
    # Staff Action APIs
    OrderApproveAPIView, OrderRejectAPIView, OrderCorrectionAPIView,
    
    # QR & Receiving APIs (New Workflow)
    GenerateQRCodeAPIView, ItemReceivingAPIView, OrderHistoryAPIView, UpdateOrderStatusAPIView,
    
    # Image Upload APIs
    OrderImageUploadAPIView,
    
    # Vendor APIs
    VendorAPIView
)


urlpatterns = [
    # ===================================================================
    # Authentication APIs
    # ===================================================================
    path('auth/register/', UserRegisterAPIView.as_view(), name='api-register'),
    path('auth/login/', UserLoginAPIView.as_view(), name='api-login'),
    path('users/<str:user_id>/', UserDetailAPIView.as_view(), name='api-user-detail'),

    # ===================================================================
    # Project APIs
    # ===================================================================
    path('projects/select/', select_project_view, name='page-project-select'),
    path('projects/list/', project_list_view, name='page-project-list'),
    path('projects/', ProjectAPIView.as_view(), name='api-projects'),
    path('projects/<str:project_id>/', ProjectDetailAPIView.as_view(), name='api-project-detail'),

    # ===================================================================
    # Product/Item APIs
    # ===================================================================
    path('products/', MasterItemAPIView.as_view(), name='api-products'),

    # ===================================================================
    # Order Management APIs
    # ===================================================================
    # Page Routes (Must be before <str:order_id>)
    path('orders/create/', create_order_view, name='page-order-create'),
    path('orders/my/', my_orders_view, name='page-my-orders'),

    # API Routes
    path('orders/', OrderAPIView.as_view(), name='api-orders'),
    path('orders/<str:order_id>/', OrderDetailAPIView.as_view(), name='api-order-detail'),
    path('orders/<str:order_id>/submit/', OrderSubmitAPIView.as_view(), name='api-order-submit'),
    path('orders/<str:order_id>/status/', OrderStatusUpdateAPIView.as_view(), name='api-order-status'),
    path('orders/<str:order_id>/export-csv/', ExportOrderCSVAPIView.as_view(), name='api-order-export'),
    
    # Staff Action APIs
    path('orders/<str:order_id>/approve/', OrderApproveAPIView.as_view(), name='api-order-approve'),
    path('orders/<str:order_id>/reject/', OrderRejectAPIView.as_view(), name='api-order-reject'),
    path('orders/<str:order_id>/correction/', OrderCorrectionAPIView.as_view(), name='api-order-correction'),

    # ===================================================================
    # Delivery & Tracking APIs
    # ===================================================================
    path('orders/<str:order_id>/deliveries/', DeliveryRecordAPIView.as_view(), name='api-order-deliveries'),

    # ===================================================================
    # Scan Data APIs
    # ===================================================================
    path('scan/<str:order_id>/data/', ScanOrderDataAPIView.as_view(), name='api-scan-data'),

    # ===================================================================
    # Frontend Pages (URL Routing)
    # ===================================================================
    path('', homepage, name='page-home'),
    path('login/', login_page, name='page-login'),
    path('register/', register_page, name='page-register'),
    path('dashboard/', requester_dashboard, name='page-dashboard'),
    path('staff/dashboard/', staff_dashboard, name='page-staff-dashboard'),
    path('staff/orders/<str:order_id>/', staff_order_detail_view, name='page-staff-order-detail'),
    
    # path('projects/list/', project_list_view, name='page-project-list'), # Moved up
    # path('projects/select/', select_project_view, name='page-project-select'), # Moved up
    
    # path('orders/create/', create_order_view, name='page-order-create'), # Moved up
    # path('orders/my/', my_orders_view, name='page-my-orders'), # Moved up
    path('orders/<str:order_id>/view/', order_detail_view, name='page-order-view'),
    path('orders/<str:order_id>/edit/', edit_order_view, name='page-order-edit'),
    
    # Print Pages
    path('orders/<str:order_id>/print/', print_order_view, name='page-order-print'),
    path('orders/<str:order_id>/print-equipment/', print_equipment_request_view, name='page-order-print-equipment'),
    
    # Scan Pages (Mobile)
    path('scan/<str:order_id>/', scan_order_view, name='page-scan-order'),
    
    # ===================================================================
    # New Workflow Routes
    # ===================================================================
    # QR Code & Receiving Pages (Requester records after offline committee inspection)
    path('orders/<str:order_id>/qr/', order_qr_view, name='page-order-qr'),
    path('orders/<str:order_id>/receive/', receive_items_view, name='page-receive-items'),
    path('orders/history/', order_history_view, name='page-order-history'),
    
    # QR Code & Receiving APIs
    path('api/orders/<str:order_id>/generate-qr/', GenerateQRCodeAPIView.as_view(), name='api-generate-qr'),
    path('api/orders/<str:order_id>/receive/', ItemReceivingAPIView.as_view(), name='api-receive-items'),
    path('api/orders/<str:order_id>/update-status/', UpdateOrderStatusAPIView.as_view(), name='api-update-order-status'),
    path('api/orders/history/', OrderHistoryAPIView.as_view(), name='api-order-history'),
    
    # Image Upload APIs
    path('orders/<str:order_id>/images/', OrderImageUploadAPIView.as_view(), name='api-order-images'),
    
    # Vendor APIs
    path('vendors/', VendorAPIView.as_view(), name='api-vendors'),
    
    # User List API
    path('users/', UserListAPIView.as_view(), name='api-users'),
    
    # ===================================================================
    # Equipment (ครุภัณฑ์) System Routes - Uses temp2 templates
    # ===================================================================
    path('equipment/projects/select/', equipment_select_project_view, name='page-equipment-project-select'),
    path('equipment/projects/list/', equipment_project_list_view, name='page-equipment-project-list'),
    path('equipment/orders/my/', equipment_my_orders_view, name='page-equipment-my-orders'),
    path('equipment/orders/create/', equipment_create_order_view, name='page-equipment-order-create'),
    path('equipment/orders/<str:order_id>/view/', equipment_order_detail_view, name='page-equipment-order-detail'),
    path('equipment/orders/<str:order_id>/edit/', equipment_edit_order_view, name='page-equipment-order-edit'),
    
    # ===================================================================
    # Admin User Management
    # ===================================================================
    path('admin/users/page/', admin_users_view, name='page-admin-users'),
    path('admin/users/', AdminUserAPIView.as_view(), name='api-admin-users'),
    path('admin/users/<str:uid>/', AdminUserAPIView.as_view(), name='api-admin-user-detail'),
    path('admin/users/<str:uid>/reset-password/', ResetPasswordAPIView.as_view(), name='api-admin-reset-password'),
]