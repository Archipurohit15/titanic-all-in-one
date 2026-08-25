from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('search/', views.search_results, name='search_results'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
]