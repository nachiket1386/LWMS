from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from companies.models import Company


class UploadBatch(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='upload_batches')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.file_name} - {self.status}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LEAVE', 'Leave'),
        ('PENDING', 'Pending'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='attendance_records')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    attendance_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    cost_center = models.CharField(max_length=100, blank=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(24)])
    supervisor_approved = models.BooleanField(default=False)
    supervisor_remarks = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_attendance')
    upload_batch = models.ForeignKey(UploadBatch, on_delete=models.SET_NULL, null=True, blank=True)
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'employee', 'attendance_date')
        ordering = ['-attendance_date']
        indexes = [
            models.Index(fields=['company', 'attendance_date']),
            models.Index(fields=['employee', 'attendance_date']),
        ]

    def __str__(self):
        return f"{self.employee.username} - {self.attendance_date}"


class ManDays(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='mandays_records')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mandays_records')
    project = models.CharField(max_length=255)
    mandays_date = models.DateField(db_index=True)
    days_allocated = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    days_utilized = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    supervisor_approved = models.BooleanField(default=False)
    supervisor_remarks = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_mandays')
    upload_batch = models.ForeignKey(UploadBatch, on_delete=models.SET_NULL, null=True, blank=True)
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'employee', 'project', 'mandays_date')
        ordering = ['-mandays_date']
        indexes = [
            models.Index(fields=['company', 'mandays_date']),
            models.Index(fields=['employee', 'mandays_date']),
        ]

    def __str__(self):
        return f"{self.employee.username} - {self.project} - {self.mandays_date}"


class Overtime(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='overtime_records')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='overtime_records')
    overtime_date = models.DateField(db_index=True)
    hours = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(24)])
    reason = models.TextField(blank=True)
    supervisor_approved = models.BooleanField(default=False)
    supervisor_remarks = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_overtime')
    upload_batch = models.ForeignKey(UploadBatch, on_delete=models.SET_NULL, null=True, blank=True)
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'employee', 'overtime_date')
        ordering = ['-overtime_date']
        indexes = [
            models.Index(fields=['company', 'overtime_date']),
            models.Index(fields=['employee', 'overtime_date']),
        ]

    def __str__(self):
        return f"{self.employee.username} - {self.overtime_date} - {self.hours}h"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('EXPORT', 'Export'),
        ('APPROVE', 'Approve'),
    ]

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='audit_logs')
    record_type = models.CharField(max_length=50)
    record_id = models.IntegerField()
    changes = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['company', 'timestamp']),
            models.Index(fields=['record_type', 'record_id']),
        ]

    def __str__(self):
        return f"{self.action} - {self.record_type} - {self.timestamp}"
