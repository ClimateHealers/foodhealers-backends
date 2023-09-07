
from .models import Volunteer
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
            media_storage = get_storage_class()()
            document_url = media_storage.url(name=obj.document.name)
            return document_url
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
            user = Volunteer.objects.get(id=obj.volunteer.id)
            user_details = UserProfileSerializer(user).data
            return user_details
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
    createdAt = serializers.SerializerMethodField()

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

    def get_createdAt(self, obj):
        if obj.createdAt is not None:
            return obj.createdAt
        else:
            return 'Date not specified'

class FoodEventSerializer(Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=100)
    address = serializers.SerializerMethodField()
    eventStartDate = serializers.SerializerMethodField()
    eventEndDate = serializers.SerializerMethodField()
    additionalInfo =serializers.CharField()
    createdBy = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    verified = serializers.BooleanField()
    status = serializers.CharField(max_length=50)
    eventPhoto = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id
    
    def get_name(self, obj):
        if obj.name is not None:
            return obj.name
        else:
            return 'Event name not specified'
    
    def get_address(self, obj):
        if obj.address is not None:
            return AddressSerializer(obj.address).data
        else:
            return 'address not specified'

    def get_eventStartDate(self, obj):
        if obj.eventStartDate is not None:
            return obj.eventStartDate
        else:
            return 'Event start date not specified'
        
    def get_eventEndDate(self, obj):
        if obj.eventEndDate is not None:
            return obj.eventEndDate
        else:
            return 'Event end date not specified' 
    
    def get_additionalInfo(self, obj):
        if obj.additionalInfo is not None:
            return obj.additionalInfo
        else:
            return "Additional information not specified"
        
    def get_createdBy(self, obj):
        if obj.createdBy is not None:
            user = Volunteer.objects.get(id=obj.createdBy.id)
            user_details = UserProfileSerializer(user).data
            return user_details
        else:
            return 'Created by details not specified'
        
    def get_createdAt(self, obj):
            if obj.createdAt is not None:
                return obj.createdAt
            else:
                return 'Date not specified'
            
    def get_verified(self, obj):
        if obj.verified is not None:
            return obj.verified
        else:
            return False

    def get_status(self, obj):
        if obj.status is not None:
            return obj.status
        else:
            return 'pending'
        
    def get_eventPhoto(self, obj): # to be modified
        if obj.eventPhoto is not None:
            media_storage = get_storage_class()()
            document_url = media_storage.url(name=obj.eventPhoto.name)
            return document_url
        else:
            return 'Event Photo not specified'

class BookmarkedEventSerializer(Serializer):
    id = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()    

    def get_id(self, obj):
        return obj.id
    
    def get_user(self, obj):
        if obj.user is not None:
            user = Volunteer.objects.get(id=obj.user.id)
            user_details = UserProfileSerializer(user).data
            return user_details
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
    categoryImage = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id
    
    def get_name(self, obj):
        if obj.name is not None:
            return obj.name
        else:
            return 'Category name not specified'
        
    def get_createdAt(self, obj):
        if obj.createdAt is not None:
            return obj.createdAt
        else:
            return 'Category created date not specified'
    
    def get_active(self, obj):
        if obj.active is not None:
            return obj.active
        else:
            return False
        
    def get_categoryImage(self, obj):
        if obj.categoryImage is not None:
            media_storage = get_storage_class()()
            document_url = media_storage.url(name=obj.categoryImage.name)
            return document_url
        else:
            return 'Category image not specified'
        
