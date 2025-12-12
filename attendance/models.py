from django.db import models
from accounts.models import User
from companies.models import Company

class TenantAwareManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def with_deleted(self):
        return super().get_queryset()

class TenantAwareModel(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='%(class)ss')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantAwareManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

class Shift(TenantAwareModel):
    name = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        unique_together = ('company', 'name')
        indexes = [
            models.Index(fields=['company', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.company.name})"

class CostCenter(TenantAwareModel):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('company', 'code')
        indexes = [
            models.Index(fields=['company', 'code']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name} ({self.company.name})"

class Employee(TenantAwareModel):
    employee_id = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    cost_center = models.ForeignKey(CostCenter, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ('company', 'employee_id')
        indexes = [
            models.Index(fields=['company', 'employee_id']),
            models.Index(fields=['company', 'email']),
        ]

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"

class UploadBatch(TenantAwareModel):
    uploader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file_name = models.CharField(max_length=255)
    upload_type = models.CharField(max_length=50) # 'attendance', 'employee', etc.
    status = models.CharField(max_length=20, default='pending') # pending, processing, completed, failed
    row_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    # error_log is handled by UploadError relation

    class Meta:
        indexes = [
            models.Index(fields=['company', 'created_at']),
        ]

class UploadError(models.Model):
    batch = models.ForeignKey(UploadBatch, on_delete=models.CASCADE, related_name='errors')
    row_number = models.IntegerField(null=True, blank=True)
    error_message = models.TextField()
    row_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AttendanceRecord(TenantAwareModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)
    batch = models.ForeignKey(UploadBatch, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')
        indexes = [
            models.Index(fields=['company', 'date']),
            models.Index(fields=['employee', 'date']),
        ]

class MandayRecord(TenantAwareModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='manday_records')
    date = models.DateField()
    manday_value = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    batch = models.ForeignKey(UploadBatch, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')
        indexes = [
             models.Index(fields=['company', 'date']),
        ]

class OvertimeEntry(TenantAwareModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='overtime_entries')
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    batch = models.ForeignKey(UploadBatch, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')
        indexes = [
             models.Index(fields=['company', 'date']),
        ]
