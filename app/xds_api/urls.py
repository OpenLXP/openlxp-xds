from django.urls import include, path
from rest_framework.routers import DefaultRouter

from xds_api import views

router = DefaultRouter()

app_name = 'xds_api'
urlpatterns = [
    path('configuration/', views.XDSConfigurationView.as_view(),
         name='xds-configuration'),
    path('ui-configuration/', views.XDSUIConfigurationView.as_view(),
         name='xds-ui-configuration'),
    path('spotlight-courses', views.get_spotlight_courses,
         name='spotlight-courses'),
    path('auth', include('knox.urls')),
    path('auth/register', views.RegisterView.as_view(), name='register'),
    path('auth/login', views.LoginView.as_view(), name='login'),
    path('courses/<str:course_id>/', views.get_courses,
         name='get_courses'),
]
