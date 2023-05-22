from .models import *
from app.authentication import create_access_token, create_refresh_token 

def getAccessToken(id):
    user = Volunteer.objects.get(id=id)
    accessToken = create_access_token(user.id)
    refreshToken = create_refresh_token(user.id)
    print('Token {token}'.format(token=str(accessToken)))