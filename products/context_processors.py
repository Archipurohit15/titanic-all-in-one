from .models import Categories


def featured_categories(request):
    return {
        'featured_categories': {
            'fmcg': Categories.objects.filter(parent=None, name__in=['FMCG', 'Fmcg', 'Personal Care & Household', 'Personal Care & Household']).first(),
            'groceries': Categories.objects.filter(parent=None, name__in=['Groceries', 'Grocery']).first(),
            'electronics': Categories.objects.filter(parent=None, name__in=['Electronics']).first(),
            'electricals': Categories.objects.filter(parent=None, name__in=['Electrical', 'Electricals']).first(),
        }
    }