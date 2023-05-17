
from .models import *
from rest_framework import serializers
from rest_framework.serializers import Serializer
from django.core.files.storage import get_storage_class



class DocumentSerializer(Serializer):
    id = serializers.SerializerMethodField()
    docType =  serializers.SerializerMethodField()
    document = serializers.SerializerMethodField()
    verified = serializers.BooleanField(default=False)
    event = serializers.SerializerMethodField()
    vehicle = serializers.SerializerMethodField()
    volunteer = serializers.SerializerMethodField()
    isActive = serializers.BooleanField(default=True)

    def get_id(self, obj):
        return obj.id
    
    def get_docType(self, obj):
        if obj.docType is not None:
            return obj.docType
        else:
            return 'Document Type Not Available'
        
    def get_document(self, obj): # to be modified
        if obj.document is not None:
            mediaStorage = get_storage_class()()
            documentUrl = mediaStorage.url(name=obj.document.name)
            return documentUrl
        else:
            return 'Document Not Available'

    def get_verified(self, obj):
        if obj.verified is not None:
            return obj.verified
        else:
            return False
        
    def get_event(self, obj):
        if obj.event is not None:
            return obj.event
        else:
            return "Event not Available"   
        
    def get_volunteer(self, obj):
        if obj.volunteer is not None:
            return obj.volunteer.name
        else: 
            return "Volunteer not Available"
        
    def get_vehicle(self, obj):
        if obj.vehicle is not None:
            return obj.vehicle
        else:
            return "Vehicle not Available"   

    def get_isActive(self, obj):
        if obj.isActive is not None:
            return obj.isActive
        else:
            return False

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

class FoodEventSerializer(Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=100)
    address = serializers.SerializerMethodField()
    eventStartDate = serializers.SerializerMethodField()
    eventEndDate = serializers.SerializerMethodField()
    additionalInfo =serializers.CharField()

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
            return 'Address not Available'

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
    
    def get_additionalInfo(self, obj):
        if obj.additionalInfo is not None:
            return obj.additionalInfo
        else:
            return "No Information"

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
            return FoodEventSerializer(obj.event).data
        else:
            return 'Food Event not Available'
        
class CategorySerializer(Serializer):
    id = serializers.SerializerMethodField()
    name =  serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    active = serializers.BooleanField(default=True)

    def get_id(self, obj):
        return obj.id
    
    def get_name(self, obj):
        if obj.name is not None:
            return obj.name
        else:
            return 'Name not Available'
        
    def get_createdAt(self, obj):
        if obj.createdAt is not None:
            return obj.createdAt.strftime('%Y-%m-%d')
        else:
            return '0000-00-00'
    
    def get_active(self, obj):
        if obj.active is not None:
            return obj.active
        else:
            return False
        
class FoodRecipeSerializer(Serializer):
    id = serializers.SerializerMethodField()
    foodName =  serializers.SerializerMethodField()
    ingredients =  serializers.SerializerMethodField()
    category = serializers.SerializerMethodField() 
    foodImage = serializers.SerializerMethodField() 
    cookingInstructions = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id
    
    def get_foodName(self, obj):
        if obj.foodName is not None:
            return obj.foodName
        else:
            return 'Name not Available'
        
    def get_ingredients(self, obj):
        if obj.ingredients is not None:
            return obj.ingredients
        else:
            return 'Ingredient not Available'
    
    def get_cookingInstructions(self, obj):
        if obj.cookingInstructions is not None:
            return obj.cookingInstructions
        else:
            return 'Cooking Instructions not Available'
        
    def get_category(self, obj):
        if obj.category is not None:
            return obj.category.name
        else:
            return 'Name not Available'
        
    def get_foodImage(self, obj):
        if obj.foodImage is not None:
            return DocumentSerializer(obj.foodImage.all(), many=True).data
        else:
            return 'Not Available'
        
class RequestTypeSerializer(Serializer):
    id = serializers.SerializerMethodField()
    name =  serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    active = serializers.BooleanField(default=True)

    def get_id(self, obj):
        return obj.id
    
    def get_name(self, obj):
        if obj.name is not None:
            return obj.name
        else:
            return 'Name not Available'
        
    def get_createdAt(self, obj):
        if obj.createdAt is not None:
            return obj.createdAt.strftime('%Y-%m-%d')
        else:
            return '0000-00-00'
    
    def get_active(self, obj):
        if obj.active is not None:
            return obj.active
        else:
            return False