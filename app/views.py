# Create your views here.
import uuid
import firebase_admin.auth as auth
import matplotlib.pyplot as plt
import io
import urllib, base64
import calendar
import tempfile
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.authentication import create_access_token, create_refresh_token, VolunteerPermissionAuthentication, VolunteerTokenAuthentication 
from .models import ( ItemType, Category, Address, Volunteer, Vehicle, FoodEvent, Document, FoodItem, FoodRecipe, DeliveryDetail, RequestType, 
                      Donation, EventVolunteer, CustomToken, Request, EventBookmark, Notification, VOLUNTEER_TYPE, DOCUMENT_TYPE, EVENT_STATUS)
from .serializers import (UserProfileSerializer, FoodEventSerializer, BookmarkedEventSerializer, CategorySerializer, FoodRecipeSerializer,
                          RequestTypeSerializer, DonationSerializer, VehicleSerializer, NotificationSerializer )
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.db.models import Q
from rest_framework.parsers import MultiPartParser
from django.core.files.base import File
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.utils import timezone
from geopy.distance import lonlat, distance
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from django.db.models.functions import Trunc
from datetime import timedelta
import matplotlib
matplotlib.use('Agg')

class GetRefreshToken(APIView):
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refreshTokenId'],
            properties={
                'refreshTokenId': openapi.Schema(type=openapi.TYPE_STRING, example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9'),
            },            
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Successfully generated Access Token'),
                    'isAuthenticated': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'accessToken': openapi.Schema(type=openapi.TYPE_STRING, example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9.3EyvZffo4g2R3Zy8sZw'),
                    'expiresIn': openapi.Schema(type=openapi.TYPE_STRING, default='2 minutes'),
                    'refreshToken': openapi.Schema(type=openapi.TYPE_STRING, example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIiwiZXhwIjoxNjgzNzk4MzU5LCJpYXQiOjE2ODM2Mrffo4g2R3Zy8sZw'),
                },
            ),
        },
        operation_description="Generating Access Token in API",
    )

    # Generate Access Token Using Referesh Token
    def post(self, request, format=None):
        if request.data.get('refreshTokenId') != None:
            refresh_token_id = request.data.get('refreshTokenId')
        else:
            return Response({'success':False, 'message':'please enter valid refresh token'})
        
        try:
            if refresh_token_id != None:
                if CustomToken.objects.filter(refreshToken=refresh_token_id).exists():
                    token = CustomToken.objects.get(refreshToken=refresh_token_id)
                    email = token.user.email

                    if Volunteer.objects.filter(email=email).exists():
                        user = Volunteer.objects.get(email=email)
                        user_details = UserProfileSerializer(user).data
                        access_token = create_access_token(user.id)
                        refresh_token = create_refresh_token(user.id)
                        token.refreshToken = refresh_token
                        token.accessToken = access_token
                        token.save()
                    else:
                        return Response({'success': False, 'message':'user with email does not exist'})
                else:
                    return Response({'success': False, 'message':'Custom Token Object does not exist'})
            else:
                return Response({'success': False, 'message': 'Please provide valid refresh token'})
            
            return Response({
                'success': True,
                'message': 'successfully generated token',
                'isAuthenticated': True,
                'token': access_token,
                'expiresIn': '31 Days',
                'refreshToken': refresh_token,
                'user': user_details,
            })
            
        except Exception as e:
            return Response({'error': str(e), 'isAuthenticated': False, 'success': False})
        
class VolunteerExpoPushToken(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['expoPushToken'],
            properties={
                'expoPushToken': openapi.Schema(type=openapi.TYPE_STRING, example='ExponentPushToken[NYM-Q0OmkFj9TkkdkV2UPW7]'),
            },            
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Successfully updated ExpoPush Token'),
                },
            ),
        },
        operation_description="Updating ExpoPushToken API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    # Update ExpoPushToken
    def put(self, request, format=None):

        if request.data.get('expoPushToken') != None:
            expo_push_token = request.data.get('expoPushToken')
        else:
            return Response({'success':False, 'message':'please enter valid Expo Push Token'})
        
        try:
            if request.user != None:
                user = request.user

                if CustomToken.objects.filter(user=user).exists():
                    token = CustomToken.objects.get(user=user)
                    token.expoPushToken = expo_push_token
                    token.save()

                    return Response({
                        'success': True, 
                        'message': 'successfully updated Expo Push Token', 
                    })
                
                else:
                    return Response({'success': False, 'message':'Custom Token Object does not exist for the user'})
            else:
                return Response({'success': False, 'message': 'User does not exist'})
            
        except Exception as e:
            return Response({'error': str(e), 'isAuthenticated': False, 'success': False})
    
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'expoPushToken': openapi.Schema(type=openapi.TYPE_STRING, default='ExponentPushToken[NYM-Q0OmkFj9TkkdkV2UPW7]'),
                },
            ),
        },
        operation_description="Get ExpoPushToken API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    ) 

    def get(self, request, format=None):
        try:
            if request.user != None:
                user = request.user

                if CustomToken.objects.filter(user=user).exists():
                    token = CustomToken.objects.get(user=user)
                    return Response({'success': True, 'expoPushToken': token.expoPushToken })
                else:
                    return Response({'success': False, 'message':'Custom Token Object does not exist for the user'})
            else:
                return Response({'success': False, 'message': 'User does not exist'})
            
        except Exception as e:
            return Response({'error': str(e), 'isAuthenticated': False, 'success': False})


class ChoicesView(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'VOLUNTEER_TYPE': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                    'DOCUMENT_TYPE': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="Get Choices API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def get(self, request, format=None):
        try:
            return Response({'success': True, 'VOLUNTEER_TYPE': VOLUNTEER_TYPE, 'DOCUMENT_TYPE': DOCUMENT_TYPE})
        except Exception as e:
            return Response({'success': False, 'error' : str(e)})
        
# Sign Up API  
class SignUp(APIView):
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['tokenId', 'name', 'email', 'isVolunteer'],
            properties={
                'tokenId': openapi.Schema(type=openapi.TYPE_STRING, example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, example='Find Food User'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, example='user@findfood.com'),
                'isVolunteer': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                'expoPushToken':openapi.Schema(type=openapi.TYPE_STRING, example='ExponentPushToken[NYM-Q0OmkFj9TkkdkV2UPW7]')
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='successfully created user'),
                    'userDetails': openapi.Schema(type=openapi.TYPE_OBJECT),
                },
            ),
        },
        operation_description="User Onboarding API",
    )

    # user onboarding API required firebase token and name
    def post(self, request, format=None):
        data = request.data

        token_id = data.get('tokenId')
        name = data.get('name')
        is_volunteer = data.get('isVolunteer')
        expo_push_token = data.get('ExpoPushToken')

        if token_id == None or token_id == '' or token_id == " ":
            return Response({'success': False, 'message': 'please enter valid token'})
        if name == None or name == '' or name == " ":
            return Response({'success': False, 'message': 'please enter valid name'})
        if is_volunteer == None or is_volunteer == '' or is_volunteer == " ":
            return Response({'success': False, 'message': 'please enter if Volunteer or not'})
        if expo_push_token == None or expo_push_token == '' or expo_push_token == " ":
            return Response({'success': False, 'message': 'please enter valid Expo Push Token'})

        password = settings.VOLUNTEER_PASSWORD

        try:
            if 'email' in request.session.keys() and request.session['email']:
                email = request.session['email']
            else:
                try:
                    decoded_token = auth.verify_id_token(token_id)
                    email = decoded_token.get('email')
                except Exception as e:
                    return Response({'success': False, 'error': str(e)})

            random_number = str(uuid.uuid4())[:6]
            username = random_number + '@' + name

            if Volunteer.objects.filter(email=email).exists():
                user = Volunteer.objects.get(email=email)
                user_details = UserProfileSerializer(user).data
                return Response({'success': True, 'message': 'user already exists', 'userDetails': user_details})

            user = Volunteer.objects.create(name=name, email=email, username=username, isVolunteer=is_volunteer, password=password)
            user_details = UserProfileSerializer(user).data
            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id)
            token, _ = CustomToken.objects.get_or_create(user=user)
            token.refreshToken = refresh_token
            token.accessToken = access_token
            token.expoPushToken = expo_push_token
            token.save()
            return Response({'success': True, 'message': 'successfully created user', 'userDetails': user_details})

        except Exception as e:
            return Response({'success': False, 'message': str(e)})

