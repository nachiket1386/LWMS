from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You don't have permission to access this page.")
            raise PermissionDenied
        return _wrapped_view
    return decorator


def root_required(view_func):
    return role_required('ROOT')(view_func)


def admin_required(view_func):
    return role_required('ROOT', 'ADMIN')(view_func)


def user1_required(view_func):
    return role_required('ROOT', 'ADMIN', 'USER1')(view_func)


def tenant_access_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        company_id = kwargs.get('company_id') or request.GET.get('company_id')
        
        if not company_id:
            return view_func(request, *args, **kwargs)
        
        if request.user.is_root():
            return view_func(request, *args, **kwargs)
        
        if hasattr(request.user, 'current_tenant') and request.user.current_tenant:
            if str(request.user.current_tenant.id) == str(company_id):
                return view_func(request, *args, **kwargs)
        
        if request.user.company and str(request.user.company.id) == str(company_id):
            return view_func(request, *args, **kwargs)
        
        if request.user.companies.filter(id=company_id).exists():
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "You don't have access to this company's data.")
        raise PermissionDenied
    
    return _wrapped_view
