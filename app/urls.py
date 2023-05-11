'''
Add new URL patterns here
'''

from django.conf import settings
from django.urls import re_path
from django.conf.urls.static import static
from app import views

app_name = "app"

urlpatterns = [
    # POST (user Signup)
    re_path(r'signup/', views.SignUp.as_view()),
    # POST (user Login)
    re_path(r'login/', views.SignIn.as_view()),
    # POST (to view food Events occuring based on Start and End Date)
    re_path(r'find-food/', views.FindFood.as_view()),
    # GET (to View Events added by user )and POST (to Add Events)
    re_path(r'event/', views.Event.as_view()), 
    # GET (to View Bookmarked Events added by user ) and POST (to Add Bookmarked Events)
    re_path(r'bookmark/', views.BookmarkEvent.as_view(),),  
    # GET (to fetch categories fo recipies)
    re_path(r'categories/', views.Categories.as_view(),),
    # GET (to View recipes) and POST (to Add recipes)
    # re_path(r'recipe/', views.FindFoodRecipe.as_view(),),
    re_path(r'recipe/(?P<categoryId>\w+)', views.FindFoodRecipe.as_view(),),
    
]+static(settings.MEDIA_URL, documne_root=settings.MEDIA_ROOT)