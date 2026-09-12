"""
URL configuration for titan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit


admin.site.site_header = "Titanic Admin Panel"
admin.site.site_title = "Titanic Admin"
admin.site.index_title = "Products & Orders Management"

# Password reset request pe rate limit — bahut zyada baar reset email na maangi ja sake
rate_limited_password_reset = method_decorator(
    ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch'
)(auth_views.PasswordResetView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('products.urls')),
    path('', include('orders.urls')),
    path('', include('agents.urls')),
    path('', include('customers.urls')),
    path('password-reset/', rate_limited_password_reset.as_view(
        template_name='registration/password_reset_form.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]
