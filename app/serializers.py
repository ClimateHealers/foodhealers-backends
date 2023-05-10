
from .models import *
from rest_framework import serializers
from rest_framework.serializers import Serializer


class UserProfileSerializer(Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.CharField()
    email = serializers.CharField()
    phoneNumber = serializers.CharField()
    isDriver = serializers.BooleanField()
    isVolunteer = serializers.BooleanField()
    volunteerType = serializers.CharField()

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
    address = serializers.CharField()
    eventStartDate = serializers.CharField()
    eventEndDate = serializers.BooleanField()
    category = serializers.CharField()

    def get_id(self, obj):
        return obj.id
    
    def get_address(self, obj):
        if obj.address is not None:
            return obj.address
        else:
            return None
        
    def get_eventStartDate(self, obj):
        if obj.eventStartDate is not None:
            return obj.eventStartDate
        else:
            return None
        
    def get_eventEndDate(self, obj):
        if obj.eventEndDate is not None:
            return obj.eventEndDate
        else:
            return None
        
    def get_category(self, obj):
        if obj.category is not None:
            return obj.category
        else:
            return None    