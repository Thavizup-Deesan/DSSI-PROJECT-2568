from rest_framework import serializers
from .models import User, Project, ProjectParticipant, PurchaseOrder, OrderItem, PartialReceive, PartialReceiveItem, Inspection, Payment


# =================================================================
# User Serializer
# =================================================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'email', 'full_name', 'role', 'is_admin', 'is_officer', 'is_head', 'department', 'created_at']


# =================================================================
# Project Serializer
# =================================================================
class ProjectSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Project
        fields = ['project_id', 'created_by', 'created_by_name', 'project_name', 
                  'ubufmis_code', 'project_code', 'responsible_person', 
                  'budget_remuneration', 'budget_operations', 'budget_materials', 'budget_equipment',
                  'total_budget', 'reserved_budget', 'remaining_budget', 'start_date', 'end_date', 'status', 'created_at']


# =================================================================
# ProjectParticipant Serializer
# =================================================================
class ProjectParticipantSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    role_in_project_display = serializers.CharField(source='get_role_in_project_display', read_only=True)
    
    class Meta:
        model = ProjectParticipant
        fields = ['project', 'user', 'user_email', 'user_full_name', 'role_in_project', 'role_in_project_display']


# =================================================================
# OrderItem Serializer
# =================================================================
class OrderItemSerializer(serializers.ModelSerializer):
    remaining_quantity = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['item_id', 'order', 'material_name', 'quantity', 'unit', 'unit_price', 'total_price', 'remaining_quantity']

    def get_remaining_quantity(self, obj):
        # Calculate received quantity from PartialReceiveItem
        # Exclude items that were rejected in inspection
        received = sum(
            item.quantity for item in obj.received_records.exclude(
                partial_receive__inspection__result='Reject'
            )
        )
        return max(0, obj.quantity - received)


# =================================================================
# PartialReceive Serializer
# =================================================================
class PartialReceiveItemSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='order_item.material_name', read_only=True)
    unit = serializers.CharField(source='order_item.unit', read_only=True)

    class Meta:
        model = PartialReceiveItem
        fields = ['item_id', 'material_name', 'quantity', 'unit']

class PartialReceiveSerializer(serializers.ModelSerializer):
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    committee_name = serializers.SerializerMethodField()
    order_no = serializers.CharField(source='order.order_no', read_only=True)
    items = PartialReceiveItemSerializer(source='receive_items', many=True, read_only=True)
    inspection_result = serializers.CharField(source='inspection.result', read_only=True)
    
    class Meta:
        model = PartialReceive
        fields = ['receive_id', 'order', 'order_no', 'receipt_no', 'receipt_file_path', 'received_date', 'recorded_by', 'recorded_by_name', 'committee', 'committee_name', 'status', 'items', 'inspection_result']

    def get_committee_name(self, obj):
        return obj.committee.full_name if obj.committee else None


# =================================================================
# PurchaseOrder Serializer
# =================================================================
class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    requester_name = serializers.CharField(source='requester.full_name', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    project_code = serializers.CharField(source='project.project_code', read_only=True)   # Added
    ubufmis_code = serializers.CharField(source='project.ubufmis_code', read_only=True)   # Added
    
    inspection_committee_email = serializers.SerializerMethodField()
    inspection_committee_full_name = serializers.SerializerMethodField()
    
    # New field for assigning committee via email
    committee_email = serializers.EmailField(write_only=True, required=False)

    partial_receives = PartialReceiveSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = ['order_id', 'project', 'project_name', 'project_code', 'ubufmis_code', 'requester', 'requester_name', 'order_no', 
                  'total_amount', 'status', 'items', 'created_at', 'inspection_committee', 
                  'inspection_committee_email', 'inspection_committee_full_name', 
                  'inspection_committee_name', 'rejection_reason', 'partial_receives',
                  'committee_email']

    def get_inspection_committee_email(self, obj):
        return obj.inspection_committee.email if obj.inspection_committee else None

    def get_inspection_committee_full_name(self, obj):
        return obj.inspection_committee.full_name if obj.inspection_committee else None

    def update(self, instance, validated_data):
        committee_email = validated_data.pop('committee_email', None)
        if committee_email:
            # Logic: Find or Create User -> Assign Committee Role -> Link to PO
            user, created = User.objects.get_or_create(
                email=committee_email,
                defaults={
                    'username': committee_email.split('@')[0], # Default username
                    'full_name': committee_email.split('@')[0], # Default name (can be updated later)
                    'role': 'Inspector'
                }
            )
            # Ensure Committee Role if currently just a User
            if user.role == 'Requester':
                user.role = 'Inspector'
                user.save()
            
            instance.inspection_committee = user
            # Also update the text field for display consistency
            instance.inspection_committee_name = user.full_name
        
        return super().update(instance, validated_data)


# =================================================================
# Inspection Serializer
# =================================================================
class InspectionSerializer(serializers.ModelSerializer):
    committee_name = serializers.CharField(source='committee.full_name', read_only=True)
    receipt_no = serializers.CharField(source='partial_receive.receipt_no', read_only=True)
    
    class Meta:
        model = Inspection
        fields = ['inspection_id', 'partial_receive', 'receipt_no', 'committee', 'committee_name', 
                  'inspection_date', 'result', 'comment']


# =================================================================
# Payment Serializer
# =================================================================
class PaymentSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['payment_id', 'order', 'paid_amount', 'payment_date', 'approved_by', 'approved_by_name', 'notes']