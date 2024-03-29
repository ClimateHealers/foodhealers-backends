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
                      Donation, EventVolunteer, CustomToken, Request, Notification, VOLUNTEER_TYPE, DOCUMENT_TYPE, STATUS, NOTIFICATION_TYPE, OTP_TYPE)
from .serializers import (UserProfileSerializer, FoodEventSerializer, BookmarkedEventSerializer, CategorySerializer, FoodRecipeSerializer,
                          RequestTypeSerializer, DonationSerializer, VehicleSerializer, NotificationSerializer, RequestSerializer, 
                          ItemTypeSerializer, EventVolunteerSerializer, VolunteerDetailSerializer )
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
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
import matplotlib
matplotlib.use('Agg')
import json
from .tasks import send_push_message
import secrets
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile

# <------------------------------- Function Call to Extract Recipe Data ---------------------------------------------------------------->    
# from .local_dev_utils import pcrm_extract_recipe_page, fok_extract_recipe_page, sharan_extract_recipe_page, veganista_extract_recipe_page, plantbased_extract_recipe_page
# pcrm_extract_recipe_page('https://www.pcrm.org/good-nutrition/plant-based-diets/')
# fok_extract_recipe_page('https://www.forksoverknives.com/')
# sharan_extract_recipe_page("https://sharan-india.org/recipe/breads-and-spreads/")
# veganista_extract_recipe_page("https://simple-veganista.com/vegan-recipe-index/")
# plantbased_extract_recipe_page("https://plantbasedcookingshow.com/2023/08/27/vegan-peach-quick-bread/")

def load_default_data():

    with open("app/defaultData/requestType.json", "r") as read_file:
        request_type_json = json.load(read_file)

    with open("app/defaultData/itemType.json", "r") as read_file:
        item_type_json = json.load(read_file)

    for item_type_dict in item_type_json['itemTypes']:
        item_type_object , _ = ItemType.objects.get_or_create(name=item_type_dict['name'], defaults={'active':item_type_dict['active']})

    for request_type_dict in request_type_json['requestTypes']:
        request_type_object , _ = RequestType.objects.get_or_create(name=request_type_dict['name'], defaults={'active':item_type_dict['active']})

# load_default_data()



