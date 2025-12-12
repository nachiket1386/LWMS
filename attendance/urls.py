from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('dashboard/', views.attendance_dashboard, name='dashboard'),

    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/create/', views.attendance_create, name='attendance_create'),
    path('attendance/<int:pk>/edit/', views.attendance_edit, name='attendance_edit'),
    path('attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
    path('attendance/export/', views.attendance_export, name='attendance_export'),
    path('attendance/bulk-approve/', views.attendance_bulk_approve, name='attendance_bulk_approve'),

    path('mandays/', views.mandays_list, name='mandays_list'),
    path('mandays/create/', views.mandays_create, name='mandays_create'),
    path('mandays/<int:pk>/edit/', views.mandays_edit, name='mandays_edit'),
    path('mandays/<int:pk>/delete/', views.mandays_delete, name='mandays_delete'),
    path('mandays/export/', views.mandays_export, name='mandays_export'),
    path('mandays/by-project/', views.mandays_by_project, name='mandays_by_project'),

    path('overtime/', views.overtime_list, name='overtime_list'),
    path('overtime/create/', views.overtime_create, name='overtime_create'),
    path('overtime/<int:pk>/edit/', views.overtime_edit, name='overtime_edit'),
    path('overtime/<int:pk>/delete/', views.overtime_delete, name='overtime_delete'),
    path('overtime/export/', views.overtime_export, name='overtime_export'),
    path('overtime/by-employee/', views.overtime_by_employee, name='overtime_by_employee'),
]
