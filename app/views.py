# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.authentication import create_access_token, create_refresh_token, VolunteerPermissionAuthentication, VolunteerTokenAuthentication
from .models import *
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import uuid
import firebase_admin.auth as auth
# from .local_dev_utils import getAccessToken
from datetime import datetime

# get Django Access token for development testing. 
# getAccessToken(2)

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
        except:
            return Response({'success': False})
        
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
                'isVolunteer': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True)
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
    def post(self, request,  format=None):

        if request.data.get('tokenId') is not None:
            tokenId = request.data.get('tokenId')
        else:
            return Response({'success':False, 'message':'please enter valid token'})
        
        if request.data.get('name') is not None:
            name = request.data.get('name')
        else:
            return Response({'success':False, 'message':'please enter valid name'})
        
        if request.data.get('isVolunteer') is not None:
            isVolunteer = request.data.get('isVolunteer')
        else:
            return Response({'success':False, 'message':'please enter if Volunteer or not'})
        
        password = 'Admin123'

        try:

            if 'email' in request.session.keys() and request.session['email'] is not None:
                email = request.session['email']
            else:
                if tokenId is not None:
                    try:
                        decoded_token = auth.verify_id_token(tokenId)
                        if decoded_token is not None:
                            if 'email' in decoded_token:
                                email = decoded_token['email']
                            else:
                                email = None
                        else:
                            return Response({'success': False, 'message': 'unable to verify user'})
                    except Exception as e:
                        return Response({'success': False, 'error': str(e)})
                else:
                    return Response({'success': False, 'message': 'Please provide valid id token'})
                
            randomNumber = str(uuid.uuid4())[:6]
            username = randomNumber + '@' + name

            if Volunteer.objects.filter(email=email).exists():
                user = Volunteer.objects.get(email=email)
                userDetails = UserProfileSerializer(user).data
                return Response({'success': True, 'message':'user already exists', 'userDetails': userDetails})
            else:
                user = Volunteer.objects.create(name=name, email=email, username=username , isVolunteer=isVolunteer, password=password)
                userDetails = UserProfileSerializer(user).data
                accessToken = create_access_token(user.id)
                refreshToken = create_refresh_token(user.id)
                if CustomToken.objects.filter(user=user).exists():
                    token = CustomToken.objects.get(user=user)
                    token.refreshToken = refreshToken
                    token.accessToken = accessToken
                    token.save()
                else:
                    token = CustomToken.objects.create(accessToken=accessToken, refreshToken=refreshToken, user=user)
                return Response({'success':True, 'message':'successfully created user', 'userDetails':userDetails})
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
                    'expiresIn': openapi.Schema(type=openapi.TYPE_STRING, default='2 minutes'),
                    'refreshToken': openapi.Schema(type=openapi.TYPE_STRING, example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIiwiZXhwIjoxNjgzNzk4MzU5LCJpYXQiOjE2ODM2Mrffo4g2R3Zy8sZw'),
                },
            ),
        },
        operation_description="User Onboarding and Sign in API",
    )

    # Login API requires Firebase token
    def post(self, request, format=None):
        if request.data.get('tokenId') is not None:
            tokenId = request.data.get('tokenId')
        else:
            return Response({'success':False, 'message':'please enter valid token'})
        
        try:
            if 'email' in request.session.keys() and request.session['email'] is not None:
                email = request.session['email']
            else:
                if tokenId is not None:
                    try:
                        decoded_token = auth.verify_id_token(tokenId)
                        if decoded_token is not None:
                            if 'email' in decoded_token:
                                email = decoded_token['email']
                            else:
                                return Response({'success':False, 'message':'email Cannot be Empty'})         
                        else:
                            return Response({'success': False, 'message': 'unable to verify user'})
                    except Exception as e:
                        return Response({'success': False, 'error': str(e)})
                else:
                    return Response({'success': False, 'message': 'Please provide valid id token'})

                if Volunteer.objects.filter(email=decoded_token['email']).exists():
                    user = Volunteer.objects.get(email=decoded_token['email'])
                    userDetails = UserProfileSerializer(user).data
                    accessToken = create_access_token(user.id)
                    refreshToken = create_refresh_token(user.id)
                else:
                    return Response({'success': False, 'message':'user with email does not exist'})

                if CustomToken.objects.filter(user=user).exists():
                    token = CustomToken.objects.get(user=user)
                    token.refreshToken = refreshToken
                    token.accessToken = accessToken
                    token.save()
                else:
                    token = CustomToken.objects.create(accessToken=accessToken, refreshToken=refreshToken, user=user)

                return Response({
                    'success': True,
                    'message': 'successfully signed in',
                    'isAuthenticated': True,
                    'token': accessToken,
                    'expiresIn': '2 minutes',
                    'refreshToken': refreshToken,
                    'user': userDetails,
                })
            
        except Exception as e:
            return Response({'error': str(e), 'isAuthenticated': False, 'success': False})
        