# Login API
class SignIn(APIView):

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['tokenId'],
            properties={
                'tokenId': openapi.Schema(type=openapi.TYPE_STRING, example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9'),
            },            
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Successfully signed in'),
                    'isAuthenticated': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'accessToken': openapi.Schema(type=openapi.TYPE_STRING, example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9.3EyvZffo4g2R3Zy8sZw'),
                    'expiresIn': openapi.Schema(type=openapi.TYPE_STRING, default='31 Days'),
                    'refreshToken': openapi.Schema(type=openapi.TYPE_STRING, example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIiwiZXhwIjoxNjgzNzk4MzU5LCJpYXQiOjE2ODM2Mrffo4g2R3Zy8sZw'),
                },
            ),
        },
        operation_description="User Onboarding and Sign in API",
    )

    # Login API requires Firebase token
    def post(self, request, format=None):
        try:
            token_id = request.data.get('tokenId')
            if token_id is None:
                return Response({'success': False, 'message': 'Please provide a valid token'})

            decoded_token = None
            try:
                decoded_token = auth.verify_id_token(token_id)
            except Exception as e:
                return Response({'success': False, 'error': str(e)})

            email = decoded_token.get('email')
            if not email:
                return Response({'success': False, 'message': 'Email cannot be empty'})

            user = Volunteer.objects.filter(email=email).first()
            if not user:
                return Response({'success': False, 'message': 'User with email does not exist'})

            user_details = UserProfileSerializer(user).data
            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id)

            token, created = CustomToken.objects.get_or_create(user=user)
            token.refreshToken = refresh_token
            token.accessToken = access_token
            token.save()

            return Response({
                'success': True,
                'message': 'Successfully signed in',
                'isAuthenticated': True,
                'token': access_token,
                'expiresIn': '30 Days',
                'refreshToken': refresh_token,
                'user': user_details,
            })

        except Exception as e:
            return Response({'error': str(e), 'isAuthenticated': False, 'success': False})
        
