from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.dispatch import receiver
from .geoutils import getFormattedAddressFromCoords
from django.db.models.signals import post_save



# <<<<<<<<<<<<---------------------------------- Choices to add in Models are here ---------------------------------->>>>>>>>>>>>

# can be modified Accordingly
VOLUNTEER_TYPE = (
    ('driver','Driver'),
    ('food_donor','Food Donor'),
    ('event_organizer','Event Organizer'),
    ('event_volunteer','Event Volunteer'),
    ('food_seeker','Food Seeker')
)

# can be modified Accordingly
DOCUMENT_TYPE = (
    ('profile_photo','Profile Photo'),
    ('event_photo','Event Photo'),
    ('food_photo','Food Photo'),
    ('vehicle_photo','Vehicle Photo')
)

# <<<<<<<<<<<<---------------------------------- Models Start from here ---------------------------------->>>>>>>>>>>>

# 1. Model to Store types of Food (food, supplies)
class ItemType(models.Model):
    name =  models.CharField(max_length=50, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    active = models.BooleanField(default=False, null=True, blank=True)

# 2. Model to Store all types of Categories
class Category(models.Model):
    name =  models.CharField(max_length=50, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    active = models.BooleanField(default=False, null=True, blank=True)

# 3. Model to Store all types of Address
class Address(models.Model):
    lat = models.FloatField(default='12.317277',null=True, blank=True) 
    lng = models.FloatField(default='78.713890',null=True, blank=True)
    alt = models.FloatField(default=' 1500.0', null=True, blank=True)
    streetAddress = models.TextField(max_length=500, default='', null=True, blank=True)
    city = models.CharField(max_length=30, default='', null=True, blank=True)
    state = models.CharField(max_length=30, default='', null=True, blank=True)
    postalCode = models.CharField(max_length=30, default='', null=True, blank=True)
    fullAddress = models.CharField(max_length=320, default='', null=True, blank=True)

    def __str__(self):
        return self.streetAddress if self.streetAddress else "Address Not Available"
    

# @receiver(post_save, sender=Address)
# def fetchFormattedAddressForCoordinates(sender, instance, created, **kwargs):
#     # convert coordinates to formatted-human-readable address
#     if created is True:s
#         response = getFormattedAddressFromCoords(instance.lat, instance.lng)
#         instance.streetAddress = response['formatted_address']
#         instance.fullAddress = response['formatted_address']
#         instance.city = response['city'] 
#         instance.state = response['state']
#         instance.postalCode = response['postal_code']
#         instance.save()
#     return True

# 4. model to store Volunteer information
class Volunteer(User):
    name = models.CharField(max_length=300, default='')
    phoneNumber = models.CharField(max_length=20, default='', null=True, blank=True)
    address =  models.ForeignKey(Address, null=True, blank=True, on_delete=models.PROTECT)
    volunteerType = models.CharField(max_length=50, choices=VOLUNTEER_TYPE, null=True, blank=True, default='food_seeker')
    verified = models.BooleanField(default=False, null=True, blank=True)
    isVolunteer = models.BooleanField(default=False, null=True, blank=True)
    isDriver = models.BooleanField(default=False, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    lastLogin = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name + '-' + str(self.volunteerType)

    class Meta:
        verbose_name = "Volunteer"

# 5. model to store the vehicle information for Volunteer Driver
class Vehicle(models.Model):
    make = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    plateNumber = models.CharField(max_length=100, null=True, blank=True, default='')
    vehicleColour = models.CharField(max_length=100, null=True, blank=True, default='')
    active = models.BooleanField(default=False, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    verified = models.BooleanField(default=False, null=True, blank=True)
    owner = models.ForeignKey(Volunteer, null=True, blank=True, on_delete=models.PROTECT) 

    def __str__(self):
        return str(self.make) + '-' + str(self.model) + '-' +  str(self.plateNumber)

# 6. model to store information about Food Events Occuring
class FoodEvent(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.PROTECT)
    organizerPhoneNumber = models.CharField(max_length=20, default='', null=True, blank=True)
    eventStartDate = models.DateTimeField(null=True, blank=True)
    eventEndDate = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=False, null=True, blank=True)
    # category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.PROTECT)
    createdBy = models.ForeignKey(Volunteer, null=True, blank=True, related_name='food_event_organiser', on_delete=models.PROTECT)
    createdAt = models.DateTimeField(null=True, blank=True) 
    additionalInfo = models.TextField(blank=True, null=True)
    # quantity = models.CharField(max_length=100, default='', null=True, blank=True) # to be modified

# 7. Model to store all the files related to driver, vehicle, Events etc
class Document(models.Model):
    docType =  models.CharField(max_length=50, null=True, blank=True, choices=DOCUMENT_TYPE, default='profile_photo') # To be modified
    document = models.FileField(upload_to='user/documents', default='', null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    verified = models.BooleanField(default=False, blank=True)
    event = models.ForeignKey(FoodEvent, null=True, blank=True, on_delete=models.PROTECT)
    vehicle = models.ForeignKey(Vehicle, null=True, blank=True, on_delete=models.PROTECT, related_name='vehicle_photo')
    volunteer = models.ForeignKey(Volunteer, null=True, blank=True, on_delete=models.PROTECT, related_name='volunteer_profile_img')
    isActive = models.BooleanField(default=True, null=True, blank=True)

# 8. model to store information about food Items
class FoodItem(models.Model):
    itemName = models.CharField(max_length=100, default='Food Name')
    expiryDate = models.DateTimeField(null=True, blank=True)
    itemPhotos = models.ManyToManyField(Document, null=True, blank=True, related_name='food_photos')
    itemType =  models.ForeignKey(ItemType, null=True, blank=True, on_delete=models.PROTECT)
    addedBy = models.ForeignKey(Volunteer,  null=True, blank=True, on_delete=models.PROTECT)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    event =  models.ForeignKey(FoodEvent, null=True, blank=True, on_delete=models.PROTECT)

# 9. model to store information about FoodRecipes
class FoodRecipe(models.Model):
    foodName = models.CharField(max_length=100, default='', null=True, blank=True)
    ingredients = models.TextField(max_length=500, default='', null=True, blank=True)
    category =  models.ForeignKey(Category, null=True, blank=True, on_delete=models.PROTECT)
    foodImage = models.ManyToManyField(Document, null=True, blank=True, related_name='recipe_photos')
    cookingInstructions = models.TextField(max_length=500, default='')
    slug = models.SlugField(unique=True, max_length=100)
    tags = TaggableManager()

    def __str__(self):
        return self.foodName + str(self.category)

# 10. model to store information about Food Delivery Details
class DeliveryDetail(models.Model):
    pickupAddress = models.ForeignKey(Address, null=True, blank=True, on_delete=models.PROTECT, related_name='pickup_address')
    pickupDate =  models.DateTimeField( null=True, blank=True)
    pickedup = models.BooleanField(default=False)
    dropAddress = models.ForeignKey(Address, null=True, blank=True, on_delete=models.PROTECT,  related_name='drop_address')
    dropDate = models.DateTimeField( null=True, blank=True)
    delivered = models.BooleanField(default=False, null=True, blank=True)
    driver = models.ForeignKey(Volunteer, null=True, blank=True, on_delete=models.PROTECT)

# 11. model to store information about Request type (PickUp, food, Supplies, Volunteers)
class RequestType(models.Model):
    name =  models.CharField(max_length=50, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    active = models.BooleanField(default=False, null=True, blank=True)

# 12. model to store information about Requests made by user (PickUp request, food, Supplies request, Volunteers Request)
class Request(models.Model):
    type = models.ForeignKey(RequestType, null=True, blank=True, on_delete=models.PROTECT)
    createdBy = models.ForeignKey(Volunteer, null=True, blank=True, on_delete=models.PROTECT)
    requiredDate = models.DateTimeField( null=True, blank=True)
    active = models.BooleanField(default=False, null=True, blank=True)
    fullfilled = models.BooleanField(default=False, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    quantity = models.CharField(max_length=100, default='', null=True, blank=True)
    foodItem = models.ForeignKey(FoodItem, null=True, blank=True, on_delete=models.PROTECT)
    deliver = models.ForeignKey(DeliveryDetail, null=True, blank=True, on_delete=models.PROTECT)
    foodEvent = models.ForeignKey(FoodEvent, null=True, blank=True, on_delete=models.PROTECT)

# 13. model to store information about Donations
class Donation(models.Model):
    donationType = models.ForeignKey(ItemType, null=True, blank=True, on_delete=models.PROTECT)
    foodItem = models.ForeignKey(FoodItem, null=True, blank=True, on_delete=models.PROTECT)
    quantity = models.CharField(max_length=100, default='', null=True, blank=True)
    donatedBy = models.ForeignKey(Volunteer, null=True, blank=True, related_name="food_donor", on_delete=models.PROTECT)
    needsPickup = models.BooleanField(default=False)
    fullfilled = models.BooleanField(default=False, null=True, blank=True)
    event = models.ForeignKey(FoodEvent, null=True, blank=True, on_delete=models.PROTECT)
    delivery = models.ForeignKey(DeliveryDetail, null=True, blank=True, on_delete=models.PROTECT)
    request = models.ForeignKey(Request, null=True, blank=True, on_delete=models.PROTECT)
    createdAt =  models.DateTimeField(auto_now_add=True, null=True, blank=True)

# 14. model to store information about Event Volunteers
class EventVolunteer(models.Model):
    event = models.ForeignKey(FoodEvent, null=True, blank=True, on_delete=models.PROTECT)
    volunteers = models.ManyToManyField(Volunteer, null=True, blank=True, related_name='event_volunteers') 
    request = models.ForeignKey(Request, null=True, blank=True, on_delete=models.PROTECT)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)

# 15. model to store information about django token 
class CustomToken(models.Model):
    accessToken = models.CharField(max_length=255, default='')
    refreshToken = models.CharField(max_length=255, default='')
    user = models.ForeignKey(Volunteer, null=True, blank=True, on_delete=models.PROTECT)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)

# 16. model to store information about Bookmarks 
class EventBookmark(models.Model):
    user = models.ForeignKey(Volunteer, null=True, blank=True, on_delete=models.PROTECT)
    event = models.ForeignKey(FoodEvent, null=True, blank=True, on_delete=models.PROTECT)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    isDeleted = models.BooleanField(default=False, null=True, blank=True)
