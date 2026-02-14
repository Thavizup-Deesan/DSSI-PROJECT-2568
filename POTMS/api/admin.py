from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import User, Project, ProjectParticipant, PurchaseOrder, OrderItem, PartialReceive, Inspection, Payment

# =================================================================
# User Admin
# =================================================================
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # ใช้ ModelForm ธรรมดาได้เลย เพราะมี field role แล้ว
    
    list_display = ('user_id', 'email', 'full_name', 'department', 'role', 'is_admin', 'is_officer', 'created_at', 'delete_button')
    
    # ใช้ built-in filter ของ Django สำหรับ field 'role' ได้เลย
    list_filter = ('role', 'created_at')
    search_fields = ('email', 'full_name', 'department')
    
    # Dropdown เปลี่ยน Role ได้ทันที
    list_editable = ('role',)
    
    def save_model(self, request, obj, form, change):
        """Ensure flags are synced when saving via Admin"""
        obj.save() # This triggers the sync logic in models.py
    fieldsets = (
        ('ข้อมูลพื้นฐาน', {
            'fields': ('user_id', 'email', 'full_name', 'department', 'created_at'),
            'classes': ('wide',)
        }),
        ('บทบาท (Role)', {
            'fields': ('role',), 
            'description': 'เลือกบทบาทของผู้ใช้ (ระบบจะตั้งค่าสิทธิ์ให้ระโนมัติ)',
            'classes': ('wide',)
        }),
        ('สิทธิ์การใช้งาน (System Flags)', {
            'fields': ('is_admin', 'is_officer', 'is_head'),
            'classes': ('collapse',),
            'description': 'ค่าเหล่านี้จะถูกตั้งอัตโนมัติตาม Role ด้านบน',
        }),
    )
    readonly_fields = ('user_id', 'created_at', 'is_admin', 'is_officer', 'is_head')
    actions = ['make_admin', 'make_officer', 'make_user']

    def delete_button(self, obj):
        return format_html('<a class="button" href="/admin/api/user/{}/delete/" style="color:red;">ลบ</a>', obj.pk)
    delete_button.short_description = 'ลบ'
    delete_button.allow_tags = True

    def make_admin(self, request, queryset):
        # Update role -> save() logic in model will handle booleans
        # But update() command bypasses save(). So we need to set both or loop.
        # Loop is safer for consistency with save() logic, but slower. 
        # For bulk update with signals/save logic, better to loop or update all fields.
        rows = queryset.update(role='Admin', is_admin=True, is_officer=False, is_head=False)
        self.message_user(request, f'เปลี่ยน {rows} ผู้ใช้เป็น Admin สำเร็จ')
    make_admin.short_description = '✅ เปลี่ยนเป็น Admin'

    def make_officer(self, request, queryset):
        rows = queryset.update(role='Officer', is_admin=False, is_officer=True, is_head=False)
        self.message_user(request, f'เปลี่ยน {rows} ผู้ใช้เป็น Officer สำเร็จ')
    make_officer.short_description = '✅ เปลี่ยนเป็น Officer'

    def make_user(self, request, queryset):
        rows = queryset.update(role='User', is_admin=False, is_officer=False, is_head=False)
        self.message_user(request, f'เปลี่ยน {rows} ผู้ใช้เป็น User สำเร็จ')
    make_user.short_description = '✅ เปลี่ยนเป็น User'

# ... (Admin อื่นๆ ด้านล่างคงเดิม) ...