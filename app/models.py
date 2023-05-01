from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

# <<<<<<<<<<<<---------------------------------- Choices to add in Models are here ---------------------------------->>>>>>>>>>>>

# can be modified Accordingly
VOLUNTEER_TYPE = (
    ('driver','Driver'),
    ('food_donor','Food Donor'),
    ('event_organizer','Event Organizer'),
    ('event_volunteer','Event Volunteer') # TODO: remove helper, make it volunteer.
)

# can be modified Accordingly
DOCUMENT_TYPE = (
    ('profile_photo','Profile Photo'),
    ('event_photo','Event Photo'),
    ('food_photo','Food Photo'),
    ('vehicle_photo','Vehicle Photo')
)

# can be modified Accordingly
# TODO: Convert this into Model. Item types can grow.
ITEM_TYPE = (
    ('food','Food'),
    ('supplies','Supplies')
)

# <<<<<<<<<<<<---------------------------------- Models Start from here ---------------------------------->>>>>>>>>>>>

# Model to store all the files related to driver, food, Events etc
# TODO: why not have Category as Model? We can have many more categories in future.
# CATEGORY = (
#     ('breakfast','Breakfast'),
#     ('lunch','Lunch'),
#     ('dinner','Dinner'),
#     ('soup','Soup'),
#     ('appetizer','Appetizer'),
#     ('vegan_food','Vegan Food'),
#     ('vegeterian_food','Vegeterian Food'),
#     ('non_vegeterian_food','Non-Vegeterian Food')
# )

class Category(models.Model):
    name =  models.CharField(max_length=50, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    active = models.BooleanField(default=False, null=True, blank=True)


class Document(models.Model):
    doctype =  models.CharField(max_length=50, null=True, blank=True, choices=DOCUMENT_TYPE, default='profile_photo') # To be modified
    document = models.FileField(upload_to='user/documents', default='', null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    isVerified = models.BooleanField(default=False, blank=True)

# Model to Store all types of Address
class Address(models.Model):
    lat = models.FloatField() # TODO: define default vaules for floats and integers.
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
        return self.name # TODO: can we add type as well?

    class Meta:
        verbose_name = "Volunteer"

# model to store information about food Items
class FoodItem(models.Model):
    itemName = models.CharField(max_length=100, default='', null=True, blank=True) # TODO: FoodItem name cannot be empty. Name is must.
    quantity = models.CharField(max_length=100, default='', null=True, blank=True)
    expiryDate = models.DateTimeField(null=True, blank=True)
    itemPhotos = models.ManyToManyField(Document, null=True, blank=True, related_name='food_photos')
    itemType = models.CharField(max_length=50, choices=ITEM_TYPE, null=True, blank=True, default='food')

# model to store information about Donations
class Donation(models.Model):
    donationType = models.CharField(max_length=50, choices=ITEM_TYPE, null=True, blank=True, default='food')
    foodItems = models.ManyToManyField(FoodItem, null=True, blank=True, related_name='donation_items')
    quantity = models.CharField(max_length=100, default='', null=True, blank=True)
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.PROTECT)
    pickupDate = models.DateTimeField(null=True, blank=True) # TODO: pickup date should be NOW.
    donorPhoneNumber = models.CharField(max_length=20, default='', null=True, blank=True)
    volunteers = models.ManyToManyField(Volunteer, null=True, blank=True, related_name='donation_volunteers')
    # TODO: Can we separate this out? Donation may or may not have volunteers
    #TODO: we should have a field for knowing who donated this --> DonatedBy


# model to store information about Food Events Occuring
'''
    Event will be organized by a person -- we need that.
    Event will have a location and address.
    Event will have some donations linked.
    Event may have photos.
    Event may have some volunteers.
    Event may have many donations --> Each donation shall have food items or something that was donated.
    Event can be active or inactive.
    Event will be automatically expired after a date. ( we should add signal to do that or a celery )
    Where does FoodType and Category be used? #TODO: Please answer this. Why should FoodType and Cateogry be here?

'''
class FoodEvent(models.Model):
    foodItems = models.ManyToManyField(FoodItem, null=True, blank=True, related_name='event_food_items')
    quantity = models.CharField(max_length=100, default='', null=True, blank=True)
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.PROTECT)
    organizerPhoneNumber = models.CharField(max_length=20, default='', null=True, blank=True) # TODO: we should have a field to know "creator of this event" --> createdBy
    pickupDate = models.DateTimeField(null=True, blank=True)
    eventPhotos = models.ManyToManyField(Document, null=True, blank=True, related_name='event_photos')
    volunteers = models.ManyToManyField(Volunteer, null=True, blank=True, related_name='event_volunteers')
    perishable = models.BooleanField(default=False, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.PROTECT)

# model to store information about FoodRecipes
class FoodRecipe(models.Model):
    foodName = models.CharField(max_length=100, default='', null=True, blank=True)
    ingredients = models.TextField(max_length=500, default='', null=True, blank=True)
    category =  models.ForeignKey(Category, null=True, blank=True, on_delete=models.PROTECT)
    foodImage = models.ManyToManyField(Document, null=True, blank=True, related_name='recipe_photos')
    cookingInstructions = models.TextField(max_length=500, default='') #TODO: can this be RICH TEXT? We can have blob type field to store rich text.
    slug = models.SlugField(unique=True, max_length=100)
    tags = TaggableManager()

    def __str__(self):
        return self.foodName + str(self.foodType) + str(self.category)
