from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'company', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff', 'company']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'company', 'companies', 'is_impersonating', 'impersonated_by', 'current_tenant')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('email', 'role', 'company', 'companies')
        }),
    )
    
    filter_horizontal = ['groups', 'user_permissions', 'companies']
