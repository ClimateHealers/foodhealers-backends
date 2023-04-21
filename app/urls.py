'''
Add new URL patterns here
'''

from django.conf import settings
from django.urls import include, re_path, path
from django.conf.urls.static import static
from app import views

app_name = "app"

urlpatterns = [
    re_path(r'test/', views.SendMessageMail.as_view()),
]+static(settings.MEDIA_URL, documne_root=settings.MEDIA_ROOT)