# fetch All Food Events for food Seekers (POST METHOD)     
class FindFood(APIView):
    ## removed authentication for find food as food seekers do not have access Token
    # authentication_classes = [VolunteerTokenAuthentication]
    # permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['lat', 'lng', 'alt', 'eventStartDate', 'eventEndDate'],
            properties={
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example='12.916540'),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example='77.651950'),
                'alt': openapi.Schema(type=openapi.FORMAT_FLOAT, example='4500'),
                'eventStartDate': openapi.Schema(type=openapi.FORMAT_DATE,example='2023-05-05'),
                'eventEndDate': openapi.Schema(type=openapi.FORMAT_DATE, example='2023-05-05'),
            },
        ),
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
        # manual_parameters=[
        #     openapi.Parameter(
        #         name='Authorization',
        #         in_=openapi.IN_HEADER,
        #         type=openapi.TYPE_STRING,
        #         description='Token',
        #     ),
        # ],
    )

    def post(self, request, format=None):
        # Find Food API will return all the Food Events occuring within same city of the User location
        # Address (latitude, longitude and altitude)
        # From and to date
        try:

            if request.data.get('lat') is not None:
                lat = request.data.get('lat')
            else:
                return Response({'success': False, 'message':'please enter valid latitude'})
            
            if request.data.get('lng') is not None:
                lng = request.data.get('lng')
            else:
                return Response({'success': False, 'message': 'please enter valid longitude'})
            
            if request.data.get('alt') is not None:
                alt = request.data.get('alt')
            else:
                return Response({'success': False, 'message': 'please enter valid altitude'})
            
            if request.data.get('eventStartDate') is not None:
                fromDate = request.data.get('eventStartDate')
            else:
                return Response({'success': False, 'message': 'please enter valid Event Start Date'})
            
            if request.data.get('eventEndDate') is not None:
                toDate = request.data.get('eventEndDate')
            else:
                return Response({'success': False, 'message': 'please enter valid Event End Date'})

            if Address.objects.filter(lat=lat, lng=lng, alt=alt).exists():
                address = Address.objects.get(lat=lat, lng=lng, alt=alt)
            else:
                address = Address.objects.create(lat=lat, lng=lng, alt=alt)

            if FoodEvent.objects.filter(eventStartDate__gte=fromDate, eventEndDate__lte=toDate, address__city = address.city).exists():
                foodEvents = FoodEvent.objects.filter(eventStartDate__gte=fromDate, eventEndDate__lte=toDate, address__city = address.city)
                foodEventsDetails = FoodEventSerializer(foodEvents, many=True).data
                return Response({'success': True, 'foodEvents': foodEventsDetails})
            else:
                return Response({'success': True, 'foodEvents': []})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})
        
