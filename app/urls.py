'''
Add new URL patterns here
'''

from django.conf import settings
from django.urls import re_path
from django.conf.urls.static import static
from app import views

app_name = "app"

urlpatterns = [
    # POST (Update AccessToken)
    re_path(r'refresh-token/', views.GetRefreshToken.as_view()),
    # GET (CHOICES)
    re_path(r'choices/', views.ChoicesView.as_view()),
    # POST (user Signup)
    re_path(r'signup/', views.SignUp.as_view(), name='user-signup'),
    # POST (user Login)
    re_path(r'login/', views.SignIn.as_view(), name='user-login'),
    # POST (to view food Events occuring based on Start and End Date)
    re_path(r'find-food/', views.FindFood.as_view(), name='find-food'),
    # GET (View All Events By All Users API)
    re_path(r'all-events/', views.AllEvents.as_view()),
    # GET (to View Events added by user) and POST (to Add Events)
    re_path(r'event/', views.Event.as_view(), name='food-event'), 
    # GET (to View Bookmarked Events added by user) and POST (to Add Bookmarked Events)
    re_path(r'bookmark/', views.BookmarkEvent.as_view(), name='bookmark-event'),  
    # GET (to fetch categories fo recipies)
    re_path(r'categories/', views.Categories.as_view(), name='fetch-category'),
    # GET (to View recipes) and POST (to Add recipes)
    re_path(r'recipe/(?P<categoryId>[-\w]*)/', views.FindFoodRecipe.as_view(), name='food-recipe'),
    # GET (to fetch requestTypes for Request API)
    re_path(r'request-types/', views.RequestTypes.as_view(), name='fetch-requestType'),
    # GET (to View food/Supplies Request) and POST (to Add food/Supplies Request)
    re_path(r'request-food/(?P<requestTypeId>[-\w]*)/', views.RequestFoodSupplies.as_view(), name='request-food'),  
    # GET (to View volunteers Request) and POST (to Add volunteers Request)
    re_path(r'request-volunteers/(?P<requestTypeId>[-\w]*)/', views.RequestVolunteers.as_view(), name='request-volunteers'), 
    # GET (to View History Donated Food) and POST (to Add donate Food)
    re_path(r'donate-food/', views.DonateFood.as_view(), name='donate-food'),
    # GET (to View Volunteer profile) and PUT (to Update Volunteer Profile)
    re_path(r'volunteer-profile/', views.VolunteerProfile.as_view(), name='volunteer-profile'), 
    # GET (to fetch vehicle Details), POST (to Add Vehicle Details) and PUT (to Update Vehicle Details)
    re_path(r'volunteer-vehicle/', views.VehicleOperations.as_view(), name='volunteer-vehicle'), 
    # DELETE (Django Template view to Delete Volunteer Profile)
    re_path(r'delete-account/(?P<uniqueID>[-\w]*)/', views.DeleteUserAccountView.as_view(), name='delete-account-view'), 
    # DELETE (Delete Action for the Django Template)
    re_path(r'delete-account-action/<(?P<uniqueID>[-\w]*)/', views.deleteUserAccountAction, name='delete-account-action'), 

]+static(settings.MEDIA_URL, documne_root=settings.MEDIA_ROOT)