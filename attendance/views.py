from django.shortcuts import render, redirect
from django.views.generic import FormView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import UploadFileForm
from .models import UploadBatch
from .utils import DataIngester

class UploadView(LoginRequiredMixin, FormView):
    template_name = 'attendance/upload.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('attendance:upload_list')

    def form_valid(self, form):
        file = form.cleaned_data['file']
        upload_type = form.cleaned_data['upload_type']
        
        # Check if user has company
        if not self.request.user.company:
            # Handle user without company
            form.add_error(None, "User is not assigned to a company.")
            return self.form_invalid(form)

        ingester = DataIngester(
            file=file,
            upload_type=upload_type,
            company=self.request.user.company,
            user=self.request.user
        )
        ingester.run()
        
        return super().form_valid(form)

class UploadBatchListView(LoginRequiredMixin, ListView):
    model = UploadBatch
    template_name = 'attendance/upload_list.html'
    context_object_name = 'batches'
    ordering = ['-created_at']

    def get_queryset(self):
        if not self.request.user.company:
            return UploadBatch.objects.none()
        return UploadBatch.objects.filter(company=self.request.user.company).order_by('-created_at')

class UploadBatchDetailView(LoginRequiredMixin, DetailView):
    model = UploadBatch
    template_name = 'attendance/upload_detail.html'
    context_object_name = 'batch'

    def get_queryset(self):
         if not self.request.user.company:
            return UploadBatch.objects.none()
         return UploadBatch.objects.filter(company=self.request.user.company)
