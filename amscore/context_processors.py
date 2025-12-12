from amscore.apps.core.models import Company


def company_context(request):
    context = {
        'current_company': request.company,
        'companies': [],
    }
    
    if hasattr(request, 'user') and request.user.is_authenticated:
        context['companies'] = Company.objects.filter(is_active=True)
    
    return context
