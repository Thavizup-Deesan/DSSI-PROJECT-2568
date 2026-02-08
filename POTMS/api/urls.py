from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ProjectAPIView, ProjectDetailAPIView, ProjectImportAPIView, 
    UserRegisterAPIView, UserLoginAPIView, StatsAPIView,
    UserListAPIView, UserDetailAPIView,  # User Management APIs
    ProjectAssignmentAPIView, ProjectAssignmentDetailAPIView,  # Project Assignment APIs
    project_dashboard, login_page, OrderAPIView, OrderSubmitAPIView, OrderDetailAPIView, 
    OrderApproveAPIView, OrderRejectAPIView, OrderCorrectionAPIView,  # Order Approval APIs
    OrderBossApproveAPIView, OrderBossRejectAPIView, OrderSendToProcurementAPIView, OrderApprovedCorrectionAPIView,  # Boss Approval & Procurement APIs
    OrderReceiveFromProcurementAPIView,  # Phase 4: Receive from Procurement
    SubOrderCreateAPIView,  # Phase 4: Create Sub-order
    InspectionAPIView,  # Phase 4: Inspection + QR Code
    HandoverAPIView, CloseOrderAPIView,  # Phase 4: Handover + Close
    BudgetSummaryAPIView, staff_reports_view,  # Phase 4: Reports
    ExportOrderCSVAPIView,  # Phase 4: Export CSV
    UserProjectsAPIView, StaffOrdersAPIView,
    create_order_view, my_orders_view, order_detail_view, edit_order_view, staff_dashboard, homepage, 
    staff_orders_view, staff_order_detail_view, staff_po_management_view, staff_po_detail_view,  # Staff page views
    register_page, user_management_page, user_select_project_view, user_dashboard,  # Page Views
    print_order_view,  # Print Order Page
    scan_suborder_view, ScanSuborderDataAPIView,  # Scan QR Code
    OrderEditHistoryAPIView, OrderEditHistoryDetailAPIView, order_edit_history_view  # Order Edit History
)



