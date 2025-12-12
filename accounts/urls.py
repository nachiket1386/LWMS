from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/deactivate/', views.UserDeactivateView.as_view(), name='user_deactivate'),
    path('users/<int:user_id>/reset-password/', views.user_reset_password, name='user_reset_password'),
    
    path('impersonate/<int:user_id>/', views.impersonate_user, name='impersonate_user'),
    path('stop-impersonation/', views.stop_impersonation, name='stop_impersonation'),
    
    path('assume-tenant/<int:company_id>/', views.assume_tenant, name='assume_tenant'),
    path('clear-tenant/', views.clear_tenant, name='clear_tenant'),
]
