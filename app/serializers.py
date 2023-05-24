
from .models import *
from rest_framework import serializers
from rest_framework.serializers import Serializer
from django.core.files.storage import get_storage_class


class AddressSerializer(Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    alt = serializers.FloatField()
    streetAddress = serializers.SerializerMethodField()
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    postalCode = serializers.CharField(max_length=100)
    fullAddress = serializers.SerializerMethodField()

    def get_lat(self, obj):
        if obj.lat is not None:
            return obj.lat
        else:
            return 'Latitude not specified'
        
    def get_lng(self, obj):
        if obj.lng is not None:
            return obj.lng
        else:
            return 'Longitude not specified'
        
    def get_alt(self, obj):
        if obj.alt is not None:
            return obj.alt
        else:
            return 'Altitude not specified'
        
    def get_streetAddress(self, obj):
        if obj.streetAddress is not None:
            return obj.streetAddress
        else:
            return 'Street address not specified'
        
    def get_city(self, obj):
        if obj.city is not None:
            return obj.city
        else:
            return 'City not specified'
        
    def get_state(self, obj):
        if obj.state is not None:
            return obj.state
        else:
            return 'State not specified'
        
    def get_postalCode(self, obj):
        if obj.postalCode is not None:
            return obj.postalCode
        else:
            return 'Postal code not specified'
        
    def get_fullAddress(self, obj):
        if obj.fullAddress is not None:
            return obj.fullAddress
        else:
            return 'Full address not specified' 

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
            return 'Document type not specified'
        
    def get_document(self, obj): # to be modified
        if obj.document is not None:
            mediaStorage = get_storage_class()()
            documentUrl = mediaStorage.url(name=obj.document.name)
            return documentUrl
        else:
            return 'Document not specified'

    def get_verified(self, obj):
        if obj.verified is not None:
            return obj.verified
        else:
            return False
        
    def get_event(self, obj):
        if obj.event is not None:
            return obj.event
        else:
            return "Event not specified"   
        
    def get_volunteer(self, obj):
        if obj.volunteer is not None:
            return obj.volunteer.name
        else: 
            return "Volunteer not specified"
        
    def get_vehicle(self, obj):
        if obj.vehicle is not None:
            return obj.vehicle
        else:
            return "Vehicle not specified"   

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
            return 'Phone number not specified'

    def get_isVolunteer(self, obj):
        if obj.isVolunteer is not None:
            return obj.isVolunteer
        else:
            return 'Volunteer not specified'
        
    def get_isDriver(self, obj):
        if obj.isDriver is not None:
            return obj.isDriver
        else:
            return False
        
    def get_volunteerType(self, obj):
        if obj.volunteerType is not None:
            return obj.volunteerType
        else:
            return 'Volunteer Type not specified'

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
            return 'Name not specified'
    
    def get_address(self, obj):
        if obj.address is not None:
            return str(obj.address)
        else:
            return 'address not specified'

    def get_eventStartDate(self, obj):
        if obj.eventStartDate is not None:
            return obj.eventStartDate.strftime('%Y-%m-%d')
        else:
            return 'Event start date not specified'
        
    def get_eventEndDate(self, obj):
        if obj.eventEndDate is not None:
            return obj.eventEndDate.strftime('%Y-%m-%d')
        else:
            return 'Event end date not specified' 
    
    def get_additionalInfo(self, obj):
        if obj.additionalInfo is not None:
            return obj.additionalInfo
        else:
            return "Additional information not specified"

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
            return 'User not specified'
    
    def get_event(self, obj):
        if obj.event is not None:
            return FoodEventSerializer(obj.event).data
        else:
            return 'Food event not specified'
        
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
            return 'Name not specified'
        
    def get_createdAt(self, obj):
        if obj.createdAt is not None:
            return obj.createdAt.strftime('%Y-%m-%d')
        else:
            return 'CreatedAt not specified'
    
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
            return 'Name not specified'
        
    def get_ingredients(self, obj):
        if obj.ingredients is not None:
            return obj.ingredients
        else:
            return 'Ingredient not specified'
    
    def get_cookingInstructions(self, obj):
        if obj.cookingInstructions is not None:
            return obj.cookingInstructions
        else:
            return 'Cooking instructions not specified'
        
    def get_category(self, obj):
        if obj.category is not None:
            return obj.category.name
        else:
            return 'Name not specified'
        
    def get_foodImage(self, obj):
        if obj.foodImage is not None:
            return DocumentSerializer(obj.foodImage.all(), many=True).data
        else:
            return 'Food image not specified'
        
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
            return 'Name not specified'
        
    def get_createdAt(self, obj):
        if obj.createdAt is not None:
            return obj.createdAt.strftime('%Y-%m-%d')
        else:
            return 'CreatedAt not specified'
    
    def get_active(self, obj):
        if obj.active is not None:
            return obj.active
        else:
            return False
        
class DeliveryDetailSerializer(Serializer):
    id = serializers.SerializerMethodField()
    pickupAddress =  serializers.SerializerMethodField()
    pickupDate = serializers.SerializerMethodField()
    pickedup =  serializers.BooleanField()
    dropAddress =  serializers.SerializerMethodField()
    dropDate = serializers.SerializerMethodField()
    delivered = serializers.BooleanField()
    driver = serializers.SerializerMethodField()
    
    def get_id(self, obj):
        return obj.id
    
    def get_pickupAddress(self, obj):
        if obj.pickupAddress is not None:
            return AddressSerializer(obj.pickupAddress).data
        else:
            return 'Pickup address not specified'
        
    def get_pickupDate(self, obj):
        if obj.pickupDate is not None:
            return obj.pickupDate.strftime('%Y-%m-%d')
        else:
            return 'Pickup date not specified'
    
    def get_pickedup(self, obj):
        if obj.pickedup is not None:
            return obj.pickedup
        else:
            return False
        
    def get_dropAddress(self, obj):
        if obj.dropAddress is not None:
            return AddressSerializer(obj.dropAddress).data
        else:
            return 'Drop address not specified'
        
    def get_dropDate(self, obj):
        if obj.dropDate is not None:
            return obj.dropDate.strftime('%Y-%m-%d')
        else:
            return 'Drop date not specified'
        
    def get_delivered(self, obj):
        if obj.delivered is not None:
            return obj.delivered
        else:
            return False
        
    def get_driver(self, obj):
        if obj.driver is not None:
            return obj.driver.name
        else:
            return 'Driver not specified'    

        
class DonationSerializer(Serializer):
    id = serializers.SerializerMethodField()
    donationType =  serializers.SerializerMethodField()
    foodItem = serializers.SerializerMethodField()
    quantity =  serializers.SerializerMethodField()
    donatedBy =  serializers.SerializerMethodField()
    fullfilled = serializers.BooleanField()
    delivery =   serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id

    def get_donationType(self, obj):
        if obj.donationType is not None:
            return obj.donationType.name
        else:
            return 'Donation type not specified'
    
    def get_foodItem(self, obj):
        if obj.foodItem is not None:
            return obj.foodItem.itemName
        else:
            return 'Food item not specified'
    
    def get_quantity(self, obj):
        if obj.quantity is not None:
            return obj.quantity
        else:
            return 'Quantity not specified'
        
    def get_donatedBy(self, obj):
        if obj.donatedBy is not None:
            return obj.donatedBy.name
        else:
            return 'DonatedBy details not specified'    

    def get_fullfilled(self, obj):
        if obj.fullfilled is not None:
            return obj.fullfilled
        else:
            return False
        
    def get_delivery(self, obj):
        if obj.delivery is not None:
            return DeliveryDetailSerializer(obj.delivery).data
        else:
            return 'Delivery details not specified'