# fetch All Food Events for food Seekers (GET METHOD)     
class FindFood(APIView):

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name='lat', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter(name='lng', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter(name='fullAddress', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter(name='postalCode', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter(name='state', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter(name='city', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter(name='eventStartDate', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True), # Date-time in epoch format
            openapi.Parameter(name='eventEndDate', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True),  # Date-time in epoch format
        ],   
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'foodEvents': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="Find Food Events API",
    )

    def get(self, request, format=None):
        # Find Food API will return Only Todays Food Events occuring within same city of the User location
        # Address (latitude, longitude and altitude)
        # From and to date
        try:
            data = request.query_params

            for param in ['lat', 'lng', 'fullAddress', 'eventStartDate']:
                if not data.get(param, '').strip():
                    return Response({'success': False, 'message': f'please enter valid {param}'})
            
            to_date_epochs = int(data.get('eventEndDate', timezone.now().timestamp()))
            to_date = datetime.fromtimestamp(to_date_epochs).astimezone(timezone.utc)

            postal_code = int(data.get('postalCode', 0))
            state = data.get('state', '')
            city = data.get('city', '')

            lat = float(data.get('lat'))
            lng = float(data.get('lng'))
            full_address = data.get('fullAddress')
            from_date_epochs = int(data.get('eventStartDate'))
            from_date = datetime.fromtimestamp(from_date_epochs).astimezone(timezone.utc)

            address, _ = Address.objects.get_or_create(lat=lat, lng=lng, streetAddress=full_address, 
                fullAddress=full_address, defaults={'postalCode': postal_code, 'state': state, 'city': city}
            )

            searched_xy = (lng, lat)
            events_qs = FoodEvent.objects.filter(
                Q(Q(eventStartDate__gte=from_date) & Q(eventStartDate__lte=to_date)) |
                Q(Q(eventStartDate__lte=from_date) & Q(eventEndDate__gte=from_date)),
                status=EVENT_STATUS[0][0]
            ).order_by('-id')

            final_food_events = [
                event for event in events_qs if
                distance(lonlat(*searched_xy), lonlat(*(event.address.lng, event.address.lat))).km <= 50
            ]

            paginator = PageNumberPagination()
            paginated_food_events = paginator.paginate_queryset(final_food_events, request)

            food_events_details = FoodEventSerializer(paginated_food_events, many=True).data
            return paginator.get_paginated_response({'success': True, 'foodEvents': food_events_details})

        except Exception as e:
            return Response({'success': False, 'message': str(e)})
        
#  GET and Post Food Event API
class Event(APIView):
    parser_classes = [MultiPartParser]
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name='Authorization', in_=openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Token',),    
            openapi.Parameter(name='eventName',in_=openapi.IN_FORM, type=openapi.TYPE_STRING, description='EVENT NAME', required=True),   
            openapi.Parameter(name='lat', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter(name='lng', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter(name='alt', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
            openapi.Parameter(name='fullAddress', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter(name='postalCode', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter(name='state', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter(name='city', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter(name='eventStartDate', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER, required=True), # Date-time in epoch format
            openapi.Parameter(name='eventEndDate', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER, required=True),  # Date-time in epoch format
            openapi.Parameter(name='additionalInfo', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, description='Free Vegan Meals', required=True),
            openapi.Parameter(name='files', in_=openapi.IN_FORM, type=openapi.TYPE_FILE, required=True),     
        ],   
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Event Posted Sucessfully'),
                },
            ),
        },
        operation_description="Post An Event API",
        consumes=['multipart/form-data'],
    )

    def post(self, request, format=None):
        try:
            required_fields = [
                'eventName', 'lat', 'lng', 'fullAddress', 'postalCode',
                'state', 'city', 'eventStartDate', 'eventEndDate', 'additionalInfo'
            ]
            for field in required_fields:
                if field not in request.data:
                    return Response({'success': False, 'message': f'Please enter valid {field.replace("event", "Event ").capitalize()}'})
                
            event_name = request.data['eventName']
            lat = request.data['lat']
            lng = request.data['lng']
            full_address = request.data['fullAddress']
            postal_code = request.data['postalCode']
            state = request.data['state']
            city = request.data['city']
            
            event_start_date = datetime.fromtimestamp(int(request.data['eventStartDate'])).astimezone(timezone.utc)
            event_end_date = datetime.fromtimestamp(int(request.data['eventEndDate'])).astimezone(timezone.utc)
            additional_info = request.data['additionalInfo']

            event_photo = request.FILES.get('files')
            temp_file = None

            if event_photo:
                file_contents = event_photo.read()
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                try:
                    temp_file.write(file_contents)
                    temp_file.close()
                except Exception as e:
                    temp_file.close()
                    return Response({'success': False, 'message': str(e)})

            address, _ = Address.objects.get_or_create(
                lat=lat, lng=lng, streetAddress=full_address, fullAddress=full_address,
                defaults={'alt': None, 'postalCode': postal_code, 'state': state, 'city': city}
            )

            organizer = Volunteer.objects.get(id=request.user.id, isVolunteer=True)

            food_event, created = FoodEvent.objects.get_or_create(
                name=event_name, address=address, eventStartDate=event_start_date, eventEndDate=event_end_date, createdBy=organizer,
                defaults={
                    'organizerPhoneNumber': organizer.phoneNumber, 'createdAt': timezone.now(),
                    'additionalInfo': additional_info, 'active': True
                }
            )

            if not created:
                food_event_details = FoodEventSerializer(food_event).data
                return Response({'success': False, 'message': 'Event Already Exists', 'eventDetails': food_event_details})

            if temp_file:
                with open(temp_file.name, 'rb') as f:
                    food_event.eventPhoto.save(event_photo.name, File(f))
                food_event.save()
                f.close()

                doc = Document.objects.create(
                    docType=DOCUMENT_TYPE[1][0], createdAt=food_event.createdAt, event=food_event
                )

                with open(temp_file.name, 'rb') as f:
                    doc.document.save(event_photo.name, File(f))

                doc.save()
                f.close()

            return Response({'success': True, 'message': 'Event Posted Successfully'})

        except Exception as e:
            return Response({'success': False, 'message': str(e)})
        
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'foodEvents': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="Get Food Events Posted by volunteer API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )
    # My Events Only 
    def get(self, request, format=None):
        try:
            user = request.user

            if FoodEvent.objects.filter(createdBy=user).exists():
                food_events = FoodEvent.objects.filter(createdBy=user)
                food_events_details = FoodEventSerializer(food_events, many=True).data
                return Response({'success': True, 'foodEvents': food_events_details})
            else:
                return Response({'success': True, 'foodEvents': []})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})

# GET and POST Bookmark Food Event API
class BookmarkEvent(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['eventId'], 
            properties={
                'eventId': openapi.Schema(type=openapi.TYPE_NUMBER, example="1"),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Event Sucessfully Added to Calender'),
                },
            ),
        },

        operation_description="Add to Calender API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def post(self, request, format=None):
        try:
            if request.data.get('eventId') != None:
                event_id = request.data.get('eventId')
            else:
                return Response({'success': False, 'message': 'please enter valid Event Id'})
            
            user = request.user

            if FoodEvent.objects.filter(id=event_id).exists():
                food_event = FoodEvent.objects.get(id=event_id)
                if EventBookmark.objects.filter(user=user, event=food_event).exists():
                    return Response({'success':False, 'message': 'Bookmark already exists'})
                else:
                    created_at = timezone.now()
                    EventBookmark.objects.create(user=user, event=food_event, createdAt=created_at)
                    return Response({'success': True, 'message': 'Succesfully Added to Bookmarks'})
                
            else:
                return Response({'success': False, 'message': 'Food Event with id does not exist'})
            
        except Exception as e:
            return Response({'success': False, 'message': str(e)})
        
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'bookmarkedEventDetails': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="Get Food Events Posted by volunteer API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def get(self, request, format=None):
        try:
            user = request.user

            if EventBookmark.objects.filter(user=user, isDeleted=False).exists():
                bookmarked_events = EventBookmark.objects.filter(user=user, isDeleted=False)
                bookmarked_event_details = BookmarkedEventSerializer(bookmarked_events, many=True).data
                return Response({'success':True, 'bookmarkedEventDetails': bookmarked_event_details})
            else:
                return Response({'success': True, 'bookmarkedEventDetails': []})
            
        except Exception as e:
            return Response({'success': False, 'message': str(e)})
        
# GET API (fetch categories of Recipe)
class Categories(APIView):
    ## removed authentication for fetch categories as food seekers do not have access Token
    # authentication_classes = [VolunteerTokenAuthentication]
    # permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'categoriesList': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },
        
        operation_description="Get Food Events Posted by volunteer API",
    )
    
    def get(self, request, format=None):
        try:            
            category = Category.objects.all()
            category_list = CategorySerializer(category, many=True).data
            return Response({'success': True, 'categoriesList': category_list})

        except Exception as e:
            return Response({'success': False, 'message': str(e)})
        
# GET and POST Food Recipe API
class FindFoodRecipe(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['categoryId','foodName','ingredients','cookingInstructions'], 
            properties={
                'categoryId': openapi.Schema(type=openapi.TYPE_NUMBER, example="1"),
                'foodName': openapi.Schema(type=openapi.TYPE_STRING, example="vegetable Stew"),
                'ingredients': openapi.Schema(type=openapi.TYPE_STRING, example="vegetables, etc"),
                'cookingInstructions': openapi.Schema(type=openapi.TYPE_STRING, example="Boil for 5 mins on High Flame"),
                'foodImage': openapi.Schema(type=openapi.TYPE_FILE,),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Food Recipe successfully created'),
                },
            ),
        },
    
        operation_description="Add to Calender API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def post(self, request, category_id, format=None):
        try:
            if category_id is None:
                return Response({'success': False, 'message': 'Please provide category Id'})

            food_name = request.data.get('foodName')
            ingredients = request.data.get('ingredients')
            cooking_instructions = request.data.get('cookingInstructions')
            files = request.FILES.getlist('foodImage', [])

            if food_name is None:
                return Response({'success': False, 'message': 'Please enter valid Food Name'})
            if ingredients is None:
                return Response({'success': False, 'message': 'Please enter valid Ingredients'})
            if cooking_instructions is None:
                return Response({'success': False, 'message': 'Please enter valid Cooking Instructions'})

            user = request.user

            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({'success': False, 'message': 'Category with id does not exist'})

            try:
                recipe = FoodRecipe.objects.get(foodName=food_name, ingredients=ingredients, category=category)
                return Response({'success': True, 'message': 'Food Recipe already exists', 'recipe': recipe.id})
            except FoodRecipe.DoesNotExist:
                recipe = FoodRecipe.objects.create(foodName=food_name, ingredients=ingredients, category=category,
                                                cookingInstructions=cooking_instructions)
                created_at = timezone.now()
                for file in files:
                    doc = Document.objects.create(docType=DOCUMENT_TYPE[2][0], document=file, createdAt=created_at)
                    recipe.foodImage.add(doc)
                recipe.save()
                return Response({'success': True, 'message': 'Food Recipe successfully created'})

        except Exception as e:
            return Response({'success': False, 'message': str(e)})
        
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'foodRecipes': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="Get Food Recipe API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def get(self, request, category_id, format=None):
        try:
            user = request.user
            
            if Category.objects.filter(id=category_id).exists():
                category = Category.objects.get(id=category_id)
            else:
                return Response({'success': False, 'message': 'Category with id does not exist'})

            if FoodRecipe.objects.filter(category=category).exists():
                recipes = FoodRecipe.objects.filter(category=category)
                paginator = PageNumberPagination()
                paginated_recipes = paginator.paginate_queryset(recipes, request)
                recipe_list = FoodRecipeSerializer(paginated_recipes, many=True).data
                return paginator.get_paginated_response({'success':True, 'recipeList': recipe_list})
            else:
                return Response({'success': True, 'recipeList': []})
            
        except Exception as e:
            return Response({'success': False, 'message': str(e)})

