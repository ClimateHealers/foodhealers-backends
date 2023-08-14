from django.test import TestCase
# Create your tests here.
from django.db import transaction
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import ( ItemType, Category, Address, Volunteer,
                      Vehicle, FoodEvent, Document, FoodItem,
                      FoodRecipe, DeliveryDetail, RequestType, 
                      Donation, EventVolunteer, CustomToken, 
                      Request, EventBookmark, Notification, VOLUNTEER_TYPE)
import json
from app.authentication import create_access_token, create_refresh_token
from rest_framework.test import force_authenticate
from datetime import datetime
from django.utils.datastructures import MultiValueDict


class UserOperations(APITestCase):
    urlpatterns = [
        path('v1/api/', include('app.urls')),
    ]

    @classmethod
    def setUpTestData(cls):
        with transaction.atomic():

            category, created = Category.objects.get_or_create(name='Breakfast', createdAt=datetime.now(), active=True)
            Category.objects.get_or_create(name='Lunch', createdAt=datetime.now(), active=True)
            Category.objects.get_or_create(name='Dinner', createdAt=datetime.now(), active=True)
            
            food_request_type, created = RequestType.objects.get_or_create(name='Food', createdAt=datetime.now(), active=True)
            RequestType.objects.get_or_create(name='Supplies', createdAt=datetime.now(), active=True)
            volunteer_request_type, created = RequestType.objects.get_or_create(name='Volunteer', createdAt=datetime.now(), active=True) 
            pickup_request_type, created = RequestType.objects.get_or_create(name='Pickup', createdAt=datetime.now(), active=True)

            food_item_type, created = ItemType.objects.get_or_create(name='Food', createdAt=datetime.now(), active=True)
            ItemType.objects.get_or_create(name='Supplies', createdAt=datetime.now(), active=True)

            user, created = Volunteer.objects.get_or_create(
                username='testuser@example.com' ,
                email='testuser@example.com',
                name='Test User',
                password='password123#',
                phoneNumber=99723234342,
                isVolunteer=True, 
                volunteerType=VOLUNTEER_TYPE[2][0],
            )

            vehicle, created = Vehicle.objects.get_or_create(
                make='Audi',
                model='R8',
                plateNumber='KA69F6969',
                vehicleColour='Black',
                active=True,
                createdAt=datetime.now(), 
                verified=True,
                owner=user
            )

            from app.authentication import create_access_token, create_refresh_token
            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id)
            expo_push_token = 'ExponentPushToken[NYM-Q0OmkFj9TUUAV2UPW7]'

            custom_token, created = CustomToken.objects.get_or_create(
                accessToken=access_token, refreshToken=refresh_token, user=user, expoPushToken=expo_push_token)

            cls.custom_token = custom_token
            cls.access_token = 'Token '+access_token
            cls.expo_push_token = expo_push_token
            cls.user = user
            cls.category = category
            cls.food_request_type = food_request_type
            cls.volunteer_request_type = volunteer_request_type
            cls.pickup_request_type = pickup_request_type 
            cls.food_item_type = food_item_type
            cls.vehicle = vehicle

            cls.test_email = 'user@example.com'
            cls.firebase_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImE1MWJiNGJkMWQwYzYxNDc2ZWIxYjcwYzNhNDdjMzE2ZDVmODkzMmIiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vZm9vZC1oZWFsZXJzLWI2YWI4IiwiYXVkIjoiZm9vZC1oZWFsZXJzLWI2YWI4IiwiYXV0aF90aW1lIjoxNjg5MTQxMjA1LCJ1c2VyX2lkIjoiS1BGZEJkWEVrdE8xeTR3bVFCMmR4dmYwSld6MSIsInN1YiI6IktQRmRCZFhFa3RPMXk0d21RQjJkeHZmMEpXejEiLCJpYXQiOjE2ODkxNDEyMDUsImV4cCI6MTY4OTE0NDgwNSwiZW1haWwiOiJtYWxpazkwMDBAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImVtYWlsIjpbIm1hbGlrOTAwMEBnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.MB5KylTs6GqQ0y_D67qH_Y8zbPe3OlFD2O2jgjfz8VYxb8tjzj2XFCLhG--2mySiSF10TSwFUpeQza4FnpfPfstRHgl2P7hogNenGFRzqblK-Dt_2bpnQy3FN5Y2gTIQXC89rhSjRZ8SMJusNvId0SVM1YvdfiuSFxyPYm2ZHeu9EE7b9Yvg-HvgBCpZWEmQO1QJnvU0xc24eUeaYWLQsZ0KB_iSTcqZVec6uUB6h33lt7oV3PuagvP241hCJL_knPKn-TQe4Lr1in_rydQb2M-GrXpk5BLT6K0T9kDi0HJy-fXLGPZpOFKvXSyqJ9JTB79A4x6xcAfeiIzkUOr15Q'
            cls.test_event_name = 'Test event'
            cls.event_additional_info = 'Free vegan Meals'
            cls.test_food_name = 'test Food'
            cls.test_ingredients = 'water, Salt, Rice'
            cls.test_cooking_instruction = 'Boil for 5 mins'
            cls.test_quantity = '54 Kg'
            cls.test_item_name = 'Food item name'

            # Test Cases Urls
            cls.onboarding_url = 'app:user-signup'
            cls.login_url = 'app:user-login'
            cls.find_food_url = 'app:find-food'
            cls.food_event_url = 'app:food-event'
            cls.bookmark_url = 'app:bookmark-event'
            cls.category_url = 'app:fetch-category'
            cls.get_recipe_url = 'app:food-recipe'
            cls.request_type_url = 'app:fetch-requestType'
            cls.request_food_url = 'app:request-food'
            cls.request_volunteer_url = 'app:request-volunteers'
            cls.donate_food_url = 'app:donate-food'
            cls.volunteer_profile_url = 'app:volunteer-profile'
            cls.volunteer_vehicle_url = 'app:volunteer-vehicle'
            cls.get_volunteer_notification_url = 'app:volunteer-notification'
            cls.volunteer_expotoken_url = 'app:volunteer-expo-push-token'

            print('<<<----------------- Start Test Cases ----------------------->>>')


    # user SignUp test cases
    '''
    Test case to test onboarding with valid data
    '''
    def test_user_onboarding_valid_data(self):
        session = self.client.session
        session['email'] = self.test_email
        session.save()

        url = reverse(self.onboarding_url)
        data = {
            'tokenId': self.firebase_token,
            'name': self.user.name,
            'email': self.test_email,
            'isVolunteer': True,
            'ExpoPushToken':self.expo_push_token
        }
        response = self.client.post(url, data, format='json')
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', result)
        self.assertIn('message', result)
        self.assertIn('userDetails', result)
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'], 'successfully created user')

        self.assertEqual(result['userDetails']['id'], 2)
        self.assertEqual(result['userDetails']['name'], self.user.name)
        self.assertEqual(result['userDetails']['email'], self.test_email)
        self.assertEqual(result['userDetails']['isDriver'], False)
        self.assertEqual(result['userDetails']['isVolunteer'], True)
        self.assertEqual(result['userDetails']['volunteerType'], 'food_seeker')
        self.assertEqual(result['userDetails']['phoneNumber'], '')

        print('1) ------ test case response for  : test_user_onboarding_valid_data ------', result)
    

    '''
    Test case to test onboarding with missing parameters (token_id)
    '''

    def test_user_onboarding_with_missing_tokenId(self):
        session = self.client.session
        session['email'] = self.test_email
        session.save()

        url = reverse(self.onboarding_url)
        data = {
            'name': self.user.name,
            'email': self.test_email,
            'isVolunteer': True,
            'ExpoPushToken':self.expo_push_token
        }
        response = self.client.post(url, data, format='json')
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', result)
        self.assertIn('message', result)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['message'], 'please enter valid token')

        print('2) ------ test case response for  : test_user_onboarding_with_missing_token_id ------',result)


    '''
    Test case to test onboarding with missing parameters (name)
    '''

    def test_user_onboarding_with_missing_name(self):
        session = self.client.session
        session['email'] = self.test_email
        session.save()

        url = reverse(self.onboarding_url)
        data = {
            'tokenId': self.firebase_token,
            'email': self.test_email,
            'isVolunteer': True,
            'ExpoPushToken':self.expo_push_token
        }
        response = self.client.post(url, data, format='json')
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertIn('success', result)
        self.assertIn('message', result)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['message'], 'please enter valid name')

        print('3) ------ test case response for  : test_user_onboarding_with_missing_name ------',result)


    '''
        Test case to test onboarding with missing parameters (email)
    '''

    def test_user_onboarding_with_missing_email(self):
        session = self.client.session
        session.save()

        url = reverse(self.onboarding_url)
        data = {
            'tokenId': self.firebase_token,
            'name': self.user.name,
            'isVolunteer': True,
            'ExpoPushToken':self.expo_push_token
        }
        response = self.client.post(url, data, format='json')
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertIn('success', result)        
        self.assertEqual(result['success'], False)

        print('4) ------ test case response for  : test_user_onboarding_with_missing_email ------',result)
    

    '''
        Test case to test onboarding with missing parameters (isVolunteer)
    '''

    def test_user_onboarding_with_missing_isVolunteer(self):
        session = self.client.session
        session['email'] = self.test_email
        session.save()

        url = reverse(self.onboarding_url)
        data = {
            'tokenId': self.firebase_token,
            'name': self.user.name,
            'email': self.test_email,
            'ExpoPushToken':self.expo_push_token
        }
        response = self.client.post(url, data, format='json')
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertIn('success', result)
        self.assertIn('message', result)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['message'], 'please enter if Volunteer or not')

        print('5) ------ test case response for  : test_user_onboarding_with_missing_isVolunteer ------' ,result)
 

    # user Login In test cases
    '''
    Test case to test login with valid data
    '''

    def test_user_login_valid_data(self):
        session = self.client.session
        session['email'] = self.user.email
        session.save()

        url = reverse(self.login_url)
        data = {
            'tokenId': self.firebase_token,
        }
        response = self.client.post(url, data, format='json')
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertIn('success', result)
        self.assertIn('message', result)
        self.assertIn('isAuthenticated', result)
        self.assertIn('token', result)
        self.assertIn('refreshToken', result)
        self.assertIn('user', result)

        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'], 'successfully signed in')

        self.assertIn('id', result['user'])
        self.assertIn('name', result['user'])
        self.assertIn('email', result['user'])
        self.assertIn('phoneNumber', result['user'])
        self.assertIn('isDriver', result['user'])
        self.assertIn('isVolunteer', result['user'])
        self.assertIn('volunteerType', result['user'])

        print('6) ------ test case response for  : test_user_login_valid_data ------',result)

    
    '''
    Test case to test login with missing parameters (token_id)
    '''

    def test_user_login_with_missing_token_id(self):
        session = self.client.session
        session['email'] = self.test_email
        session.save()
        
        url = reverse(self.login_url)
        data = {}
        response = self.client.post(url, data, format='json')
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertIn('success', result)
        self.assertIn('message', result)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['message'], 'Please provide a valid token')

        print('7) ------ test case response for  : test_user_login_with_missing_token_id ------',result)
        

    '''
    Test case to test login with missing parameters (email)
    '''

    def test_user_login_with_email_notExist(self):
        session = self.client.session
        session['email'] = ""
        session.save()

        url = reverse(self.login_url)
        data = {
            'tokenId': 'eyJhbGciO1Qid-hmd3L_DjrVMgIPIa-7Ztj209vo-bavQTUm_InW9vLCT=YTRkYz_06V-lnHXaf_c1bb6cQauj-U48q_C2sgW5t-UdabrwgD56Pw',
        }
        response = self.client.post(url, data, format='json')
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertIn('success', result)
        self.assertIn('message', result)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['message'], 'user with email does not exist')

        print('8) ------ test case response for  : test_user_login_with_email_notExist ------', result)

    # Volunteer Post Food Events test cases
    '''
    Test case to test post food Events with valid data
    '''
    def test_volunteer_postFoodEvents_valid_data(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.food_event_url)
            data = {
                'eventName':self.test_event_name,
                'lat': '23.5777',
                'lng': '72.5777',
                'alt': '54777',
                'eventStartDate': '2023-6-6',
                'eventEndDate': '2023-6-6',
                'additionalInfo':self.event_additional_info,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.food_event_url)

            address = Address.objects.create(lat=23.5777, lng=72.5777, alt=54777)
            FoodEvent.objects.create(
                name=self.test_event_name,
                address=address,
                eventStartDate='2023-6-6',
                eventEndDate='2023-6-6', 
                createdAt=datetime.now(),
                createdBy=self.user,
                additionalInfo=self.event_additional_info,
                active=True
            )
    
            data = {
                'eventName':self.test_event_name,
                'lat': '23.5777',
                'lng': '72.5777',
                'alt': '54777',
                'eventStartDate': '2023-6-6',
                'eventEndDate': '2023-6-6',
                'additionalInfo':self.event_additional_info,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.food_event_url)
            data = {
                'eventName':self.test_event_name,
                'lng': '52.5777',
                'alt': '54777',
                'eventStartDate': '2023-06-06',
                'eventEndDate': '2023-06-06',
                'additionalInfo':self.event_additional_info,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.food_event_url)
            data = {
                'eventName':self.test_event_name,
                'lat': '22.5777',
                'alt': '54777',
                'eventStartDate': '2023-06-06',
                'eventEndDate': '2023-06-06',
                'additionalInfo':self.event_additional_info,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.food_event_url)
            data = {
                'eventName':self.test_event_name,
                'lat': '22.5777',
                'lng': '52.5777',
                'eventStartDate': '2023-06-06',
                'eventEndDate': '2023-06-06',
                'additionalInfo':self.event_additional_info,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.food_event_url)
            data = {
                'eventName':self.test_event_name,
                'lat': '22.5777',
                'lng': '52.5777',
                'alt': '54777',
                'eventEndDate': '2023-06-06',
                'additionalInfo':self.event_additional_info,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.food_event_url)
            data = {
                'eventName':self.test_event_name,
                'lat': '22.5777',
                'lng': '52.5777',
                'alt': '54777',
                'eventStartDate': '2023-06-06',
                'additionalInfo':self.event_additional_info,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.food_event_url)
            data = {
                'eventName':self.test_event_name,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.food_event_url)

            address = Address.objects.create(lat=23.5777, lng=72.5777, alt=54777)
            FoodEvent.objects.create(
                name=self.test_event_name,
                address=address,
                eventStartDate='2023-6-6',
                eventEndDate='2023-6-6', 
                createdAt=datetime.now(),
                createdBy=self.user,
                additionalInfo=self.event_additional_info,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.food_event_url)
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
            # self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.find_food_url)

            address = Address.objects.create(lat=23.5777, lng=72.5777, alt=54777)
            FoodEvent.objects.create(
                name=self.test_event_name,
                address=address,
                eventStartDate='2023-6-6',
                eventEndDate='2023-6-6', 
                createdAt=datetime.now(),
                createdBy=self.user,
                additionalInfo=self.event_additional_info,
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
            # self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.find_food_url)
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
            # self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.find_food_url)
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
            # self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.find_food_url)
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
            # self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.find_food_url)
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
            # self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.find_food_url)
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
            # self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.find_food_url)
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.category_url,)
            
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_type_url,)
            
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.bookmark_url)
            
            food_event = FoodEvent.objects.create(
                name=self.test_event_name,
                organizerPhoneNumber=997263, 
                eventStartDate=datetime.now(),
                eventEndDate=datetime.now(), 
                createdAt=datetime.now(),
                additionalInfo=self.event_additional_info,
                active=True
            )
            
            data = {
                'eventId': food_event.id,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.bookmark_url)
            
            food_event = FoodEvent.objects.create(
                name=self.test_event_name,
                organizerPhoneNumber=997263, 
                eventStartDate=datetime.now(),
                eventEndDate=datetime.now(), 
                createdAt=datetime.now(),
                additionalInfo=self.event_additional_info,
                active=True
            )
            
            data = {
                'eventId': food_event.id,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.bookmark_url)
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.bookmark_url)
            
            food_event = FoodEvent.objects.create(
                name=self.test_event_name,
                organizerPhoneNumber=997263, 
                eventStartDate=datetime.now(),
                eventEndDate=datetime.now(), 
                createdAt=datetime.now(),
                additionalInfo=self.event_additional_info,
                active=True
            )

            EventBookmark.objects.create(user=self.user, event=food_event, createdAt=datetime.now())
            data = {'eventId': food_event.id}
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.bookmark_url)
            
            food_event = FoodEvent.objects.create(
                name=self.test_event_name,
                organizerPhoneNumber=997263, 
                eventStartDate=datetime.now(),
                eventEndDate=datetime.now(), 
                createdAt=datetime.now(),
                additionalInfo=self.event_additional_info,
                active=True
            )

            EventBookmark.objects.create(user=self.user, event=food_event, createdAt=datetime.now())

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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.bookmark_url)
            
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.get_recipe_url, kwargs={'category_id': self.category.id})
            data = {
                'foodName':self.test_food_name,
                'ingredients': self.test_ingredients,
                'cookingInstructions': self.test_cooking_instruction,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)

            url = reverse(self.get_recipe_url, kwargs={'category_id': 0})
            data = {
                'foodName':self.test_food_name,
                'ingredients': self.test_ingredients,
                'cookingInstructions': self.test_cooking_instruction,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.get_recipe_url, kwargs={'category_id': self.category.id})

            FoodRecipe.objects.create(
                foodName=self.test_food_name, 
                ingredients=self.test_ingredients, 
                cookingInstructions=self.test_cooking_instruction, 
                category=self.category
            )

            data = {
                'foodName':self.test_food_name,
                'ingredients': self.test_ingredients,
                'cookingInstructions': self.test_cooking_instruction,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.get_recipe_url, kwargs={'category_id': self.category.id})
            
            data = {
                'ingredients': self.test_ingredients,
                'cookingInstructions': self.test_cooking_instruction,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.get_recipe_url, kwargs={'category_id': self.category.id})
            
            data = {
                'foodName': self.test_food_name,
                'cookingInstructions': self.test_cooking_instruction,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.get_recipe_url, kwargs={'category_id': self.category.id})
            
            data = {
                'foodName': self.test_food_name,
                'ingredients': self.test_ingredients,
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
    #         self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
    #         url = reverse(self.get_recipe_url)
            
    #         data = {
    #             'foodName': self.test_food_name,
    #             'ingredients': self.test_ingredients,
    #             'cookingInstructions': self.test_cooking_instruction,
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.get_recipe_url, kwargs={'category_id': self.category.id})

            FoodRecipe.objects.create(
                foodName=self.test_food_name, 
                ingredients=self.test_ingredients, 
                cookingInstructions=self.test_cooking_instruction, 
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.get_recipe_url, kwargs={'category_id': self.category.id})
    
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
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.get_recipe_url, kwargs={'category_id': 0})

            FoodRecipe.objects.create(
                foodName=self.test_food_name, 
                ingredients=self.test_ingredients, 
                cookingInstructions=self.test_cooking_instruction, 
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

    def test_volunteer_requestFoodSupplies_valid_data(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_food_url, kwargs={'request_type_id': self.food_request_type.id})
            
            data = {
                'itemTypeId':self.food_item_type.id,
                'itemName': self.test_item_name,
                'requiredDate': '2023-6-6',
                'quantity': self.test_quantity,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestFoodSupplies_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    '''
    Test case to test post food Supplies Request with ItemTypeId Does not exist
    '''

    def test_volunteer_requestFoodSupplies_invalid_itemTypeId(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_food_url, kwargs={'request_type_id': self.food_request_type.id})
            
            data = {
                'itemTypeId':0,
                'itemName': self.test_item_name,
                'requiredDate': '2023-6-6',
                'quantity': self.test_quantity,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestFoodSupplies_invalid_itemTypeId ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post food Supplies Request with requestTypeId Does not exist
    '''

    def test_volunteer_requestFoodSupplies_invalid_requestTypeId(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_food_url, kwargs={'request_type_id': 0})
            
            data = {
                'itemTypeId':self.food_item_type.id,
                'itemName': self.test_item_name,
                'requiredDate': '2023-6-6',
                'quantity': self.test_quantity,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestFoodSupplies_invalid_requestTypeId ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Food Supplies Request with missing parameters (itemTypeId)
    '''

    def test_volunteer_requestFoodSupplies_missing_itemTypeId(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_food_url, kwargs={'request_type_id': self.food_request_type.id})
            data = {
                'itemName': self.test_item_name,
                'requiredDate': '2023-6-6',
                'quantity': self.test_quantity,
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestFoodSupplies_missing_itemTypeId ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Food Supplies Request with missing parameters (itemName)
    '''

    def test_volunteer_requestFoodSupplies_missing_itemName(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_food_url, kwargs={'request_type_id': self.food_request_type.id})
            data = {
                'itemTypeId':self.food_item_type.id,
                'requiredDate': '2023-6-6',
                'quantity': self.test_quantity,
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestFoodSupplies_missing_itemName ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)    
        
    '''
    Test case to test post Food Supplies Request with missing parameters (requiredDate)
    '''

    def test_volunteer_requestFoodSupplies_missing_requiredDate(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_food_url, kwargs={'request_type_id': self.food_request_type.id})
            data = {
                'itemTypeId':self.food_item_type.id,
                'itemName': self.test_item_name,
                'quantity': self.test_quantity,
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestFoodSupplies_missing_requiredDate ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)     

    '''
    Test case to test post Food Supplies Request with missing parameters (quantity)
    '''

    def test_volunteer_requestFoodSupplies_missing_quantity(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_food_url, kwargs={'request_type_id': self.food_request_type.id})
            data = {
                'itemTypeId':self.food_item_type.id,
                'itemName': self.test_item_name,
                'requiredDate': '2023-6-6',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestFoodSupplies_missing_quantity ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e) 
                
    '''
    Test case to test post Food Supplies Request (Existing Request)
    '''

    def test_volunteer_requestFoodSupplies_with_existing_request(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_food_url, kwargs={'request_type_id': self.food_request_type.id})

            food_item = FoodItem.objects.create(
                itemName=self.test_item_name, 
                itemType=self.food_item_type, 
                addedBy=self.user, 
                createdAt=datetime.now()
            )

            Request.objects.create(
                type=self.food_request_type, 
                createdBy=self.user,
                requiredDate='2023-6-6',
                active=True, 
                quantity='5 kg', 
                foodItem=food_item, 
                createdAt=datetime.now()
            )

            data = {
                'itemTypeId':self.food_item_type.id,
                'itemName': self.test_item_name,
                'requiredDate': '2023-6-6',
                'quantity': '5 kg'
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestFoodSupplies_with_existing_request ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    # Volunteer/Organizer Post Volunteer Request test cases
    '''
    Test case to test post Volunteer Request with valid data
    '''

    def test_volunteer_requestVolunteer_valid_data(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_volunteer_url, kwargs={'request_type_id': self.food_request_type.id})
            
            food_event = FoodEvent.objects.create(
                name=self.test_event_name,
                organizerPhoneNumber=997263, 
                eventStartDate='2023-05-05',
                eventEndDate='2023-05-05', 
                createdAt=datetime.now(),
                additionalInfo=self.event_additional_info,
                active=True,
                createdBy=self.user,
            )

            data = {
                'eventId':food_event.id,
                'lat': '12.916540',
                'lng': '77.651950',
                'alt': '4500',
                'requiredDate': '2023-05-05',
                'numberOfVolunteers': '15',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestVolunteer_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    '''
    Test case to test post Volunteer Request with eventId Does not exist
    '''

    def test_volunteer_requestVolunteers_invalid_eventId(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_volunteer_url, kwargs={'request_type_id': self.food_request_type.id})
            
            data = {
                'eventId': 0,
                'lat': '12.916540',
                'lng': '77.651950',
                'alt': '4500',
                'requiredDate': '2023-05-05',
                'numberOfVolunteers': '15',
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestVolunteers_invalid_eventId ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Volunteer Request with requestTypeId Does not exist
    '''

    def test_volunteer_requestVolunteer_invalid_requestTypeId(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_volunteer_url, kwargs={'request_type_id': 0})
            
            food_event = FoodEvent.objects.create(
                name=self.test_event_name,
                organizerPhoneNumber=997263, 
                eventStartDate='2023-05-05',
                eventEndDate='2023-05-05', 
                createdAt=datetime.now(),
                additionalInfo=self.event_additional_info,
                active=True,
                createdBy=self.user,
            )

            data = {
                'eventId':food_event.id,
                'lat': '12.916540',
                'lng': '77.651950',
                'alt': '4500',
                'requiredDate': '2023-05-05',
                'numberOfVolunteers': '15',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestVolunteer_invalid_requestTypeId ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Volunteers Request with missing parameters (eventId)
    '''

    def test_volunteer_requestVolunteers_missing_eventId(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_volunteer_url, kwargs={'request_type_id': self.food_request_type.id})
            
            data = {
                'lat': '12.916540',
                'lng': '77.651950',
                'alt': '4500',
                'requiredDate': '2023-05-05',
                'numberOfVolunteers': '15',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestVolunteers_missing_eventId ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Volunteers Request with missing parameters (lat)
    '''

    def test_volunteer_requestVolunteers_missing_lat(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_volunteer_url, kwargs={'request_type_id': self.food_request_type.id})
            
            food_event = FoodEvent.objects.create(
                name=self.test_event_name,
                organizerPhoneNumber=997263, 
                eventStartDate='2023-05-05',
                eventEndDate='2023-05-05', 
                createdAt=datetime.now(),
                additionalInfo=self.event_additional_info,
                active=True,
                createdBy=self.user,
            )

            data = {
                'eventId':food_event.id,
                'lng': '77.651950',
                'alt': '4500',
                'requiredDate': '2023-05-05',
                'numberOfVolunteers': '15',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestVolunteers_missing_lat ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)    

    '''
    Test case to test post Volunteers Request with missing parameters (lng)
    '''

    def test_volunteer_requestVolunteers_missing_lng(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_volunteer_url, kwargs={'request_type_id': self.food_request_type.id})
            
            food_event = FoodEvent.objects.create(
                name=self.test_event_name,
                organizerPhoneNumber=997263, 
                eventStartDate='2023-05-05',
                eventEndDate='2023-05-05', 
                createdAt=datetime.now(),
                additionalInfo=self.event_additional_info,
                active=True,
                createdBy=self.user,
            )

            data = {
                'eventId':food_event.id,
                'lat': '12.916540',
                'alt': '4500',
                'requiredDate': '2023-05-05',
                'numberOfVolunteers': '15',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestVolunteers_missing_lng ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)  
        
    '''
    Test case to test post Volunteers Request with missing parameters (alt)
    '''

    def test_volunteer_requestVolunteers_missing_alt(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_volunteer_url, kwargs={'request_type_id': self.food_request_type.id})
            
            food_event = FoodEvent.objects.create(
                name=self.test_event_name,
                organizerPhoneNumber=997263, 
                eventStartDate='2023-05-05',
                eventEndDate='2023-05-05', 
                createdAt=datetime.now(),
                additionalInfo=self.event_additional_info,
                active=True,
                createdBy=self.user,
            )

            data = {
                'eventId':food_event.id,
                'lat': '12.916540',
                'lng': '77.651950',
                'requiredDate': '2023-05-05',
                'numberOfVolunteers': '15',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestVolunteers_missing_alt ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)  
        
    '''
    Test case to test post Volunteers Request with missing parameters (requiredDate)
    '''

    def test_volunteer_requestVolunteers_missing_requiredDate(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_volunteer_url, kwargs={'request_type_id': self.food_request_type.id})
            
            food_event = FoodEvent.objects.create(
                name=self.test_event_name,
                organizerPhoneNumber=997263, 
                eventStartDate='2023-05-05',
                eventEndDate='2023-05-05', 
                createdAt=datetime.now(),
                additionalInfo=self.event_additional_info,
                active=True,
                createdBy=self.user,
            )

            data = {
                'eventId':food_event.id,
                'lat': '12.916540',
                'lng': '77.651950',
                'alt': '4500',
                'numberOfVolunteers': '15',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestVolunteers_missing_requiredDate ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)     

    '''
    Test case to test post Volunteers Request with missing parameters (numberOfVolunteers)
    '''

    def test_volunteer_requestVolunteers_missing_numberOfVolunteers(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_volunteer_url, kwargs={'request_type_id': self.food_request_type.id})
            
            food_event = FoodEvent.objects.create(
                name=self.test_event_name,
                organizerPhoneNumber=997263, 
                eventStartDate='2023-05-05',
                eventEndDate='2023-05-05', 
                createdAt=datetime.now(),
                additionalInfo=self.event_additional_info,
                active=True,
                createdBy=self.user,
            )

            data = {
                'eventId':food_event.id,
                'lat': '12.916540',
                'lng': '77.651950',
                'alt': '4500',
                'requiredDate': '2023-05-05',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestVolunteers_missing_numberOfVolunteers ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e) 
                
    '''
    Test case to test post Volunteers Request (Existing Request)
    '''

    def test_volunteer_requestVolunteers_with_existing_request(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.request_volunteer_url, kwargs={'request_type_id': self.food_request_type.id})

            food_event = FoodEvent.objects.create(
                name=self.test_event_name,
                organizerPhoneNumber=997263, 
                eventStartDate='2023-05-05',
                eventEndDate='2023-05-05', 
                createdAt=datetime.now(),
                additionalInfo=self.event_additional_info,
                active=True,
                createdBy=self.user,
            )

            Request.objects.create(
                type=self.food_request_type, 
                createdBy=self.user,
                requiredDate='2023-05-05',
                active=True, 
                quantity='15', 
                foodEvent=food_event, 
                createdAt=datetime.now()
            )

            data = {
                'eventId':food_event.id,
                'lat': '12.916540',
                'lng': '77.651950',
                'alt': '4500',
                'requiredDate': '2023-05-05',
                'numberOfVolunteers': '15',
            }

            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_requestVolunteers_with_existing_request ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    # Volunteer Post Donate Food test cases
    '''
    Test case to test post  Donate Food with valid data
    '''
    def test_volunteer_postDonateFood_valid_data(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)
            data = {
                'itemTypeId': '1',
                'foodName': "foodName",
                'quantity': self.test_quantity,
                'pickupDate': '2023-05-05',
                'lat': 12.916540,
                'lng': 77.651950,
                'alt': 4500,
                'phoneNumber':99802732,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postDonateFood_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
    
    '''
        Test case to test post Donate Food with valid data But ItemTypeId not Exist 
    '''
    
    def test_volunteer_postDonateFood_ItemTypeId_notExist(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)
            data = {
                'itemTypeId': 0,
                'foodName': "foodName",
                'quantity': self.test_quantity,
                'pickupDate': '2023-05-05',
                'lat': 12.916540,
                'lng': 77.651950,
                'alt': 4500,
                'phoneNumber':99802732,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postDonateFood_ItemTypeId_notExist ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    '''
    Test case to test post Donate Food With donation is Already Present
    '''
    def test_volunteer_postDonateFood_donation_alreadyPresent(self):

        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)

            pickup_address = Address.objects.create(lat=12.916540, lng=77.651950, alt=4500)
            food_item = FoodItem.objects.create(
                itemName='foodName',
                addedBy=self.user, 
                itemType= self.food_item_type, 
                createdAt=datetime.now()
            )
            delivery_details = DeliveryDetail.objects.create(
                pickupAddress=pickup_address, 
                pickupDate='2023-05-05'
            )
            Donation.objects.create(
                donationType= self.food_item_type,
                foodItem=food_item,
                quantity=self.test_quantity,
                donatedBy=self.user,
                needsPickup=True,
                delivery=delivery_details,
            )

            data = {
                'itemTypeId': '1',
                'foodName': "foodName",
                'quantity': self.test_quantity,
                'pickupDate': '2023-05-05',
                'lat': 12.916540,
                'lng': 77.651950,
                'alt': 4500,
                'phoneNumber':99802732,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postDonateFood_donation_alreadyPresent ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    '''
    Test case to test post Donate Food with missing parameters (itemTypeId)
    '''
    def test_volunteer_postDonateFood_missing_itemTypeId(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)
            data = {
                'foodName': "foodName",
                'quantity': self.test_quantity,
                'pickupDate': '2023-05-05',
                'lat': 12.916540,
                'lng': 77.651950,
                'alt': 4500,
                'phoneNumber':99802732,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postDonateFood_missing_itemTypeId ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    '''
    Test case to test post Donate Food with missing parameters (foodName)
    '''
    def test_volunteer_postDonateFood_missing_foodName(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)
            data = {
                'itemTypeId': '1',
                'quantity': self.test_quantity,
                'pickupDate': '2023-05-05',
                'lat': 12.916540,
                'lng': 77.651950,
                'alt': 4500,
                'phoneNumber':99802732,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postDonateFood_missing_foodName ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Donate Food with missing parameters (quantity)
    '''
    def test_volunteer_postDonateFood_missing_quantity(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)
            data = {
                'itemTypeId': '1',
                'foodName': "foodName",
                'pickupDate': '2023-05-05',
                'lat': 12.916540,
                'lng': 77.651950,
                'alt': 4500,
                'phoneNumber':99802732,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postDonateFood_missing_quantity ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Donate Food with missing parameters (pickupDate)
    '''
    def test_volunteer_postDonateFood_missing_pickupDate(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)
            data = {
                'itemTypeId': '1',
                'foodName': "foodName",
                'quantity': self.test_quantity,
                'lat': 12.916540,
                'lng': 77.651950,
                'alt': 4500,
                'phoneNumber':99802732,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postDonateFood_missing_pickupDate ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Donate Food with missing parameters (lat)
    '''
    def test_volunteer_postDonateFood_missing_lat(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)
            data = {
                'itemTypeId': '1',
                'foodName': "foodName",
                'quantity': self.test_quantity,
                'pickupDate': '2023-05-05',
                'lng': 77.651950,
                'alt': 4500,
                'phoneNumber':99802732,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postDonateFood_missing_lat ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Donate Food with missing parameters (lng)
    '''
    def test_volunteer_postDonateFood_missing_lng(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)
            data = {
                'itemTypeId': '1',
                'foodName': "foodName",
                'quantity': self.test_quantity,
                'pickupDate': '2023-05-05',
                'lat': 12.916540,
                'alt': 4500,
                'phoneNumber':99802732,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postDonateFood_missing_lng ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    '''
    Test case to test post Donate Food with missing parameters (alt)
    '''
    def test_volunteer_postDonateFood_missing_alt(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)
            data = {
                'itemTypeId': '1',
                'foodName': "foodName",
                'quantity': self.test_quantity,
                'pickupDate': '2023-05-05',
                'lat': 12.916540,
                'lng': 77.651950,
                'phoneNumber':99802732,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postDonateFood_missing_alt ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test post Donate Food with missing parameters (phoneNumber)
    '''
    def test_volunteer_postDonateFood_missing_phoneNumber(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)
            data = {
                'itemTypeId': '1',
                'foodName': "foodName",
                'quantity': self.test_quantity,
                'pickupDate': '2023-05-05',
                'lat': 12.916540,
                'lng': 77.651950,
                'alt': 4500,
            }
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_postDonateFood_missing_phoneNumber ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test GET Donate Food History with donation Present
    '''
    def test_volunteer_getDonateFoodHistory_with_donationPresent(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)

            food_item = FoodItem.objects.create(
                itemName='foodName', 
                addedBy=self.user, 
                itemType=self.food_item_type, 
                createdAt=datetime.now()
            )

            pickup_address = Address.objects.create(
                lat=12.916540, lng=77.651950, alt=4500
            )

            delivery_details = DeliveryDetail.objects.create(
                pickupAddress=pickup_address, pickupDate='2023-05-05'
            )

            Donation.objects.create(
                donationType=self.food_item_type,
                foodItem=food_item,
                quantity='50 kg',
                donatedBy=self.user,
                needsPickup=True,
                delivery=delivery_details,
            )  

            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_getDonateFoodHistory_donationPresent ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test GET Donate Food History with no donation Present
    '''
    def test_volunteer_getDonateFoodHistory_with_noDonationPresent(self):
        
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.donate_food_url)

            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_getDonateFoodHistory_with_noDonationPresent ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    # Volunteer View Profile test cases
    '''
    Test case to test Get Volunteer Profile with valid data
    '''
    def test_volunteer_getVolunteerProfile_valid_data(self):
        
        try:

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_profile_url)
            
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_getVolunteerProfile_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    '''
    Test case to test Update Volunteer Profile with valid data
    '''
    def test_volunteer_updateVolunteerProfile_validData(self):
        
        try:
            data = {
                'name':'update User',
                'email':self.user.email,
                'lat':22.5777,
                'lng':52.5777,
                'alt':54777,
                'phoneNumber':9178626772,
                'volunteerType':VOLUNTEER_TYPE[3][0],
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_profile_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVolunteerProfile_validData ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)   
        
    '''
    Test case to test Update Volunteer Profile for volunteer with email does not exist
    '''
    def test_volunteer_updateVolunteerProfile_email_notExist(self):
        
        try:
            data = {
                'name':self.user.name,
                'email':'noemail@example.com',
                'lat':22.5777,
                'lng':52.5777,
                'alt':54777,
                'phoneNumber':9178626772,
                'volunteerType':VOLUNTEER_TYPE[3][0],
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_profile_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVolunteerProfile_email_notExist ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)   
        
    '''
    Test case to test Update Volunteer Profile with missing parameter (name)
    '''
    def test_volunteer_updateVolunteerProfile_missing_name(self):
        
        try:
            data = {
                'email':self.user.email,
                'lat':22.5777,
                'lng':52.5777,
                'alt':54777,
                'phoneNumber':9178626772,
                'volunteerType':VOLUNTEER_TYPE[3][0],
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_profile_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVolunteerProfile_missing_name ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)   
        
    '''
    Test case to test Update Volunteer Profile with missing parameter (email)
    '''
    def test_volunteer_updateVolunteerProfile_missing_email(self):
        
        try:
            data = {
                'name':self.user.name,
                'lat':22.5777,
                'lng':52.5777,
                'alt':54777,
                'phoneNumber':9178626772,
                'volunteerType':VOLUNTEER_TYPE[3][0],
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_profile_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVolunteerProfile_missing_email ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)   
        
    '''
    Test case to test Update Volunteer Profile with missing parameter (lat)
    '''
    def test_volunteer_updateVolunteerProfile_missing_lat(self):
        
        try:
            data = {
                'name':self.user.name,
                'email':self.user.email,
                'lng':52.5777,
                'alt':54777,
                'phoneNumber':9178626772,
                'volunteerType':VOLUNTEER_TYPE[3][0],
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_profile_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVolunteerProfile_missing_lat ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)   
        
    '''
    Test case to test Update Volunteer Profile with missing parameter (lng)
    '''
    def test_volunteer_updateVolunteerProfile_missing_lng(self):
        
        try:
            data = {
                'name':self.user.name,
                'email':self.user.email,
                'lat':22.5777,
                'alt':54777,
                'phoneNumber':9178626772,
                'volunteerType':VOLUNTEER_TYPE[3][0],
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_profile_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVolunteerProfile_missing_lng ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)   
        
    '''
    Test case to test Update Volunteer Profile with missing parameter (alt)
    '''
    def test_volunteer_updateVolunteerProfile_missing_alt(self):
        
        try:
            data = {
                'name':self.user.name,
                'email':self.user.email,
                'lat':22.5777,
                'lng':52.5777,
                'phoneNumber':9178626772,
                'volunteerType':VOLUNTEER_TYPE[3][0],
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_profile_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVolunteerProfile_missing_alt ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)   
        
    '''
    Test case to test Update Volunteer Profile with missing parameter (phoneNumber)
    '''
    def test_volunteer_updateVolunteerProfile_missing_phoneNumber(self):
        
        try:
            data = {
                'name':self.user.name,
                'email':self.user.email,
                'lat':22.5777,
                'lng':52.5777,
                'alt':54777,
                'volunteerType':VOLUNTEER_TYPE[3][0],
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_profile_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVolunteerProfile_missing_phoneNumber ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)   
        
    '''
    Test case to test Update Volunteer Profile with missing parameter (volunteerType)
    '''
    def test_volunteer_updateVolunteerProfile_missing_volunteerType(self):
        
        try:
            data = {
                'name':self.user.name,
                'email':self.user.email,
                'lat':22.5777,
                'lng':52.5777,
                'alt':54777,
                'phoneNumber':9178626772,
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_profile_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVolunteerProfile_missing_volunteerType ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)   
        
    # Volunteer Vehicle test cases
    '''
    Test case to test Get Vehicle Details with valid data
    '''
    def test_volunteer_getVehicleDetails_valid_data(self):
        
        try:

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_getVehicleDetails_valid_data ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test Get Vehicle Details with No Vehicle details
    '''
    def test_volunteer_getVehicleDetails_noVehicle_present(self):
        
        try:
            
            volunteer = Volunteer.objects.create(name = 'UserTestVolunteer')
            access_token = create_access_token(volunteer.id)

            self.client.credentials(HTTP_AUTHORIZATION='Token ' + access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_getVehicleDetails_noVehicle_present ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)

    '''
    Test case to test Add Vehicle Details with valid data
    '''
    def test_volunteer_addVehicleDetails_validData(self):
        
        try:
            
            data = {
                'make':'Audi', 
                'model':'R8',
                'vehicleColour':'Blue',
                'plateNumber':'AB77C7777',
                'active':False,
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_addVehicleDetails_validData ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)   
        
    '''
    Test case to test Add Vehicle Details with Vehicle Already exist
    '''
    def test_volunteer_addVehicleDetails_vehicle_alreadyExist(self):
        
        try:
            
            data = {
                'make':'Audi', 
                'model':'R8',
                'vehicleColour':'Black',
                'plateNumber':'KA69F6969',
                'active':True,
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_addVehicleDetails_vehicle_alreadyExist ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e) 
        
    '''
    Test case to test Add Vehicle Details with missing parameter (make)
    '''
    def test_volunteer_addVehicleDetails_missing_make(self):
        
        try:
            
            data = {
                'model':'R8',
                'vehicleColour':'Blue',
                'plateNumber':'AB77C7777',
                'active':False,
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_addVehicleDetails_missing_make ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e) 

    '''
    Test case to test Add Vehicle Details with missing parameter (model)
    '''
    def test_volunteer_addVehicleDetails_missing_model(self):
        
        try:
            
            data = {
                'make':'Audi', 
                'vehicleColour':'Blue',
                'plateNumber':'AB77C7777',
                'active':False,
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_addVehicleDetails_missing_model ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e) 
        
    '''
    Test case to test Add Vehicle Details with missing parameter (vehicleColour)
    '''
    def test_volunteer_addVehicleDetails_missing_vehicleColour(self):
        
        try:
            
            data = {
                'make':'Audi', 
                'model':'R8',
                'plateNumber':'AB77C7777',
                'active':False,
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_addVehicleDetails_missing_vehicleColour ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e) 
        
    '''
    Test case to test Add Vehicle Details with missing parameter (plateNumber)
    '''
    def test_volunteer_addVehicleDetails_missing_plateNumber(self):
        
        try:
            
            data = {
                'make':'Audi', 
                'model':'R8',
                'vehicleColour':'Blue',
                'active':False,
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_addVehicleDetails_missing_plateNumber ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e) 
        
    '''
    Test case to test Add Vehicle Details with missing parameter (active)
    '''
    def test_volunteer_addVehicleDetails_missing_active(self):
        
        try:
            
            data = {
                'make':'Audi', 
                'model':'R8',
                'vehicleColour':'Blue',
                'plateNumber':'AB77C7777',
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.post(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_addVehicleDetails_missing_active ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test Update Vehicle Details with valid data
    '''
    def test_volunteer_updateVehicleDetails_validData(self):
        
        try:
            
            data = {
                'vehicleId':self.vehicle.id,
                'vehicleColour':'Blue',
                'plateNumber':'AB77C7777',
                'active':False,
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVehicleDetails_validData ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)   
        
    '''
    Test case to test Update Vehicle Details with Vehicleid not exist
    '''
    def test_volunteer_updateVehicleDetails_vehicleid_notExist(self):
        
        try:
            
            data = {
                'vehicleId':0,
                'vehicleColour':'Blue',
                'plateNumber':'AB77C7777',
                'active':False,
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVehicleDetails_vehicleid_notExist ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e) 
        
    '''
    Test case to test Update Vehicle Details with missing parameter (vehicleId)
    '''
    def test_volunteer_updateVehicleDetails_missing_vehicleId(self):
        
        try:
            
            data = {
                'vehicleColour':'Blue',
                'plateNumber':'AB77C7777',
                'active':False,
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVehicleDetails_missing_vehicleId ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e) 

    '''
    Test case to test Update Vehicle Details with missing parameter (vehicleColour)
    '''
    def test_volunteer_updateVehicleDetails_missing_vehicleColour(self):
        
        try:
            
            data = {
                'vehicleId':0,
                'plateNumber':'AB77C7777',
                'active':False,
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVehicleDetails_missing_vehicleColour ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e) 
        
    '''
    Test case to test Update Vehicle Details with missing parameter (plateNumber)
    '''
    def test_volunteer_updateVehicleDetails_missing_plateNumber(self):
        
        try:
            
            data = {
                'vehicleId':0,
                'vehicleColour':'Blue',
                'active':False,
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVehicleDetails_missing_plateNumber ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e) 
        
    '''
    Test case to test Update Vehicle Details with missing parameter (active)
    '''
    def test_volunteer_updateVehicleDetails_missing_active(self):
        
        try:
            
            data = {
                'vehicleId':0,
                'vehicleColour':'Blue',
                'plateNumber':'AB77C7777',
            }

            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.volunteer_vehicle_url)
            
            response = self.client.put(url, data, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_updateVehicleDetails_missing_active ------',result)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test get Notification for volunteer (Existing Notifications)
    '''

    def test_volunteer_getNotification(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.get_volunteer_notification_url)

            Notification.objects.create(
                user=self.user,
                title='Event Rejected',
                message='Your Event has beend Rejected', 
                notificationType='event'
            )
    
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_getNotification ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)
        
    '''
    Test case to test get Notifications for volunteer (No Notifications)
    '''

    def test_volunteer_getNotification_with_noNotification(self):
        try:
            self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
            url = reverse(self.get_volunteer_notification_url)
            response = self.client.get(url, format='json')
            result = json.loads(response.content)
            print('------ test case response for  : test_volunteer_getNotification_with_noNotification ------',result)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return result
        except Exception as e:
            return str(e)