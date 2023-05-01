from django.shortcuts import render
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class SendMessageMail(APIView):
    def get(self, request, format=None):
        try:
            print('Successfully sent message')
            return Response({'success':True})
        except:
            print("Failed to send message")
            return Response({'success':False})


class TestAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return Response({'version': request.version})