# GET API (fetch Request Type of Request Food/ Volunteers/ Supplies/ pickup)
class RequestTypes(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'requestTypeList': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },
        
        operation_description="Get Request Type API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )
    
    def get(self, request, format=None):
        try:
            user = request.user
            
            request_type = RequestType.objects.all()
            request_type_list = RequestTypeSerializer(request_type, many=True).data
            return Response({'success': True, 'requestTypeList': request_type_list})

        except Exception as e:
            return Response({'success': False, 'message': str(e)})
               
# GET and POST (Request Food / Supplies) API
class RequestFoodSupplies(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['itemTypeId','itemName','requiredDate','quantity'], 
            properties={
                'itemTypeId': openapi.Schema(type=openapi.TYPE_NUMBER, example="1"),
                'itemName': openapi.Schema(type=openapi.TYPE_STRING, example="Tomatoe"),
                'requiredDate': openapi.Schema(type=openapi.FORMAT_DATE, example="2023-06-06"),
                'quantity': openapi.Schema(type=openapi.TYPE_STRING, example="5 Kg"),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Successfully requested items'), 
                },
            ),
        },
    
        operation_description="Request Food or Supplies API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def post(self, request, request_type_id, format=None):
        try:
            
            if request.data.get('itemTypeId') != None:
                item_type_id = request.data.get('itemTypeId')
            else:
                return Response({'success': False, 'message': 'please enter valid Item Type'})
            
            if request.data.get('itemName') != None:
                item_name = request.data.get('itemName')
            else:
                return Response({'success': False, 'message': 'please enter valid Item Name'})
            
            if request.data.get('requiredDate') != None:
                required_date = request.data.get('requiredDate')
            else:
                return Response({'success': False, 'message': 'please enter valid Required Date'})
            
            if request.data.get('quantity') != None:
                quantity = request.data.get('quantity')
            else:
                return  Response({'success': False, 'message': 'please enter valid quantity'})
            
            user = request.user

            if ItemType.objects.filter(id=item_type_id).exists():
                item_type = ItemType.objects.get(id=item_type_id)
            else:
                return Response({'success': False, 'message': 'Item Type with id does not exist'})
            
            if FoodItem.objects.filter(itemName=item_name, itemType=item_type).exists():
                food_item = FoodItem.objects.get(itemName=item_name, itemType=item_type)
            else:
                food_item = FoodItem.objects.create(itemName=item_name, itemType=item_type, addedBy=user, createdAt=timezone.now())
            
            if RequestType.objects.filter(id=request_type_id).exists():
                request_type = RequestType.objects.get(id=request_type_id)
            else:
                return Response({'success': False, 'message': 'Request Type with id does not exist'})
            
            if Request.objects.filter(type=request_type, createdBy=user, requiredDate=required_date, active=True, quantity=quantity, foodItem=food_item).exists():
                item_request = Request.objects.get(type=request_type, createdBy=user, requiredDate=required_date, active=True, quantity=quantity, foodItem=food_item)
                return Response({'success': True, 'message': 'Request already exists','itemRequest':item_request.id})
            else:
                created_at = timezone.now()
                item_request = Request.objects.create(type=request_type, createdBy=user, requiredDate=required_date, active=True, quantity=quantity, foodItem=food_item, createdAt=created_at)
                return Response({'success': True, 'message': 'Successfully requested items'})
            
        except Exception as e:
            return Response({'success': False, 'message': str(e)})

# GET and POST  (Request Volunteers) API
class RequestVolunteers(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['eventId', 'lat', 'lng', 'alt', 'requiredDate', 'numberOfVolunteers'], 
            properties={
                'eventId': openapi.Schema(type=openapi.TYPE_NUMBER, example="1"),
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example='12.916540'),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example='77.651950'),
                'alt': openapi.Schema(type=openapi.FORMAT_FLOAT, example='4500'),
                'fullAddress': openapi.Schema(type=openapi.TYPE_STRING, example='318 CLINTON AVE NEWARK NJ 07108-2899 USA'),
                'postalCode': openapi.Schema(description='Postal Code of the Area', type=openapi.TYPE_NUMBER,example=7108-2899),
                'state': openapi.Schema(type=openapi.TYPE_STRING, example='New Jersey State'),
                'city': openapi.Schema(type=openapi.TYPE_STRING, example='Newark City'),
                'requiredDate': openapi.Schema(type=openapi.FORMAT_DATE,example='2023-05-05'),
                'numberOfVolunteers': openapi.Schema(type=openapi.TYPE_NUMBER, example='15'),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Volunteers Request successfully created'),
                },
            ),
        },
    
        operation_description="Request Volunteers API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def post(self, request, request_type_id, format=None):
        try:
            if request.data.get('eventId') != None:
                event_id = request.data.get('eventId')
            else:
                return Response({'success': False, 'message': 'please enter valid Event Id'})
            
            if request.data.get('lat') != None:
                lat = request.data.get('lat')
            else:
                return Response({'success': False, 'message': 'please enter valid latitude'})
            
            if request.data.get('lng') != None:
                lng = request.data.get('lng')
            else:
                return Response({'success': False, 'message': 'please enter valid longitude'})
            
            if request.data.get('alt') != None:
                alt = request.data.get('alt')
            else:
                alt = None

            if request.data.get('fullAddress') != None:
                full_address = request.data.get('fullAddress')
            else:
                return Response({'success': False, 'message': 'please enter valid full address'})
            
            if request.data.get('postalCode') != None:
                postal_code = request.data.get('postalCode')
            else:
                return Response({'success': False, 'message': 'please enter valid postal code'})
            
            if request.data.get('state') != None:
                state = request.data.get('state')
            else:
                return Response({'success': False, 'message': 'please enter valid state'})
            
            if request.data.get('city') != None:
                city = request.data.get('city')
            else:
                return Response({'success': False, 'message': 'please enter valid city'})
            
            if request.data.get('requiredDate') != None:
                required_date = request.data.get('requiredDate')
            else:
                return Response({'success': False, 'message': 'please enter valid Required Date'})
            
            if request.data.get('numberOfVolunteers') != None:
                number_of_volunteers = request.data.get('numberOfVolunteers')
            else:
                return Response({'success': False, 'message': 'please enter valid Number of required Volunteers'})

            user = request.user            

            if FoodEvent.objects.filter(id=event_id, createdBy=user).exists():
                food_event = FoodEvent.objects.get(id=event_id, createdBy=user)
            else:
                return Response({'success': False, 'message': 'Food event with id does not exist'})

            if RequestType.objects.filter(id=request_type_id, active=True).exists():
                request_type = RequestType.objects.get(id=request_type_id, active=True)
            else:
                return Response({'success':False, 'message':'Request Type with id does not exist'})
            
            
            if Request.objects.filter(type=request_type, createdBy=user, requiredDate=required_date, active=True, fullfilled=False, quantity=number_of_volunteers,foodEvent=food_event).exists():
                request = Request.objects.filter(type=request_type, createdBy=user, requiredDate=required_date, active=True, fullfilled=False, quantity=number_of_volunteers, foodEvent=food_event)
                return Response({'success':False, 'message':'Request Already Exists for this particular Event'})
            else:
                Request.objects.create(
                    type=request_type, 
                    createdBy=user, 
                    requiredDate=required_date,
                    active=True,
                    createdAt=timezone.now(),
                    quantity=number_of_volunteers,
                    foodEvent=food_event
                )
                return Response({'success':True, 'message':'Volunteers Request successfully created'})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})
        
