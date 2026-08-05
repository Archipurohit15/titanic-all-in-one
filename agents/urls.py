from django.urls import path
from . import views

urlpatterns = [
    path('agent/signup/', views.agent_signup, name='agent_signup'),
]