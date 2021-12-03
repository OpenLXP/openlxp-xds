from django.urls import path
from es_api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('more-like-this/<str:doc_id>/', views.get_more_like_this),
    path('filter-search/', views.filters),
    path('', views.search_index),
]
