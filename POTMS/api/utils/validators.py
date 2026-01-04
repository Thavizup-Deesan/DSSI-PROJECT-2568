"""
Security Validators for POTMS
Prevents XSS, injection attacks, and validates business logic
"""
import re
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any


def validate_order_items(items: List[Dict[str, Any]]) -> bool:
    """
    Validate order items for security vulnerabilities
    
    Prevents:
    - XSS attacks (HTML/script injection)
    - Negative quantities/prices
    - Excessively large values
    - Missing required fields
    
    Raises:
        ValueError: If validation fails with specific error message
    
    Returns:
        bool: True if all validations pass
    """
    if not items or not isinstance(items, list):
        raise ValueError('Items must be a non-empty list')
    
    if len(items) > 50:
        raise ValueError('Maximum 50 items allowed per order')
    
    for idx, item in enumerate(items):
        item_num = idx + 1
        
        # Validate item name
        name = str(item.get('item_name', '')).strip()
        if not name or len(name) < 3:
            raise ValueError(f'Item {item_num}: Name must be at least 3 characters')
        
        if len(name) > 200:
            raise ValueError(f'Item {item_num}: Name too long (max 200 characters)')
        
        # Check for HTML/script tags (XSS prevention)
        if re.search(r'<[^>]+>', name):
            raise ValueError(f'Item {item_num}: HTML tags not allowed in item name')
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'javascript:',
            r'onerror=',
            r'onclick=',
            r'<script',
            r'</script',
        ]
        for pattern in suspicious_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                raise ValueError(f'Item {item_num}: Suspicious content detected')
        
        # Validate quantity
        qty_raw = item.get('quantity', item.get('quantity_requested', 0))
        try:
            qty = Decimal(str(qty_raw))
            if qty <= 0:
                raise ValueError(f'Item {item_num}: Quantity must be positive')
            if qty > 999999:
                raise ValueError(f'Item {item_num}: Quantity too large')
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError(f'Item {item_num}: Invalid quantity value')
        
        # Validate unit price
        price_raw = item.get('unit_price', item.get('estimated_unit_price', 0))
        try:
            price = Decimal(str(price_raw))
            if price <= 0:
                raise ValueError(f'Item {item_num}: Price must be positive')
            if price > Decimal('999999999.99'):
                raise ValueError(f'Item {item_num}: Price too large')
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError(f'Item {item_num}: Invalid price value')
        
        # Validate unit
        unit = str(item.get('unit', '')).strip()
        if not unit:
            raise ValueError(f'Item {item_num}: Unit is required')
        if len(unit) > 50:
            raise ValueError(f'Item {item_num}: Unit name too long')
        
        # Check for script in unit field too
        if re.search(r'<[^>]+>', unit):
            raise ValueError(f'Item {item_num}: Invalid characters in unit')
    
    return True


def validate_order_description(description: str) -> str:
    """
    Sanitize and validate order description
    
    Args:
        description: Raw description text
    
    Returns:
        str: Sanitized description
    
    Raises:
        ValueError: If description is invalid
    """
    if not description:
        return ''
    
    desc = str(description).strip()
    
    if len(desc) > 1000:
        raise ValueError('Description too long (max 1000 characters)')
    
    # Remove HTML tags
    desc = re.sub(r'<[^>]+>', '', desc)
    
    return desc


def validate_order_title(title: str) -> str:
    """
    Validate order title
    
    Args:
        title: Order title
    
    Returns:
        str: Validated title
    
    Raises:
        ValueError: If title is invalid
    """
    if not title:
        raise ValueError('Order title is required')
    
    title = str(title).strip()
    
    if len(title) < 5:
        raise ValueError('Title too short (min 5 characters)')
    
    if len(title) > 200:
        raise ValueError('Title too long (max 200 characters)')
    
    # Remove HTML
    if re.search(r'<[^>]+>', title):
        raise ValueError('HTML tags not allowed in title')
    
    return title


# Status transition validation
VALID_TRANSITIONS = {
    'Draft': ['Pending', 'Cancelled'],
    'Pending': ['WaitingBossApproval', 'CorrectionNeeded', 'Rejected'],
    'WaitingBossApproval': ['Approved', 'Rejected'],
    'Approved': ['SentToProcurement'],
    'SentToProcurement': ['ReceivedFromProcurement'],
    'ReceivedFromProcurement': ['WaitingInspection'],
    'WaitingInspection': ['Inspected'],
    'Inspected': ['Received'],
    'Received': ['Closed'],
    'CorrectionNeeded': ['Draft'],
    'Rejected': [],  # Terminal state
    'Cancelled': [],  # Terminal state
    'Closed': [],  # Terminal state
}


def validate_status_transition(current_status: str, new_status: str) -> bool:
    """
    Validate that status transition is allowed
    
    Prevents users from skipping workflow steps
    
    Args:
        current_status: Current order status
        new_status: Desired new status
    
    Returns:
        bool: True if transition is valid
    
    Raises:
        ValueError: If transition is not allowed
    """
    if current_status not in VALID_TRANSITIONS:
        raise ValueError(f'Invalid current status: {current_status}')
    
    allowed = VALID_TRANSITIONS[current_status]
    
    if new_status not in allowed:
        raise ValueError(
            f'Invalid status transition: {current_status} → {new_status}. '
            f'Allowed transitions: {", ".join(allowed) if allowed else "None (terminal state)"}'
        )
    
    return True


def validate_budget_amount(amount: Any, field_name: str = 'amount') -> Decimal:
    """
    Validate budget/price amount
    
    Args:
        amount: Amount to validate
        field_name: Name of field for error messages
    
    Returns:
        Decimal: Validated amount
    
    Raises:
        ValueError: If amount is invalid
    """
    try:
        decimal_amount = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f'{field_name} must be a valid number')
    
    if decimal_amount < 0:
        raise ValueError(f'{field_name} cannot be negative')
    
    if decimal_amount > Decimal('9999999999.99'):
        raise ValueError(f'{field_name} is too large')
    
    # Check decimal places (max 2)
    if decimal_amount.as_tuple().exponent < -2:
        raise ValueError(f'{field_name} can have at most 2 decimal places')
    
    return decimal_amount
