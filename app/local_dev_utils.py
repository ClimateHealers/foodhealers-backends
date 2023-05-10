from .models import *
from app.authentication import create_access_token, create_refresh_token, decode_access_token, VolunteerPermissionAuthentication, decode_refresh_token, VolunteerTokenAuthentication

def getAccessTokenForDriver(id):
    user = Volunteer.objects.get(id=id)
    accessToken = create_access_token(user.id)
    refreshToken = create_refresh_token(user.id)
    print('{token}'.format(token=str(accessToken)))