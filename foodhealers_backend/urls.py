"""
URL configuration for foodhealers_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="Food Healers API Documentation",
        terms_of_service="https://climatehealers.org/transform/foodhealers/",
        contact=openapi.Contact(email='apps@alamanceinc.com',),
        license=openapi.License(name="Alamance IT Solutions"),  
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url='https://api.climatehealers.com'
)

if settings.DEBUG :
   urlpatterns = [
        path('admin/', admin.site.urls),
        path('docs/', schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
        path('__debug__/', include('debug_toolbar.urls')),

        re_path(r'^v1/api/', include('app.urls', namespace='v1')),
        re_path(r'^v2/api/', include('app.urls', namespace='v2')),

    ]
else:
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('docs/', schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),

        re_path(r'^v1/api/', include('app.urls', namespace='v1')),
        re_path(r'^v2/api/', include('app.urls', namespace='v2')),

    ]
