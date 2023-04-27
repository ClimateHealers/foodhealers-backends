# <<<<<<<<<<<<---------------------------------- Necessary Imports for models are here ---------------------------------->>>>>>>>>>>>

from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

# <<<<<<<<<<<<---------------------------------- Choices to add in Models are here ---------------------------------->>>>>>>>>>>>

# can be modified Accordingly
VOLUNTEER_TYPE = (
    ('driver','Driver'),
    ('food_donor','Food Donor'),
    ('event_organizer','Event Organizer'),
    ('event_helper','Event Helper')
)

# can be modified Accordingly
DOCUMENT_TYPE = (
    ('profile_photo','Profile Photo'),
    ('event_photo','Event Photo'),
    ('food_photo','Food Photo'),
    ('vehicle_photo','Vehicle Photo')
)

# can be modified Accordingly
ITEM_TYPE = (
    ('food','Food'),
    ('supplies','Supplies')
)

# can be modified Accordingly
CATEGORY = (
    ('breakfast','Breakfast'),
    ('lunch','Lunch'),
    ('dinner','Dinner'),
    ('soup','Soup'),
    ('appetizer','Appetizer'),
    ('vegan_food','Vegan Food'),
    ('vegeterian_food','Vegeterian Food'),
    ('non_vegeterian_food','Non-Vegeterian Food')
)

# can be modified Accordingly
FOOD_TYPE = (
    ('perishable','Perishable'),
    ('non_perishable','Non Perishable')
)

# <<<<<<<<<<<<---------------------------------- Models Start from here ---------------------------------->>>>>>>>>>>>

# Model to store all the files related to driver, food, Events etc 
class Document(models.Model):
    documentType =  models.CharField(max_length=50, null=True, blank=True, choices=DOCUMENT_TYPE, default='profile_photo') # To be modified
    document = models.FileField(upload_to='user/documents', default='', null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)   
    isVerified = models.BooleanField(default=False, blank=True) 

# Model to Store all types of Address 
class Address(models.Model):
    lat = models.FloatField()
    lng = models.FloatField()
    alt = models.FloatField()
    streetAddress = models.TextField(max_length=500, default='')
    city = models.CharField(max_length=30, default='', null=True, blank=True)
    state = models.CharField(max_length=30, default='', null=True, blank=True)
    postalCode = models.CharField(max_length=30, default='', null=True, blank=True)
    formattedAddress = models.CharField(max_length=320, default='', null=True, blank=True)
    
    def __str__(self):
        return self.formattedAddress if self.formattedAddress else "Address Not Available"
    
# model to store the vehicle information for Volunteer Driver
class Vehicle(models.Model):
    make = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    plateNumber = models.CharField(max_length=100, null=True, blank=True, default='')
    vehicleColour = models.CharField(max_length=100, null=True, blank=True, default='')
    isDeleted = models.BooleanField(default=False, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    isVerified = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return str(self.make) + '-' + str(self.model) + '-' +  str(self.plateNumber) 
    
# model to store Volunteer information 
class Volunteer(User):
    name = models.CharField(max_length=300, default='')
    phoneNumber = models.CharField(max_length=20, default='', null=True, blank=True)
    address =  models.ForeignKey(Address, null=True, blank=True, on_delete=models.PROTECT)
    vehicle = models.ForeignKey(Vehicle, null=True, blank=True, on_delete=models.PROTECT, related_name='driver_vehicle')
    volunteerType = models.CharField(max_length=50, choices=VOLUNTEER_TYPE, null=True, blank=True, default='food_donar')
    profilePhoto = models.ForeignKey(Document, null=True, blank=True, on_delete=models.PROTECT, related_name='volunteer_photo')
    isVerified = models.BooleanField(default=False, null=True, blank=True)
    isDriver = models.BooleanField(default=False, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Volunteer"

# model to store information about food Items
class FoodItem(models.Model):
    itemName = models.CharField(max_length=100, default='', null=True, blank=True)
    quantity = models.CharField(max_length=100, default='', null=True, blank=True)    
    expiryDate = models.DateTimeField(null=True, blank=True) 
    itemPhotos = models.ManyToManyField(Document, null=True, blank=True, related_name='food_photos')      
    itemType = models.CharField(max_length=50, choices=ITEM_TYPE, null=True, blank=True, default='food')

# model to store information about Donations
class Donation(models.Model):
    donationType = models.CharField(max_length=50, choices=ITEM_TYPE, null=True, blank=True, default='food')
    foodItems = models.ManyToManyField(FoodItem, null=True, blank=True, related_name='donation_food_items')
    quantity = models.CharField(max_length=100, default='', null=True, blank=True)   
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.PROTECT)
    pickupDate = models.DateTimeField(null=True, blank=True) 
    donorPhoneNumber = models.CharField(max_length=20, default='', null=True, blank=True)
    volunteers = models.ManyToManyField(Volunteer, null=True, blank=True, related_name='donation_volunteers')

# model to store information about Food Events Occuring
class FoodEvent(models.Model):
    foodItems = models.ManyToManyField(FoodItem, null=True, blank=True, related_name='event_food_items')        
    quantity = models.CharField(max_length=100, default='', null=True, blank=True)               
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.PROTECT)
    organizerPhoneNumber = models.CharField(max_length=20, default='', null=True, blank=True)
    pickupDate = models.DateTimeField(null=True, blank=True) 
    eventPhotos = models.ManyToManyField(Document, null=True, blank=True, related_name='event_photos')
    volunteers = models.ManyToManyField(Volunteer, null=True, blank=True, related_name='event_volunteers')
    foodType = models.CharField(max_length=50, choices=FOOD_TYPE, null=True, blank=True) 
    category = models.CharField(max_length=50, choices=CATEGORY, null=True, blank=True)

# model to store information about FoodRecipes
class FoodRecipe(models.Model):
    foodName = models.CharField(max_length=100, default='', null=True, blank=True)
    ingredients = models.TextField(max_length=500, default='', null=True, blank=True)
    foodType = models.CharField(max_length=50, choices=FOOD_TYPE, null=True, blank=True) 
    category = models.CharField(max_length=50, choices=CATEGORY, null=True, blank=True) 
    foodImage = models.ManyToManyField(Document, null=True, blank=True, related_name='recipe_photos') 
    cookingInstructions = models.TextField(max_length=500, default='')
    slug = models.SlugField(unique=True, max_length=100)
    tags = TaggableManager()

    def __str__(self):
        return self.foodName + str(self.foodType) + str(self.category)
