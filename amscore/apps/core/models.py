from django.db import models
from django.utils import timezone
import pytz


class TenantManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class TenantAwareModel(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='%(class)s_company')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        abstract = True


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, help_text='Subdomain slug for multi-tenancy')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name


class TenantProfile(TenantAwareModel):
    TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]

    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='tenant_profile')
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default='UTC')
    primary_color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Tenant Profile'
        verbose_name_plural = 'Tenant Profiles'

    def __str__(self):
        return f'Profile - {self.company.name}'

    def get_timezone(self):
        return pytz.timezone(self.timezone)
