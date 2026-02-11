"""
Authorization utilities for POTMS
Verify user permissions and access rights
"""
# from backend.firebase_config import db  <-- REMOVED


def verify_staff_project_access(staff_id, project_id):
    """
    Verify that staff has access to a specific project (PostgreSQL)
    """
    try:
        from api.models import ProjectAssignment
        return ProjectAssignment.objects.filter(user_id=staff_id, project_id=project_id).exists()
    except Exception as e:
        print(f"Error checking project access: {str(e)}")
        return False


def verify_order_ownership(user_id, order_id):
    """
    Verify that user owns the order (PostgreSQL)
    """
    try:
        from api.models import MainOrder
        order = MainOrder.objects.get(pk=order_id)
        return order.requester_id == user_id
    except MainOrder.DoesNotExist:
        return False
    except Exception as e:
        print(f"Error checking order ownership: {str(e)}")
        return False