# GET and POST  (Donate Food) API
class DonateFood(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['itemTypeId', 'foodName', 'quantity', 'pickupDate', 'lat', 'lng', 'fullAddress', 'postalCode', 'state', 'city', 'phoneNumber'], 
            properties={
                'itemTypeId': openapi.Schema(type=openapi.TYPE_NUMBER, example="1"),
                'foodName': openapi.Schema(type=openapi.TYPE_STRING, example="foodName"),  #to be modified # for now conside Food iTem Id
                'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, example='15'),
                'pickupDate': openapi.Schema(type=openapi.FORMAT_DATE,example='2023-05-05'),
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example='12.916540'),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example='77.651950'),
                'alt': openapi.Schema(type=openapi.FORMAT_FLOAT, example='4500'),
                'fullAddress': openapi.Schema(type=openapi.TYPE_STRING, example='318 CLINTON AVE NEWARK NJ 07108-2899 USA'),
                'postalCode': openapi.Schema(description='Postal Code of the Area', type=openapi.TYPE_NUMBER,example=7108-2899),
                'state': openapi.Schema(type=openapi.TYPE_STRING, example='New Jersey State'),
                'city': openapi.Schema(type=openapi.TYPE_STRING, example='Newark City'),
                'phoneNumber': openapi.Schema(type=openapi.TYPE_NUMBER, example='99802732'),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Volunteers Request successfully created'),
                },
            ),
        },
    
        operation_description="Request Volunteers API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def post(self, request, format=None):
        try:

            if request.data.get('itemTypeId') != None:
                itemTypeId = request.data.get('itemTypeId')
            else:
                return Response({'success': False, 'message': 'please enter valid item Type Id'})
            
            if request.data.get('foodName') != None:
                foodName = request.data.get('foodName')
            else:
                return Response({'success': False, 'message': 'please enter valid Food Item'})
            
            if request.data.get('quantity') != None:
                quantity = request.data.get('quantity')
            else:
                return Response({'success': False, 'message': 'please enter valid quantity'})
            
            if request.data.get('pickupDate') != None:
                pickupDate = request.data.get('pickupDate')
            else:
                return Response({'success': False, 'message': 'please enter valid pickup Date'})
         
            if request.data.get('lat') != None:
                lat = request.data.get('lat')
            else:
                return Response({'success': False, 'message': 'please enter valid latitude'})
            
            if request.data.get('lng') != None:
                lng = request.data.get('lng')
            else:
                return Response({'success': False, 'message': 'please enter valid longitude'})
            
            if request.data.get('alt') != None:
                alt = request.data.get('alt')
            else:
                alt = None

            if request.data.get('fullAddress') != None:
                full_address = request.data.get('fullAddress')
            else:
                return Response({'success': False, 'message': 'please enter valid full address'})
            
            if request.data.get('postalCode') != None:
                postal_code = request.data.get('postalCode')
            else:
                return Response({'success': False, 'message': 'please enter valid postal code'})
            
            if request.data.get('state') != None:
                state = request.data.get('state')
            else:
                return Response({'success': False, 'message': 'please enter valid state'})
            
            if request.data.get('city') != None:
                city = request.data.get('city')
            else:
                return Response({'success': False, 'message': 'please enter valid city'})
            
            if request.data.get('phoneNumber') != None:
                phoneNumber = request.data.get('phoneNumber')
            else:
                return Response({'success': False, 'message': 'please enter valid phone Number'})

            user = request.user
            
            if ItemType.objects.filter(id=itemTypeId).exists():
                itemType = ItemType.objects.get(id=itemTypeId)
            else:
                return Response({'success': False, 'message': 'Item Type with id does not exist'})
            
            if Address.objects.filter(lat=lat, lng=lng, streetAddress=full_address, fullAddress=full_address).exists():
                pickupAddress = Address.objects.get(lat=lat, lng=lng, streetAddress=full_address, fullAddress=full_address)
            else:
                pickupAddress = Address.objects.create(lat=lat, lng=lng, alt=alt, fullAddress=full_address, streetAddress=full_address, postalCode=postal_code, state=state, city=city)

            if FoodItem.objects.filter(itemName=foodName).exists():
                foodItem = FoodItem.objects.get(itemName=foodName, addedBy=user, itemType=itemType)
            else:
                foodItem = FoodItem.objects.create(itemName=foodName, addedBy=user, itemType=itemType, createdAt=timezone.now())

            if DeliveryDetail.objects.filter(pickupAddress=pickupAddress, pickupDate=pickupDate).exists():
                deliveryDetails = DeliveryDetail.objects.get(pickupAddress=pickupAddress, pickupDate=pickupDate)
            else:
                deliveryDetails = DeliveryDetail.objects.create(pickupAddress=pickupAddress, pickupDate=pickupDate)

            if Donation.objects.filter(donationType=itemType, foodItem=foodItem, quantity=quantity, donatedBy=user).exists(): 
                donation = Donation.objects.get(donationType=itemType, foodItem=foodItem, quantity=quantity, donatedBy=user)
                donationDetails = DonationSerializer(donation).data
                return Response({'success': False, 'message': 'Donation Already Exists', 'donationDetails':donationDetails})     
            else:
                donation = Donation.objects.create(
                    donationType=itemType,
                    foodItem=foodItem,
                    quantity=quantity,
                    donatedBy=user,
                    needsPickup=True,
                    delivery=deliveryDetails,
                )  
                donationDetails = DonationSerializer(donation).data
                return Response({'success': True, 'message': 'Donation Created Successfully', 'donationDetails':donationDetails})     
    
        except Exception as e:
            return Response({'success': False, 'message': str(e)})
        
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'donationList': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },
    
        operation_description="Donation History API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def get(self, request, format=None):
        try:  
            user = request.user

            if Donation.objects.filter(donatedBy=user).exists(): 
                donation = Donation.objects.filter(donatedBy=user)
                donationDetails = DonationSerializer(donation, many=True).data
                return Response({'success': True, 'donationList':donationDetails})    
             
            else:
                return Response({'success': True,'donationList':[]})     
    
        except Exception as e:
            return Response({'success': False, 'message': str(e)})

 
