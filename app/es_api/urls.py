from django.urls import include, path
from rest_framework.routers import DefaultRouter

from es_api import views

router = DefaultRouter()

urlpatterns = [
    path('', views.search_index),
]