class FoodRecipeSerializer(Serializer):
    id = serializers.SerializerMethodField()
    foodName =  serializers.SerializerMethodField()
    ingredients =  serializers.SerializerMethodField()
    category = serializers.SerializerMethodField() 
    foodImage = serializers.SerializerMethodField() 
    cookingInstructions = serializers.SerializerMethodField()
    recipeSource = serializers.SerializerMethodField()
    recipeCredits = serializers.SerializerMethodField()
    preparationTime = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id
    
    def get_foodName(self, obj):
        if obj.foodName is not None:
            return obj.foodName
        else:
            return 'Recipe name not specified'
        
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
            return CategorySerializer(obj.category.all(), many=True).data
        else:
            return 'Category name not specified'
        
    def get_foodImage(self, obj):
        if obj.foodImage is not None:
            media_storage = get_storage_class()()
            document_url = media_storage.url(name=obj.foodImage.name)
            return document_url
        else:
            return 'Food image not specified'

    def get_recipeCredits(self, obj):
        if obj.recipeCredits is not None:
            return obj.recipeCredits
        else:
            return 'Recipe Credits not specified'

    def get_recipeSource(self, obj):
        if obj.recipeSource is not None:
            return obj.recipeSource
        else:
            return 'Recipe Source not specified'
        
    def get_preparationTime(self, obj):
        if obj.preparationTime is not None:
            return obj.preparationTime
        else:
            return 'preparation time not specified'
        
    def get_preparationTime(self, obj):
        if obj.preparationTime is not None:
            return obj.preparationTime
        else:
            return 'preparation time not specified'
        
    def get_preparationTime(self, obj):
        if obj.preparationTime is not None:
            return obj.preparationTime
        else:
            return 'preparation time not specified'
        
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
            return 'Request type not specified'
        
    def get_createdAt(self, obj):
        if obj.createdAt is not None:
            return obj.createdAt
        else:
            return 'Request type created date not specified'
    
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
            return obj.pickupDate
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
            return obj.dropDate
        else:
            return 'Drop date not specified'
        
    def get_delivered(self, obj):
        if obj.delivered is not None:
            return obj.delivered
        else:
            return False
        
    def get_driver(self, obj):
        if obj.driver is not None:
            user = Volunteer.objects.get(id=obj.driver.id)
            user_details = UserProfileSerializer(user).data
            return user_details
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
    createdAt = serializers.SerializerMethodField()

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
            user = Volunteer.objects.get(id=obj.donatedBy.id)
            user_details = UserProfileSerializer(user).data
            return user_details
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
        
    def get_createdAt(self, obj):
        if obj.createdAt is not None:
            return obj.createdAt
        else:
            return 'Donation created date not specified'
        
class VehicleSerializer(Serializer):
    id = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    make =  serializers.CharField(max_length=100)
    model = serializers.CharField(max_length=100)
    plateNumber =  serializers.SerializerMethodField()
    vehicleColour =  serializers.CharField(max_length=100)
    active = serializers.BooleanField()
    createdAt = serializers.SerializerMethodField()
    verified = serializers.BooleanField()

    def get_id(self, obj):
        return obj.id

    def get_owner(self, obj):
        if obj.owner is not None:
            user = Volunteer.objects.get(id=obj.owner.id)
            user_details = UserProfileSerializer(user).data
            return user_details
        else:
            return 'vehicle owner not specified'
        
    def get_make(self, obj):
        if obj.make is not None:
            return obj.make
        else:
            return 'Vehicle make not specified'
        
    def get_model(self, obj):
        if obj.model is not None:
            return obj.model
        else:
            return 'Vehicle model not specified'
        
    def get_plateNumber(self, obj):
        if obj.plateNumber is not None:
            return obj.plateNumber
        else:
            return 'Vehicle plate number not specified'
        
    def get_vehicleColour(self, obj):
        if obj.vehicleColour is not None:
            return obj.vehicleColour
        else:
            return 'Vehicle colour not specified'
        
    def get_active(self, obj):
        if obj.active is not None:
            return obj.active
        else:
            return False

    def get_createdAt(self, obj):
        if obj.createdAt is not None:
            return obj.createdAt
        else:
            return 'Vehicle created date not specified'
        
    def get_verified(self, obj):
        if obj.verified is not None:
            return obj.verified
        else:
            return False
        
class NotificationSerializer(Serializer):
    id = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    title =  serializers.CharField(max_length=50)
    message = serializers.CharField(max_length=255)
    is_unread = serializers.BooleanField()
    modifiedAt = serializers.SerializerMethodField()
    notificationType = serializers.CharField(max_length=50)
    isDeleted = serializers.BooleanField()

    def get_id(self, obj):
        return obj.id

    def get_user(self, obj):
        if obj.user is not None:
            user = Volunteer.objects.get(id=obj.user.id)
            user_details = UserProfileSerializer(user).data
            return user_details
        else:
            return 'Notification user not specified'
        
    def get_createdAt(self, obj):
        if obj.createdAt is not None:
            return obj.createdAt
        else:
            return 'Notification created date not specified'
        
    def get_title(self, obj):
        if obj.title is not None:
            return obj.title
        else:
            return 'Notification Title not specified'
        
    def get_message(self, obj):
        if obj.message is not None:
            return obj.message
        else:
            return 'Notification Message not specified'
        
    def get_is_unread(self, obj):
        if obj.is_unread is not None:
            return obj.is_unread
        else:
            return False

    def get_modifiedAt(self, obj):
        if obj.modifiedAt is not None:
            return obj.modifiedAt
        else:
            return 'Notification modifiedAt not specified'
    
    def get_notificationType(self, obj):
        if obj.notificationType is not None:
            return obj.notificationType
        else:
            return 'other'
        
    def get_isDeleted(self, obj):
        if obj.isDeleted is not None:
            return obj.isDeleted
        else:
            return True