# GET and PUT Volunteer Profile API  
class VolunteerProfile(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]
    
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'userDetails': openapi.Schema(type=openapi.TYPE_OBJECT),
                },
            ),
        },
        operation_description="Fetch Profile User API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    # fetch volunteer Profile API
    def get(self, request,  format=None):
        try:
            if request.user.id != None:
                userId= request.user.id
                if Volunteer.objects.filter(id=userId).exists():
                    user = Volunteer.objects.get(id=userId)
                    user_details = UserProfileSerializer(user).data
                    return Response({'success':True, 'userDetails':user_details})
                else:
                    return Response({'success': False, 'message': 'user not found'})
            else :
                return Response({'success': False, 'message': 'unable to get user id'})

        except Exception as e:
            return Response({'success': False, 'message': str(e)})
        
        
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name','email','lat','lng', 'fullAddress', 'postalCode', 'state', 'city','phoneNumber'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, example='Find Food User'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, example='user@findfood.com'),
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example=12.916540),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example=77.651950),
                'alt': openapi.Schema(type=openapi.FORMAT_FLOAT, example=4500),
                'fullAddress': openapi.Schema(type=openapi.TYPE_STRING, example='318 CLINTON AVE NEWARK NJ 07108-2899 USA'),
                'postalCode': openapi.Schema(description='Postal Code of the Area', type=openapi.TYPE_NUMBER,example=7108-2899),
                'state': openapi.Schema(type=openapi.TYPE_STRING, example='New Jersey State'),
                'city': openapi.Schema(type=openapi.TYPE_STRING, example='Newark City'),
                'phoneNumber': openapi.Schema(type=openapi.TYPE_NUMBER, example=99723732),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Profile updated successfully'),
                },
            ),
        },
        operation_description="Update Volunteer Profile API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    # update Volunteer Profile API
    def put(self, request,  format=None):

        if request.data.get('name') != None:
            name = request.data.get('name')
        else:
            return Response({'success':False, 'message':'Please enter valid name'})
        
        if request.data.get('email') != None:
            email = request.data.get('email')
        else:
            return Response({'success':False, 'message':'Please enter valid email'})
        
        if request.data.get('lat') != None:
            lat = request.data.get('lat')
        else:
            return Response({'success':False, 'message':'Please enter valid latitude'})
        
        if request.data.get('lng') != None:
            lng = request.data.get('lng')
        else:
            return Response({'success':False, 'message':'Please enter valid longitude'})
        
        if request.data.get('alt') != None:
            alt = request.data.get('alt')
        else:
            alt = None

        if request.data.get('fullAddress') != None:
            full_address = request.data.get('fullAddress')
        else:
            return Response({'success': False, 'message': 'please enter valid full address'})
        
        if request.data.get('postalCode') != None:
            postal_code = request.data.get('postalCode')
        else:
            return Response({'success': False, 'message': 'please enter valid postal code'})
        
        if request.data.get('state') != None:
            state = request.data.get('state')
        else:
            return Response({'success': False, 'message': 'please enter valid state'})
        
        if request.data.get('city') != None:
            city = request.data.get('city')
        else:
            return Response({'success': False, 'message': 'please enter valid city'})

        if request.data.get('phoneNumber') != None:
            phoneNumber = request.data.get('phoneNumber')
        else:
            return Response({'success':False, 'message':'Please enter valid phoneNumber'})
        
        if request.data.get('volunteerType') != None:
            volunteerType = request.data.get('volunteerType')
        else:
            return Response({'success':False, 'message':'Please enter valid volunteer Type'})
        
        try:

            if Address.objects.filter(lat=lat, lng=lng, streetAddress=full_address, fullAddress=full_address).exists():
                address = Address.objects.get(lat=lat, lng=lng, streetAddress=full_address, fullAddress=full_address)
            else:
                address = Address.objects.create(lat=lat, lng=lng, alt=alt, fullAddress=full_address, streetAddress=full_address, postalCode=postal_code, state=state, city=city)           

            if Volunteer.objects.filter(email=email).exists():
                user = Volunteer.objects.get(email=email)
                user.name = name
                user.phoneNumber = phoneNumber
                user.address = address

                if volunteerType == VOLUNTEER_TYPE[0][0]:
                    user.volunteerType = VOLUNTEER_TYPE[0][0]
                elif volunteerType == VOLUNTEER_TYPE[1][0]:
                    user.volunteerType = VOLUNTEER_TYPE[1][0]
                elif volunteerType == VOLUNTEER_TYPE[2][0]:
                    user.volunteerType = VOLUNTEER_TYPE[2][0]
                elif volunteerType == VOLUNTEER_TYPE[3][0]:
                    user.volunteerType = VOLUNTEER_TYPE[3][0]
                else:
                    return Response({'success': False, 'message': 'Volunteer type does not exist'})
                
                user.save()
                user_details = UserProfileSerializer(user).data
                return Response({'success': True, 'message':'Profile updated successfully', 'userDetails':user_details})
            else:
                return Response({'success':False, 'message':'Volunteer with email does not exist'})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        },
        operation_description="Delete Profile User API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

   
    # Delete Volunteer Object, Documents Object, Vehicle Object, Food Events Object, Donations Object, To be Implemented ---> [Requests Object (Volunteer, food/supplies/ pickup/drop)], 
    def delete(self, request,  format=None):
        try:            
            if request.user.id != None:
                res = send_mail_for_confirm_deletion(request.user.id)
                if res['success'] == True:
                    return Response({'success':True, 'message':'E-Mail has been sent successfully'})
                else:
                    return Response({'success': False, 'message': 'Email not sent'})
            else :
                return Response({'success': False, 'message': 'unable to get user id'})

        except Exception as e:
            return Response({'success': False, 'message': str(e)})


def send_mail_for_confirm_deletion(userId):
    try:
        if Volunteer.objects.filter(id=userId).exists():
            user = Volunteer.objects.get(id=userId)

            subject = f'Confirmation E-Mail To Delete your Account'
            email_from = settings.DEFAULT_SENDER
            recipient_list = [user.email]

            firebase_user = auth.get_user_by_email(email=user.email)

            html = open(os.path.join(settings.PROJECT_DIR,'emailTemplates/ConfirmUserAccountDelete.html')).read()
            email_text = html.replace('{{name}}', user.name).replace('{{email}}', user.email).replace('{{delete_url}}', settings.PRODUCTION_URL).replace('{{unique_id}}', firebase_user.uid)
            
            try:
                
                msg = EmailMultiAlternatives(subject=subject, from_email=email_from, to=recipient_list)
                msg.attach_alternative(email_text, "text/html")
                msg.send()

                return ({'success': True, 'message': 'Message is sent'})
            
            except Exception as e:
                return ({'success': False, 'message': 'Failed to send email invitation', 'error': str(e)})
        else:
            return ({'success': False, 'message': 'User with Id does not exist'})
    except Exception as e:
        return ({'success': False, 'error': str(e)})
    



