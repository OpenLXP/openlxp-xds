from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

app_name = 'users'
urlpatterns = [
    path('auth/register', views.RegisterView.as_view(), name='register'),
    path('auth/login', views.LoginView.as_view(), name='login'),
    path('auth/logout', views.LogoutView.as_view(), name='logout'),
    path('auth/validate', views.IsLoggedInView.as_view(), name='validate'),
]
