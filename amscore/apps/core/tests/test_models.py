import pytest
from amscore.apps.core.models import Company, TenantProfile

pytestmark = pytest.mark.django_db


class TestCompanyModel:
    def test_company_creation(self):
        company = Company.objects.create(
            name='Test Company',
            slug='test-company'
        )
        assert company.id is not None
        assert company.name == 'Test Company'
        assert company.is_active is True

    def test_company_str_representation(self, company):
        assert str(company) == 'Test Company'

    def test_company_slug_uniqueness(self, company):
        with pytest.raises(Exception):
            Company.objects.create(
                name='Another Company',
                slug='test-company'
            )


class TestTenantProfileModel:
    def test_tenant_profile_creation(self, tenant_profile):
        assert tenant_profile.id is not None
        assert tenant_profile.timezone == 'UTC'
        assert tenant_profile.company.name == 'Test Company'

    def test_tenant_profile_str_representation(self, tenant_profile):
        assert 'Test Company' in str(tenant_profile)

    def test_get_timezone(self, tenant_profile):
        tz = tenant_profile.get_timezone()
        assert tz.zone == 'UTC'
