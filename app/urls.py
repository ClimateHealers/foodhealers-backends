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
    re_path(r'signup/', views.SignUp.as_view(), name='user-signup'),
    # POST (user Login)
    re_path(r'login/', views.SignIn.as_view(), name='user-login'),
    # POST (to view food Events occuring based on Start and End Date)
    re_path(r'find-food/', views.FindFood.as_view(), name='find-food'),
    # GET (to View Events added by user )and POST (to Add Events)
    re_path(r'event/', views.Event.as_view(), name='food-event'), 
    # GET (to View Bookmarked Events added by user ) and POST (to Add Bookmarked Events)
    re_path(r'bookmark/', views.BookmarkEvent.as_view(),),  
    # GET (to fetch categories fo recipies)
    re_path(r'categories/', views.Categories.as_view(),),
    # GET (to View recipes) and POST (to Add recipes)
    re_path(r'recipe/(?P<categoryId>[-\w]*)/', views.FindFoodRecipe.as_view(),),
    # GET (to fetch requestTypes for Request API)
    re_path(r'request-types/', views.RequestTypes.as_view(),),
    # GET (to View food/Supplies Request) and POST (to Add food/Supplies Request)
    re_path(r'request-food/(?P<requestTypeId>[-\w]*)/', views.RequestFoodSupplies.as_view(),),   
    
]+static(settings.MEDIA_URL, documne_root=settings.MEDIA_ROOT)