#  GET and Post Food Event API
class Event(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['eventName', 'lat', 'lng', 'alt', 'eventStartDate', 'eventEndDate', 'additionalInfo', 'files'], 
            properties={
                'eventName': openapi.Schema(type=openapi.TYPE_STRING, example="EVENT NAME"),
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example='12.916540'),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example='77.651950'),
                'alt': openapi.Schema(type=openapi.FORMAT_FLOAT, example='4500'),
                'eventStartDate': openapi.Schema(type=openapi.FORMAT_DATE,example='2023-05-05'),
                'eventEndDate': openapi.Schema(type=openapi.FORMAT_DATE, example='2023-05-05'),
                'additionalInfo': openapi.Schema(type=openapi.TYPE_STRING, example='Free Vegan Meals'),
                'files': openapi.Schema(type=openapi.TYPE_FILE,),
            },
        ),
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
            
            if request.data.get('eventName') is not None:
                eventName = request.data.get('eventName')
            else:
                return Response({'success': False, 'message': 'please enter valid Event Name'})
            
            if request.data.get('lat') is not None:
                lat = request.data.get('lat')
            else:
                return Response({'success': False, 'message':'please enter valid latitude'})
            
            if request.data.get('lng') is not None:
                lng = request.data.get('lng')
            else:
                return Response({'success': False, 'message': 'please enter valid longitude'})
            
            if request.data.get('alt') is not None:
                alt = request.data.get('alt')
            else:
                return Response({'success': False, 'message': 'please enter valid altitude'})
            
            if request.data.get('eventStartDate') is not None:
                eventStartDate = request.data.get('eventStartDate')
            else:
                return Response({'success': False, 'message': 'please enter valid Event Start Date'})
            
            if request.data.get('eventEndDate') is not None:
                eventEndDate = request.data.get('eventEndDate')
            else:
                return Response({'success': False, 'message': 'please enter valid Event End Date'})
            
            if request.data.get('additionalInfo') is not None:
                additionalInfo = request.data.get('additionalInfo')
            else:
                return Response({'success': False, 'message': 'please enter valid Description'})
            
            if request.FILES.getlist('files') is not None:
                files = request.FILES.getlist('files')
            else:
                files=[]
                return  files
            
            if Address.objects.filter(lat=lat, lng=lng, alt=alt).exists():
                address = Address.objects.get(lat=lat, lng=lng, alt=alt)
            else:
                address = Address.objects.create(lat=lat, lng=lng, alt=alt)

            
            organizer = Volunteer.objects.get(id=request.user.id, isVolunteer=True, volunteerType=VOLUNTEER_TYPE[2][0])
            
            
            if FoodEvent.objects.filter(address=address, eventStartDate=eventStartDate, eventEndDate=eventEndDate, createdBy=organizer).exists():
                foodEvent = FoodEvent.objects.get(address=address, eventStartDate=eventStartDate, eventEndDate=eventEndDate, createdBy=organizer)
                foodEventDetaills = FoodEventSerializer(foodEvent).data
                return Response({'success': False, 'message': 'Event Already Exists', 'eventDetails':foodEventDetaills})
            else:
                createdAt = datetime.now()
                foodEvent = FoodEvent.objects.create(
                    name = eventName,
                    address=address, 
                    eventStartDate=eventStartDate, 
                    eventEndDate=eventEndDate, 
                    createdBy=organizer, 
                    organizerPhoneNumber=organizer.phoneNumber, 
                    createdAt=createdAt, 
                    additionalInfo=additionalInfo,
                    active=True 
                ) # to be modified if active True or False
                for file in files:
                    Document.objects.create(
                        docType=DOCUMENT_TYPE[1][0], 
                        document=file, 
                        createdAt=createdAt, 
                        event=foodEvent
                    )
                return Response({'success': True, 'message': 'Event Posted Sucessfully'})
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
    def get(self, request, format=None):
        try:
            user = request.user

            if FoodEvent.objects.filter(createdBy=user).exists():
                foodEvents = FoodEvent.objects.filter(createdBy=user)
                foodEventsDetails = FoodEventSerializer(foodEvents, many=True).data
                return Response({'success': True, 'foodEvents': foodEventsDetails})
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
            if request.data.get('eventId') is not None:
                eventId = request.data.get('eventId')
            else:
                return Response({'success': False, 'message': 'please enter valid Event Id'})
            
            user = request.user

            if FoodEvent.objects.filter(id=eventId).exists():
                foodEvent = FoodEvent.objects.get(id=eventId)
                if EventBookmark.objects.filter(user=user, event=foodEvent).exists():
                    return Response({'success':False, 'message': 'Bookmark already exists'})
                else:
                    createdAt = datetime.now()
                    EventBookmark.objects.create(user=user, event=foodEvent, createdAt=createdAt)
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
                bookmarkedEvents = EventBookmark.objects.filter(user=user, isDeleted=False)
                bookmarkedEventDetails = BookmarkedEventSerializer(bookmarkedEvents, many=True).data
                return Response({'success':True, 'bookmarkedEventDetails': bookmarkedEventDetails})
            else:
                return Response({'success': True, 'bookmarkedEventDetails': []})
            
        except Exception as e:
            return Response({'success': False, 'message': str(e)})
        
