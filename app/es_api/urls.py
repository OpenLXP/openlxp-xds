from django.urls import path
from rest_framework.routers import DefaultRouter

from es_api import views

router = DefaultRouter()

urlpatterns = [
    path('more-like-this/<str:doc_id>/', views.get_more_like_this),
    path('filter-search/', views.filters),
    path('', views.search_index),
]
