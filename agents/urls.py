from django.urls import path
from . import views

urlpatterns = [
    path('agent/signup/', views.agent_signup, name='agent_signup'),
    path('agent/login/', views.agent_login, name='agent_login'),
    path('agent/logout/', views.agent_logout, name='agent_logout'),
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),
]