#  GET, POST and PUT Vehicle API
class VehicleOperations(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'vehicleDetails': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="Fetch all vehicle API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def get(self, request, format=None):
        try:
            user = request.user 
            if Vehicle.objects.filter(owner=user).exists():
                vehicle = Vehicle.objects.filter(owner=user)
                vehicleDetails = VehicleSerializer(vehicle, many=True).data
                return Response({'success': True, 'vehicleDetails': vehicleDetails})
            else:
                return Response({'success': True, 'message': f'No vehicle found for user {user.name}', 'vehicleDetails': []})
            
        except Exception as e:
            return Response({'success': False, 'message': str(e)})
    
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['make', 'model', 'vehicleColour',  'plateNumber', 'active'], 
            properties={
                'make': openapi.Schema(type=openapi.TYPE_STRING, example="Audi"),
                'model': openapi.Schema(type=openapi.TYPE_STRING, example='R8'),
                'plateNumber': openapi.Schema(type=openapi.TYPE_STRING, example='KA59W6969'),
                'vehicleColour': openapi.Schema(type=openapi.TYPE_STRING, example='Balck'),
                'active': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Vehicle added successfully'),
                },
            ),
        },

        operation_description="Add Vehicle API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def post(self, request, format=None):
        try:
            
            if request.data.get('make') != None:
                make = request.data.get('make')
            else:
                return Response({'success': False, 'message': 'please enter valid make'})
            
            if request.data.get('model') != None:
                model = request.data.get('model')
            else:
                return Response({'success': False, 'message':'please enter valid model'})
            
            if request.data.get('vehicleColour') != None:
                vehicleColour = request.data.get('vehicleColour')
            else:
                return Response({'success': False, 'message': 'please enter valid vehicle colour'})
            
            if request.data.get('plateNumber') != None:
                plateNumber = request.data.get('plateNumber')
            else:
                return Response({'success': False, 'message': 'please enter valid plate number'})
            
            if request.data.get('active') != None:
                active = request.data.get('active')
            else:
                return Response({'success': False, 'message': 'please enter True if active and False if not active'})
            
            user = request.user

            if Vehicle.objects.filter(make=make, model=model, plateNumber=plateNumber, owner=user, vehicleColour=vehicleColour).exists():
                vehicle = Vehicle.objects.get(make=make, model=model, plateNumber=plateNumber, owner=user, vehicleColour=vehicleColour)
                vehicleDetails = VehicleSerializer(vehicle).data
                return Response({'success': False, 'message': 'Vehicle with data already exists', 'vehicleDetails': vehicleDetails})
            else:
                vehicle = Vehicle.objects.create(make=make, model=model, plateNumber=plateNumber, owner=user, vehicleColour=vehicleColour, active=active, createdAt=timezone.now())
                vehicleDetails = VehicleSerializer(vehicle).data

                # updating isDriver Field of Volunteer model when the user Adds a vehicle.
                user.isDriver = True
                user.save()

                return Response({'success': True, 'message': 'Vehicle added successfully', 'vehicleDetails': vehicleDetails})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})    
    
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['vehicleId', 'vehicleColour', 'plateNumber', 'active'], 
            properties={
                'vehicleId': openapi.Schema(type=openapi.TYPE_NUMBER, example=1),
                'plateNumber': openapi.Schema(type=openapi.TYPE_STRING, example='KA59W6969'),
                'vehicleColour': openapi.Schema(type=openapi.TYPE_STRING, example='Balck'),
                'active': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Vehicle details updated successfully'),
                },
            ),
        },

        operation_description="Update Vehicle API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def put(self, request, format=None):
        try:
            if request.data.get('vehicleId') != None:
                vehicleId = request.data.get('vehicleId')
            else:
                return Response({'success': False, 'message': 'Please enter valid vehicle Id'})
            
            if request.data.get('vehicleColour') != None:
                vehicleColour = request.data.get('vehicleColour')
            else:
                return Response({'success': False, 'message': 'Please enter valid vehicle colour'})
            
            if request.data.get('plateNumber') != None:
                plateNumber = request.data.get('plateNumber')
            else:
                return Response({'success': False, 'message': 'Please enter valid plate number'})
            
            if request.data.get('active') != None:
                active = request.data.get('active')
            else:
                return Response({'success': False, 'message': 'Please enter True if active and False if not active'})
            
            user = request.user

            if Vehicle.objects.filter(id=vehicleId, owner=user).exists():
                vehicle = Vehicle.objects.get(id=vehicleId, owner=user)
                vehicle.vehicleColour = vehicleColour
                vehicle.plateNumber = plateNumber
                vehicle.active = active
                vehicle.save()
                vehicleDetails = VehicleSerializer(vehicle).data
                return Response({'success': True, 'message': 'Vehicle details updated successfully', 'vehicleDetails': vehicleDetails})
            else:
                return Response({'success': False, 'message': f'Vehicle with id {vehicleId} not found'})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})
 
class AllEvents(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'AllEvents': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="Fetch all Events API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def get(self, request, format=None):
        try:
            todayDate = timezone.now()

            if FoodEvent.objects.filter(Q(eventStartDate__gte=todayDate) | Q(eventEndDate__gte=todayDate)).exists():
                foodEvents = FoodEvent.objects.filter(Q(eventStartDate__gte=todayDate) | Q(eventEndDate__gte=todayDate))
                foodEventsDetails = FoodEventSerializer(foodEvents, many=True).data
                return Response({'success': True, 'foodEvents': foodEventsDetails})
            else:
                return Response({'success': True, 'foodEvents': []})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})

# <-------------------------------- Pie Graph -------------------------------->
def create_pie_graph(x_data, y_data, title):
    
    fig, ax = plt.subplots()
    ax.pie(x_data, labels=y_data, autopct='%1.0f%%')

    # Create Pie Graph, Set labels and title
    ax.set_title(title)
    # ax.legend(title = title)

    # Save graph in png format
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    return image_png

# <-------------------------------- Bar Graph -------------------------------->
def create_bar_graph(x_data, y_data, title, x_label, y_label):

    fig, ax = plt.subplots()
    bars = ax.bar(x_data, y_data)

    # Set labels and title
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    if len(y_data) > 0:
        ax.set_yticks(range(int(min(y_data)), int(max(y_data)) + 1))

    # Add values to the bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval, yval, ha='center', va='bottom')

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    matplotlib.pyplot.close()
    return image_png

# <-------------------------------- Line Graph -------------------------------->
def create_line_graph(x_data, y_data, title, x_label, y_label):
    
    fig, ax = plt.subplots()
    ax.plot(x_data, y_data)

    # Set labels and title
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    if len(y_data)>0:
        ax.set_yticks(range(int(min(y_data)), int(max(y_data)) + 1))

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    return image_png

# <-------------------------------- Scatter Graph -------------------------------->
def create_scatter_graph(x_data, y_data, title, x_label, y_label):
    
    fig, ax = plt.subplots()
    ax.scatter(x_data, y_data)

    # Set labels and title
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    if len(y_data)>0:
        ax.set_yticks(range(int(min(y_data)), int(max(y_data)) + 1))

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    return image_png

def get_last_12_months(current_date):
    
    # Get the current month and year
    current_month = current_date.month
    current_year = current_date.year

    # Create a list to store the last 12 months
    last_12_months = []    

    # Loop through the range from 12 months ago until the current month
    for i in range(12):
        
        # Calculate the month and year for the current iteration
        month = current_month - i
        year = current_year

        # Adjust the month and year if necessary
        if month <= 0:
            month += 12
            year -= 1

        # Get the last day of the month
        last_day = calendar.monthrange(year, month)[1]

        # Create a datetime object for the last day of the month
        last_day_of_month = datetime(year, month, last_day)

        # Add the last day of the month to the list
        last_12_months.append(last_day_of_month.strftime("%B %Y"))
        
    return last_12_months[::-1]

