from django.contrib import admin
from .models import Company, TenantProfile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Company Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ['company', 'timezone', 'created_at']
    list_filter = ['timezone', 'created_at']
    search_fields = ['company__name']
    fieldsets = (
        ('Company', {
            'fields': ('company',)
        }),
        ('Profile Settings', {
            'fields': ('timezone', 'primary_color', 'logo', 'phone', 'website')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
