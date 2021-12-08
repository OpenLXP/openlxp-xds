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
    path('auth/logout', views.logout_view, name='logout'),
    path('auth/validate', views.is_logged_in, name='validate'),
    path('experiences/<str:exp_hash>/', views.get_experiences,
         name='get_courses'),
    path('interest-lists/', views.interest_lists,
         name='interest-lists'),
    path('interest-lists/<int:list_id>', views.interest_list,
         name='interest-list'),
    path('experiences/<str:exp_hash>/interest-lists',
         views.add_course_to_lists,
         name='add_course_to_lists'),
    path('interest-lists/owned',
         views.interest_lists_owned,
         name='owned-lists'),
    path('interest-lists/subscriptions',
         views.interest_lists_subscriptions,
         name='interest-list-subscriptions'),
    path('interest-lists/<int:list_id>/subscribe',
         views.interest_list_subscribe,
         name='interest-list-subscribe'),
    path('interest-lists/<int:list_id>/unsubscribe',
         views.interest_list_unsubscribe,
         name='interest-list-unsubscribe'),
    path('saved-filters/<int:filter_id>', views.saved_filter,
         name='saved-filter'),
    path('saved-filters/owned',
         views.saved_filters_owned,
         name='owned-filters'),
    path('saved-filters',
         views.saved_filters,
         name='saved-filters'),
]
