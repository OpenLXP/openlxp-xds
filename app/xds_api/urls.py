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
     path('experiences/<str:exp_hash>/', views.get_experiences,
          name='get_courses'),
     path('interest-lists/', views.interest_lists,
          name='interest-lists'),
     path('interest-lists/<int:list_id>', views.interest_list,
          name='interest-list'),
     path('experiences/<str:exp_hash>/interest-lists',
          views.add_course_to_lists,
          name='add_course_to_lists'),
]
