from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import User
from companies.models import Company
from .decorators import root_required, admin_required
from .mixins import RootRequiredMixin, AdminRequiredMixin
from .forms import UserLoginForm, UserCreationForm, UserUpdateForm, PasswordResetRequestForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'accounts:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    username = request.user.username
    logout(request)
    messages.success(request, f'Goodbye, {username}!')
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    context = {
        'user': request.user,
        'current_tenant': getattr(request, 'current_tenant', None),
    }
    
    if request.user.is_root():
        context['companies_count'] = Company.objects.count()
        context['users_count'] = User.objects.count()
    elif request.user.is_admin():
        if request.user.company:
            context['company_users_count'] = request.user.company.users.count()
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
@root_required
def impersonate_user(request, user_id):
    if not request.user.can_impersonate():
        messages.error(request, "You don't have permission to impersonate users.")
        return redirect('accounts:dashboard')
    
    target_user = get_object_or_404(User, id=user_id)
    
    if target_user.is_root():
        messages.error(request, "You cannot impersonate a ROOT user.")
        return redirect('accounts:user_list')
    
    original_user_id = request.user.id
    
    logout(request)
    login(request, target_user, backend='django.contrib.auth.backends.ModelBackend')
    
    request.session['_impersonate'] = {
        'original_user_id': original_user_id,
        'impersonated_user_id': target_user.id,
    }
    
    target_user.is_impersonating = True
    target_user.impersonated_by_id = original_user_id
    target_user.save()
    
    messages.success(request, f'You are now impersonating {target_user.username}')
    return redirect('accounts:dashboard')


@login_required
def stop_impersonation(request):
    impersonate_data = request.session.get('_impersonate')
    
    if not impersonate_data:
        messages.error(request, "You are not currently impersonating anyone.")
        return redirect('accounts:dashboard')
    
    original_user = get_object_or_404(User, id=impersonate_data['original_user_id'])
    
    current_user = request.user
    current_user.is_impersonating = False
    current_user.impersonated_by = None
    current_user.save()
    
    logout(request)
    login(request, original_user, backend='django.contrib.auth.backends.ModelBackend')
    
    del request.session['_impersonate']
    
    messages.success(request, 'Impersonation stopped.')
    return redirect('accounts:user_list')


@login_required
@root_required
def assume_tenant(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    
    request.user.current_tenant = company
    request.user.save()
    
    messages.success(request, f'You are now viewing as tenant: {company.name}')
    return redirect('accounts:dashboard')


@login_required
@root_required
def clear_tenant(request):
    request.user.current_tenant = None
    request.user.save()
    
    messages.success(request, 'Tenant context cleared.')
    return redirect('accounts:dashboard')


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.all()
        
        if not self.request.user.is_root():
            if self.request.user.company:
                queryset = queryset.filter(company=self.request.user.company)
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        
        role_filter = self.request.GET.get('role', '')
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        
        company_filter = self.request.GET.get('company', '')
        if company_filter:
            queryset = queryset.filter(company_id=company_filter)
        
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.select_related('company')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['companies'] = Company.objects.all()
        context['roles'] = User.Role.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['company_filter'] = self.request.GET.get('company', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs


class UserDeactivateView(AdminRequiredMixin, UpdateView):
    model = User
    fields = []
    template_name = 'accounts/user_confirm_deactivate.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        self.object.is_active = not self.object.is_active
        self.object.save()
        
        status = 'activated' if self.object.is_active else 'deactivated'
        messages.success(self.request, f'User {status} successfully.')
        return redirect(self.success_url)


@login_required
@admin_required
def user_reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if not request.user.is_root() and user.company != request.user.company:
        messages.error(request, "You don't have permission to reset this user's password.")
        return redirect('accounts:user_list')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password and new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, f'Password reset successfully for {user.username}.')
            return redirect('accounts:user_list')
        else:
            messages.error(request, 'Passwords do not match.')
    
    return render(request, 'accounts/user_reset_password.html', {'target_user': user})


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            messages.success(request, 'Password reset instructions have been sent to your email.')
            return redirect('accounts:login')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'accounts/password_reset_request.html', {'form': form})
