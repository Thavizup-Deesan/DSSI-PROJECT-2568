"""
URL configuration for backend project.
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from api.views import homepage, run_migrations
from api.urls import page_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),

    # Homepage → redirect to login
    path('', homepage, name='homepage'),
    path('migrate_db/', run_migrations, name='run_migrations'),

    # API routes (prefix: /api/)
    path('api/', include('api.urls')),

    # django-allauth (Google OAuth 2.0)
    path('accounts/', include('allauth.urls')),

    # Page routes (templates)
] + page_urlpatterns
# Serve media files in development
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
