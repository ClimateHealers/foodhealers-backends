import datetime
import jwt
from rest_framework.authentication import (get_authorization_header, TokenAuthentication)
from rest_framework.permissions import BasePermission
from rest_framework import exceptions
from app.models import Volunteer
from django.core import signing


def create_access_token(userId):
    value = signing.dumps(str(userId))
    return jwt.encode({
        'data': value,
        # Expiry time of a token
        'exp': datetime.datetime.utcnow()+datetime.timedelta(days=31),
        'iat': datetime.datetime.utcnow()  # created at
    }, 'access_secret', algorithm='HS256')


def decode_access_token(token):
    try:
        payload = jwt.decode(token, 'access_secret', algorithms='HS256')
        return payload['data']
    except:
        raise exceptions.AuthenticationFailed('Access denied')


def create_refresh_token(userId):
    value = signing.dumps(str(userId))
    return jwt.encode({
        'data': value,
        'exp': datetime.datetime.utcnow()+datetime.timedelta(days=38),
        'iat': datetime.datetime.utcnow()
    }, 'refresh_secret', algorithm='HS256')


def decode_refresh_token(token):
    try:
        payload = jwt.decode(token, 'refresh_secret', algorithms='HS256')
        return payload['data']
    except Exception as e:
        raise exceptions.AuthenticationFailed(str(e))


class VolunteerTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        try:
            auth = get_authorization_header(request).split()
            if auth and len(auth) == 2:
                token = auth[1].decode('utf-8')
                encodedUserId = decode_access_token(token)
                userId = signing.loads(encodedUserId)
                volunteer = Volunteer.objects.get(id=userId)

                return (volunteer, token)
        except Exception as e:
            print(e)
            raise exceptions.AuthenticationFailed(str(e))


class VolunteerPermissionAuthentication(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user)
    

