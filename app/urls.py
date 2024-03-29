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
    # GET (to fetch expoPushToken), PUT (Update expoPushToken)
    re_path(r'expo-push-token/', views.VolunteerExpoPushToken.as_view(), name='volunteer-expo-push-token'),
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
    # GET (to fetch categories fo recipies)
    re_path(r'categories/', views.Categories.as_view(), name='fetch-category'),
    # GET (to View recipes) 
    re_path(r'recipe/(?P<category_id>[-\w]*)/', views.FindFoodRecipe.as_view(), name='food-recipe'),
    # GET (SEARCH RECIPE KEYWORD)
    re_path(r'search-recipe/', views.SearchFoodRecipe.as_view(), name='search-food-recipe'),
    # POST (to Add recipes)
    re_path(r'add-recipe/(?P<category_id>[-\w]*)/', views.PostFoodRecipe.as_view(), name='Post-food-recipe'),

    # GET (to fetch requestTypes for Request API)
    re_path(r'request-types/', views.RequestTypes.as_view(), name='fetch-requestType'),
    # GET (to View food/Supplies Request) and POST (to Add food/Supplies Request)
    re_path(r'request-food/(?P<request_type_id>[-\w]*)/', views.RequestFoodSupplies.as_view(), name='request-food'),  
    # GET (to View volunteers Request) and POST (to Add volunteers Request)
    re_path(r'request-volunteers/(?P<request_type_id>[-\w]*)/', views.RequestVolunteers.as_view(), name='request-volunteers'), 
    # GET (to View History Donated Food) and POST (to Add donate Food)
    re_path(r'donate-food/', views.DonateFood.as_view(), name='donate-food'),
    # GET (to View Volunteer profile) and PUT (to Update Volunteer Profile)
    re_path(r'volunteer-profile/', views.VolunteerProfile.as_view(), name='volunteer-profile'), 
    # GET (to fetch vehicle Details), POST (to Add Vehicle Details) and PUT (to Update Vehicle Details)
    re_path(r'volunteer-vehicle/', views.VehicleOperations.as_view(), name='volunteer-vehicle'), 
    # GET (to fetch Volunteer notification of last 7 days)
    re_path(r'volunteer-notifications/', views.VolunteerNotification.as_view(), name='volunteer-notification'), 
    # GET ( Fetch Calender Events )
    re_path(r'calender-events/', views.CalenderEvents.as_view(), name='calender-events'),
    # GET (View All Donations By All Users API)
    re_path(r'all-donations/', views.AllDonations.as_view()),
    # GET (View All Food/Supplies Requests By All Users API) AddEventVolunteer
    re_path(r'all-requests/(?P<request_type_id>[-\w]*)/', views.AllRequests.as_view()),
    # POST (Add Event Volunteer API) 
    re_path(r'apply-event-volunteer/', views.AddEventVolunteer.as_view()),
    # GET (to fetch itemTypes for Request API)
    re_path(r'item-types/', views.ViewItemTypes.as_view()),    
    # GET (View My Volunteering History API)
    re_path(r'volunteer-history/', views.VolunteerHistory.as_view()),
    # GET (Fetch Volunteer Details of Event API)    
    re_path(r'event-volunteer-details/(?P<event_id>[-\w]*)/', views.GetEventVolunteer.as_view()),
    # Post (update Volunteer profile Photo)
    re_path(r'volunteer-profile-photo/', views.UpdateProfilePhoto.as_view()),
    # Put (Accept Exisiting Food Donation)
    re_path(r'accept-food-donation/', views.AcceptFoodDonation.as_view()),
    # Put (Accept Exisiting Food Request)
    re_path(r'accept-food-request/', views.AcceptFoodRequest.as_view()),
    # Post (Accept Pickup Request By Driver)
    re_path(r'accept-pickup-request/', views.AcceptPickup.as_view()),
    # Post (Generate OTP)
    re_path(r'generate-otp/', views.GenerateConfirmationOTP.as_view()),


]+static(settings.MEDIA_URL, documne_root=settings.MEDIA_ROOT)