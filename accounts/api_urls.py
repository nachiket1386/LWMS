from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import UserViewSet, CompanyViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'companies', CompanyViewSet, basename='company')

urlpatterns = [
    path('', include(router.urls)),
]
