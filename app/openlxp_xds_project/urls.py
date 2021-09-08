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
from django.urls import include, path
import django_saml2_auth.views

urlpatterns = [
    # These are the SAML2 related URLs. You can change "^saml2_auth/" regex to
    # any path you want, like "^sso_auth/", "^sso_login/", etc. (required)
    path('saml2_auth/', include('django_saml2_auth.urls')),
    # If you want to specific the after-login-redirect-URL,
    # use parameter "?next=/the/path/you/want" with this view.
    path('saml2-login/', django_saml2_auth.views.signin),
    path('admin/', admin.site.urls),
    path('api/', include('xds_api.urls')),
    path('es-api/', include('es_api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
