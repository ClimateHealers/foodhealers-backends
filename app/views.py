from django.shortcuts import render
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
    
class SendMessageMail(APIView):
    def get(self, request, format=None):
        try:
            print('Successfully sent message')
            return Response({'success':True})
        except:
            print("Failed to send message")
            return Response({'success':False})
    
        