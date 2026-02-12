"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from api.views import homepage
from api.urls import page_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),

    # Homepage → redirect to login
    path('', homepage, name='homepage'),

    # API routes (prefix: /api/)
    path('api/', include('api.urls')),

    # django-allauth (Google OAuth 2.0)
    path('accounts/', include('allauth.urls')),

    # Page routes (templates)
] + page_urlpatterns