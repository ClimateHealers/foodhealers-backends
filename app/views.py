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
from .local_dev_utils import getAccessTokenForDriver

# get Django Access token for development testing. 
getAccessTokenForDriver(id=14)

# Sign Up API  
class SignUp(APIView):

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['token', 'name', 'email', 'isVolunteer'],
            properties={
                'token_id': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'isVolunteer': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            },
        ),
        responses={200: "Successful operation"},
        operation_description="User Onboarding API",
    )

    # user onboarding API required firebase token and name
    def post(self, request,  format=None):
        token_id = request.data.get('token_id')
        password = 'Admin123'
        name = request.data.get('name')
        isVolunteer = request.data.get('isVolunteer')
        email = None
        try:
            if 'email' in request.session.keys() and request.session['email'] is not None:
                email = request.session['email']

            else:
                if token_id is not None:
                    try:
                        decoded_token = auth.verify_id_token(token_id)

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
            username = randomNumber + '@' + decoded_token['name']

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
            required=['token_id'],
            properties={
                'token_id': openapi.Schema(type=openapi.TYPE_STRING),
            },            
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['token_id'],
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, default='Successfully signed in'),
                    'is_authenticated': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'accessToken': openapi.Schema(type=openapi.TYPE_STRING, example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpgtZ2Z1QWxBNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIizU5LCJpYXQiOjE2ODM2MjU1NTl9.3EyvZffo4g2R3Zy8sZw'),
                    'expires_in': openapi.Schema(type=openapi.TYPE_STRING, example='2 minutes'),
                    'refreshToken': openapi.Schema(type=openapi.TYPE_STRING, example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVNmZBQTQyU09DNkI0STR4Qng5UXlUSmhIcW9VIiwiZXhwIjoxNjgzNzk4MzU5LCJpYXQiOjE2ODM2Mrffo4g2R3Zy8sZw'),
                },
            ),
        },
        operation_description="User Onboarding and Sign in API",
    )

    # Login API requires Firebase token
    def post(self, request, format=None):
        token_id = request.data.get('token_id')
        password = 'Admin123'
        try:
            if 'email' in request.session.keys() and request.session['email'] is not None:
                email = request.session['email']
            else:
                if token_id is not None:
                    try:
                        decoded_token = auth.verify_id_token(token_id)
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
                
                user, created = Volunteer.objects.get_or_create(email=decoded_token['email'])
                if created:
                    randomNumber = str(uuid.uuid4())[:6]
                    username = randomNumber + '@' + decoded_token['name']
                    user.username = username
                    user.password = password
                    if 'name' in decoded_token:
                        user.name = decoded_token['name']
                    user.save()

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
                return Response({
                    'success': True,
                    'message': 'successfully signed in',
                    'is_authenticated': True,
                    'token': accessToken,
                    'expires_in': '2 minutes',
                    'refreshToken': refreshToken,
                    # 'user': user.id,
                })
        except Exception as e:
            return Response({'error': str(e), 'is_authenticated': False, 'success': False})
        
        
class FindFood(APIView):
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [IsAuthenticated, VolunteerPermissionAuthentication]

    # OpenApi specification and Swagger Documentation
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['lat', 'lng', 'alt', 'eventStartDate', 'eventEndDate'],
            properties={
                'lat': openapi.Schema(type=openapi.TYPE_NUMBER,),
                'lng': openapi.Schema(type=openapi.TYPE_NUMBER,),
                'alt': openapi.Schema(type=openapi.TYPE_NUMBER,),
                'eventStartDate': openapi.Schema(type=openapi.FORMAT_DATE,),
                'eventEndDate': openapi.Schema(type=openapi.FORMAT_DATE,),
            },
        ),
        responses={200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['token_id'],
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                    'foodEvents': openapi.Schema(type=openapi.TYPE_OBJECT),
                },
            ),},
        operation_description="Find food Events API",
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
        # Find Food API will return all the Food Events occuring within 50kms of the User location
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

            # To be Modified According to Address
            # for now only Date time feature implemented
            if FoodEvent.objects.filter(eventStartDate__gte=fromDate, eventEndDate__lte=toDate).exists():
                foodEvents = FoodEvent.objects.filter(eventStartDate__gte = fromDate, eventEndDate__lte=toDate).order_by('-eventStartDate')
                foodEventsDetails = foodEventSerializer(foodEvents).data
                return Response({'success': True, 'foodEvents': foodEventsDetails})
            else:
                return Response({'success': True, 'foodEvents': []})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})
