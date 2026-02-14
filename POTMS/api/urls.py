from django.urls import path
from . import views

urlpatterns = [
    # =================================================================
    # Auth APIs — Google OAuth 2.0 (via django-allauth)
    # =================================================================
    path('auth/logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('auth/me/', views.CurrentUserAPIView.as_view(), name='current_user'),

    # =================================================================
    # Project APIs
    # Activity: นำเข้าโครงการ → ตรวจสอบ → ระบุผู้เข้าร่วม → เริ่ม PRJ
    # =================================================================
    path('projects/', views.ProjectAPIView.as_view(), name='project_list'),
    path('projects/<int:project_id>/', views.ProjectDetailAPIView.as_view(), name='project_detail'),
    path('projects/<int:project_id>/start/', views.ProjectStartAPIView.as_view(), name='project_start'),
    path('projects/<int:project_id>/close/', views.ProjectCloseAPIView.as_view(), name='project_close'),

    # =================================================================
    # Participant APIs
    # Activity: ระบุผู้เข้าร่วมโครงการ
    # =================================================================
    path('projects/<int:project_id>/participants/', views.ProjectParticipantAPIView.as_view(), name='participants'),
    path('projects/<int:project_id>/participants/<int:user_id>/', views.ParticipantDeleteAPIView.as_view(), name='participant_delete'),

    # =================================================================
    # Purchase Order APIs
    # Activity: สร้างใบสั่งซื้อ → Check Budget → Reserve → Export → Approve
    # =================================================================
    path('orders/', views.PurchaseOrderAPIView.as_view(), name='order_list'),
    path('orders/<int:order_id>/', views.PurchaseOrderDetailAPIView.as_view(), name='order_detail'),
    path('orders/<int:order_id>/submit/', views.OrderSubmitAPIView.as_view(), name='order_submit'),
    path('orders/<int:order_id>/export/', views.OrderExportAPIView.as_view(), name='order_export'),
    path('orders/<int:order_id>/approve/', views.OrderApprovalRecordAPIView.as_view(), name='order_approve'),
    path('orders/<int:order_id>/process/', views.OrderProcessAPIView.as_view(), name='order_process'),

    # =================================================================
    # Partial Receive APIs
    # Activity: สร้างใบสั่งซื้อย่อย พร้อมแนบใบเสร็จ
    # =================================================================
    path('partial-receives/', views.PartialReceiveAPIView.as_view(), name='partial_receives'),
    path('partial-receives/<int:receive_id>/', views.PartialReceiveDetailAPIView.as_view(), name='partial_receive_detail'),

    # =================================================================
    # Inspection APIs
    # Activity: กก.ตรวจรับ: ตรวจนับจำนวน/คุณภาพ
    # =================================================================
    path('inspections/', views.InspectionAPIView.as_view(), name='inspections'),

    # =================================================================
    # Payment APIs
    # Activity: ตั้งเบิกจ่ายเงิน
    # =================================================================
    path('payments/', views.PaymentAPIView.as_view(), name='payments'),
    path('payments/<int:payment_id>/confirm/', views.PaymentConfirmAPIView.as_view(), name='payment_confirm'),

    # =================================================================
    # Admin Management APIs
    # =================================================================
    path('admins/', views.AdminListAPIView.as_view(), name='admin_list'),
    path('admins/<int:user_id>/', views.AdminRemoveAPIView.as_view(), name='admin_remove'),

    # =================================================================
    # User Management APIs
    # =================================================================
    path('users/', views.UserListAPIView.as_view(), name='user_list'),
    path('users/<int:user_id>/', views.UserDetailAPIView.as_view(), name='user_detail'),

    # =================================================================
    # Dashboard Stats
    # =================================================================
    path('stats/', views.StatsAPIView.as_view(), name='stats'),
]

# =================================================================
# Page Routes — Template rendering
# =================================================================
page_urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login_page, name='login_page'),
    path('auth/post-login/', views.allauth_post_login_view, name='allauth_post_login'),
    path('officer/dashboard/', views.officer_dashboard_page, name='officer_dashboard'),
    path('user/dashboard/', views.user_dashboard_page, name='user_dashboard'),
    path('projects/', views.project_list_page, name='project_list_page'),
    path('projects/participants/', views.participant_setup_page, name='participant_setup'),
    path('orders/create/', views.create_order_page, name='create_order'),
    path('orders/edit/', views.edit_order_page, name='edit_order'),
    path('orders/my/', views.my_orders_page, name='my_orders'),
    path('orders/detail/', views.order_detail_page, name='order_detail_page'),
    path('officer/orders/', views.officer_orders_page, name='officer_orders'),
    path('partial-receives/', views.partial_receive_page, name='partial_receive'),
    path('inspections/', views.inspection_page, name='inspection'),
    path('payments/', views.payment_page, name='payment'),
    path('projects/closure/', views.project_closure_page, name='project_closure'),
    path('officer/users/', views.user_management_page, name='user_management'),
    path('officer/admins/', views.admin_management_page, name='admin_management'),
    path('orders/inspect-landing/', views.inspector_landing_page, name='inspector_landing'),
]
