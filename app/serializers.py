
from .models import *
from rest_framework import serializers
from rest_framework.serializers import Serializer


class UserProfileSerializer(Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=100)
    phoneNumber = serializers.CharField(max_length=100)
    isDriver = serializers.BooleanField()
    isVolunteer = serializers.BooleanField()
    volunteerType = serializers.CharField(max_length=100)

    def get_id(self, obj):
        return obj.id
    
    def get_name(self, obj):
        return obj.name

    def get_phoneNumber(self, obj):
        if obj.phoneNumber is not None:
            return obj.phoneNumber
        else:
            return None

    def get_isVolunteer(self, obj):
        if obj.isVolunteer is not None:
            return obj.isVolunteer
        else:
            return False
        
    def get_isDriver(self, obj):
        if obj.isDriver is not None:
            return obj.isDriver
        else:
            return False
        
    def get_volunteerType(self, obj):
        if obj.volunteerType is not None:
            return obj.volunteerType
        else:
            return None

class foodEventSerializer(Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=100)
    address = serializers.SerializerMethodField()
    eventStartDate = serializers.SerializerMethodField()
    eventEndDate = serializers.SerializerMethodField()
    category = serializers.CharField(max_length=100)

    def get_id(self, obj):
        return obj.id
    
    def get_name(self, obj):
        if obj.name is not None:
            return obj.name
        else:
            return 'Name not Available'
    
    def get_address(self, obj):
        if obj.address is not None:
            return str(obj.address)
        else:
            return '0000-00-00'

    def get_eventStartDate(self, obj):
        if obj.eventStartDate is not None:
            return obj.eventStartDate.strftime('%Y-%m-%d')
        else:
            return None
        
    def get_eventEndDate(self, obj):
        if obj.eventEndDate is not None:
            return obj.eventEndDate.strftime('%Y-%m-%d')
        else:
            return None
        
    def get_category(self, obj):
        if obj.category is not None:
            return obj.category
        else:
            return None  

class BookmarkedEventSerializer(Serializer):
    id = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()    

    def get_id(self, obj):
        return obj.id
    
    def get_user(self, obj):
        if obj.user is not None:
            return obj.user.name
        else:
            return 'user not Available'
    
    def get_event(self, obj):
        if obj.event is not None:
            return foodEventSerializer(obj.event).data
        else:
            return 'Food Event not Available'