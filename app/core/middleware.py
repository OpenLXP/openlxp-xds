from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class HealthCheckSSLRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    

    def __call__(self, request):
        if request.path.startswith('/health'):
            return self.get_response(request)

        
        if settings.SECURE_SSL_REDIRECT and not request.is_secure():
            return HttpResponsePermanentRedirect(f'https://{request.get_host()}{request.get_full_path()}')
        
        
        return self.get_response(request)