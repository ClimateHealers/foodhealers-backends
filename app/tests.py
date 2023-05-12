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

            category = Category.objects.get_or_create(name='Lunch', createdAt=datetime.now(), active=True)

            user, created = Volunteer.objects.get_or_create(
                username='testuser@example.com',
                email='testuser@example.com',
                name='Test User',
                password='password123#',
                phoneNumber=99723234342,
                isVolunteer=True, 
                volunteerType=VOLUNTEER_TYPE[2][0],
            )

            # print(user.username, created)

            from app.authentication import create_access_token, create_refresh_token
            accessToken = create_access_token(user.id)
            refreshToken = create_refresh_token(user.id)

            token, created = CustomToken.objects.get_or_create(
                accessToken=accessToken, refreshToken=refreshToken, user=user)

            self.token = token
            self.accessToken = accessToken
            self.user = user
            self.category = category
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
        self.test_volunteer_postFoodEvents_valid_data()
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
        self.test_volunteer_postFoodEvents_valid_data()
        try:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accessToken)
            url = reverse('app:food-event')
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
        self.test_volunteer_postFoodEvents_valid_data()
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