class PlotView(APIView):
    def get(self, request):

        # Get the current month and year
        current_date = datetime.now()

        # function to get the list of last 12 months of the current year
        last_12_monthList = get_last_12_months(current_date)

        # ---------------VOLUNTEERS JOINED ON GRAPH -----------------
        data = Volunteer.objects.annotate(month=Trunc('date_joined', 'month')).values('month').annotate(count=Count('id')).order_by('month')

        for da in data:
            print(da['month'].strftime("%B %Y"))

        # Extract the x and y values from the data
        x = [entry['month'].strftime('%B-%Y') for entry in data]
        y = [entry['count'] for entry in data]

        # call the create bar graph function
        bar_img_png = create_bar_graph(x, y, 'User Growth', 'Joined Month', 'Number of Users Joined')
        line_img_png = create_line_graph(x, y, 'User Growth', 'Joined Month', 'Number of Users Joined')
        scatter_img_png = create_scatter_graph(x, y, 'User Growth', 'Joined Month', 'Number of Users Joined')
        pie_img_png = create_pie_graph(y, x, 'Number of Users Joined')


        # Encode the image in base64 for embedding in HTML
        bar_volunteerGraphic = urllib.parse.quote(base64.b64encode(bar_img_png))
        line_volunteerGraphic = urllib.parse.quote(base64.b64encode(line_img_png))
        scatter_volunteerGraphic = urllib.parse.quote(base64.b64encode(scatter_img_png))
        pie_volunteerGraphic = urllib.parse.quote(base64.b64encode(pie_img_png))

        # ---------------FOOD EVENTS CREATED ON GRAPH -----------------
        foodEvents = FoodEvent.objects.annotate(month=Trunc('createdAt', 'month')).values('month').annotate(count=Count('id')).order_by('month')

        # Extract the x and y values from the data
        a = [foodEventEntry['month'].strftime('%B-%Y') for foodEventEntry in foodEvents]
        b = [foodEventEntry['count'] for foodEventEntry in foodEvents]

        # call the create bar graph function
        bar_foodEventImage_png = create_bar_graph(a, b, 'Food Events', 'Created Month', 'Number of Events Created')
        line_foodEventImage_png = create_line_graph(a, b, 'Food Events', 'Created Month', 'Number of Events Created')
        scatter_foodEventImage_png = create_scatter_graph(a, b, 'Food Events', 'Created Month', 'Number of Events Created')
        pie_foodEventImage_png = create_pie_graph(b, a, 'Food Events',)

        # Encode the image in base64 for embedding in HTML
        bar_foodEventGraphic = urllib.parse.quote(base64.b64encode(bar_foodEventImage_png))
        line_foodEventGraphic = urllib.parse.quote(base64.b64encode(line_foodEventImage_png))
        scatter_foodEventGraphic = urllib.parse.quote(base64.b64encode(scatter_foodEventImage_png))
        pie_foodEventGraphic = urllib.parse.quote(base64.b64encode(pie_foodEventImage_png))

        # ---------------DONATIONS CREATED ON GRAPH -----------------
        foodDonation = Donation.objects.annotate(month=Trunc('createdAt', 'month')).values('month').annotate(count=Count('id')).order_by('month')

        # Extract the x and y values from the data
        a = [foodDonationEntry['month'].strftime('%B-%Y') for foodDonationEntry in foodDonation]
        b = [foodDonationEntry['count'] for foodDonationEntry in foodDonation]

        # call the create bar graph function
        bar_foodDonationImage_png = create_bar_graph(a, b, 'Food Donations', 'Created Month', 'Number of Donations Created')
        line_foodDonationImage_png = create_line_graph(a, b, 'Food Donations', 'Created Month', 'Number of Donations Created')
        scatter_foodDonationImage_png = create_scatter_graph(a, b, 'Food Donations', 'Created Month', 'Number of Donations Created')
        pie_foodDonationImage_png = create_pie_graph(b, a, 'Food Donations',)

        # Encode the image in base64 for embedding in HTML
        bar_foodDonationGraphic = urllib.parse.quote(base64.b64encode(bar_foodDonationImage_png))
        line_foodDonationGraphic = urllib.parse.quote(base64.b64encode(line_foodDonationImage_png))
        scatter_foodDonationGraphic = urllib.parse.quote(base64.b64encode(scatter_foodDonationImage_png))
        pie_foodDonationGraphic = urllib.parse.quote(base64.b64encode(pie_foodDonationImage_png))

        #---------------   -----------------
        bar_graphData = {'bar_volunteerGraphic':bar_volunteerGraphic,'bar_foodEventGraphic':bar_foodEventGraphic, 'bar_foodDonationGraphic':bar_foodDonationGraphic}
        line_graphData = {'line_volunteerGraphic':line_volunteerGraphic,'line_foodEventGraphic':line_foodEventGraphic, 'line_foodDonationGraphic':line_foodDonationGraphic}
        scatter_graphData = {'scatter_volunteerGraphic':scatter_volunteerGraphic,'scatter_foodEventGraphic':scatter_foodEventGraphic, 'scatter_foodDonationGraphic':scatter_foodDonationGraphic}
        pie_graphData = {'pie_volunteerGraphic':pie_volunteerGraphic, 'pie_foodEventGraphic':pie_foodEventGraphic, 'pie_foodDonationGraphic':pie_foodDonationGraphic}

        # Pass the graphic to the template context
        context = {'bar_graphData':bar_graphData, 'line_graphData':line_graphData, 'scatter_graphData':scatter_graphData, 'pie_graphData':pie_graphData, 'updatedTime':0}
        return render(request, 'base.html', context)

class AdminDashboardView(APIView):
    def get(self,request):

        # Get the current month and year
        current_date = datetime.now()

        # ---------------VOLUNTEERS JOINED ON GRAPH -----------------
        users = Volunteer.objects.all().order_by('-id')
        user_details = UserProfileSerializer(users, many=True).data

        # ---------------FOOD EVENTS CREATED ON GRAPH -----------------
        foodEvents = FoodEvent.objects.filter(status=EVENT_STATUS[2][0]).order_by('-id')
        eventDetails = FoodEventSerializer(foodEvents, many=True).data

        # ---------------DONATIONS CREATED ON GRAPH -----------------
        foodDonations = Donation.objects.all().order_by('-id')
        donationDetails = DonationSerializer(foodDonations, many=True).data

        # Pass the graphic to the template context
        context = {"volunteerDetails" : user_details,'eventDetails':eventDetails, 'donationDetails':donationDetails,  'updatedTime':0}
        return render(request, 'dashboard.html', context)

class VolunteerNotification(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'notificationa': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="Get Volunteer Notifications API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    # My notifications 
    def get(self, request, format=None):
        try:
            user = request.user
            today = timezone.now().date()
            seven_days_ago = today - timedelta(days=7, hours=0.0)

            if Notification.objects.filter(user=user, createdAt__date__gte=seven_days_ago, createdAt__date__lte=today).exists():
                notification = Notification.objects.filter(user=user, createdAt__date__gte=seven_days_ago, createdAt__date__lte=today)
                notification_details = NotificationSerializer(notification, many=True).data
                return Response({'success': True, 'notifications': notification_details})
            else:
                return Response({'success': True, 'notifications': []})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})
