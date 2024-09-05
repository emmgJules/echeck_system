from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

class CustomErrorPagesMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if not getattr(settings, 'CUSTOM_ERROR_PAGES', True):
            return None  # Let Django handle errors normally
        
        if isinstance(exception, Http404):
            return render(request, '404.html', status=404)
        elif isinstance(exception, Exception):
            return render(request, '500.html', status=500)
        
        return None
