# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ( ItemType, Category, Address, Volunteer,
                      Vehicle, FoodEvent, Document, FoodItem,
                      FoodRecipe, DeliveryDetail, RequestType, 
                      Donation, EventVolunteer, CustomToken, 
                      Request, EventBookmark, Notification )

from django.contrib.admin.widgets import AdminFileWidget
from django.utils.html import format_html
from django.db import models

class CustomAdminFileWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        result = []
        if value!= None and value != '' and value!=' ':
            if hasattr(value, "url"):
                result.append(
                    f'''<a href="{value.url}" target="_blank">
                          <img 
                            src="{value.url}" alt="{value}" 
                            width="300" height="300"
                            style="object-fit: cover;"
                          />
                        </a>'''
                )

            result.append(super().render(name, value, attrs, renderer))
            return format_html("".join(result))
        else:
            result.append(super().render(name, value, attrs, renderer))
            return format_html("".join(result))
    
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'createdAt', 'active')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'createdAt', 'active')

class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'state', 'postalCode')
    search_fields = ['city', 'state', 'postalCode', 'lat', 'lng']

class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phoneNumber', 'email', 'isDriver')
    search_fields = ['name', 'phoneNumber', 'email']
    filter_fields = ['name', 'phoneNumber', 'volunteerType', 'isDriver', 'verified']

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'make', 'model', 'plateNumber', 'active')
    search_fields = ['make', 'model', 'plateNumber', 'vehicleColour']
    filter_fields = ['isDeleted', 'model', 'vehicleColour', 'verified']

class FoodEventAdmin(admin.ModelAdmin):
    formfield_overrides = {         
        models.FileField: {"widget": CustomAdminFileWidget}
    }
    list_display = ('id', 'createdBy', 'name','eventStartDate', 'status', 'active')
    search_fields = ['createdBy__name', 'name', 'eventStartDate', 'status', 'active', 'additionalInfo', 'verified']

class DocumentAdmin(admin.ModelAdmin):
    formfield_overrides = {         
        models.FileField: {"widget": CustomAdminFileWidget}
    }
    list_display = ('id', 'createdAt', 'docType', 'name', 'verified')
    search_fields = ['docType', 'volunteer__name', 'event__name', 'vehicle__make', 'food__foodName']

class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'itemName', 'itemType', 'addedBy', 'expiryDate')
    search_fields = ['itemName', 'itemType__name', 'addedBy__name', 'expiryDate']
    filter_fields = ['itemName', 'itemType', 'addedBy', 'expiryDate']

class FoodRecipeAdmin(admin.ModelAdmin):
    formfield_overrides = {         
        models.FileField: {"widget": CustomAdminFileWidget}
    }
    list_display = ('id', 'foodName', 'display_categories')
    search_fields = ['foodName', 'category__name']
    filter_fields = ['foodName']

    def display_categories(self, obj):
        return ", ".join([cat.name for cat in obj.category.all()])
    display_categories.short_description = 'Category'

class DeliveryDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'pickupDate', 'pickedup', 'dropDate', 'delivered', 'driver')
    search_fields = ['pickupDate', 'dropDate', 'driver__name']
    filter_fields = ['pickupDate', 'dropDate', 'driver']

class RequestTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'createdAt', 'active')

class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'createdBy','type' ,'fullfilled', 'active')
    search_fields = ['createdBy__name', 'requiredDate', 'dropDate']
    filter_fields = ['createdBy', 'type', 'fullfilled', 'active']

class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'donationType', 'donatedBy','fullfilled')
    search_fields = ['donationType', 'donatedBy__name']
    filter_fields = ['donationType', 'donatedBy', 'needsPickup', 'fullfilled']

class EventVolunteerAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'createdAt')

class CustomeTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'createdAt')
    search_fields = ['user__name']

class EventBookmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'user', 'createdAt')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'createdAt')
    search_fields = ['user__name', 'title']

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
admin.site.register(Notification, NotificationAdmin)
