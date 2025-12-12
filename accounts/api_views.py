from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import User
from companies.models import Company
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordResetSerializer, CompanySerializer
)
from .permissions import IsRootUser, IsAdminUser


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        if not self.request.user.is_root():
            if self.request.user.company:
                queryset = queryset.filter(company=self.request.user.company)
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )
        
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        
        company_id = self.request.query_params.get('company', None)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        return queryset.select_related('company')
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        
        if not request.user.is_root() and user.company != request.user.company:
            return Response(
                {'error': "You don't have permission to reset this user's password."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password reset successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        
        if not request.user.is_root() and user.company != request.user.company:
            return Response(
                {'error': "You don't have permission to deactivate this user."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.is_active = not user.is_active
        user.save()
        
        status_text = 'activated' if user.is_active else 'deactivated'
        return Response({'message': f'User {status_text} successfully.'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsRootUser])
    def impersonate(self, request, pk=None):
        target_user = self.get_object()
        
        if target_user.is_root():
            return Response(
                {'error': 'You cannot impersonate a ROOT user.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        request.session['_impersonate'] = {
            'original_user_id': request.user.id,
            'impersonated_user_id': target_user.id,
        }
        
        return Response({
            'message': f'Now impersonating {target_user.username}',
            'impersonated_user': UserSerializer(target_user).data
        })


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.filter(is_active=True)
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Company.objects.filter(is_active=True)
        
        if not self.request.user.is_root():
            if self.request.user.company:
                queryset = queryset.filter(id=self.request.user.company.id)
        
        return queryset
