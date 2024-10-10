"""openlxp_xds_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path, path
from django.http import HttpResponse


def health_check(request):
    return HttpResponse("OK", status=200)


urlpatterns = [
    re_path('admin/', admin.site.urls),
    re_path('api/', include('xds_api.urls')),
    re_path('api/', include('users.urls')),
    re_path('api/', include('configurations.urls')),
    re_path('es-api/', include('es_api.urls')),
    re_path('api-auth/', include(
        'rest_framework.urls',
        namespace='rest_framework')),
    path('health/', health_check, name='health-check')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