# GET API (fetch categories of Recipe)
class Categories(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

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
            
            category = Category.objects.all()
            categoryList = CategorySerializer(category, many=True).data
            return Response({'success': True, 'categoriesList': categoryList})

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

    def post(self, request, categoryId, format=None):
        try:

            if categoryId is None:
                return Response({'success': False, 'message':'Please provide category Id'})
            
            if request.data.get('foodName') is not None:
                foodName = request.data.get('foodName')
            else:
                return Response({'success': False, 'message': 'please enter valid Food Name'})
            
            if request.data.get('ingredients') is not None:
                ingredients = request.data.get('ingredients')
            else:
                return Response({'success': False, 'message': 'please enter valid Ingredients'})
            
            if request.data.get('cookingInstructions') is not None:
                cookingInstructions = request.data.get('cookingInstructions')
            else:
                return Response({'success': False, 'message': 'please enter valid Cooking Instructions'})
            
            if request.FILES.getlist('foodImage') is not None:
                files = request.FILES.getlist('foodImage')
            else:
                files=[]
                return  files
            
            # Slugs and tags to  be modified later

            user = request.user
            
            if Category.objects.filter(id=categoryId).exists():
                category = Category.objects.get(id=categoryId)
            else:
                return Response({'success': False, 'message': 'Category with id does not exist'})
            
            if FoodRecipe.objects.filter(foodName=foodName, ingredients=ingredients, category=category).exists():
                recipe = FoodRecipe.objects.get(foodName=foodName, ingredients=ingredients, category=category)
                return Response({'success': True, 'message': 'Food Recipe already exists','recipe':recipe.id})
            else:
                recipe = FoodRecipe.objects.create(foodName=foodName, ingredients=ingredients, category=category, cookingInstructions=cookingInstructions)
                createdAt = datetime.now()
                for file in files:
                    doc = Document.objects.create(
                        docType=DOCUMENT_TYPE[2][0], 
                        document=file, 
                        createdAt=createdAt, 
                    )
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

    def get(self, request, categoryId, format=None):
        try:
            user = request.user
            
            if Category.objects.filter(id=categoryId).exists():
                category = Category.objects.get(id=categoryId)
            else:
                return Response({'success': False, 'message': 'Category with id does not exist'})

            if FoodRecipe.objects.filter(category=category).exists():
                recipes = FoodRecipe.objects.filter(category=category)
                recipeList = FoodRecipeSerializer(recipes, many=True).data
                return Response({'success':True, 'recipeList': recipeList})
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
            
            requestType = RequestType.objects.all()
            requestTypeList = RequestTypeSerializer(requestType, many=True).data
            return Response({'success': True, 'requestTypeList': requestTypeList})

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

    def post(self, request, requestTypeId, format=None):
        try:
            
            if request.data.get('itemTypeId') is not None:
                itemTypeId = request.data.get('itemTypeId')
            else:
                return Response({'success': False, 'message': 'please enter valid Item Type'})
            
            if request.data.get('itemName') is not None:
                itemName = request.data.get('itemName')
            else:
                return Response({'success': False, 'message': 'please enter valid Item Name'})
            
            if request.data.get('requiredDate') is not None:
                requiredDate = request.data.get('requiredDate')
            else:
                return Response({'success': False, 'message': 'please enter valid Required Date'})
            
            if request.data.get('quantity') is not None:
                quantity = request.data.get('quantity')
            else:
                return  Response({'success': False, 'message': 'please enter valid quantity'})
            
            user = request.user

            if ItemType.objects.filter(id=itemTypeId).exists():
                itemType = ItemType.objects.get(id=itemTypeId)
            else:
                return Response({'success': False, 'message': 'Item Type with id does not exist'})
            
            if FoodItem.objects.filter(itemName=itemName, itemType=itemType).exists():
                foodItem = FoodItem.objects.get(itemName=itemName, itemType=itemType)
            else:
                foodItem = FoodItem.objects.create(itemName=itemName, itemType=itemType, addedBy=user, createdAt=datetime.now())
            
            if RequestType.objects.filter(id=requestTypeId).exists():
                requestType = RequestType.objects.get(id=requestTypeId)
            else:
                return Response({'success': False, 'message': 'Request Type with id does not exist'})
            
            if Request.objects.filter(type=requestType, createdBy=user, requiredDate=requiredDate, active=True, quantity=quantity, foodItem=foodItem).exists():
                itemRequest = Request.objects.get(type=requestType, createdBy=user, requiredDate=requiredDate, active=True, quantity=quantity, foodItem=foodItem)
                return Response({'success': True, 'message': 'Request already exists','itemRequest':itemRequest.id})
            else:
                createdAt = datetime.now()
                itemRequest = Request.objects.create(type=requestType, createdBy=user, requiredDate=requiredDate, active=True, quantity=quantity, foodItem=foodItem, createdAt=createdAt)
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

    def post(self, request, requestTypeId, format=None):
        try:
            if request.data.get('eventId') is not None:
                eventId = request.data.get('eventId')
            else:
                return Response({'success': False, 'message': 'please enter valid Event Id'})
            
            if request.data.get('lat') is not None:
                lat = request.data.get('lat')
            else:
                return Response({'success': False, 'message': 'please enter valid latitude'})
            
            if request.data.get('lng') is not None:
                lng = request.data.get('lng')
            else:
                return Response({'success': False, 'message': 'please enter valid longitude'})
            
            if request.data.get('alt') is not None:
                alt = request.data.get('alt')
            else:
                return Response({'success': False, 'message': 'please enter valid altitude'})
            
            if request.data.get('requiredDate') is not None:
                requiredDate = request.data.get('requiredDate')
            else:
                return Response({'success': False, 'message': 'please enter valid Required Date'})
            
            if request.data.get('numberOfVolunteers') is not None:
                numberOfVolunteers = request.data.get('numberOfVolunteers')
            else:
                return Response({'success': False, 'message': 'please enter valid Number of required Volunteers'})

            user = request.user            

            if FoodEvent.objects.filter(id=eventId, createdBy=user).exists():
                foodEvent = FoodEvent.objects.get(id=eventId, createdBy=user)
            else:
                return Response({'success': False, 'message': 'Food event with id does not exist'})

            if RequestType.objects.filter(id=requestTypeId, active=True).exists():
                requestType = RequestType.objects.get(id=requestTypeId, active=True)
            else:
                return Response({'success':False, 'message':'Request Type with id does not exist'})
            
            
            if Request.objects.filter(type=requestType, createdBy=user, requiredDate=requiredDate, active=True, fullfilled=False, quantity=numberOfVolunteers,foodEvent=foodEvent).exists():
                request = Request.objects.filter(type=requestType, createdBy=user, requiredDate=requiredDate, active=True, fullfilled=False, quantity=numberOfVolunteers, foodEvent=foodEvent)
                return Response({'success':False, 'message':'Request Already Exists for this particular Event'})
            else:
                Request.objects.create(
                    type=requestType, 
                    createdBy=user, 
                    requiredDate=requiredDate,
                    active=True,
                    createdAt=datetime.now(),
                    quantity=numberOfVolunteers,
                    foodEvent=foodEvent
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
            required=['itemTypeId', 'foodName', 'quantity', 'pickupDate', 'lat', 'lng', 'alt', 'phoneNumber'], 
            properties={
                'itemTypeId': openapi.Schema(type=openapi.TYPE_NUMBER, example="1"),
                'foodName': openapi.Schema(type=openapi.TYPE_STRING, example="foodName"),  #to be modified # for now conside Food iTem Id
                'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, example='15'),
                'pickupDate': openapi.Schema(type=openapi.FORMAT_DATE,example='2023-05-05'),
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example='12.916540'),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example='77.651950'),
                'alt': openapi.Schema(type=openapi.FORMAT_FLOAT, example='4500'),
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

            if request.data.get('itemTypeId') is not None:
                itemTypeId = request.data.get('itemTypeId')
            else:
                return Response({'success': False, 'message': 'please enter valid item Type Id'})
            
            if request.data.get('foodName') is not None:
                foodName = request.data.get('foodName')
            else:
                return Response({'success': False, 'message': 'please enter valid Food Item'})
            
            if request.data.get('quantity') is not None:
                quantity = request.data.get('quantity')
            else:
                return Response({'success': False, 'message': 'please enter valid quantity'})
            
            if request.data.get('pickupDate') is not None:
                pickupDate = request.data.get('pickupDate')
            else:
                return Response({'success': False, 'message': 'please enter valid pickup Date'})
         
            if request.data.get('lat') is not None:
                lat = request.data.get('lat')
            else:
                return Response({'success': False, 'message': 'please enter valid latitude'})
            
            if request.data.get('lng') is not None:
                lng = request.data.get('lng')
            else:
                return Response({'success': False, 'message': 'please enter valid longitude'})
            
            if request.data.get('alt') is not None:
                alt = request.data.get('alt')
            else:
                return Response({'success': False, 'message': 'please enter valid altitude'})
            
            if request.data.get('phoneNumber') is not None:
                phoneNumber = request.data.get('phoneNumber')
            else:
                return Response({'success': False, 'message': 'please enter valid phone Number'})

            user = request.user
            
            if ItemType.objects.filter(id=itemTypeId).exists():
                itemType = ItemType.objects.get(id=itemTypeId)
            else:
                return Response({'success': False, 'message': 'Item Type with id does not exist'})
            
            if Address.objects.filter(lat=lat, lng=lng, alt=alt).exists():
                pickupAddress = Address.objects.get(lat=lat, lng=lng, alt=alt)
            else:
                pickupAddress = Address.objects.create(lat=lat, lng=lng, alt=alt)

            if FoodItem.objects.filter(itemName=foodName).exists():
                foodItem = FoodItem.objects.get(itemName=foodName, addedBy=user, itemType=itemType)
            else:
                foodItem = FoodItem.objects.create(itemName=foodName, addedBy=user, itemType=itemType, createdAt=datetime.now())

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

 
# Update Volunteer Profile API  
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
    )

    # fetch volunteer Profile API
    def get(self, request,  format=None):
        try:
            if request.user.id is not None:
                userId= request.user.id
                if Volunteer.objects.filter(id=userId).exists():
                    user = Volunteer.objects.get(id=userId)
                    userDetails = UserProfileSerializer(user).data
                    return Response({'success':True, 'userDetails':userDetails})
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
            required=['name','email','lat','longitude','altitude','phoneNumber'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, example='Find Food User'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, example='user@findfood.com'),
                'lat': openapi.Schema(type=openapi.FORMAT_FLOAT, example=12.916540),
                'lng': openapi.Schema(type=openapi.FORMAT_FLOAT, example=77.651950),
                'alt': openapi.Schema(type=openapi.FORMAT_FLOAT, example=4500),
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
    )

    # user onboarding API required firebase token and name
    def put(self, request,  format=None):

        if request.data.get('name') is not None:
            name = request.data.get('name')
        else:
            return Response({'success':False, 'message':'Please enter valid name'})
        
        if request.data.get('email') is not None:
            email = request.data.get('email')
        else:
            return Response({'success':False, 'message':'Please enter valid email'})
        
        if request.data.get('lat') is not None:
            lat = request.data.get('lat')
        else:
            return Response({'success':False, 'message':'Please enter valid latitude'})
        
        if request.data.get('lng') is not None:
            lng = request.data.get('lng')
        else:
            return Response({'success':False, 'message':'Please enter valid longitude'})
        
        if request.data.get('alt') is not None:
            alt = request.data.get('alt')
        else:
            return Response({'success':False, 'message':'Please enter valid altitude'})

        if request.data.get('phoneNumber') is not None:
            phoneNumber = request.data.get('phoneNumber')
        else:
            return Response({'success':False, 'message':'Please enter valid phoneNumber'})
        
        if request.data.get('volunteerType') is not None:
            volunteerType = request.data.get('volunteerType')
        else:
            return Response({'success':False, 'message':'Please enter valid volunteer Type'})
        
        try:

            if Address.objects.filter(lat=lat, lng=lng, alt=alt).exists():
                address = Address.objects.get(lat=lat, lng=lng, alt=alt)
            else:
                address = Address.objects.create(lat=lat, lng=lng, alt=alt)            

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
                userDetails = UserProfileSerializer(user).data
                return Response({'success': True, 'message':'Profile updated successfully', 'userDetails':userDetails})
            else:
                return Response({'success':False, 'message':'Volunteer with email does not exist'})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})
