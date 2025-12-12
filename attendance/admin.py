from django.contrib import admin
from .models import Attendance, ManDays, Overtime, UploadBatch, AuditLog


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'company', 'attendance_date', 'status', 'supervisor_approved', 'created_at')
    list_filter = ('status', 'supervisor_approved', 'company', 'attendance_date')
    search_fields = ('employee__username', 'cost_center')
    readonly_fields = ('created_at', 'updated_at', 'version')
    date_hierarchy = 'attendance_date'


@admin.register(ManDays)
class ManDaysAdmin(admin.ModelAdmin):
    list_display = ('employee', 'company', 'project', 'mandays_date', 'days_allocated', 'days_utilized', 'supervisor_approved')
    list_filter = ('supervisor_approved', 'company', 'mandays_date', 'project')
    search_fields = ('employee__username', 'project')
    readonly_fields = ('created_at', 'updated_at', 'version')
    date_hierarchy = 'mandays_date'


@admin.register(Overtime)
class OvertimeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'company', 'overtime_date', 'hours', 'supervisor_approved', 'created_at')
    list_filter = ('supervisor_approved', 'company', 'overtime_date')
    search_fields = ('employee__username', 'reason')
    readonly_fields = ('created_at', 'updated_at', 'version')
    date_hierarchy = 'overtime_date'


@admin.register(UploadBatch)
class UploadBatchAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'company', 'uploaded_by', 'status', 'total_records', 'processed_records', 'created_at')
    list_filter = ('status', 'company', 'created_at')
    search_fields = ('file_name', 'uploaded_by__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'record_type', 'record_id', 'user', 'company', 'timestamp')
    list_filter = ('action', 'record_type', 'company', 'timestamp')
    search_fields = ('user__username', 'record_type')
    readonly_fields = ('action', 'user', 'company', 'record_type', 'record_id', 'changes', 'timestamp')
    date_hierarchy = 'timestamp'
