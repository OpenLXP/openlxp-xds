from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

app_name = 'configurations'
urlpatterns = [
    path('configuration/', views.XDSConfigurationView.as_view(),
         name='xds-configuration'),
    path('ui-configuration/', views.XDSUIConfigurationView.as_view(),
         name='xds-ui-configuration'),
]
