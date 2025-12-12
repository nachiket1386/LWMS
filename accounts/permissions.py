from rest_framework import permissions


class IsRootUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_root()


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_root() or request.user.is_admin()
        )


class IsUser1(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_root() or request.user.is_admin() or request.user.is_user1()
        )


class HasTenantAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_root():
            return True
        
        if hasattr(obj, 'company'):
            return request.user.has_access_to_company(obj.company)
        
        return False
