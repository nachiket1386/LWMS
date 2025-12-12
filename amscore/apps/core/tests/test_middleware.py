import pytest
from django.test import RequestFactory
from amscore.middleware import TenantMiddleware
from amscore.apps.core.models import Company

pytestmark = pytest.mark.django_db


class TestTenantMiddleware:
    def setup_method(self):
        self.middleware = TenantMiddleware(lambda r: None)
        self.factory = RequestFactory()
        self.company = Company.objects.create(
            name='Test Company',
            slug='test'
        )

    def test_middleware_sets_company_from_session(self):
        request = self.factory.get('/')
        request.session = {'company_id': self.company.id}
        
        self.middleware.process_request(request)
        
        assert request.company == self.company

    def test_middleware_handles_invalid_session_company(self):
        request = self.factory.get('/')
        request.session = {'company_id': 99999}
        
        self.middleware.process_request(request)
        
        assert request.company is None
        assert request.session.get('company_id') is None

    def test_middleware_sets_company_none_for_localhost(self):
        request = self.factory.get('/', HTTP_HOST='localhost:8000')
        request.session = {}
        
        self.middleware.process_request(request)
        
        assert request.company is None
