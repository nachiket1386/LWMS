from django.core.exceptions import PermissionDenied
from django.contrib import messages


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.is_root():
                if hasattr(request.user, 'current_tenant') and request.user.current_tenant:
                    request.current_tenant = request.user.current_tenant
                elif request.user.company:
                    request.current_tenant = request.user.company
                else:
                    request.current_tenant = None
            else:
                request.current_tenant = request.user.current_tenant if hasattr(request.user, 'current_tenant') else None
        else:
            request.current_tenant = None

        response = self.get_response(request)
        return response
