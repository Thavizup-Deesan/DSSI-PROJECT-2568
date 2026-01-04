"""
Authorization utilities for POTMS
Verify user permissions and access rights
"""
from backend.firebase_config import db


def verify_staff_project_access(staff_id, project_id):
    """
    Verify that staff has access to a specific project
    
    Args:
        staff_id: Staff user ID
        project_id: Project ID to check access for
    
    Returns:
        bool: True if staff has access, False otherwise
    """
    try:
        # Check project_assignments collection
        assignments = db.collection('project_assignments')\
            .where('user_id', '==', staff_id)\
            .where('project_id', '==', project_id)\
            .limit(1)\
            .stream()
        
        # If any assignment found, staff has access
        for _ in assignments:
            return True
        
        return False
    except Exception as e:
        print(f"Error checking project access: {str(e)}")
        return False


def verify_order_ownership(user_id, order_id):
    """
    Verify that user owns the order
    
    Args:
        user_id: User ID
        order_id: Order ID
    
    Returns:
        bool: True if user owns the order
    """
    try:
        order_doc = db.collection('orders').document(order_id).get()
        if not order_doc.exists:
            return False
        
        order_data = order_doc.to_dict()
        return order_data.get('requester_id') == user_id
    except Exception as e:
        print(f"Error checking order ownership: {str(e)}")
        return False
