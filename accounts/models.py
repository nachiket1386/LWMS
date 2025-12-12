from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ROOT = 'ROOT', 'Root'
        ADMIN = 'ADMIN', 'Admin'
        USER1 = 'USER1', 'User1'

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER1
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    companies = models.ManyToManyField(
        'companies.Company',
        related_name='all_users',
        blank=True
    )
    is_impersonating = models.BooleanField(default=False)
    impersonated_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='impersonations'
    )
    current_tenant = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_users'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username

    def is_root(self):
        return self.role == self.Role.ROOT

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_user1(self):
        return self.role == self.Role.USER1

    def can_impersonate(self):
        return self.is_root()

    def has_access_to_company(self, company):
        if self.is_root():
            return True
        if self.company == company:
            return True
        return self.companies.filter(id=company.id).exists()
