from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = []

    def test_func(self):
        return self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this page.")
        raise PermissionDenied


class RootRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['ROOT']


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['ROOT', 'ADMIN']


class User1RequiredMixin(RoleRequiredMixin):
    allowed_roles = ['ROOT', 'ADMIN', 'USER1']


class TenantAccessMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        company_id = kwargs.get('company_id') or self.request.GET.get('company_id')
        
        if company_id:
            if not request.user.is_root():
                has_access = False
                
                if hasattr(request.user, 'current_tenant') and request.user.current_tenant:
                    if str(request.user.current_tenant.id) == str(company_id):
                        has_access = True
                
                if request.user.company and str(request.user.company.id) == str(company_id):
                    has_access = True
                
                if request.user.companies.filter(id=company_id).exists():
                    has_access = True
                
                if not has_access:
                    messages.error(request, "You don't have access to this company's data.")
                    raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)
