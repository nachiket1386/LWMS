from django.urls import path
from .views import UploadView, UploadBatchListView, UploadBatchDetailView

app_name = 'attendance'

urlpatterns = [
    path('upload/', UploadView.as_view(), name='upload'),
    path('uploads/', UploadBatchListView.as_view(), name='upload_list'),
    path('uploads/<int:pk>/', UploadBatchDetailView.as_view(), name='upload_detail'),
]
