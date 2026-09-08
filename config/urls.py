
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Documentação automática
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Apps
    path('api/users/', include('apps.users.urls')),
    path('api/permissions/', include('apps.permissions.urls')),
    path('api/core/', include('apps.core.urls')),
    path('api/auth/', include('apps.auth.urls')),
    path('api/leads/', include('apps.leads.urls')),
]
