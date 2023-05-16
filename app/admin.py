# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'createdAt', 'active')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'createdAt', 'active')

class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'state', 'postalCode')

class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phoneNumber', 'volunteerType', 'isDriver')
    search_fields = ['name', 'phoneNumber']
    filter_fields = ['name', 'phoneNumber', 'volunteerType', 'isDriver', 'verified']

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'make', 'model', 'plateNumber', 'active')
    search_fields = ['make', 'model', 'plateNumber', 'vehicleColour']
    filter_fields = ['isDeleted', 'model', 'vehicleColour', 'verified']

class FoodEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'createdBy', 'eventStartDate', 'active')
    search_fields = ['organizerPhoneNumber', 'foodType', 'createdBy']
    filter_fields = ['address', 'pickupDate', 'foodType', 'createdBy']

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'createdAt', 'docType', 'verified')

class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'itemName', 'itemType', 'addedBy', 'expiryDate')
    search_fields = ['itemName', 'itemType', 'addedBy', 'expiryDate']
    filter_fields = ['itemName', 'itemType', 'addedBy', 'expiryDate']

class FoodRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'foodName', 'category', 'tags')
    search_fields = ['foodName', 'tags', 'category']
    filter_fields = ['foodName', 'tags', 'category']

class DeliveryDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'pickupDate', 'dropDate', 'driver')
    search_fields = ['pickupDate', 'dropDate', 'driver']
    filter_fields = ['pickupDate', 'dropDate', 'driver']

class RequestTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'createdAt', 'active')

class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'createdBy','type' ,'fullfilled', 'active')
    search_fields = ['createdBy', 'requiredDate', 'dropDate']
    filter_fields = ['createdBy', 'type', 'fullfilled', 'active']

class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'donationType', 'donatedBy','fullfilled')
    search_fields = ['donationType', 'donatedBy']
    filter_fields = ['donationType', 'donatedBy', 'needsPickup', 'fullfilled']

class EventVolunteerAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'createdAt')

class CustomeTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'createdAt')

class EventBookmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'user', 'createdAt')

admin.site.register(ItemType, ItemTypeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(FoodEvent, FoodEventAdmin)
admin.site.register(Document, DocumentAdmin) 
admin.site.register(FoodItem, FoodItemAdmin)
admin.site.register(FoodRecipe, FoodRecipeAdmin)
admin.site.register(DeliveryDetail, DeliveryDetailAdmin)
admin.site.register(RequestType, RequestTypeAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(EventVolunteer, EventVolunteerAdmin)
admin.site.register(CustomToken, CustomeTokenAdmin)
admin.site.register(EventBookmark, EventBookmarkAdmin)
