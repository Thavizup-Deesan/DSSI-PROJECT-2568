"""
Audit Trail System for POTMS
Logs all important actions for security and compliance
"""
import datetime
# from backend.firebase_config import db  <-- REMOVED


def log_audit(action, user_id, resource_type, resource_id, details=None, ip_address=None):
    """
    Log audit trail for important actions
    """
    try:
        audit_log = {
            'action': action,
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details or {},
            'ip_address': ip_address,
            'timestamp': datetime.datetime.now(),
        }
        
        # Save to Firestore -> REMOVED
        # update_time, doc_ref = db.collection('audit_logs').add(audit_log)
        
        # Temporary: Print to console
        print(f"AUDIT LOG: {audit_log}")
        
        return "log_id_placeholder"
    except Exception as e:
        # Don't fail the main operation if logging fails
        print(f"Audit log error: {str(e)}")
        return None


def get_client_ip(request):
    """
    Get client IP address from request
    
    Args:
        request: Django request object
    
    Returns:
        str: IP address
    """
    # Check for proxy headers first
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Common audit actions
AUDIT_ACTIONS = {
    # Order actions
    'ORDER_CREATED': 'order_created',
    'ORDER_SUBMITTED': 'order_submitted',
    'ORDER_APPROVED': 'order_approved',
    'ORDER_REJECTED': 'order_rejected',
    'ORDER_BOSS_APPROVED': 'order_boss_approved',
    'ORDER_SENT_PROCUREMENT': 'order_sent_to_procurement',
    'ORDER_INSPECTED': 'order_inspected',
    'ORDER_HANDED_OVER': 'order_handed_over',
    'ORDER_CLOSED': 'order_closed',
    
    # Budget actions
    'BUDGET_RESERVED': 'budget_reserved',
    'BUDGET_RELEASED': 'budget_released',
    'BUDGET_SPENT': 'budget_spent',
    
    # User actions
    'USER_LOGIN': 'user_login',
    'USER_LOGOUT': 'user_logout',
    'USER_CREATED': 'user_created',
    
    # Project actions
    'PROJECT_ASSIGNED': 'project_assigned',
    'PROJECT_UPDATED': 'project_updated',
}