def generate_image_with_text(text, event_id, doc_type):

    try:

        food_event = FoodEvent.objects.get(id=event_id)
        
        image_size=(620, 360)
        background_color="green"

        # Create a new image with a white background
        image = Image.new('RGB', image_size, background_color)
        
        # Create a drawing object
        draw = ImageDraw.Draw(image)
        
        # Define the maximum width for the text to fit in the image
        max_width = image_size[0] - 100
        
        # initial height for the text
        y = 20
        
        # Load font 
        font = ImageFont.truetype('app/fonts/OpenSans-ExtraBold.ttf', size=36)
        header_text = "Food Healers"
        
        # Add Climate Healers Header
        _, _, header_text_width, header_text_height = draw.textbbox((0,0), header_text, font=font)
        x = (image_size[0] - header_text_width) // 2
        draw.text((x,y), header_text, font=font, fill='white')
        y+=20+header_text_height

        # Change font
        font = ImageFont.truetype('app/fonts/OpenSans-Bold.ttf', size=30)
        sub_head_text = food_event.name

        # Add Sub Header Event Name
        _, _, sub_head_text_width, sub_head_text_height = draw.textbbox((0,0), sub_head_text, font=font)
        x = (image_size[0] - sub_head_text_width) // 2
        draw.text((x,y), sub_head_text, font=font, fill='white')
        draw.line([(x, y + sub_head_text_height + 10), (x + sub_head_text_width, y + sub_head_text_height+10)], fill='white', width=3)
        y+=2*sub_head_text_height

        # Split the text into lines that fit within the specified width
        lines = []
        words = text.split()
        current_line = words[0]

        # Change font
        font = ImageFont.truetype('app/fonts/OpenSans-SemiBold.ttf', size=24)
        for word in words[1:]:
            # Check if adding the next word exceeds the maximum width
            if draw.textbbox((0,0), current_line + ' ' + word, font=font)[2] <= max_width:
                current_line += ' ' + word
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)
        
        # Calculate the total height needed for the text
        total_height = sum([draw.textbbox((0,0), line, font=font)[3] for line in lines])
        

        # Draw each line of text on the image
        for line in lines:
            _, _, text_width, text_height = draw.textbbox((0,0), line, font=font)
            x = (image_size[0] - text_width) // 2
            draw.text((x, y), line, font=font, fill='white')
            y += text_height
        
        # Save the image
        image.save('output_image.png')

        img_w, img_h = image.size

        # Open the background image
        background = Image.open(food_event.eventPhoto)
        bg_w, bg_h = background.size

        image = image.resize((bg_w, bg_h//2))

        new_image = Image.new('RGB',(bg_w, 3*bg_h//2), (0,0,0))
        new_image.paste(background,(0,0))
        new_image.paste(image, (0, bg_h))
        new_image = new_image.resize((1080,1350))
        # new_image.save("merged_image.png")

        buffer = io.BytesIO()
        new_image.save(buffer, format='PNG')
        buffer.seek(0)

        # Create a Document object and save the image to its 'document' field
        doc = Document.objects.create(
            docType=doc_type,
            createdAt=timezone.now(),
            event=food_event
        )

        filename = str(timezone.now().timestamp())+food_event.name+'sharing.png'
        doc.document.save(filename, ContentFile(buffer.read()))
        doc.save()
        return ({'success': True, 'message':'Succuesfully generated image'})
    except Exception as e:
        return ({'success': False, 'message': str(e)},)
    
# Post Refresh Token API
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
            return Response({'success':False, 'message':'please enter valid refresh token'}, status=HTTP_400_BAD_REQUEST)
        
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
                        return Response({'success': False, 'message':'user with email does not exist'}, status=HTTP_401_UNAUTHORIZED)
                else:
                    return Response({'success': False, 'message':'Custom Token Object does not exist'}, status=HTTP_404_NOT_FOUND)
            else:
                return Response({'success': False, 'message': 'Please provide valid refresh token'}, status=HTTP_400_BAD_REQUEST)
            
            return Response({
                'success': True,
                'message': 'successfully generated token',
                'isAuthenticated': True,
                'token': access_token,
                'expiresIn': '31 Days',
                'refreshToken': refresh_token,
                'user': user_details,
            }, status=HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e), 'isAuthenticated': False, 'success': False}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
# Put Expo Push Token API      
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
            return Response({'success':False, 'message':'please enter valid Expo Push Token'}, status=HTTP_400_BAD_REQUEST)
        
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
                    }, status=HTTP_200_OK)
                
                else:
                    return Response({'success': False, 'message':'Custom Token Object does not exist for the user'}, status=HTTP_404_NOT_FOUND)
            else:
                return Response({'success': False, 'message': 'User does not exist'}, status=HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            return Response({'error': str(e), 'isAuthenticated': False, 'success': False}, status=HTTP_500_INTERNAL_SERVER_ERROR)
    
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
                    return Response({'success': True, 'expoPushToken': token.expoPushToken }, status=HTTP_200_OK)
                else:
                    return Response({'success': False, 'message':'Custom Token Object does not exist for the user'}, status=HTTP_404_NOT_FOUND)
            else:
                return Response({'success': False, 'message': 'User does not exist'}, status=HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            return Response({'error': str(e), 'isAuthenticated': False, 'success': False}, status=HTTP_500_INTERNAL_SERVER_ERROR)

# Get Choices API
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
                    'OTP_TYPE': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
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
            return Response({'success': True, 'VOLUNTEER_TYPE': VOLUNTEER_TYPE, 'DOCUMENT_TYPE': DOCUMENT_TYPE, 'OTP_TYPE': OTP_TYPE},  status=HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'error' : str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
# Sign Up API  
class SignUp(APIView):
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['tokenId', 'name', 'email', 'isVolunteer',],
            properties={
                'tokenId': openapi.Schema(type=openapi.TYPE_STRING, example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, example='Find Food User'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, example='user@findfood.com'),
                'isVolunteer': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                # 'expoPushToken':openapi.Schema(type=openapi.TYPE_STRING, example='ExponentPushToken[NYM-Q0OmkFj9TkkdkV2UPW7]')
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
        # expo_push_token = data.get('expoPushToken')

        if token_id == None or token_id == '' or token_id == " ":
            return Response({'success': False, 'message': 'please enter valid token'}, status=HTTP_400_BAD_REQUEST)
        if name == None or name == '' or name == " ":
            return Response({'success': False, 'message': 'please enter valid name'}, status=HTTP_400_BAD_REQUEST)
        if is_volunteer == None or is_volunteer == '' or is_volunteer == " ":
            return Response({'success': False, 'message': 'please enter if Volunteer or not'}, status=HTTP_400_BAD_REQUEST)

        # if expo_push_token == None or expo_push_token == '' or expo_push_token == " ":
        #     return Response({'success': False, 'message': 'please enter valid Expo Push Token'})

        password = settings.VOLUNTEER_PASSWORD

        try:
            if 'email' in request.session.keys() and request.session['email']:
                email = request.session['email']
            else:
                try:
                    decoded_token = auth.verify_id_token(token_id)
                    email = decoded_token.get('email')
                except Exception as e:
                    return Response({'success': False, 'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

            random_number = str(uuid.uuid4())[:6]
            username = random_number + '@' + name

            if Volunteer.objects.filter(email=email).exists():
                user = Volunteer.objects.get(email=email)
                user_details = UserProfileSerializer(user).data
                return Response({'success': False, 'message': 'user already exists', 'userDetails': user_details}, status=HTTP_400_BAD_REQUEST)

            user = Volunteer.objects.create(name=name, email=email, username=username, isVolunteer=is_volunteer, password=password)
            user_details = UserProfileSerializer(user).data
            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id)
            token, _ = CustomToken.objects.get_or_create(user=user)
            token.refreshToken = refresh_token
            token.accessToken = access_token
            # token.expoPushToken = expo_push_token
            token.save()
            return Response({'success': True, 'message': 'successfully created user', 'userDetails': user_details}, status=HTTP_200_OK)

        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

# Login API
class SignIn(APIView):

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['tokenId'],
            properties={
                'tokenId': openapi.Schema(type=openapi.TYPE_STRING, example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9'),
                # 'expoPushToken':openapi.Schema(type=openapi.TYPE_STRING, example='ExponentPushToken[NYM-Q0OmkFj9TkkdkV2UPW7]')

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
            # expo_push_token = request.data.get('expoPushToken')
            if token_id is None:
                return Response({'success': False, 'message': 'Please provide a valid token'}, status=HTTP_400_BAD_REQUEST)
            
            # if expo_push_token == None or expo_push_token == '' or expo_push_token == " ":
                # return Response({'success': False, 'message': 'please enter valid Expo Push Token'})

            decoded_token = None
            try:
                decoded_token = auth.verify_id_token(token_id)
            except Exception as e:
                return Response({'success': False, 'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

            email = decoded_token.get('email')
            if not email:
                return Response({'success': False, 'message': 'Email cannot be empty'}, status=HTTP_400_BAD_REQUEST)

            user = Volunteer.objects.filter(email=email).first()
            if not user:
                return Response({'success': False, 'message': 'User with email does not exist'}, status=HTTP_401_UNAUTHORIZED)

            user_details = UserProfileSerializer(user).data
            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id)

            token, created = CustomToken.objects.get_or_create(user=user)
            token.refreshToken = refresh_token
            token.accessToken = access_token
            # token.expoPushToken = expo_push_token
            token.save()

            return Response({
                'success': True,
                'message': 'Successfully signed in',
                'isAuthenticated': True,
                'token': access_token,
                'expiresIn': '30 Days',
                'refreshToken': refresh_token,
                'user': user_details,
            }, status=HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e), 'isAuthenticated': False, 'success': False}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
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
                    return Response({'success': False, 'message': f'please enter valid {param}'}, status=HTTP_400_BAD_REQUEST)
            
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

            searched_xy = (lng, lat)
            events_qs = FoodEvent.objects.filter(
                Q(Q(eventStartDate__gte=from_date) & Q(eventStartDate__lte=to_date)) |
                Q(Q(eventStartDate__lte=from_date) & Q(eventEndDate__gte=from_date)),
                status=STATUS[0][0]
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
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
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
            openapi.Parameter(name='requiredVolunteers', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
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
                    return Response({'success': False, 'message': f'Please enter valid {field.replace("event", "Event ").capitalize()}'}, status=HTTP_400_BAD_REQUEST)
                
            event_name = request.data['eventName']
            lat = request.data['lat']
            lng = request.data['lng']
            full_address = request.data['fullAddress']
            postal_code = request.data['postalCode']
            state = request.data['state']
            city = request.data['city']
            requiredVolunteers = request.data['requiredVolunteers']
            
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
                    return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

            address, _ = Address.objects.get_or_create(
                lat=lat, lng=lng, streetAddress=full_address, fullAddress=full_address,
                defaults={'alt': None, 'postalCode': postal_code, 'state': state, 'city': city}
            )

            organizer = Volunteer.objects.get(id=request.user.id, isVolunteer=True)

            food_event, created = FoodEvent.objects.get_or_create(
                name=event_name, address=address, eventStartDate=event_start_date, eventEndDate=event_end_date, createdBy=organizer,
                defaults={
                    'organizerPhoneNumber': organizer.phoneNumber, 'createdAt': timezone.now(),
                    'additionalInfo': additional_info, 'active': True, 'requiredVolunteers':requiredVolunteers
                }
            )

            if not created:
                food_event_details = FoodEventSerializer(food_event).data
                return Response({'success': False, 'message': 'Event Already Exists', 'eventDetails': food_event_details}, status=HTTP_400_BAD_REQUEST)

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

                event_sharing_text = f'''I'm attending {food_event.name} Event from {food_event.eventStartDate.strftime("%d %B %I:%M %p")} to {food_event.eventEndDate.strftime("%d %B %I:%M %p")}. Join me at {food_event.address}. '''
                event_sharing_resp = generate_image_with_text(event_sharing_text, food_event.id, DOCUMENT_TYPE[4][0])

                volunteer_sharing_text = f'''I'm Volunteering at {food_event.name} Event from {food_event.eventStartDate.strftime("%d %B %I:%M %p")} to {food_event.eventEndDate.strftime("%d %B %I:%M %p")}. Join me at {food_event.address}. '''
                volunteer_sharing_resp = generate_image_with_text(volunteer_sharing_text, food_event.id, DOCUMENT_TYPE[5][0])
                print(event_sharing_resp,volunteer_sharing_resp)

            if  food_event.requiredVolunteers!= None:
                volunteer_result = request_volunteer(food_event, organizer)
                if volunteer_result['success'] == False:
                    return Response({'success': False, 'message':f'Event Posted Successfully but Volunteer Request Could not be Created. {volunteer_result.message} '}, status=HTTP_400_BAD_REQUEST)

            return Response({'success': True, 'message': 'Event Posted Successfully'}, status=HTTP_200_OK)

        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
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
                return Response({'success': True, 'foodEvents': food_events_details}, status=HTTP_200_OK)
            else:
                return Response({'success': True, 'foodEvents': []}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

# Create Volunteer Request function
def request_volunteer(food_event, organizer):
    try:

        if RequestType.objects.filter(name='Volunteer', active=True).exists():
            request_type = RequestType.objects.get(name='Volunteer', active=True)
        else:
            return {'success':False, 'message':'Request Type does not exist'}
        
        if Request.objects.filter(type=request_type, createdBy=organizer, requiredDate=food_event.eventStartDate, active=True, fullfilled=False, quantity=food_event.requiredVolunteers, foodEvent=food_event).exists():
            request = Request.objects.filter(type=request_type, createdBy=organizer, requiredDate=food_event.eventStartDate, active=True, fullfilled=False, quantity=food_event.requiredVolunteers, foodEvent=food_event)
            return {'success':False, 'message':'Request Already Exists for this particular Event'}
        else:
            Request.objects.create(
                type=request_type, 
                createdBy=organizer, 
                requiredDate=food_event.eventStartDate,
                active=True,
                createdAt=timezone.now(),
                quantity=food_event.requiredVolunteers,
                foodEvent=food_event
            )
            return {'success':True, 'message':'Volunteers Request successfully created'}
    except Exception as e:
        return {'success': False, 'message': str(e)}
      
# GET API (fetch categories of Recipe)
class Categories(APIView):

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
            return Response({'success': True, 'categoriesList': category_list}, status=HTTP_200_OK)

        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
# GET Food Recipe API
class FindFoodRecipe(APIView):
        
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
            if Category.objects.filter(id=category_id).exists():
                category = Category.objects.get(id=category_id)
            else:
                return Response({'success': False, 'message': 'Category with id does not exist'}, status=HTTP_400_BAD_REQUEST)

            if FoodRecipe.objects.filter(category=category).exists():
                recipes = FoodRecipe.objects.filter(category=category)
                paginator = PageNumberPagination()
                paginated_recipes = paginator.paginate_queryset(recipes, request)
                recipe_list = FoodRecipeSerializer(paginated_recipes, many=True).data
                return paginator.get_paginated_response({'success':True, 'recipeList': recipe_list})
            else:
                return Response({'success': True, 'recipeList': []}, status=HTTP_200_OK)
            
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        

# GET Food Recipe API
class SearchFoodRecipe(APIView):
        
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

        operation_description="Search Food Recipe API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
            openapi.Parameter(name='search_keyword', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter(name='category_id', in_=openapi.IN_QUERY, type=openapi.TYPE_NUMBER),
        ],
    )

    def get(self, request, format=None):
        try:           

            if not request.query_params.get('search_keyword', '').strip():
                return Response({'success': False, 'message': f'please enter valid search_keyword'}, status=HTTP_400_BAD_REQUEST)
            search_keyword = request.query_params.get('search_keyword', '')

            category_id = int(request.query_params.get('category_id', 0))

            if category_id != 0:
                if Category.objects.filter(id=category_id).exists():
                    category = Category.objects.get(id=category_id)
                else:
                    return Response({'success': False, 'message': 'Category with id does not exist'}, status=HTTP_400_BAD_REQUEST)
                
                if FoodRecipe.objects.filter(Q(Q(foodName__icontains=search_keyword)|Q(ingredients__icontains=search_keyword)|Q(cookingInstructions__icontains=search_keyword)|Q(recipeCredits__icontains=search_keyword)) & Q(category=category)).exists():
                    recipes = FoodRecipe.objects.filter(Q(Q(foodName__icontains=search_keyword)|Q(ingredients__icontains=search_keyword)|Q(cookingInstructions__icontains=search_keyword)|Q(recipeCredits__icontains=search_keyword)) & Q(category=category))
                else:
                    return Response({'success': True, 'recipeList': []}, status=HTTP_200_OK)   
            else:
        
                if FoodRecipe.objects.filter(Q(foodName__icontains=search_keyword)|Q(ingredients__icontains=search_keyword)|Q(cookingInstructions__icontains=search_keyword)|Q(recipeCredits__icontains=search_keyword)).exists():
                    recipes = FoodRecipe.objects.filter(Q(foodName__icontains=search_keyword)|Q(ingredients__icontains=search_keyword)|Q(cookingInstructions__icontains=search_keyword)|Q(recipeCredits__icontains=search_keyword))
                else:
                    return Response({'success': True, 'recipeList': []}, status=HTTP_200_OK)
            
            paginator = PageNumberPagination()
            paginated_recipes = paginator.paginate_queryset(recipes, request)
            recipe_list = FoodRecipeSerializer(paginated_recipes, many=True).data
            return paginator.get_paginated_response({'success':True, 'recipeList': recipe_list})
        
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)


# POST Food Recipe API
class PostFoodRecipe(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['categoryId','foodName','ingredients','cookingInstructions', 'preparationTime'], 
            properties={
                'categoryId': openapi.Schema(type=openapi.TYPE_NUMBER, example="1"),
                'foodName': openapi.Schema(type=openapi.TYPE_STRING, example="vegetable Stew"),
                'ingredients': openapi.Schema(type=openapi.TYPE_STRING, example="vegetables, etc"),
                'cookingInstructions': openapi.Schema(type=openapi.TYPE_STRING, example="Boil for 5 mins on High Flame"),
                'preparationTime':openapi.Schema(type=openapi.TYPE_STRING, example="45 mins"),
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
    
        operation_description="Add Food Recipe API",
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
                return Response({'success': False, 'message': 'Please provide category Id'}, status=HTTP_400_BAD_REQUEST)

            food_name = request.data.get('foodName')
            ingredients = request.data.get('ingredients')
            cooking_instructions = request.data.get('cookingInstructions')
            files = request.FILES.getlist('foodImage', [])
            preparation_time = request.data.get('preparationTime')

            if food_name is None:
                return Response({'success': False, 'message': 'Please enter valid Food Name'}, status=HTTP_400_BAD_REQUEST)
            if ingredients is None:
                return Response({'success': False, 'message': 'Please enter valid Ingredients'}, status=HTTP_400_BAD_REQUEST)
            if cooking_instructions is None:
                return Response({'success': False, 'message': 'Please enter valid Cooking Instructions'}, status=HTTP_400_BAD_REQUEST)
            if preparation_time is None:
                return Response({'success': False, 'message': 'Please enter valid Preparation Time'}, status=HTTP_400_BAD_REQUEST)

            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({'success': False, 'message': 'Category with id does not exist'}, status=HTTP_400_BAD_REQUEST)

            try:
                recipe = FoodRecipe.objects.get(foodName=food_name, ingredients=ingredients, category=category)
                return Response({'success': True, 'message': 'Food Recipe already exists', 'recipe': recipe.id}, status=HTTP_200_OK)
            except FoodRecipe.DoesNotExist:
                recipe = FoodRecipe.objects.create(foodName=food_name, ingredients=ingredients, category=category,
                                                cookingInstructions=cooking_instructions, preparationTime=preparation_time)
                created_at = timezone.now()
                for file in files:
                    doc = Document.objects.create(docType=DOCUMENT_TYPE[2][0], document=file, createdAt=created_at)
                    recipe.foodImage.add(doc)
                recipe.save()
                return Response({'success': True, 'message': 'Food Recipe successfully created'}, status=HTTP_200_OK)

        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

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
            request_type = RequestType.objects.all()
            request_type_list = RequestTypeSerializer(request_type, many=True).data
            return Response({'success': True, 'requestTypeList': request_type_list}, status=HTTP_200_OK)

        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
               
# GET and POST (My Request Food / Supplies) API
class RequestFoodSupplies(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['itemTypeId','itemName','requiredDate','quantity', 'lat', 'lng', 'fullAddress', 'postalCode', 'state', 'city', 'phoneNumber'], 
            properties={
                'itemTypeId': openapi.Schema(type=openapi.TYPE_NUMBER, example="1"),
                'itemName': openapi.Schema(type=openapi.TYPE_STRING, example="Tomatoe"),
                'requiredDate': openapi.Schema(type=openapi.TYPE_NUMBER),
                'quantity': openapi.Schema(type=openapi.TYPE_STRING, example="5 Kg"),
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example='12.916540'),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example='77.651950'),
                'fullAddress': openapi.Schema(type=openapi.TYPE_STRING, example='318 CLINTON AVE NEWARK NJ 07108-2899 USA'),
                'postalCode': openapi.Schema(description='Postal Code of the Area', type=openapi.TYPE_NUMBER,example=7108-2899),
                'state': openapi.Schema(type=openapi.TYPE_STRING, example='New Jersey State'),
                'city': openapi.Schema(type=openapi.TYPE_STRING, example='Newark City'),
                'phoneNumber': openapi.Schema(type=openapi.TYPE_NUMBER, example='+91 9972373887'),
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
            
            if request.data.get('itemTypeId') == None:
                return Response({'success': False, 'message': 'please enter valid Item Type'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('itemName') == None:
                return Response({'success': False, 'message': 'please enter valid Item Name'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('requiredDate') == None:
                return Response({'success': False, 'message': 'please enter valid Required Date'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('quantity') == None:                
                return  Response({'success': False, 'message': 'please enter valid quantity'}, status=HTTP_400_BAD_REQUEST)
              
            if request.data.get('lat') == None:
                return Response({'success': False, 'message': 'please enter valid latitude'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('lat') == None:
                return Response({'success': False, 'message': 'please enter valid latitude'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('lng') == None:
                return Response({'success': False, 'message': 'please enter valid longitude'}, status=HTTP_400_BAD_REQUEST)

            if request.data.get('fullAddress') == None:
                return Response({'success': False, 'message': 'please enter valid full address'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('postalCode') == None:
                return Response({'success': False, 'message': 'please enter valid postal code'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('state') == None:
                return Response({'success': False, 'message': 'please enter valid state'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('city') == None:
                return Response({'success': False, 'message': 'please enter valid city'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('phoneNumber') == None:
                return Response({'success':False, 'message':'Please enter valid phoneNumber'}, status=HTTP_400_BAD_REQUEST)

            item_type_id = request.data.get('itemTypeId')
            item_name = request.data.get('itemName')
            required_date_epochs = int(request.data.get('requiredDate', timezone.now().timestamp()))
            required_date = datetime.fromtimestamp(required_date_epochs).astimezone(timezone.utc)
            quantity = request.data.get('quantity')
            lat = request.data.get('lat')
            lng = request.data.get('lng')
            full_address = request.data.get('fullAddress')
            postal_code = request.data.get('postalCode')
            state = request.data.get('state')
            city = request.data.get('city')
            phone_number = request.data.get('phoneNumber')

            user_email = request.user.email
            if  Volunteer.objects.filter(email=user_email).exists():
                user = Volunteer.objects.get(email=user_email)
                user.phoneNumber = phone_number
                user.save()
            else:
                return Response({'success': False, 'message': 'user not found'}, status=HTTP_401_UNAUTHORIZED)
            
            request_address, _ = Address.objects.get_or_create(
                lat=lat, lng=lng, streetAddress=full_address, fullAddress=full_address, 
                defaults={'postalCode': postal_code, 'state': state, 'city': city}
            )  

            if ItemType.objects.filter(id=item_type_id).exists():
                item_type = ItemType.objects.get(id=item_type_id)
            else:
                return Response({'success': False, 'message': 'Item Type with id does not exist'}, status=HTTP_400_BAD_REQUEST)
                        
            if RequestType.objects.filter(id=request_type_id).exists():
                request_type = RequestType.objects.get(id=request_type_id)
            else:
                return Response({'success': False, 'message': 'Request Type with id does not exist'}, status=HTTP_400_BAD_REQUEST)

            food_item = FoodItem.objects.create(itemName=item_name, itemType=item_type, addedBy=user, createdAt=timezone.now())

            delivery_details = DeliveryDetail.objects.create(dropAddress=request_address, dropDate=required_date)

            if Request.objects.filter(type=request_type, createdBy=user, requiredDate=required_date, active=True, quantity=quantity, foodItem=food_item, deliver=delivery_details).exists():
                item_request = Request.objects.get(type=request_type, createdBy=user, requiredDate=required_date, active=True, quantity=quantity, foodItem=food_item, deliver=delivery_details)
                return Response({'success': False, 'message': 'Request already exists','itemRequest':item_request.id}, status=HTTP_400_BAD_REQUEST)
            else:
                created_at = timezone.now()
                item_request = Request.objects.create(type=request_type, createdBy=user, requiredDate=required_date, active=True, quantity=quantity, foodItem=food_item, deliver=delivery_details,  createdAt=created_at)
                return Response({'success': True, 'message': 'Successfully requested items'}, status=HTTP_200_OK)
            
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
    
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'requestList': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },
        
        operation_description="Get My (Food/Supplies, Volunteers, Pickup) Requests API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def get(self, request, request_type_id, format=None):
        try:  
            user = request.user
            
            if RequestType.objects.filter(id=request_type_id).exists():
                request_type = RequestType.objects.get(id=request_type_id)
            else:
                return Response({'success': False, 'message': 'Request Type with id does not exist'}, status=HTTP_400_BAD_REQUEST)
            
            if Request.objects.filter(type=request_type, createdBy=user).exists(): 
                food_request = Request.objects.filter(type=request_type, createdBy=user)
                food_request_details = RequestSerializer(food_request, many=True).data
                return Response({'success': True, 'requestList':food_request_details}, status=HTTP_200_OK)    
             
            else:
                return Response({'success': True,'requestList':[]}, status=HTTP_200_OK)     
    
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

# POST  (Request Volunteers) API --> not using
class RequestVolunteers(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['eventId', 'requiredDate', 'numberOfVolunteers'], 
            properties={
                'eventId': openapi.Schema(type=openapi.TYPE_NUMBER, example="1"),
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
                return Response({'success': False, 'message': 'please enter valid Event Id'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('requiredDate') != None:
                required_date = request.data.get('requiredDate')
            else:
                return Response({'success': False, 'message': 'please enter valid Required Date'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('numberOfVolunteers') != None:
                number_of_volunteers = request.data.get('numberOfVolunteers')
            else:
                return Response({'success': False, 'message': 'please enter valid Number of required Volunteers'}, status=HTTP_400_BAD_REQUEST)

            user = request.user            

            if FoodEvent.objects.filter(id=event_id, createdBy=user).exists():
                food_event = FoodEvent.objects.get(id=event_id, createdBy=user)
            else:
                return Response({'success': False, 'message': 'Food event with id does not exist'}, status=HTTP_400_BAD_REQUEST)

            if RequestType.objects.filter(id=request_type_id, active=True).exists():
                request_type = RequestType.objects.get(id=request_type_id, active=True)
            else:
                return Response({'success':False, 'message':'Request Type with id does not exist'}, status=HTTP_400_BAD_REQUEST)
            
            
            if Request.objects.filter(type=request_type, createdBy=user, requiredDate=required_date, active=True, fullfilled=False, quantity=number_of_volunteers,foodEvent=food_event).exists():
                request = Request.objects.filter(type=request_type, createdBy=user, requiredDate=required_date, active=True, fullfilled=False, quantity=number_of_volunteers, foodEvent=food_event)
                return Response({'success':False, 'message':'Request Already Exists for this particular Event'}, status=HTTP_400_BAD_REQUEST)
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
                return Response({'success':True, 'message':'Volunteers Request successfully created'}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
# <------------------------------------------- END of Request Volunteers API -------------------------------------->

# GET API (fetch Item Type of Request Food/ Supplies)
class ViewItemTypes(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'itemTypeList': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },
        
        operation_description="Get Item Type API",
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
            item_type = ItemType.objects.all()
            item_type_list = ItemTypeSerializer(item_type, many=True).data
            return Response({'success': True, 'itemTypeList': item_type_list}, status=HTTP_200_OK)

        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

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
                'quantity': openapi.Schema(type=openapi.TYPE_STRING, example='15 KG'),
                'pickupDate': openapi.Schema(type=openapi.TYPE_NUMBER),
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example='12.916540'),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example='77.651950'),
                'fullAddress': openapi.Schema(type=openapi.TYPE_STRING, example='318 CLINTON AVE NEWARK NJ 07108-2899 USA'),
                'postalCode': openapi.Schema(description='Postal Code of the Area', type=openapi.TYPE_NUMBER,example=7108-2899),
                'state': openapi.Schema(type=openapi.TYPE_STRING, example='New Jersey State'),
                'city': openapi.Schema(type=openapi.TYPE_STRING, example='Newark City'),
                'phoneNumber': openapi.Schema(type=openapi.TYPE_NUMBER, example='+91 9972373887'),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Donation Created Successfully'),
                    'donationDetails': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },
    
        operation_description="Donate Food API",
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

            if request.data.get('itemTypeId') == None:
                return Response({'success': False, 'message': 'please enter valid item Type Id'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('foodName') == None:
                return Response({'success': False, 'message': 'please enter valid Food Item'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('quantity') == None:
                return Response({'success': False, 'message': 'please enter valid quantity'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('pickupDate') == None:
                return Response({'success': False, 'message': 'please enter valid pickup Date'}, status=HTTP_400_BAD_REQUEST)
         
            if request.data.get('lat') == None:
                return Response({'success': False, 'message': 'please enter valid latitude'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('lng') == None:
                return Response({'success': False, 'message': 'please enter valid longitude'}, status=HTTP_400_BAD_REQUEST)

            if request.data.get('fullAddress') == None:
                return Response({'success': False, 'message': 'please enter valid full address'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('postalCode') == None:
                return Response({'success': False, 'message': 'please enter valid postal code'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('state') == None:
                return Response({'success': False, 'message': 'please enter valid state'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('city') == None:
                return Response({'success': False, 'message': 'please enter valid city'}, status=HTTP_400_BAD_REQUEST)

            if request.data.get('phoneNumber') == None:
                return Response({'success':False, 'message':'Please enter valid phoneNumber'}, status=HTTP_400_BAD_REQUEST)

            item_type_id = request.data.get('itemTypeId')
            food_name = request.data.get('foodName')
            quantity = request.data.get('quantity')            
            pick_up_date_epochs = int(request.data.get('pickupDate', timezone.now().timestamp()))
            pick_up_date = datetime.fromtimestamp(pick_up_date_epochs).astimezone(timezone.utc)
            lat = request.data.get('lat')
            lng = request.data.get('lng')
            full_address = request.data.get('fullAddress')
            postal_code = request.data.get('postalCode')
            state = request.data.get('state')
            city = request.data.get('city')
            phone_number = request.data.get('phoneNumber')

            user_email = request.user.email
            if  Volunteer.objects.filter(email=user_email).exists():
                user = Volunteer.objects.get(email=user_email)
                user.phoneNumber = phone_number
                user.save()
            else:
                return Response({'success': False, 'message': 'user not found'}, status=HTTP_401_UNAUTHORIZED)
            
            if ItemType.objects.filter(id=item_type_id).exists():
                item_type = ItemType.objects.get(id=item_type_id)
            else:
                return Response({'success': False, 'message': 'Item Type with id does not exist'}, status=HTTP_400_BAD_REQUEST)
            
            pickup_address, _ = Address.objects.get_or_create(
                lat=lat, lng=lng, streetAddress=full_address, fullAddress=full_address, 
                defaults={'postalCode': postal_code, 'state': state, 'city': city}
            )  

            food_item = FoodItem.objects.create(itemName=food_name, addedBy=user, itemType=item_type)

            delivery_details = DeliveryDetail.objects.create(pickupAddress=pickup_address, pickupDate=pick_up_date)

            if Donation.objects.filter(donationType=item_type, foodItem=food_item, quantity=quantity, donatedBy=user).exists(): 
                donation = Donation.objects.get(donationType=item_type, foodItem=food_item, quantity=quantity, donatedBy=user)
                donation_details = DonationSerializer(donation).data
                return Response({'success': False, 'message': 'Donation Already Exists', 'donationDetails':donation_details}, status=HTTP_400_BAD_REQUEST)     
            else:
                donation = Donation.objects.create(
                    donationType=item_type,
                    foodItem=food_item,
                    quantity=quantity,
                    donatedBy=user,
                    needsPickup=True,
                    delivery=delivery_details,
                )  
                donation_details = DonationSerializer(donation).data
                return Response({'success': True, 'message': 'Donation Created Successfully', 'donationDetails':donation_details}, status=HTTP_200_OK)     
    
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
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
    
        operation_description="My Donation History API",
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
                donation_details = DonationSerializer(donation, many=True).data
                return Response({'success': True, 'donationList':donation_details}, status=HTTP_200_OK)    
             
            else:
                return Response({'success': True,'donationList':[]}, status=HTTP_200_OK)     
    
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

# GET PUT and DELETE Volunteer Profile API  
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
                user_id= request.user.id
                if Volunteer.objects.filter(id=user_id).exists():
                    user = Volunteer.objects.get(id=user_id)
                    user_details = UserProfileSerializer(user).data
                    return Response({'success':True, 'userDetails':user_details}, status=HTTP_200_OK)
                else:
                    return Response({'success': False, 'message': 'user not found'}, status=HTTP_401_UNAUTHORIZED)
            else :
                return Response({'success': False, 'message': 'unable to get user id'}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'email','lat','lng','fullAddress','state','city','postalCode','phoneNumber'], 
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, example="Volunteer User"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, example="volunteer@foodhealers.com"),
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example='12.916540'),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example='77.651950'),
                'fullAddress': openapi.Schema(type=openapi.TYPE_STRING, example='318 CLINTON AVE NEWARK NJ 07108-2899 USA'),
                'postalCode': openapi.Schema(description='Postal Code of the Area', type=openapi.TYPE_NUMBER, example=7108-2899),         
                'state': openapi.Schema(type=openapi.TYPE_STRING, example='New Jersey State'),
                'city': openapi.Schema(type=openapi.TYPE_STRING, example='Newark City'),
                'phoneNumber': openapi.Schema(type=openapi.TYPE_NUMBER, example='+91 9972373887'),
            }
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
                description='Token'
            ),  
        ],
    )

    # update Volunteer Profile API
    def put(self, request,  format=None):

        if request.data.get('name') == None:
            return Response({'success':False, 'message':'Please enter valid name'}, status=HTTP_400_BAD_REQUEST)
        
        if request.data.get('email') == None:
            return Response({'success':False, 'message':'Please enter valid email'}, status=HTTP_400_BAD_REQUEST)
        
        if request.data.get('lat') == None:
            return Response({'success':False, 'message':'Please enter valid latitude'}, status=HTTP_400_BAD_REQUEST)
        
        if request.data.get('lng') == None:
            return Response({'success':False, 'message':'Please enter valid longitude'}, status=HTTP_400_BAD_REQUEST)

        if request.data.get('fullAddress') == None:
            return Response({'success': False, 'message': 'please enter valid full address'}, status=HTTP_400_BAD_REQUEST)
        
        if request.data.get('postalCode') == None:
            return Response({'success': False, 'message': 'please enter valid postal code'}, status=HTTP_400_BAD_REQUEST)
        
        if request.data.get('state') == None:
            return Response({'success': False, 'message': 'please enter valid state'}, status=HTTP_400_BAD_REQUEST)
        
        if request.data.get('city') == None:
            return Response({'success': False, 'message': 'please enter valid city'}, status=HTTP_400_BAD_REQUEST)

        if request.data.get('phoneNumber') == None:
            return Response({'success':False, 'message':'Please enter valid phoneNumber'}, status=HTTP_400_BAD_REQUEST)

        name = request.data.get('name')
        email = request.data.get('email')
        lat = request.data.get('lat')
        lng = request.data.get('lng')
        full_address = request.data.get('fullAddress')
        postal_code = request.data.get('postalCode')
        state = request.data.get('state')
        city = request.data.get('city')
        phone_number = request.data.get('phoneNumber')

        try:
            address, _ = Address.objects.get_or_create(
                lat=lat, lng=lng, streetAddress=full_address, fullAddress=full_address, 
                defaults={'postalCode': postal_code, 'state': state, 'city': city}
            )          

            if Volunteer.objects.filter(email=email).exists():
                user = Volunteer.objects.get(email=email)
                user.name = name
                user.phoneNumber = phone_number
                user.address = address
                
                user.save()
                user_details = UserProfileSerializer(user).data
                return Response({'success': True, 'message':'Profile updated successfully', 'userDetails':user_details}, status=HTTP_200_OK)
            else:
                return Response({'success':False, 'message':'Volunteer with email does not exist'}, status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

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
                    return Response({'success':True, 'message':'E-Mail has been sent successfully'}, status=HTTP_200_OK)
                else:
                    return Response({'success': False, 'message': 'Email not sent'}, status=HTTP_400_BAD_REQUEST)
            else :
                return Response({'success': False, 'message': 'unable to get user id'}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

# Email Function for Delete
def send_mail_for_confirm_deletion(user_id):
    try:
        if Volunteer.objects.filter(id=user_id).exists():
            user = Volunteer.objects.get(id=user_id)

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
                vehicle_details = VehicleSerializer(vehicle, many=True).data
                return Response({'success': True, 'vehicleDetails': vehicle_details}, status=HTTP_200_OK)
            else:
                return Response({'success': False, 'message': f'No vehicle found for user {user.name}', 'vehicleDetails': []}, status=HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
    
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
                return Response({'success': False, 'message': 'please enter valid make'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('model') != None:
                model = request.data.get('model')
            else:
                return Response({'success': False, 'message':'please enter valid model'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('vehicleColour') != None:
                vehicle_colour = request.data.get('vehicleColour')
            else:
                return Response({'success': False, 'message': 'please enter valid vehicle colour'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('plateNumber') != None:
                plate_number = request.data.get('plateNumber')
            else:
                return Response({'success': False, 'message': 'please enter valid plate number'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('active') != None:
                active = request.data.get('active')
            else:
                return Response({'success': False, 'message': 'please enter True if active and False if not active'}, status=HTTP_400_BAD_REQUEST)
            
            user = request.user

            if Vehicle.objects.filter(make=make, model=model, plateNumber=plate_number, owner=user, vehicleColour=vehicle_colour).exists():
                vehicle = Vehicle.objects.get(make=make, model=model, plateNumber=plate_number, owner=user, vehicleColour=vehicle_colour)
                vehicle_details = VehicleSerializer(vehicle).data
                return Response({'success': False, 'message': 'Vehicle with data already exists', 'vehicleDetails': vehicle_details}, status=HTTP_400_BAD_REQUEST)
            else:

                old_vehicle_list = Vehicle.objects.filter(owner=user)
                for old_vehicle in old_vehicle_list:
                    old_vehicle.active = False
                    old_vehicle.save()
                
                vehicle = Vehicle.objects.create(make=make, model=model, plateNumber=plate_number, owner=user, vehicleColour=vehicle_colour, active=active, createdAt=timezone.now())
                vehicle_details = VehicleSerializer(vehicle).data

                # updating isDriver Field of Volunteer model when the user Adds a vehicle.
                user.isDriver = True
                user.save()

                return Response({'success': True, 'message': 'Vehicle added successfully', 'vehicleDetails': vehicle_details}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)    
    
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
                vehicle_id = request.data.get('vehicleId')
            else:
                return Response({'success': False, 'message': 'Please enter valid vehicle Id'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('vehicleColour') != None:
                vehicle_colour = request.data.get('vehicleColour')
            else:
                return Response({'success': False, 'message': 'Please enter valid vehicle colour'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('plateNumber') != None:
                plate_number = request.data.get('plateNumber')
            else:
                return Response({'success': False, 'message': 'Please enter valid plate number'}, status=HTTP_400_BAD_REQUEST)
            
            if request.data.get('active') != None:
                active = request.data.get('active')
            else:
                return Response({'success': False, 'message': 'Please enter True if active and False if not active'}, status=HTTP_400_BAD_REQUEST)
            
            user = request.user

            if Vehicle.objects.filter(id=vehicle_id, owner=user).exists():
                old_vehicle_list = Vehicle.objects.filter(owner=user)
                for old_vehicle in old_vehicle_list:
                    old_vehicle.active = False
                    old_vehicle.save()

                vehicle = Vehicle.objects.get(id=vehicle_id, owner=user)
                vehicle.vehicleColour = vehicle_colour
                vehicle.plateNumber = plate_number
                vehicle.active = active
                vehicle.save()
                vehicle_details = VehicleSerializer(vehicle).data
                return Response({'success': True, 'message': 'Vehicle details updated successfully', 'vehicleDetails': vehicle_details}, status=HTTP_200_OK)
            else:
                return Response({'success': False, 'message': f'Vehicle with id {vehicle_id} not found'}, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
 
# Get All Events API
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
            today_date = timezone.now()

            if FoodEvent.objects.filter(Q(eventStartDate__gte=today_date) | Q(eventEndDate__gte=today_date), status=STATUS[0][0]).exists():
                food_events = FoodEvent.objects.filter(Q(eventStartDate__gte=today_date) | Q(eventEndDate__gte=today_date), status=STATUS[0][0])
                food_events_details = FoodEventSerializer(food_events, many=True).data
                return Response({'success': True, 'foodEvents': food_events_details}, status=HTTP_200_OK)
            else:
                return Response({'success': True, 'foodEvents': []}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

# Get All Donations API
class AllDonations(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'AllDonations': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="Fetch all Donations API",
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
            if Donation.objects.filter(fullfilled=False, status=STATUS[0][0], active=True).exists():
                food_donations = Donation.objects.filter(fullfilled=False, status=STATUS[0][0], active=True)
                food_donations_details = DonationSerializer(food_donations, many=True).data
                return Response({'success': True, 'AllDonations': food_donations_details}, status=HTTP_200_OK)
            else:
                return Response({'success': True, 'AllDonations': []}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

# Get All Requests API
class AllRequests(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'AllRequests': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="Fetch all Food/Supplies, Volunteer, Pickup Requests API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def get(self, request, request_type_id, format=None):
        try:        
            if RequestType.objects.filter(id=request_type_id, active=True).exists():
                request_type = RequestType.objects.get(id=request_type_id, active=True)
            else:
                return Response({'success':False, 'message':'Request Type with id does not exist'}, status=HTTP_400_BAD_REQUEST)
                
            if Request.objects.filter(type = request_type, active=True, fullfilled=False).exists(): 
                food_request = Request.objects.filter(type = request_type, active=True, fullfilled=False)
                food_request_details = RequestSerializer(food_request, many=True).data
                return Response({'success': True, 'AllRequests':food_request_details}, status=HTTP_200_OK)    
             
            else:
                return Response({'success': True,'AllRequests':[]}, status=HTTP_200_OK)     
    
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
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

# <---------------------------------------------------------------->
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

# Graph API
class PlotView(APIView):
    def get(self, request):

        # Get the current month and year
        current_date = datetime.now()

        # function to get the list of last 12 months of the current year
        last_year_month_list = get_last_12_months(current_date)

        # ---------------VOLUNTEERS JOINED ON GRAPH -----------------
        data = Volunteer.objects.annotate(month=Trunc('date_joined', 'month')).values('month').annotate(count=Count('id')).order_by('month')

        formatted_month = '%B-%Y'
        # Extract the x and y values from the data
        x = [entry['month'].strftime(formatted_month) for entry in data]
        y = [entry['count'] for entry in data]

        user_graph_title = 'User Growth'
        user_x_axis_label = 'Joined Month'
        user_y_axis_label = 'Number of Users Joined'

        # call the create bar graph function
        bar_img_png = create_bar_graph(x, y, user_graph_title, user_x_axis_label, user_y_axis_label)
        line_img_png = create_line_graph(x, y, user_graph_title, user_x_axis_label, user_y_axis_label)
        scatter_img_png = create_scatter_graph(x, y, user_graph_title, user_x_axis_label, user_y_axis_label)
        pie_img_png = create_pie_graph(y, x, user_graph_title)


        # Encode the image in base64 for embedding in HTML
        bar_volunteer_graphic = urllib.parse.quote(base64.b64encode(bar_img_png))
        line_volunteer_graphic = urllib.parse.quote(base64.b64encode(line_img_png))
        scatter_volunteer_graphic = urllib.parse.quote(base64.b64encode(scatter_img_png))
        pie_volunteer_graphic = urllib.parse.quote(base64.b64encode(pie_img_png))

        # ---------------FOOD EVENTS CREATED ON GRAPH -----------------
        food_events = FoodEvent.objects.annotate(month=Trunc('createdAt', 'month')).values('month').annotate(count=Count('id')).order_by('month')

        # Extract the x and y values from the data
        a = [food_event_entry['month'].strftime(formatted_month) for food_event_entry in food_events]
        b = [food_event_entry['count'] for food_event_entry in food_events]

        event_graph_title = 'Food Events'
        x_axis_label = 'Created Month'
        event_y_axis_label = 'Number of Events Created'

        # call the create bar graph function
        bar_food_event_image_png = create_bar_graph(a, b, event_graph_title, x_axis_label, event_y_axis_label)
        line_food_event_image_png = create_line_graph(a, b, event_graph_title, x_axis_label, event_y_axis_label)
        scatter_food_event_image_png = create_scatter_graph(a, b, event_graph_title, x_axis_label, event_y_axis_label)
        pie_food_event_image_png = create_pie_graph(b, a, event_graph_title,)

        # Encode the image in base64 for embedding in HTML
        bar_food_event_graphic = urllib.parse.quote(base64.b64encode(bar_food_event_image_png))
        line_food_event_graphic = urllib.parse.quote(base64.b64encode(line_food_event_image_png))
        scatter_food_event_graphic = urllib.parse.quote(base64.b64encode(scatter_food_event_image_png))
        pie_food_event_graphic = urllib.parse.quote(base64.b64encode(pie_food_event_image_png))

        # ---------------DONATIONS CREATED ON GRAPH -----------------
        food_donation = Donation.objects.annotate(month=Trunc('createdAt', 'month')).values('month').annotate(count=Count('id')).order_by('month')

        # Extract the x and y values from the data
        a = [food_donation_entry['month'].strftime(formatted_month) for food_donation_entry in food_donation]
        b = [food_donation_entry['count'] for food_donation_entry in food_donation]

        donation_graph_title = 'Food Donations'
        donation_y_axis_label = 'Number of Donations Created'

        # call the create bar graph function
        bar_food_donation_image_png = create_bar_graph(a, b, donation_graph_title, x_axis_label, donation_y_axis_label)
        line_food_donation_image_png = create_line_graph(a, b, donation_graph_title, x_axis_label, donation_y_axis_label)
        scatter_food_donation_image_png = create_scatter_graph(a, b, donation_graph_title, x_axis_label, donation_y_axis_label)
        pie_food_donation_image_png = create_pie_graph(b, a, donation_graph_title,)

        # Encode the image in base64 for embedding in HTML
        bar_food_donation_graphic = urllib.parse.quote(base64.b64encode(bar_food_donation_image_png))
        line_food_donation_graphic = urllib.parse.quote(base64.b64encode(line_food_donation_image_png))
        scatter_food_donation_graphic = urllib.parse.quote(base64.b64encode(scatter_food_donation_image_png))
        pie_food_donation_graphic = urllib.parse.quote(base64.b64encode(pie_food_donation_image_png))

        #---------------   -----------------
        bar_graph_data = {'bar_volunteerGraphic':bar_volunteer_graphic,'bar_foodEventGraphic':bar_food_event_graphic, 'bar_foodDonationGraphic':bar_food_donation_graphic}
        line_graph_data = {'line_volunteerGraphic':line_volunteer_graphic,'line_foodEventGraphic':line_food_event_graphic, 'line_foodDonationGraphic':line_food_donation_graphic}
        scatter_graph_data = {'scatter_volunteerGraphic':scatter_volunteer_graphic,'scatter_foodEventGraphic':scatter_food_event_graphic, 'scatter_foodDonationGraphic':scatter_food_donation_graphic}
        pie_graph_data = {'pie_volunteerGraphic':pie_volunteer_graphic, 'pie_foodEventGraphic':pie_food_event_graphic, 'pie_foodDonationGraphic':pie_food_donation_graphic}

        # Pass the graphic to the template context
        context = {'bar_graphData':bar_graph_data, 'line_graphData':line_graph_data, 'scatter_graphData':scatter_graph_data, 'pie_graphData':pie_graph_data, 'updatedTime':0}
        return render(request, 'base.html', context)

# Admin Dashboard Dashboard
class AdminDashboardView(APIView):
    def get(self,request):

        # ---------------VOLUNTEERS JOINED ON GRAPH -----------------
        users = Volunteer.objects.all().order_by('-id')
        user_details = UserProfileSerializer(users, many=True).data

        # ---------------FOOD EVENTS CREATED ON GRAPH -----------------
        food_events = FoodEvent.objects.filter(status=STATUS[2][0]).order_by('-id')
        event_details = FoodEventSerializer(food_events, many=True).data

        # ---------------DONATIONS CREATED ON GRAPH -----------------
        food_donations = Donation.objects.all().order_by('-id')
        donation_details = DonationSerializer(food_donations, many=True).data

        # Pass the graphic to the template context
        context = {"volunteerDetails" : user_details,'eventDetails':event_details, 'donationDetails':donation_details,  'updatedTime':0}
        return render(request, 'dashboard.html', context)

# get Notification API
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
                return Response({'success': True, 'notifications': notification_details}, status=HTTP_200_OK)
            else:
                return Response({'success': True, 'notifications': []}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['notificationId'], 
            properties={
                'notificationId': openapi.Schema(type=openapi.TYPE_NUMBER, example=1),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Successfully updated volunteer notifications'),
                },
            ),
        },

        operation_description="Update Volunteer Notifications API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    # Updated My notifications 
    def put(self, request, format=None):
        try:
            if request.data.get('notificationId') != None:
                notification_id = request.data.get('notificationId')
            else:
                return Response({'success': False, 'message': 'Please enter valid notification Id'}, status=HTTP_400_BAD_REQUEST)
            
            if Notification.objects.filter(id=notification_id).exists():
                notification = Notification.objects.get(id=notification_id)
                notification.is_unread = False
                notification.modifiedAt = timezone.now()
                notification.save()
                return Response({'success': True, 'message': 'Successfully updated volunteer notifications'}, status=HTTP_200_OK)
            else:
                return Response({'success': False, 'message': f'Notification with id {notification_id} not found'}, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['notificationId'], 
            properties={
                'notificationId': openapi.Schema(type=openapi.TYPE_NUMBER, example=1),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Successfully deleted volunteer notifications'),
                },
            ),
        },

        operation_description="Delete Volunteer Notifications API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    # Delete My notifications 
    def delete(self, request, format=None):
        try:
            if request.data.get('notificationId') != None:
                notification_id = request.data.get('notificationId')
            else:
                return Response({'success': False, 'message': 'Please enter valid notification Id'}, status=HTTP_400_BAD_REQUEST)
            
            if Notification.objects.filter(id=notification_id).exists():
                notification = Notification.objects.get(id=notification_id)
                notification.is_unread = False
                notification.modifiedAt = timezone.now()
                notification.isDeleted = True
                notification.save()
                return Response({'success': True, 'message': 'Successfully deleted volunteer notifications'}, status=HTTP_200_OK)
            else:
                return Response({'success': False, 'message': f'Notification with id {notification_id} not found'}, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
                
# FETCH EVENTS API According to Calender Dates
class CalenderEvents(APIView):

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name='startDate', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True), # Date-time in epoch format
            openapi.Parameter(name='endDate', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True),  # Date-time in epoch format
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

        operation_description="Fetch Calender Events API",
    )

    def get(self, request, format=None):
        try:

            from_date_epochs = int(request.query_params.get('startDate'))
            from_date = datetime.fromtimestamp(from_date_epochs).astimezone(timezone.utc)

            to_date_epochs = int(request.query_params.get('endDate', timezone.now().timestamp()))
            to_date = datetime.fromtimestamp(to_date_epochs).astimezone(timezone.utc)

            if FoodEvent.objects.filter(Q(eventStartDate__date__lte=from_date) & Q(eventEndDate__date__gte=to_date), status=STATUS[0][0]).exists():
                food_events = FoodEvent.objects.filter(Q(eventStartDate__date__lte=from_date) & Q(eventEndDate__date__gte=to_date), status=STATUS[0][0])
                food_events_details = FoodEventSerializer(food_events, many=True).data
                return Response({'success': True, 'foodEvents': food_events_details}, status=HTTP_200_OK)
            else:
                return Response({'success': True, 'foodEvents': []}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
# Post Event Volunteer API      
class AddEventVolunteer(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['eventId', 'volunteerPhoneNumber', 'availableToDate', 'availableFromDate', 'lat', 'lng', 'volunteerFullAddress'], 
            properties={
                'eventId': openapi.Schema(type=openapi.TYPE_NUMBER),
                'volunteerPhoneNumber': openapi.Schema(type=openapi.TYPE_NUMBER), 
                'availableToDate': openapi.Schema(type=openapi.TYPE_NUMBER),
                'availableFromDate': openapi.Schema(type=openapi.TYPE_NUMBER),
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example='12.916540'),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example='77.651950'),
                'volunteerFullAddress': openapi.Schema(type=openapi.TYPE_STRING, example='318 CLINTON AVE NEWARK NJ 07108-2899 USA'),
                'postalCode': openapi.Schema(type=openapi.TYPE_NUMBER, example=7108-2899),
                'state': openapi.Schema(type=openapi.TYPE_STRING, example='New Jersey State'),
                'city': openapi.Schema(type=openapi.TYPE_STRING, example='Newark City'),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Volunteer Added Successfully'),
                    'eventVolunteerlist': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },
    
        operation_description="Add Event Volunteer API",
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
            user_id = request.user.id

            for param in ['eventId', 'volunteerPhoneNumber', 'availableFromDate', 'availableToDate', 'lat', 'lng', 'volunteerFullAddress']:
                if not request.data.get(param):
                    return Response({'success': False, 'message': f'please enter valid {param}'}, status=HTTP_400_BAD_REQUEST)

            event_id = request.data.get('eventId')
            phone_number = request.data.get('volunteerPhoneNumber')

            from_date_epochs = int(request.data.get('availableFromDate', timezone.now().timestamp()))
            from_date = datetime.fromtimestamp(from_date_epochs).astimezone(timezone.utc)

            to_date_epochs = int(request.data.get('availableToDate', timezone.now().timestamp()))
            to_date = datetime.fromtimestamp(to_date_epochs).astimezone(timezone.utc)

            lat = request.data.get('lat')
            lng = request.data.get('lng')
            full_address = request.data.get('volunteerFullAddress')

            postal_code = request.data.get('postalCode')
            state = request.data.get('state')
            city = request.data.get('city')

            volunteer_address, _ = Address.objects.get_or_create(
                lat=lat, lng=lng, streetAddress=full_address, fullAddress=full_address, 
                defaults={'postalCode': postal_code, 'state': state, 'city': city}
            )  
            
            if Volunteer.objects.filter(id=user_id).exists():
                volunteer = Volunteer.objects.get(id=user_id)
                if volunteer.address == None:
                    volunteer.address = volunteer_address
                if volunteer.phoneNumber == None or volunteer.phoneNumber == '':
                    volunteer.phoneNumber = phone_number
                volunteer.save()
            else:
                return Response({'success': False, 'message': 'user not found'}, status=HTTP_401_UNAUTHORIZED)
            
            if FoodEvent.objects.filter(id=event_id).exists():
                food_event = FoodEvent.objects.get(id=event_id)

                if food_event.requiredVolunteers != None :
                    if food_event.requiredVolunteers > 0:
                        
                        volunteer_request = Request.objects.get(type__name='Volunteer', createdBy=food_event.createdBy, fullfilled=False, foodEvent=food_event)
                        event_vol, created = EventVolunteer.objects.get_or_create(event=food_event, request=volunteer_request, volunteer=volunteer, defaults={'fromDate':from_date, 'toDate':to_date})
                                                
                        if not created :                         
                            return Response({'success': False, 'message': 'Volunteer has Already Applied'}, status=HTTP_400_BAD_REQUEST)     

                        food_event.volunteers.add(volunteer)
                        food_event.requiredVolunteers = food_event.requiredVolunteers-1
                        food_event.save()

                        volunteer_request.quantity = food_event.requiredVolunteers
                        if volunteer_request.quantity == 0:
                            volunteer_request.fullfilled = True
                            volunteer_request.active = False
                        volunteer_request.save()

                        return Response({'success': True, 'message': 'Successfully Applied to Volunteer'}, status=HTTP_200_OK)     
                    
                    else:
                        return Response({'success': False, 'message': 'Volunteer Request is Full'}, status=HTTP_400_BAD_REQUEST)                     
                else:
                    return Response({'success': False, 'message': 'Invalid Volunteers Request'}, status=HTTP_400_BAD_REQUEST)     
            else:
                return Response({'success': False, 'message': f'Food Event with id {event_id} does not exist'}, status=HTTP_400_BAD_REQUEST)      
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
   
#  Volunteer History API
class VolunteerHistory(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'volunteerHistory': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="My volunteering History API",
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

            if request.user.id != None:
                user_id= request.user.id
                if Volunteer.objects.filter(id=user_id).exists():
                    user = Volunteer.objects.get(id=user_id)
                    if EventVolunteer.objects.filter(volunteer=user).exists():
                        volunteered_events = EventVolunteer.objects.filter(volunteer=user)
                        volunteering_history = EventVolunteerSerializer(volunteered_events, many=True).data
                        return Response({'success': True,'volunteerHistory':volunteering_history}, status=HTTP_200_OK)
                    else:
                        return Response({'success': True,'volunteerHistory':[]}, status=HTTP_200_OK)
                else:
                    return Response({'success': False, 'message': 'user not found'}, status=HTTP_401_UNAUTHORIZED)
            else :
                return Response({'success': False, 'message': 'unable to get user id'}, status=HTTP_400_BAD_REQUEST) 
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)    

# Get Event Volunteers
class GetEventVolunteer(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'EventVolunteers': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="Fetch Event Volunteer Details API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token',
            ),
        ],
    )

    def get(self, request, event_id, format=None):
        try:        
            if FoodEvent.objects.filter(id=event_id).exists():
                food_event = FoodEvent.objects.get(id=event_id)
                if EventVolunteer.objects.filter(event=food_event).exists():
                    event_volunteers_list = EventVolunteer.objects.filter(event=food_event)
                    event_volunteer_details = VolunteerDetailSerializer(event_volunteers_list, many=True).data
                    return Response({'success': True, 'EventVolunteers': event_volunteer_details}, status=HTTP_200_OK)
                else:
                    return Response({'success': True, 'EventVolunteers':[]}, status=HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': False, 'message': 'Food Event with id does not exists'}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateProfilePhoto(APIView):
    parser_classes = [MultiPartParser]
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name='Authorization', in_=openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Token',),    
            openapi.Parameter(name='profilePhoto', in_=openapi.IN_FORM, type=openapi.TYPE_FILE),     
        ],

        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Volunteer profile photo updated successfully'),
                },
            ),
        },
        operation_description="Update Volunteer Profile Photo API",
        consumes=['multipart/form-data'],
    )

    def post(self, request, format=None):
        profile_photo = request.FILES.get('profilePhoto')
        temp_file = None

        if profile_photo != None:
            file_contents = profile_photo.read()
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            try:
                temp_file.write(file_contents)
                temp_file.close()

                volunteer_docs = Document.objects.filter(docType=DOCUMENT_TYPE[0][0], volunteer = request.user, isActive=True)
                for doc in volunteer_docs:
                    if os.path.basename(doc.document.name) == profile_photo.name:
                        return Response({'success':False, 'message':'Volunteer profile is upto date'}, status=HTTP_400_BAD_REQUEST)
                    else:
                        doc.isActive = False
                        doc.save()

            except Exception as e:
                temp_file.close()
                return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
            
            if temp_file:
                volunteer_document = Document.objects.create(docType=DOCUMENT_TYPE[0][0], volunteer=request.user)
                with open(temp_file.name, 'rb') as f:
                    volunteer_document.document.save(profile_photo.name, File(f))
                volunteer_document.save()
                f.close()
                return Response({'success':True, 'message':'Volunteer profile photo updated succesfully'}, status=HTTP_200_OK)
            else:
                return Response({'success':False, 'message':'Unable to read content of file'}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False, 'message': 'Please upload valid profile photo'}, status=HTTP_400_BAD_REQUEST)

# Accept Existing Food/Suppplies Request 
class AcceptFoodRequest(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]
    
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['requestId','pickupRequestTypeId','lat','lng','fullAddress','postalCode','state','city','phoneNumber','pickupDate'], 
            properties={
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example='12.916540'),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example='77.651950'),
                'fullAddress': openapi.Schema(type=openapi.TYPE_STRING, example='318 CLINTON AVE NEWARK NJ 07108-2899 USA'),
                'postalCode': openapi.Schema(description='Postal Code of the Area', type=openapi.TYPE_NUMBER, example=7108-2899),         
                'state': openapi.Schema(type=openapi.TYPE_STRING, example='New Jersey State'),
                'city': openapi.Schema(type=openapi.TYPE_STRING, example='Newark City'),
                'requestId': openapi.Schema(type=openapi.TYPE_NUMBER, example=1),
                'phoneNumber': openapi.Schema(type=openapi.TYPE_NUMBER, example='+91 9972373887'),
                'pickupRequestTypeId': openapi.Schema(type=openapi.TYPE_NUMBER, example=1),
                'pickupDate':openapi.Schema(type=openapi.TYPE_NUMBER),
            }
        ),
        
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Request Accepted successfully'),
                },
            ),
        },

        operation_description="Update Food/Supplies Request API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization', 
                in_=openapi.IN_HEADER, 
                type=openapi.TYPE_STRING, 
                description='Token'
            ),  
        ],
    )

    # update Food/Supplies Request API (used for Accepting By Donar)
    def put(self, request, format=None):

        try:

            for param in ['requestId','pickupRequestTypeId','lat','lng','fullAddress','postalCode','state','city','phoneNumber','pickupDate']:
                if not request.data.get(param):
                    return Response({'success': False, 'message': f'please enter valid {param}'}, status=HTTP_400_BAD_REQUEST)
            
            request_id = request.data.get('requestId')
            pickup_type_id = request.data.get('pickupRequestTypeId')
            lat = request.data.get('lat')
            lng = request.data.get('lng')
            full_address = request.data.get('fullAddress')
            postal_code = request.data.get('postalCode')
            state = request.data.get('state')
            city = request.data.get('city')
            phone_number = request.data.get('phoneNumber')
            pickup_date_epochs = int(request.data.get('pickupDate', timezone.now().timestamp()))
            pickup_date = datetime.fromtimestamp(pickup_date_epochs).astimezone(timezone.utc)

            user_email = request.user.email
            if  Volunteer.objects.filter(email=user_email).exists():
                user = Volunteer.objects.get(email=user_email)
                user.phoneNumber = phone_number
                user.save()
            else:
                return Response({'success': False, 'message': 'user not found'}, status=HTTP_401_UNAUTHORIZED)
            
            if Request.objects.filter(id=request_id, active=True, status=STATUS[0][0]).exists():
                item_request = Request.objects.get(id=request_id, active=True, status=STATUS[0][0])
                
                pickup_address, _ = Address.objects.get_or_create(
                    lat=lat, lng=lng, streetAddress=full_address, fullAddress=full_address, 
                    defaults={'postalCode': postal_code, 'state': state, 'city': city}
                )  

                delivery_details = DeliveryDetail.objects.get(id=item_request.deliver.id)
                delivery_details.pickupAddress = pickup_address
                delivery_details.pickupDate=pickup_date
                delivery_details.save()

                donation = Donation.objects.create(donationType=item_request.foodItem.itemType,
                    foodItem=item_request.foodItem,
                    quantity=item_request.quantity,
                    donatedBy=user,
                    needsPickup=True,
                    delivery=delivery_details,
                    request=item_request,
                    verified=True,
                    status=STATUS[0][0], 
                    active = False
                )  
                
                item_request.active = False
                item_request.save()

                if RequestType.objects.filter(id=pickup_type_id).exists():
                    request_type = RequestType.objects.get(id=pickup_type_id)
                    pickup_request = Request.objects.create(type=request_type, createdBy=user, active=True, quantity=item_request.quantity, foodItem=item_request.foodItem, deliver=delivery_details)
                else:
                    return Response({'success': False, 'message': 'Request Type with id does not exist'}, status=HTTP_400_BAD_REQUEST)
                
                # TRIGGER EMAIL to Food Requestor's email ID with the Food Donor's Details like <Name>, <Phone Number>, <Address> and <Email ID> for the <Food Name, Qty and other details> 
                title = f'{item_request.type.name} Request has been Accepted'
                message = f'''<p>Your {item_request.type.name} Request - for {item_request.quantity} of {item_request.foodItem.itemName} has been Accepted by {user.name} </p></br>
                <p>    
                <h3>{item_request.type.name} Donor's Details : </h3>
                Name    :  {user.name}</br>
                Phone   :  {user.phoneNumber}</br>
                Email   :  {user.email}</br>
                </p>
                '''
                notification_type= NOTIFICATION_TYPE[3][0]
                is_email_notification = True
                send_push_message(item_request.createdBy, title, message, notification_type, is_email_notification)

                # TRIGGER EMAIL to Food Donor's email ID with the Food Requestor's Details like <Name>, <Phone Number>, <Address> and <Email ID> for the <Food Name, Qty and other details>
                title = f'You Accepted {item_request.type.name} Request'
                message = f'''<p>You Accepted to Donate {item_request.quantity} of {item_request.foodItem.itemName} to {item_request.createdBy.name} on {item_request.requiredDate.date()}</p></br>
                <p>    
                <h3>{item_request.type.name} Requestor's Details : </h3>
                Name    :  {item_request.createdBy.name}</br>
                Phone   :  {item_request.createdBy.phoneNumber}</br>
                Email   :  {item_request.createdBy.email}</br>
                </p>
                '''
                notification_type= NOTIFICATION_TYPE[3][0]
                is_email_notification = True
                send_push_message(user, title, message, notification_type, is_email_notification)
                return Response({'success': True, 'message': 'Successfully requested items'}, status=HTTP_200_OK)
            else:
                return Response({'success': False, 'message': f'Request with Id {request_id} does not exists'}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

# Accept Existing Food/Suppplies Donation 
class AcceptFoodDonation(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]
    
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['donationId','pickupRequestTypeId','lat','lng','fullAddress','postalCode','state','city','phoneNumber','dropDate'], 
            properties={
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example='12.916540'),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example='77.651950'),
                'fullAddress': openapi.Schema(type=openapi.TYPE_STRING, example='318 CLINTON AVE NEWARK NJ 07108-2899 USA'),
                'postalCode': openapi.Schema(description='Postal Code of the Area', type=openapi.TYPE_NUMBER, example=7108-2899),         
                'state': openapi.Schema(type=openapi.TYPE_STRING, example='New Jersey State'),
                'city': openapi.Schema(type=openapi.TYPE_STRING, example='Newark City'),
                'donationId': openapi.Schema(type=openapi.TYPE_NUMBER, example=1),
                'phoneNumber': openapi.Schema(type=openapi.TYPE_NUMBER, example='+91 9972373887'),
                'pickupRequestTypeId': openapi.Schema(type=openapi.TYPE_NUMBER, example=1),
                'dropDate':openapi.Schema(type=openapi.TYPE_NUMBER),
            }
        ),
        
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Request Accepted successfully'),
                },
            ),
        },

        operation_description="Update Food/Supplies Donation API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization', 
                in_=openapi.IN_HEADER, 
                type=openapi.TYPE_STRING, 
                description='Token'
            ),  
        ],
    )

    # update Food/Supplies Donation API (used for Accepting By Requestor)
    def put(self, request, format=None):

        try:

            for param in ['donationId','pickupRequestTypeId','lat','lng','fullAddress','postalCode','state','city','phoneNumber','dropDate']:
                if not request.data.get(param):
                    return Response({'success': False, 'message': f'please enter valid {param}'}, status=HTTP_400_BAD_REQUEST)
            
            donation_id = request.data.get('donationId')
            pickup_type_id = request.data.get('pickupRequestTypeId')
            lat = request.data.get('lat')
            lng = request.data.get('lng')
            full_address = request.data.get('fullAddress')
            postal_code = request.data.get('postalCode')
            state = request.data.get('state')
            city = request.data.get('city')
            phone_number = request.data.get('phoneNumber')
            drop_date_epochs = int(request.data.get('dropDate', timezone.now().timestamp()))
            drop_date = datetime.fromtimestamp(drop_date_epochs).astimezone(timezone.utc)

            user_email = request.user.email
            if  Volunteer.objects.filter(email=user_email).exists():
                user = Volunteer.objects.get(email=user_email)
                user.phoneNumber = phone_number
                user.save()
            else:
                return Response({'success': False, 'message': 'user not found'}, status=HTTP_401_UNAUTHORIZED)
            
            if Donation.objects.filter(id=donation_id, active=True, status=STATUS[0][0]).exists():
                item_donation = Donation.objects.get(id=donation_id, active=True, status=STATUS[0][0])
                
                drop_address, _ = Address.objects.get_or_create(
                    lat=lat, lng=lng, streetAddress=full_address, fullAddress=full_address, 
                    defaults={'postalCode': postal_code, 'state': state, 'city': city}
                )  

                delivery_details = DeliveryDetail.objects.get(id=item_donation.delivery.id)
                delivery_details.dropAddress = drop_address
                delivery_details.dropDate = drop_date
                delivery_details.save()

                if RequestType.objects.filter(id=pickup_type_id).exists():
                    food_request_type = RequestType.objects.get(name=item_donation.donationType.name)
                else:
                    return Response({'success': False, 'message': 'Request Type with id does not exist'}, status=HTTP_400_BAD_REQUEST)
                
                food_request = Request.objects.create(
                    type=food_request_type,
                    createdBy=user,
                    requiredDate=drop_date,
                    quantity=item_donation.quantity,
                    foodItem=item_donation.foodItem,
                    deliver=delivery_details,
                    verified=True,
                    status=STATUS[0][0], 
                    active=False,
                )  
                
                item_donation.request=food_request
                item_donation.active=False
                item_donation.save()

                if RequestType.objects.filter(id=pickup_type_id).exists():
                    request_type = RequestType.objects.get(id=pickup_type_id)
                    pickup_request = Request.objects.create(type=request_type, createdBy=user, active=True, quantity=item_donation.quantity, foodItem=item_donation.foodItem, deliver=delivery_details)
                else:
                    return Response({'success': False, 'message': 'Request Type with id does not exist'}, status=HTTP_400_BAD_REQUEST)
                
                # TRIGGER EMAIL to Food Donor's email ID with the Food Requestor's Details like <Name>, <Phone Number>, <Address> and <Email ID> for the <Food Name, Qty and other details> 
                title = f'{item_donation.donationType.name} Donation has been Accepted'
                message = f'''<p>Your {item_donation.donationType.name} Donation - for {item_donation.quantity} of {item_donation.foodItem.itemName} has been Accepted by {user.name} </p></br>
                <p>    
                <h3>{item_donation.donationType.name} Requestor's Details : </h3>
                Name    :  {user.name}</br>
                Phone   :  {user.phoneNumber}</br>
                Email   :  {user.email}</br>
                </p>
                '''
                notification_type= NOTIFICATION_TYPE[1][0]
                is_email_notification = True
                send_push_message(item_donation.donatedBy, title, message, notification_type, is_email_notification)

                # TRIGGER EMAIL to Food Requestor's email ID with the Food Donor's Details like <Name>, <Phone Number>, <Address> and <Email ID> for the <Food Name, Qty and other details>
                title = f'You Accepted {item_donation.donationType.name} Donation'
                message = f'''<p>You Accepted {item_donation.quantity} of {item_donation.foodItem.itemName} from {item_donation.donatedBy.name}  on {food_request.requiredDate.date()}</p></br>
                <p>    
                <h3>{item_donation.donationType.name} Donors's Details : </h3>
                Name    :  {item_donation.donatedBy.name}</br>
                Phone   :  {item_donation.donatedBy.phoneNumber}</br>
                Email   :  {item_donation.donatedBy.email}</br>
                </p>
                '''
                notification_type= NOTIFICATION_TYPE[1][0]
                is_email_notification = True
                send_push_message(user, title, message, notification_type, is_email_notification)
                return Response({'success': True, 'message': 'Successfully requested items'}, status=HTTP_200_OK)
            else:
                return Response({'success': False, 'message': f'Request with Id {donation_id} does not exists'}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

# Accept Food/Supplies Pickup API
class AcceptPickup(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]
    
    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['requestId'], 
            properties={
                'requestId': openapi.Schema(type=openapi.TYPE_NUMBER, example=1),
            }
        ),
        
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Pickup Request Accepted successfully'),
                },
            ),
        },

        operation_description="Accept Food/Supplies Pickup by Driver API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization', 
                in_=openapi.IN_HEADER, 
                type=openapi.TYPE_STRING, 
                description='Token'
            ),  
        ],
    )

    # Accept Food/Supplies Pickup API (used for Accepting pickup By Driver)
    def post(self, request, format=None):

        try:

            for param in ['requestId']:
                if not request.data.get(param):
                    return Response({'success': False, 'message': f'please enter valid {param}'}, status=HTTP_400_BAD_REQUEST)
            
            request_id = request.data.get('requestId')

            user_email = request.user.email
            if  Volunteer.objects.filter(email=user_email, isDriver=True).exists():
                user = Volunteer.objects.get(email=user_email, isDriver=True)
            else:
                return Response({'success': False, 'message': 'Volunteer is not a Driver'}, status=HTTP_401_UNAUTHORIZED)
            
            if Request.objects.filter(id=request_id, active=True, fullfilled=False).exists():
                pickup_request = Request.objects.get(id=request_id, active=True, fullfilled=False)
                pickup_request.deliver.driver = user
                pickup_request.deliver.save()
                pickup_request.active=False
                pickup_request.save()

                if Donation.objects.filter(foodItem=pickup_request.foodItem).exists():
                    donation_details = Donation.objects.get(foodItem=pickup_request.foodItem)

                    # TRIGGER EMAIL to Driver ID with the Food Donors Details like <Name>, <Phone Number>, <Address> and <Email ID> for the <Food Name, Qty and other details>
                    title = f'You Accepted {pickup_request.type.name} Request'
                    message = f'''<p>You Accepted to pick and Drop {pickup_request.quantity} of {pickup_request.foodItem.itemName} </p></br>
                    <p>    
                    <h3> Pickup Details : </h3>
                    Name    :  {donation_details.donatedBy.name}</br>
                    Phone   :  {donation_details.donatedBy.phoneNumber}</br>
                    Date    : {pickup_request.deliver.pickupDate.date()}
                    Time    : {pickup_request.deliver.pickupDate.time()}</br>
                    Address   :  {pickup_request.deliver.pickupAddress}</br>
                    </p></br>
                    <p>    
                    <h3> Drop Details : </h3>
                    Name    :  {donation_details.request.createdBy.name}</br>
                    Phone   :  {donation_details.request.createdBy.phoneNumber}</br>
                    Date    :  {pickup_request.deliver.dropDate.date()}
                    Time    :  {pickup_request.deliver.dropDate.time()}</br>
                    Address :  {pickup_request.deliver.dropAddress}</br>
                    </p>
                    '''
                    notification_type= NOTIFICATION_TYPE[3][0]
                    is_email_notification = True
                    send_push_message(user, title, message, notification_type, is_email_notification)

                    # TRIGGER EMAIL to Food Donor's email ID with the Driver Details like <Name>, <Phone Number>, <Address> and <Email ID> 
                    title = f'{user.name} has Accepted to Pick {pickup_request.foodItem.itemName}'
                    message = f'''<p>{user.name} Accepted to Pickup {pickup_request.quantity} of {pickup_request.foodItem.itemName} on {pickup_request.deliver.pickupDate.date()} at {pickup_request.deliver.pickupDate.time()}</p></br>
                    <p>    
                    <h3> Driver Details : </h3>
                    Name    :  {user.name}</br>
                    Phone   :  {user.phoneNumber}</br>
                    Email   :  {user.email}</br>
                    </p>
                    '''
                    notification_type= NOTIFICATION_TYPE[4][0] 
                    is_email_notification = True
                    send_push_message(donation_details.donatedBy, title, message, notification_type, is_email_notification)

                    # TRIGGER EMAIL to Food Requestor's email ID with the Driver Details like <Name>, <Phone Number>, <Address> and <Email ID>
                    title = f'{user.name} has Accepted to Deliver {pickup_request.foodItem.itemName}'
                    message = f'''<p>{user.name} Accepted to Deliver {pickup_request.quantity} of {pickup_request.foodItem.itemName} on {pickup_request.deliver.dropDate.date()} at {pickup_request.deliver.dropDate.time()}</p></br>
                    <p>    
                    <h3> Driver Details : </h3>
                    Name    :  {user.name}</br>
                    Phone   :  {user.phoneNumber}</br>
                    Email   :  {user.email}</br>
                    </p>
                    '''
                    notification_type= NOTIFICATION_TYPE[4][0] 
                    is_email_notification = True
                    send_push_message(donation_details.request.createdBy, title, message, notification_type, is_email_notification)

                    return Response({'success': True, 'message': 'Successfully requested items'}, status=HTTP_200_OK)
                else:
                    return Response({'success': False, 'message': f'Pickup and Drop Details incomplete'}, status=HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': False, 'message': f'Request with Id {request_id} does not exists'}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['requestId', 'otp', 'otpType'], 
            properties={
                'requestId': openapi.Schema(type=openapi.TYPE_NUMBER, example=1),
                'otp': openapi.Schema(type=openapi.TYPE_NUMBER, example=123456),
                'otpType' : openapi.Schema(type=openapi.TYPE_STRING, example='pickup')
            }
        ),
        
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Successfully updated request details'),
                },
            ),
        },

        operation_description="Update Food/Supplies Pickup Status Details by Driver API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization', 
                in_=openapi.IN_HEADER, 
                type=openapi.TYPE_STRING, 
                description='Token'
            ),  
        ],
    )

    # update Food/Supplies Pickup API (used for updating pickup status details By Driver)
    def put(self, request, format=None):

        try:

            for param in ['requestId', 'otp', 'otpType']:
                if not request.data.get(param):
                    return Response({'success': False, 'message': f'please enter valid {param}'}, status=HTTP_400_BAD_REQUEST)
            
            request_id = request.data.get('requestId')
            otp = request.data.get('otp')
            otp_type = request.data.get('otpType')

            user_email = request.user.email
            if  Volunteer.objects.filter(email=user_email, isDriver=True).exists():
                user = Volunteer.objects.get(email=user_email, isDriver=True)
            else:
                return Response({'success': False, 'message': 'Volunteer is not a Driver'}, status=HTTP_401_UNAUTHORIZED)

            if Request.objects.filter(id=request_id, fullfilled=False).exists():
                pickup_request = Request.objects.get(id=request_id, fullfilled=False)
                
                if otp_type == OTP_TYPE[0][0]:
                    if pickup_request.deliver.pickupOtp == otp:
                        pickup_request.deliver.pickedup = True
                        pickup_request.deliver.save()
                        return Response({'success': True, 'message': 'Successfully updated request details'}, status=HTTP_200_OK)
                    else:
                        return Response({'success': False, 'message': 'OTP is invalid'}, status=HTTP_401_UNAUTHORIZED)
                
                elif otp_type == OTP_TYPE[1][0] and pickup_request.deliver.pickedup == True:
                    if pickup_request.deliver.dropOtp == otp:
                        pickup_request.deliver.delivered = True
                        pickup_request.deliver.save()
                        pickup_request.fullfilled = True
                        pickup_request.save()
                        if Donation.objects.filter(foodItem=pickup_request.foodItem).exists():
                            donation_details = Donation.objects.get(foodItem=pickup_request.foodItem)
                            donation_details.request.fullfilled=True
                            donation_details.request.save()
                            donation_details.fullfilled=True
                            donation_details.save()
                            is_email_notification = False

                            # TRIGGER Notification to Donor Congratulating on Completion of Donation
                            title = f'Congratulations!! Your {donation_details.donationType.name} Donation was successfully completed.' 
                            message = f'''Congratulations {donation_details.donatedBy.name} on successfully donating {donation_details.foodItem.itemName} to {donation_details.request.createdBy.name}.'''
                            notification_type= NOTIFICATION_TYPE[1][0] 
                            send_push_message(donation_details.donatedBy, title, message, notification_type, is_email_notification)

                            # TRIGGER Notification to Requestor Congratulating on Completion of Request
                            title = f'Congratulations!! Your {donation_details.donationType.name} Request was successfully completed.'
                            message = f'''Congratulations {donation_details.request.createdBy.name} on successfully receiving {donation_details.foodItem.itemName} from {donation_details.donatedBy.name}.'''
                            notification_type= NOTIFICATION_TYPE[3][0] 
                            send_push_message(donation_details.request.createdBy, title, message, notification_type, is_email_notification)

                            # TRIGGER Notification to Driver Congratulating on Completion of Pickup Request
                            title = f'Congratulations!! On successfully completing {donation_details.donationType.name} Delivery' 
                            message = f'''Congratulations {pickup_request.deliver.driver.name} on successfully delivering {donation_details.foodItem.itemName} to {donation_details.request.createdBy.name}.'''
                            notification_type= NOTIFICATION_TYPE[3][0] 
                            send_push_message(pickup_request.deliver.driver, title, message, notification_type, is_email_notification)

                            return Response({'success': True, 'message': 'Successfully updated request details'}, status=HTTP_200_OK)
                        else:
                            return Response({'success': False, 'message': f'Pickup and Drop Details incomplete'}, status=HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'success': False, 'message': 'OTP is invalid'}, status=HTTP_401_UNAUTHORIZED)
                else:
                    return Response({'success': False, 'message': 'Invalid OTP Type'}, status=HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': False, 'message': f'Request with Id {request_id} does not exists'}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name='requestTypeId', in_=openapi.IN_QUERY, type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter(name='Authorization', in_=openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Token'),
        ],   

        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'PickupRequests': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),),
                },
            ),
        },

        operation_description="Fetch My Pickups API",
    )

    def get(self, request, format=None):
        try:        
            data = request.query_params

            for param in ['requestTypeId']:
                if not data.get(param, '').strip():
                    return Response({'success': False, 'message': f'please enter valid {param}'}, status=HTTP_400_BAD_REQUEST)

            request_type_id = data.get('requestTypeId')
                
            user_email = request.user.email
            if  Volunteer.objects.filter(email=user_email, isDriver=True).exists():
                user = Volunteer.objects.get(email=user_email, isDriver=True)
            else:
                return Response({'success': False, 'message': 'Volunteer is not a Driver'}, status=HTTP_401_UNAUTHORIZED)

            if RequestType.objects.filter(id=request_type_id).exists():
                request_type = RequestType.objects.get(id=request_type_id)
            else:
                return Response({'success': False, 'message': 'Request Type with id does not exist'}, status=HTTP_400_BAD_REQUEST)
            
            if Request.objects.filter(deliver__driver=user, type=request_type).exists(): 
                pickup_request = Request.objects.filter(deliver__driver=user, type=request_type)
                pickup_request_details = RequestSerializer(pickup_request, many=True).data
                return Response({'success': True, 'PickupRequests':pickup_request_details}, status=HTTP_200_OK)    
            else:
                return Response({'success': True, 'PickupRequests':[]}, status=HTTP_200_OK)     
            
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
# Generate OTP to Confirm Pickup and Deliver Food/Supplies 
class GenerateConfirmationOTP(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['requestId', 'otpType'], 
            properties={
                'requestId': openapi.Schema(type=openapi.TYPE_NUMBER, example=1),
                'otpType' : openapi.Schema(type=openapi.TYPE_STRING, example='pickup or drop')
            }
        ),
        
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='OTP Sent Successfully'),
                },
            ),
        },

        operation_description="Generate OTP for Confirmation of Pickup or Drop by Driver API",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization', 
                in_=openapi.IN_HEADER, 
                type=openapi.TYPE_STRING, 
                description='Token'
            ),  
        ],
    )

    # Generate OTP API (used for generating otp for pickup or drop confirmation By Driver)
    def post(self, request, format=None):

        try:

            for param in ['requestId', 'otpType']:
                if not request.data.get(param):
                    return Response({'success': False, 'message': f'please enter valid {param}'}, status=HTTP_400_BAD_REQUEST)
            
            request_id = request.data.get('requestId')
            otp_type = request.data.get('otpType')

            user_email = request.user.email
            if  Volunteer.objects.filter(email=user_email, isDriver=True).exists():
                user = Volunteer.objects.get(email=user_email, isDriver=True)
            else:
                return Response({'success': False, 'message': 'Volunteer is not a Driver'}, status=HTTP_401_UNAUTHORIZED)

            if Request.objects.filter(id=request_id, fullfilled=False).exists():
                pickup_request = Request.objects.get(id=request_id, fullfilled=False)
                
                # Store OTP and its expiration time
                otp = str(secrets.randbelow(10**6)).zfill(6)

                if Donation.objects.filter(foodItem=pickup_request.foodItem).exists():
                    donation_details = Donation.objects.get(foodItem=pickup_request.foodItem)

                if otp_type == OTP_TYPE[0][0]:
                    pickup_request.deliver.pickupOtp = otp
                    pickup_request.deliver.save()
                    title = f'Your OTP for Pickup Verification'
                    message = f'Your Food healers Secure Pickup Code is {otp} and its valid for next 24 hours. Share this Pickup Code with the Volunteer after handing over your parcel.'
                    notification_type= NOTIFICATION_TYPE[4][0]
                    is_email_notification = True
                    send_push_message(donation_details.donatedBy, title, message, notification_type, is_email_notification)
                    return Response({'success': True, 'message': 'OTP sent Successfully'}, status=HTTP_200_OK)
                    
                elif otp_type == OTP_TYPE[1][0]:
                    pickup_request.deliver.dropOtp = otp
                    pickup_request.deliver.save()
                    title = f'Your OTP for Delivery Verification'
                    message = f'Your Food healers Secure Delivery Code is {otp} and its valid for next 24 hours. Share this Delivery Code with the Volunteer to receive the packacge'
                    notification_type= NOTIFICATION_TYPE[4][0]
                    is_email_notification = True
                    send_push_message(donation_details.request.createdBy, title, message, notification_type, is_email_notification)
                    return Response({'success': True, 'message': 'OTP sent Successfully'}, status=HTTP_200_OK)
                else:
                    return Response({'success': False, 'message': 'Invalid OTP Type'}, status=HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': False, 'message': f'Request with Id {request_id} does not exists'}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

