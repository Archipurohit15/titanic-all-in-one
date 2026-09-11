from .models import Categories


def featured_categories(request):
    return {
        'featured_categories': {
            'industrial': Categories.objects.filter(parent=None, name__in=['Industrial', 'FMCG', 'Fmcg', 'Personal Care & Household']).first(),
            'tools': Categories.objects.filter(parent=None, name__in=['Tools', 'Groceries', 'Grocery']).first(),
            'electronics': Categories.objects.filter(parent=None, name__in=['Electronics']).first(),
            'electricals': Categories.objects.filter(parent=None, name__in=['Electrical', 'Electricals']).first(),
        }
    }