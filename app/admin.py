# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'documentType', 'createdAt')
    filter_fields = ['documentType', 'createdAt']

class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'streetAddress', 'city', 'state', 'formattedAddress')

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'make', 'model', 'plateNumber', 'vehicleColour')
    search_fields = ['make', 'model', 'plateNumber', 'vehicleColour']
    filter_fields = ['isDeleted', 'model', 'vehicleColour']
     
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phoneNumber', 'volunteerType', 'isDriver')
    search_fields = ['name', 'phoneNumber']
    filter_fields = ['name', 'phoneNumber', 'volunteerType', 'isDriver']

class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'itemName', 'itemType', 'expiryDate', 'quantity')
    search_fields = ['itemName', 'itemType']
    filter_fields = ['itemName', 'itemType', 'expiryDate']

class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'donationType', 'donorPhoneNumber', 'quantity', 'address','pickupDate')
    search_fields = ['donationType']
    filter_fields = ['donationType', 'pickupDate']

class FoodEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'foodType', 'organizerPhoneNumber', 'quantity', 'address', 'pickupDate')
    search_fields = ['organizerPhoneNumber', 'foodType']
    filter_fields = ['address', 'pickupDate', 'foodType']
    
class FoodRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'foodName', 'foodType', 'category', 'tags')
    search_fields = ['foodName', 'foodType', 'tags', 'category']
    filter_fields = ['foodName', 'foodType', 'tags', 'category']

admin.site.register(Document, DocumentAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(FoodEvent, FoodEventAdmin)
admin.site.register(FoodRecipe, FoodRecipeAdmin)