urlpatterns = [
    # ===================================================================
    # JWT Authentication - Token Management
    # ===================================================================
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ===================================================================
    # Project APIs - จัดการข้อมูลโครงการ
    # ===================================================================
    path('projects/', ProjectAPIView.as_view(), name='project-list-create'),
    # สำหรับ Import (ต้องอยู่ก่อน <str:project_id> ไม่งั้นจะถูกจับผิด)
    path('projects/import/', ProjectImportAPIView.as_view(), name='project-import'),
    # ลิงก์สำหรับจัดการโครงการแต่ละตัว (ลบ/แก้ไข)
    path('projects/<str:project_id>/', ProjectDetailAPIView.as_view(), name='project-detail'),
    
    # ===================================================================
    # Project Assignment APIs - มอบหมายโครงการ (Staff)
    # ===================================================================
    path('project-assignments/', ProjectAssignmentAPIView.as_view(), name='project-assignment-list'),
    path('project-assignments/<str:assignment_id>/', ProjectAssignmentDetailAPIView.as_view(), name='project-assignment-detail'),
    
    # ===================================================================
    # User Management APIs - จัดการผู้ใช้งาน (Admin)
    # ===================================================================
    path('users/', UserListAPIView.as_view(), name='user-list'),  # GET: ดึงรายชื่อผู้ใช้ทั้งหมด
    path('users/<str:user_id>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('users/<str:user_id>/projects/', UserProjectsAPIView.as_view(), name='user-projects'),  # โครงการที่ user รับผิดชอบ  # GET/PUT/DELETE
    
    # ===================================================================
    # Page Views - หน้าเว็บ HTML
    # ===================================================================
    path('project_list/', project_dashboard, name='project-dashboard'),
    path('user-dashboard/', user_dashboard, name='user-dashboard'),  # User Dashboard ใหม่
    path('login-page/', login_page, name='login-page'),
    path('register-page/', register_page, name='register-page'),  # หน้าสมัครสมาชิก
    path('staff-dashboard/', staff_dashboard, name='staff-dashboard'),
    path('user-management/', user_management_page, name='user-management'),  # Admin Panel
    path('select_project/', user_select_project_view, name='user_select_project'),
    
    # ===================================================================
    # User Authentication APIs - ระบบ Login/Register
    # ===================================================================
    path('register/', UserRegisterAPIView.as_view(), name='user-register'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    
    # ===================================================================
    # Stats API - ดึงสถิติ
    # ===================================================================
    path('stats/', StatsAPIView.as_view(), name='stats'),
    path('orders/', OrderAPIView.as_view(), name='order-list'),
    path('orders/<str:order_id>/', OrderDetailAPIView.as_view(), name='order-detail'),  # GET/PUT/DELETE order
    path('orders/<str:order_id>/submit/', OrderSubmitAPIView.as_view(), name='order-submit'),  # ส่งใบสั่งซื้อ + ตัดงบ
    path('orders/<str:order_id>/detail/', order_detail_view, name='order-detail-view'),  # หน้ารายละเอียด
    path('orders/<str:order_id>/edit/', edit_order_view, name='edit-order'),  # หน้าแก้ไขใบสั่งซื้อ
    
    # ===================================================================
    # Staff Order Management - จัดการใบสั่งซื้อ (Staff)
    # ===================================================================
    path('staff/orders/', StaffOrdersAPIView.as_view(), name='staff-orders-api'),  # API: ดึงรายการทั้งหมด
    path('staff/orders/page/', staff_orders_view, name='staff-orders-page'),  # หน้าจัดการรออนุมัติ
    path('staff/po-management/', staff_po_management_view, name='staff-po-management'),  # หน้าจัดการ PO ทั้งหมด
    path('staff/orders/<str:order_id>/detail/', staff_order_detail_view, name='staff-order-detail'),  # หน้าตรวจสอบรายละเอียด
    path('staff/po/<str:order_id>/detail/', staff_po_detail_view, name='staff-po-detail'),  # หน้าดูรายละเอียด PO
    
    # Order Approval APIs
    path('orders/<str:order_id>/approve/', OrderApproveAPIView.as_view(), name='order-approve'),  # Staff อนุมัติ → รอหัวหน้า
    path('orders/<str:order_id>/reject/', OrderRejectAPIView.as_view(), name='order-reject'),  # ปฏิเสธ
    path('orders/<str:order_id>/correction/', OrderCorrectionAPIView.as_view(), name='order-correction'),  # ส่งกลับแก้ไข
    path('orders/<str:order_id>/boss-approve/', OrderBossApproveAPIView.as_view(), name='order-boss-approve'),  # หัวหน้าอนุมัติ
    path('orders/<str:order_id>/boss-reject/', OrderBossRejectAPIView.as_view(), name='order-boss-reject'),  # หัวหน้าไม่อนุมัติ (WaitingBossApproval)
    path('orders/<str:order_id>/approved-correction/', OrderApprovedCorrectionAPIView.as_view(), name='order-approved-correction'),  # ส่งกลับแก้ไข (Approved)
    path('orders/<str:order_id>/send-to-procurement/', OrderSendToProcurementAPIView.as_view(), name='order-send-procurement'),  # ส่งพัสดุ
    path('orders/<str:order_id>/receive-procurement/', OrderReceiveFromProcurementAPIView.as_view(), name='order-receive-procurement'),  # รับของจากพัสดุ
    path('orders/<str:order_id>/create-suborder/', SubOrderCreateAPIView.as_view(), name='order-create-suborder'),  # สร้าง Sub-order
    path('suborders/<str:suborder_id>/inspection/', InspectionAPIView.as_view(), name='suborder-inspection'),  # ตรวจรับ + QR Code
    path('orders/<str:order_id>/handover/', HandoverAPIView.as_view(), name='order-handover'),  # จ่ายของ
    path('orders/<str:order_id>/close/', CloseOrderAPIView.as_view(), name='order-close'),  # ปิดงาน
    path('orders/<str:order_id>/print/', print_order_view, name='order-print'),  # พิมพ์ใบสั่งซื้อ
    
    path('create-order/', create_order_view, name='create-order'),
    path('my-orders/', my_orders_view, name='my-orders'),  # หน้ารายการสั่งซื้อของ User
    path('stats/', StatsAPIView.as_view(), name='dashboard-stats'),
    
    # Scan QR Code
    path('scan/<str:suborder_id>/', scan_suborder_view, name='scan-suborder'),  # หน้าสแกน QR
    path('scan/<str:suborder_id>/data/', ScanSuborderDataAPIView.as_view(), name='scan-suborder-data'),  # API ดึงข้อมูล
    
    # ===================================================================
    # Reports & Budget Summary APIs - รายงานสรุป
    # ===================================================================
    path('budget-summary/', BudgetSummaryAPIView.as_view(), name='budget-summary'),  # API สรุปงบประมาณ
    path('staff/reports/', staff_reports_view, name='staff-reports'),  # หน้ารายงานสรุป
    path('orders/<str:order_id>/export-csv/', ExportOrderCSVAPIView.as_view(), name='order-export-csv'),  # Export CSV
    
    # ===================================================================
    # Order Edit History - ประวัติการแก้ไขใบสั่งซื้อ
    # ===================================================================
    path('order-edit-history/', OrderEditHistoryAPIView.as_view(), name='order-edit-history-list'),  # API ดึงประวัติ
    path('order-edit-history/<int:history_id>/', OrderEditHistoryDetailAPIView.as_view(), name='order-edit-history-detail'),  # API รายละเอียด
    path('staff/order-history/', order_edit_history_view, name='order-edit-history-page'),  # หน้าประวัติการแก้ไข
]