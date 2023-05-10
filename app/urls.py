'''
Add new URL patterns here
'''

from django.conf import settings
from django.urls import re_path
from django.conf.urls.static import static
from app import views

app_name = "app"

urlpatterns = [
    re_path(r'signup/', views.SignUp.as_view()),
    re_path(r'login/', views.SignIn.as_view()),
    re_path(r'find-food/', views.FindFood.as_view()),
    re_path(r'event/', views.Event.as_view()),
]+static(settings.MEDIA_URL, documne_root=settings.MEDIA_ROOT)