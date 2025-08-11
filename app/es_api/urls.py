from django.urls import path
from rest_framework.routers import DefaultRouter

from es_api import views

router = DefaultRouter()

app_name = 'es_api'
urlpatterns = [
    path('more-like-this/<str:doc_id>/', views.GetMoreLikeThisView.as_view(),
         name='get-more-like-this'),
    path('filter-search/', views.FiltersView.as_view(), name='filters'),
    path('', views.SearchIndexView.as_view(), name='search-index'),
    path('suggest/', views.SuggestionsView.as_view(), name='suggest'),
    path('derived-from/', views.SearchDerivedView.as_view(),
         name='search-derived'),
    path('teaches/', views.SearchCompetencyView.as_view(),
         name='search-competency'),
    path('similar-courses/<str:key>/',
         views.GetSimilarCoursesView.as_view(), name='get-similar-courses'),
]
