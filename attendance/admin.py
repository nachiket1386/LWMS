from django.contrib import admin
from .models import Shift, CostCenter, Employee, UploadBatch, UploadError, AttendanceRecord, MandayRecord, OvertimeEntry
import csv
from django.http import HttpResponse

def export_as_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response

export_as_csv.short_description = "Export Selected"

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'company')
    list_filter = ('company',)
    actions = [export_as_csv]

@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'company')
    list_filter = ('company',)
    actions = [export_as_csv]

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'email', 'company')
    list_filter = ('company', 'department', 'cost_center')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email')
    actions = [export_as_csv]

class UploadErrorInline(admin.TabularInline):
    model = UploadError
    extra = 0
    readonly_fields = ('row_number', 'error_message', 'row_data')

@admin.register(UploadBatch)
class UploadBatchAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'upload_type', 'status', 'row_count', 'success_count', 'error_count', 'company', 'created_at')
    list_filter = ('company', 'upload_type', 'status', 'created_at')
    inlines = [UploadErrorInline]
    actions = [export_as_csv]

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'shift', 'company')
    list_filter = ('company', 'date', 'shift')
    search_fields = ('employee__employee_id', 'employee__first_name', 'employee__last_name')
    actions = [export_as_csv]

@admin.register(MandayRecord)
class MandayRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'manday_value', 'company')
    list_filter = ('company', 'date')
    actions = [export_as_csv]

@admin.register(OvertimeEntry)
class OvertimeEntryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'hours', 'company')
    list_filter = ('company', 'date')
    actions = [export_as_csv]
