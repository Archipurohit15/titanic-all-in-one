from django.urls import path
from . import views

urlpatterns = [
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/verify/', views.payment_verify, name='payment_verify'),
    path('payment/failed/<int:order_id>/', views.payment_failed, name='payment_failed'),
    path('payment/retry/<int:order_id>/', views.retry_payment, name='retry_payment'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('verify-delivery/', views.verify_delivery, name='verify_delivery'),
]