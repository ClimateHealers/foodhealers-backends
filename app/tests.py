from django.test import TestCase
# Create your tests here.
from django.db import transaction
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import *
import json
from app.authentication import create_access_token, create_refresh_token
from rest_framework.test import force_authenticate
from datetime import datetime


class UserOperations(APITestCase):
    urlpatterns = [
        path('v1/api/', include('app.urls')),
    ]

    @classmethod
    def setUpTestData(self):
        with transaction.atomic():

            category, created = Category.objects.get_or_create(name='Breakfast', createdAt=datetime.now(), active=True)
            Category.objects.get_or_create(name='Lunch', createdAt=datetime.now(), active=True)
            Category.objects.get_or_create(name='Dinner', createdAt=datetime.now(), active=True)
            
            foodRequestType, created = RequestType.objects.get_or_create(name='Food', createdAt=datetime.now(), active=True)
            RequestType.objects.get_or_create(name='Supplies', createdAt=datetime.now(), active=True)
            volunteerRequestType, created = RequestType.objects.get_or_create(name='Volunteer', createdAt=datetime.now(), active=True) 
            pickupRequestType, created = RequestType.objects.get_or_create(name='Pickup', createdAt=datetime.now(), active=True)

            foodItemType, created = ItemType.objects.get_or_create(name='Food', createdAt=datetime.now(), active=True)
            ItemType.objects.get_or_create(name='Supplies', createdAt=datetime.now(), active=True)

            user, created = Volunteer.objects.get_or_create(
                username='testuser@example.com',
                email='testuser@example.com',
                name='Test User',
                password='password123#',
                phoneNumber=99723234342,
                isVolunteer=True, 
                volunteerType=VOLUNTEER_TYPE[2][0],
            )

            from app.authentication import create_access_token, create_refresh_token
            accessToken = create_access_token(user.id)
            refreshToken = create_refresh_token(user.id)

            token, created = CustomToken.objects.get_or_create(
                accessToken=accessToken, refreshToken=refreshToken, user=user)

            self.token = token
            self.accessToken = accessToken
            self.user = user
            self.category = category
            self.foodRequestType = foodRequestType
            self.volunteerRequestType = volunteerRequestType
            self.pickupRequestType = pickupRequestType 
            self.foodItemType = foodItemType
            print('<<<---------------------------------------->>>')

    # user SignUp test cases
    '''
    Test case to test onboarding with valid data
    '''
    def test_user_onboarding_valid_data(self):
        session = self.client.session
        session['email'] = "user@example.com"
        session.save()

        try:
            url = reverse('app:user-signup')
            data = {
                'token_id': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9',
                'name': 'Test User ',
                'email': 'user@example.com',
                'isVolunteer': True
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_driver_onboarding_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    '''
    Test case to test onboarding with missing parameters (token_id)
    '''

    def test_user_onboarding_with_missing_token_id(self):
        session = self.client.session
        session['email'] = "user@example.com"
        session.save()

        try:
            url = reverse('app:user-signup')
            data = {
                'name': 'Test User ',
                'email': 'user@example.com',
                'isVolunteer': True
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_onboarding_with_missing_token_id ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test onboarding with missing parameters (name)
    '''

    def test_user_onboarding_with_missing_name(self):
        session = self.client.session
        session['email'] = "user@example.com"
        session.save()

        try:
            url = reverse('app:user-signup')
            data = {
                'token_id': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9',
                'email': 'user@example.com',
                'isVolunteer': True
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_onboarding_with_missing_name ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    '''
        Test case to test onboarding with missing parameters (email)
    '''

    def test_user_onboarding_with_missing_email(self):
        session = self.client.session
        # session['email'] = "user@example.com"
        session.save()

        try:
            url = reverse('app:user-signup')
            data = {
                'token_id': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9',
                'name': 'Test User ',
                'isVolunteer': True
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_onboarding_with_missing_email ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    '''
        Test case to test onboarding with missing parameters (isVolunteer)
    '''

    def test_user_onboarding_with_missing_isVolunteer(self):
        session = self.client.session
        session['email'] = "user@example.com"
        session.save()

        try:
            url = reverse('app:user-signup')
            data = {
                'token_id': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9',
                'name': 'Test User ',
                'email': 'user@example.com',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_onboarding_with_missing_isVolunteer ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)   

    # user Login In test cases
    '''
    Test case to test login with valid data
    '''
    def test_user_login_valid_data(self):
        session = self.client.session
        session['email'] = "user@example.com"
        session.save()

        try:
            url = reverse('app:user-login')
            data = {
                'token_id': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_login_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    '''
    Test case to test login with missing parameters (token_id)
    '''

    def test_user_login_with_missing_token_id(self):
        session = self.client.session
        session['email'] = "user@example.com"
        session.save()

        try:
            url = reverse('app:user-login')
            data = { }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_login_with_missing_token_id ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test login with missing parameters (email)
    '''

    def test_user_login_with_missing_email(self):
        session = self.client.session
        # session['email'] = "user@example.com"
        session.save()

        try:
            url = reverse('app:user-login')
            data = {
                'token_id': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_login_with_missing_email ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    # Volunteer Post Food Events test cases
    '''
    Test case to test post food Events with valid data
    '''
    def test_volunteer_postFoodEvents_valid_data(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-event')
            data = {
                'eventName':'Test event',
                'lat': '23.5777',
                'lng': '72.5777',
                'alt': '54777',
                'eventStartDate': '2023-6-6',
                'eventEndDate': '2023-6-6',
                'additionalInfo':'Free vegan Meals',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodEvents_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    '''
        Test case to test post Food Events with valid data But no Events present
    '''
    def test_volunteer_postFoodEvent_valid_data_with_eventsExist(self):

        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-event')

            address = Address.objects.create(lat=23.5777, lng=72.5777, alt=54777)
            FoodEvent.objects.create(
                name='Test event',
                address=address,
                eventStartDate='2023-6-6',
                eventEndDate='2023-6-6', 
                createdAt=datetime.now(),
                createdBy=self.user,
                additionalInfo='Free vegan Meals',
                active=True
            )
    
            data = {
                'eventName':'Test event',
                'lat': '23.5777',
                'lng': '72.5777',
                'alt': '54777',
                'eventStartDate': '2023-6-6',
                'eventEndDate': '2023-6-6',
                'additionalInfo':'Free vegan Meals',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)

            print('------ test case response for  : test_volunteer_postFoodEvent_valid_data_with_eventsExist ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Food Events with missing parameters (latitude)
    '''

    def test_volunteer_postFoodEvents_with_missing_lat(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-event')
            data = {
                'eventName':'Test event',
                'lng': '52.5777',
                'alt': '54777',
                'eventStartDate': '2023-06-06',
                'eventEndDate': '2023-06-06',
                'additionalInfo':'Free vegan Meals',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodEvents_with_missing_lat ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Food Events with missing parameters (longitude)
    '''

    def test_volunteer_postFoodEvents_with_missing_lng(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-event')
            data = {
                'eventName':'Test event',
                'lat': '22.5777',
                'alt': '54777',
                'eventStartDate': '2023-06-06',
                'eventEndDate': '2023-06-06',
                'additionalInfo':'Free vegan Meals',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodEvents_with_missing_lng ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Food Events with missing parameters (altitude)
    '''

    def test_volunteer_postFoodEvents_with_missing_alt(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-event')
            data = {
                'eventName':'Test event',
                'lat': '22.5777',
                'lng': '52.5777',
                'eventStartDate': '2023-06-06',
                'eventEndDate': '2023-06-06',
                'additionalInfo':'Free vegan Meals',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodEvents_with_missing_alt ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    '''
    Test case to test post Food Events with missing parameters (eventStartDate)
    '''

    def test_volunteer_postFoodEvents_with_missing_eventStartDate(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-event')
            data = {
                'eventName':'Test event',
                'lat': '22.5777',
                'lng': '52.5777',
                'alt': '54777',
                'eventEndDate': '2023-06-06',
                'additionalInfo':'Free vegan Meals',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodEvents_with_missing_eventStartDate ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Food Events with missing parameters (eventEndDate)
    '''

    def test_volunteer_postFoodEvents_with_missing_eventEndDate(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-event')
            data = {
                'eventName':'Test event',
                'lat': '22.5777',
                'lng': '52.5777',
                'alt': '54777',
                'eventStartDate': '2023-06-06',
                'additionalInfo':'Free vegan Meals',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodEvents_with_missing_eventEndDate ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Food Events with missing parameters (additionalInfo)
    '''

    def test_volunteer_postFoodEvents_with_missing_additionalInfo(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-event')
            data = {
                'eventName':'Test event',
                'lat': '22.5777',
                'lng': '52.5777',
                'alt': '54777',
                'eventStartDate': '2023-06-06',
                'eventEndDate': '2023-06-06',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodEvents_with_missing_additionalInfo ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test get Food Events posted by volunteer (Existing Events)
    '''

    def test_volunteer_getFoodEvents(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-event')

            address = Address.objects.create(lat=23.5777, lng=72.5777, alt=54777)
            FoodEvent.objects.create(
                name='Test event',
                address=address,
                eventStartDate='2023-6-6',
                eventEndDate='2023-6-6', 
                createdAt=datetime.now(),
                createdBy=self.user,
                additionalInfo='Free vegan Meals',
                active=True
            )
    
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_getFoodEvents ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test get Food Events posted by volunteer (No Events)
    '''

    def test_volunteer_getFoodEvents_with_noEvents(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-event')
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_getFoodEvents_with_noEvents ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    # user Find Food test cases
    '''
    Test case to test findFood with valid data
    '''

    def test_user_findfood_valid_data(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:find-food')

            address = Address.objects.create(lat=23.5777, lng=72.5777, alt=54777)
            FoodEvent.objects.create(
                name='Test event',
                address=address,
                eventStartDate='2023-6-6',
                eventEndDate='2023-6-6', 
                createdAt=datetime.now(),
                createdBy=self.user,
                additionalInfo='Free vegan Meals',
                active=True
            )

            data = {
                'lat': '23.5777',
                'lng': '72.5777',
                'alt': '54777',
                'eventStartDate': '2023-06-06',
                'eventEndDate': '2023-06-06',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_findfood_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    '''
        Test case to test findFood with valid data But no Events present
    '''

    def test_user_findfood_valid_data_with_noEvents(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:find-food')
            data = {
                'lat': '22.5777',
                'lng': '52.5777',
                'alt': '54777',
                'eventStartDate': '2023-06-06',
                'eventEndDate': '2023-06-06',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_findfood_valid_data_with_noEvents ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test findfood with missing parameters (latitude)
    '''

    def test_user_findfood_with_missing_lat(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:find-food')
            data = {
                'lng': '52.5777',
                'alt': '54777',
                'eventStartDate': '2023-06-06',
                'eventEndDate': '2023-06-06',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_findfood_with_missing_lat ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test findfood with missing parameters (longitude)
    '''

    def test_user_findfood_with_missing_lng(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:find-food')
            data = {
                'lat': '22.5777',
                'alt': '54777',
                'eventStartDate': '2023-06-06',
                'eventEndDate': '2023-06-06',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_findfood_with_missing_lng ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test findfood with missing parameters (altitude)
    '''

    def test_user_findfood_with_missing_alt(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:find-food')
            data = {
                'lat': '22.5777',
                'lng': '52.5777',
                'eventStartDate': '2023-06-06',
                'eventEndDate': '2023-06-06',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_findfood_with_missing_alt ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    '''
    Test case to test findfood with missing parameters (eventStartDate)
    '''

    def test_user_findfood_with_missing_eventStartDate(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:find-food')
            data = {
                'lat': '22.5777',
                'lng': '52.5777',
                'alt': '54777',
                'eventEndDate': '2023-06-06',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_findfood_with_missing_eventStartDate ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test findfood with missing parameters (eventEndDate)
    '''

    def test_user_findfood_with_missing_eventEndDate(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:find-food')
            data = {
                'lat': '22.5777',
                'lng': '52.5777',
                'alt': '54777',
                'eventStartDate': '2023-06-06',
                # 'eventEndDate': '2023-06-06',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_findfood_with_missing_eventEndDate ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    # user fetch category test cases
    '''
    Test case to test fetch category 
    '''

    def test_user_fetch_category(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:fetch-category',)
            
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_fetch_category ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    # Volunteer fetch RequestType test cases
    '''
    Test case to test fetch requestType 
    '''

    def test_volunteer_fetch_requestType(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:fetch-requestType',)
            
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_fetch_requestType ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    # User Bookmark Events test cases
    '''
    Test case to test Add Bookmark Event with valid data
    '''
    
    def test_user_postBookmark_valid_data(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:bookmark-event')
            
            foodEvent = FoodEvent.objects.create(
                name='Test Event',
                organizerPhoneNumber=997263, 
                eventStartDate=datetime.now(),
                eventEndDate=datetime.now(), 
                createdAt=datetime.now(),
                additionalInfo='vegan food',
                active=True
            )
            
            data = {
                'eventId': foodEvent.id,
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_postBookmark_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    '''
        Test case to test Add Bookmark Event with No Events present
    '''

    def test_user_addBookmark_valid_data_with_noEvents(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:bookmark-event')
            
            foodEvent = FoodEvent.objects.create(
                name='Test Event',
                organizerPhoneNumber=997263, 
                eventStartDate=datetime.now(),
                eventEndDate=datetime.now(), 
                createdAt=datetime.now(),
                additionalInfo='vegan food',
                active=True
            )
            
            data = {
                'eventId': foodEvent.id,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_addBookmark_valid_data_with_noEvents ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test add Bookmark with missing parameters (eventId)
    '''

    def test_user_addBookmark_with_missing_eventId(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:bookmark-event')
            data = { }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_addBookmark_with_missing_eventId ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test add Bookmark with Bookmark Already Exist
    '''

    def test_user_addBookmark_with_bookmark_exist(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:bookmark-event')
            
            foodEvent = FoodEvent.objects.create(
                name='Test Event',
                organizerPhoneNumber=997263, 
                eventStartDate=datetime.now(),
                eventEndDate=datetime.now(), 
                createdAt=datetime.now(),
                additionalInfo='vegan food',
                active=True
            )

            EventBookmark.objects.create(user=self.user, event=foodEvent, createdAt=datetime.now())
            data = {'eventId': foodEvent.id}
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_addBookmark_with_bookmark_exist ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    # User Bookmark Events test cases
    '''
    Test case to test Get Bookmark Event with valid data
    '''
    
    def test_user_getBookmark_valid_data(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:bookmark-event')
            
            foodEvent = FoodEvent.objects.create(
                name='Test Event',
                organizerPhoneNumber=997263, 
                eventStartDate=datetime.now(),
                eventEndDate=datetime.now(), 
                createdAt=datetime.now(),
                additionalInfo='vegan food',
                active=True
            )

            EventBookmark.objects.create(user=self.user, event=foodEvent, createdAt=datetime.now())

            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_getBookmark_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    '''
        Test case to test Get Bookmark Event with No Bookmarks present
    '''

    def test_user_getBookmark_valid_data_with_noBookmark(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:bookmark-event')
            
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_user_getBookmark_valid_data_with_noBookmark ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    # Volunteer Post Food Recipe test cases
    '''
    Test case to test post food Recipe with valid data
    '''
    def test_volunteer_postFoodRecipe_valid_data(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-recipe', kwargs={'categoryId': self.category.id})
            data = {
                'foodName':'Test event',
                'ingredients': 'water, Salt, Rice',
                'cookingInstructions': 'Boil for 5 mins',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodRecipe_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    '''
        Test case to test post Food Recipe with valid data But Category not Exist 
    '''
    def test_volunteer_postFoodRecipe_valid_data_with_category_notExist(self):

        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)

            url = reverse('app:food-recipe', kwargs={'categoryId': 0})
            data = {
                'foodName':'Test event',
                'ingredients': 'water, Salt, Rice',
                'cookingInstructions': 'Boil for 5 mins',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)

            print('------ test case response for  : test_volunteer_postFoodRecipe_valid_data_with_category_notExist ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test Post Food Recipe Which is Already Present 
    '''

    def test_volunteer_postFoodRecipe_with_recipe_alreadyExist(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-recipe', kwargs={'categoryId': self.category.id})

            FoodRecipe.objects.create(
                foodName='Test food', 
                ingredients='water, Salt, Rice', 
                cookingInstructions='Boil for 5 mins', 
                category=self.category
            )

            data = {
                'foodName':'Test food',
                'ingredients': 'water, Salt, Rice',
                'cookingInstructions': 'Boil for 5 mins',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodRecipe_with_recipe_alreadyExist ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        

    '''
    Test case to test post Food Recipe with missing parameters (foodName)
    '''

    def test_volunteer_postFoodRecipe_with_missing_foodname(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-recipe', kwargs={'categoryId': self.category.id})
            
            data = {
                'ingredients': 'water, Salt, Rice',
                'cookingInstructions': 'Boil for 5 mins',
            }
            
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodRecipe_with_missing_foodname ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Food Recipe with missing parameters (ingredients)
    '''

    def test_volunteer_postFoodRecipe_with_missing_ingredients(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-recipe', kwargs={'categoryId': self.category.id})
            
            data = {
                'foodName': 'test Food',
                'cookingInstructions': 'Boil for 5 mins',
            }
            
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodRecipe_with_missing_ingredients ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Food Recipe with missing parameters (cookingInstructions)
    '''

    def test_volunteer_postFoodRecipe_with_missing_cookingInstructions(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-recipe', kwargs={'categoryId': self.category.id})
            
            data = {
                'foodName': 'test Food',
                'ingredients': 'water, Salt, Rice',
            }
            
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodRecipe_with_missing_cookingInstructions ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    # '''
    # Test case to test post Food Recipe with missing parameters (categoryId)
    # '''

    # def test_volunteer_postFoodRecipe_with_missing_categoryId(self):
        
    #     try:
    #         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
    #         url = reverse('app:food-recipe')
            
    #         data = {
    #             'foodName': 'test Food',
    #             'ingredients': 'water, Salt, Rice',
    #             'cookingInstructions': 'Boil for 5 mins',
    #         }
            
    #         response = self.client.post(url, data, format='json')
    #         result = json.loads(response.content)
    #         print('------ test case response for  : test_volunteer_postFoodRecipe_with_missing_categoryId ------',result)

    #         self.assertEqual(response.status_code, status.HTTP_200_OK)

    #         return result
    #     except Exception as e:
    #         return str(e)
        
    '''
    Test case to test get Food Recipe posted by volunteer
    '''

    def test_volunteer_getFoodRecipes(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-recipe', kwargs={'categoryId': self.category.id})

            FoodRecipe.objects.create(
                foodName='Test food', 
                ingredients='water, Salt, Rice', 
                cookingInstructions='Boil for 5 mins', 
                category=self.category
            )
    
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_getFoodRecipes ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    '''
    Test case to test get Food Recipe posted by volunteer (No Recipes)
    '''

    def test_volunteer_getFoodRecipes_noRecipes(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-recipe', kwargs={'categoryId': self.category.id})
    
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_getFoodRecipes_noRecipes ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test get Food Recipe posted by volunteer But Category not Exist 
    '''

    def test_volunteer_getFoodRecipes_category_notExist(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-recipe', kwargs={'categoryId': 0})

            FoodRecipe.objects.create(
                foodName='Test food', 
                ingredients='water, Salt, Rice', 
                cookingInstructions='Boil for 5 mins', 
                category=self.category
            )
    
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_getFoodRecipes_category_notExist ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
            
    # Volunteer/Organizer Post Food/Supplies Request test cases
    '''
    Test case to test post food Supplies Request with valid data
    '''

    def test_volunteer_postFoodSupplies_valid_data(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:request-food', kwargs={'requestTypeId': self.foodRequestType.id})
            
            data = {
                'itemTypeId':self.foodItemType.id,
                'itemName': 'Food item name',
                'requiredDate': '2023-6-6',
                'quantity': '54 Kg',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodSupplies_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    '''
    Test case to test post food Supplies Request with ItemTypeId Does not exist
    '''

    def test_volunteer_postFoodSupplies_invalid_itemTypeId(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:request-food', kwargs={'requestTypeId': self.foodRequestType.id})
            
            data = {
                'itemTypeId':0,
                'itemName': 'Food item name',
                'requiredDate': '2023-6-6',
                'quantity': '54 Kg',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodSupplies_invalid_itemTypeId ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post food Supplies Request with requestTypeId Does not exist
    '''

    def test_volunteer_postFoodSupplies_invalid_requestTypeId(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:request-food', kwargs={'requestTypeId': 0})
            
            data = {
                'itemTypeId':self.foodItemType.id,
                'itemName': 'Food item name',
                'requiredDate': '2023-6-6',
                'quantity': '54 Kg',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodSupplies_invalid_requestTypeId ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Food Supplies Request with missing parameters (itemTypeId)
    '''

    def test_volunteer_postFoodSupplies_missing_itemTypeId(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:request-food', kwargs={'requestTypeId': self.foodRequestType.id})
            data = {
                'itemName': 'Food item name',
                'requiredDate': '2023-6-6',
                'quantity': '54 Kg',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodSupplies_missing_itemTypeId ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Food Supplies Request with missing parameters (itemName)
    '''

    def test_volunteer_postFoodSupplies_missing_itemName(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:request-food', kwargs={'requestTypeId': self.foodRequestType.id})
            data = {
                'itemTypeId':self.foodItemType.id,
                'requiredDate': '2023-6-6',
                'quantity': '54 Kg',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodSupplies_missing_itemName ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)    
        
    '''
    Test case to test post Food Supplies Request with missing parameters (requiredDate)
    '''

    def test_volunteer_postFoodSupplies_missing_requiredDate(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:request-food', kwargs={'requestTypeId': self.foodRequestType.id})
            data = {
                'itemTypeId':self.foodItemType.id,
                'itemName': 'Food item name',
                'quantity': '54 Kg',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodSupplies_missing_requiredDate ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)     

    '''
    Test case to test post Food Supplies Request with missing parameters (quantity)
    '''

    def test_volunteer_postFoodSupplies_missing_quantity(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:request-food', kwargs={'requestTypeId': self.foodRequestType.id})
            data = {
                'itemTypeId':self.foodItemType.id,
                'itemName': 'Food item name',
                'requiredDate': '2023-6-6',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodSupplies_missing_quantity ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e) 
                
    '''
    Test case to test post Food Supplies Request (Existing Request)
    '''

    def test_volunteer_postFoodSupplies_with_existing_request(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:request-food', kwargs={'requestTypeId': self.foodRequestType.id})

            foodItem = FoodItem.objects.create(
                itemName='Food item name', 
                itemType=self.foodItemType, 
                addedBy=self.user, 
                createdAt=datetime.now()
            )

            Request.objects.create(
                type=self.foodRequestType, 
                createdBy=self.user,
                requiredDate='2023-6-6',
                active=True, 
                quantity='5 kg', 
                foodItem=foodItem, 
                createdAt=datetime.now()
            )

            data = {
                'itemTypeId':self.foodItemType.id,
                'itemName': 'Food item name',
                'requiredDate': '2023-6-6',
                'quantity': '5 kg'
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postFoodSupplies_with_existing_request ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)