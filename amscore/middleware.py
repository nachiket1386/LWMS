from django.utils.deprecation import MiddlewareMixin
from amscore.apps.core.models import Company


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.company = None
        company_id = request.session.get('company_id')
        
        if company_id:
            try:
                request.company = Company.objects.get(id=company_id, is_active=True)
            except Company.DoesNotExist:
                request.session.pop('company_id', None)
        
        if not request.company:
            host = request.get_host().split(':')[0]
            subdomain = host.split('.')[0]
            
            if subdomain != 'localhost' and subdomain != '127':
                try:
                    request.company = Company.objects.get(slug=subdomain, is_active=True)
                except Company.DoesNotExist:
                    pass
        
        return None
