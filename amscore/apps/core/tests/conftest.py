import pytest
from django.contrib.auth.models import User
from amscore.apps.core.models import Company, TenantProfile


@pytest.fixture
def company():
    return Company.objects.create(
        name='Test Company',
        slug='test-company',
        description='A test company for testing'
    )


@pytest.fixture
def tenant_profile(company):
    return TenantProfile.objects.create(
        company=company,
        timezone='UTC',
        phone='+1234567890',
        website='https://testcompany.com'
    )


@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_user(user, rf):
    request = rf.get('/')
    request.user = user
    return request
