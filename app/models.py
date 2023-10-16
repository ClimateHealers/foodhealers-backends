from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from .validators import validate_file_size

document_path = 'user/documents'

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

STATUS = (
    ('approved','Approved'),
    ('rejected','Rejected'),
    ('pending','Pending'),
)

NOTIFICATION_TYPE = (
    ('event', 'Event'),
    ('donation', 'Donation'),
    ('volunteer','Volunteer'),
    ('request', 'Request'),
    ('other','Other')
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
    categoryImage = models.FileField(upload_to=document_path, default='', null=True, blank=True, validators=[validate_file_size])

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
        return self.name

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
    createdBy = models.ForeignKey(Volunteer, null=True, blank=True, related_name='food_event_organiser', on_delete=models.PROTECT)
    createdAt = models.DateTimeField(null=True, blank=True) 
    additionalInfo = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True, choices=STATUS, default=STATUS[2][0])
    eventPhoto = models.FileField(upload_to=document_path, default='', null=True, blank=True, validators=[validate_file_size])
    requiredVolunteers = models.IntegerField(null=True, blank=True, default=0)
    volunteers = models.ManyToManyField(Volunteer, null=True, blank=True, related_name='food_event_volunteers') 

@receiver(post_save, sender=FoodEvent)
def send_notification_on_change(sender, instance, created , **kwargs):
    from .tasks import send_push_message
    
    # if event has been created
    if created :
        title = 'Event Under Review'
        message = f'Your Event - {instance.name} is under review'
        notification_type = NOTIFICATION_TYPE[0][0]
        send_push_message(instance.createdBy, title, message, notification_type)

    # logic to check if status has changed to approved or rejected
    elif instance.status == STATUS[0][0]:
        title = 'Event Approved'
        message = f'Your Event - {instance.name} has been approved by Food healers team'
        notification_type= NOTIFICATION_TYPE[0][0]
        send_push_message(instance.createdBy, title, message, notification_type)

    elif instance.status == STATUS[1][0]:
        title = 'Event Rejected'
        message = f'Your Event - {instance.name} has been rejected by Food healers team'
        notification_type= NOTIFICATION_TYPE[0][0]
        send_push_message(instance.createdBy, title, message, notification_type)

# 7. Model to store all the files related to driver, vehicle, Events etc
class Document(models.Model):
    docType =  models.CharField(max_length=50, null=True, blank=True, choices=DOCUMENT_TYPE, default='profile_photo') # To be modified
    document = models.FileField(upload_to=document_path, default='', null=True, blank=True, validators=[validate_file_size])
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    verified = models.BooleanField(default=False, blank=True)
    event = models.ForeignKey(FoodEvent, null=True, blank=True, on_delete=models.PROTECT)
    vehicle = models.ForeignKey(Vehicle, null=True, blank=True, on_delete=models.PROTECT, related_name='vehicle_photo')
    volunteer = models.ForeignKey(Volunteer, null=True, blank=True, on_delete=models.PROTECT, related_name='volunteer_profile_img')
    food = models.ForeignKey('FoodRecipe', null=True, blank=True, on_delete=models.PROTECT, related_name='food_recipe_img')
    isActive = models.BooleanField(default=True, null=True, blank=True)
    
    def name(self):
        if self.docType == DOCUMENT_TYPE[0][0]:
            return self.volunteer.name
        elif self.docType == DOCUMENT_TYPE[1][0]:
            return self.event.name
        elif self.docType == DOCUMENT_TYPE[2][0]:
            return self.food
        elif self.docType == DOCUMENT_TYPE[3][0]:
            return self.vehicle.make
        
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
    ingredients = models.TextField(max_length=1000, default='', null=True, blank=True)
    category =  models.ManyToManyField(Category, null=True, blank=True, related_name='recipe_category')
    foodImage = models.FileField(upload_to=document_path, default='', null=True, blank=True, validators=[validate_file_size])
    cookingInstructions = models.TextField(max_length=1000, default='', null=True, blank=True)
    recipeSource = models.CharField(max_length=100, null=True, blank=True)
    recipeCredits = models.CharField(max_length=100, null=True, blank=True)
    preparationTime = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=100)
    tags = TaggableManager()

    def __str__(self):
        return self.foodName

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
    verified = models.BooleanField(default=False, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True, choices=STATUS, default=STATUS[2][0])

@receiver(post_save, sender=Request)
def send_notification_on_change(sender, instance, created , **kwargs):
    from .tasks import send_push_message
    
    if instance.type.name == 'Food' or instance.type.name == 'Supplies' :
        # Food/Supplies Request has been created
        if created :
            title = f'{instance.type.name} Request Under Review'
            message = f'Your {instance.type.name} Request - for {instance.quantity} of {instance.foodItem.itemName} is under review'
            notification_type = NOTIFICATION_TYPE[3][0]
            send_push_message(instance.createdBy, title, message, notification_type)

        # logic to check if status has changed to approved or rejected
        elif instance.status == STATUS[0][0]:
            title = f'{instance.type.name} Request Approved'
            message = f'Your {instance.type.name} Request - for {instance.quantity} of {instance.foodItem.itemName} has been approved by Food healers team'
            notification_type= NOTIFICATION_TYPE[3][0]
            send_push_message(instance.createdBy, title, message, notification_type)

        elif instance.status == STATUS[1][0]:
            title = f'{instance.type.name} Request Rejected'
            message = f'Your {instance.type.name} Request - for {instance.quantity} of {instance.foodItem.itemName} has been rejected by Food healers team'
            notification_type= NOTIFICATION_TYPE[3][0]
            send_push_message(instance.createdBy, title, message, notification_type)

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
    verified = models.BooleanField(default=False, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True, choices=STATUS, default=STATUS[2][0])

@receiver(post_save, sender=Donation)
def send_donation_notification_on_change(sender, instance, created , **kwargs):
    from .tasks import send_push_message
    
    # if donation has been created
    if created :
        title = 'Donation Under Review'
        message = f'Your Donation - {instance.foodItem.itemName} is under review'
        notification_type = NOTIFICATION_TYPE[1][0]
        send_push_message(instance.donatedBy, title, message, notification_type)

    # logic to check if status has changed to approved or rejected
    elif instance.status == STATUS[0][0]:
        title = 'Donation Approved'
        message = f'Your Donation - {instance.foodItem.itemName} has been approved by Food healers team'
        notification_type= NOTIFICATION_TYPE[1][0]
        send_push_message(instance.donatedBy, title, message, notification_type)

    elif instance.status == STATUS[1][0]:
        title = 'Donation Rejected'
        message = f'Your Donation - {instance.foodItem.itemName} has been rejected by Food healers team'
        notification_type= NOTIFICATION_TYPE[1][0]
        send_push_message(instance.donatedBy, title, message, notification_type)

# 14. model to store information about Event Volunteers
class EventVolunteer(models.Model):
    event = models.ForeignKey(FoodEvent, null=True, blank=True, on_delete=models.PROTECT)
    volunteer = models.ForeignKey(Volunteer, null=True, blank=True, on_delete=models.PROTECT) 
    request = models.ForeignKey(Request, null=True, blank=True, on_delete=models.PROTECT)
    fromDate = models.DateTimeField(null=True, blank=True)
    toDate = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)

@receiver(post_save, sender=EventVolunteer)
def send_volunteer_notification_on_applied(sender, instance, created , **kwargs):
    from .tasks import send_push_message
    
    # if EventVolunteer has been created
    if created :
        title = 'Volunteer Registered For Your Event'
        message = f'{instance.volunteer.name} wants to volunteer for {instance.event.name}'
        notification_type = NOTIFICATION_TYPE[2][0]
        send_push_message(instance.event.createdBy, title, message, notification_type)


# 15. model to store information about django token 
class CustomToken(models.Model):
    accessToken = models.CharField(max_length=255, default='')
    refreshToken = models.CharField(max_length=255, default='')
    expoPushToken = models.CharField(max_length=255, default='', null=True, blank=True,)
    user = models.ForeignKey(Volunteer, null=True, blank=True, on_delete=models.PROTECT)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)

# 16. model to store information about Bookmarks 
class EventBookmark(models.Model):
    user = models.ForeignKey(Volunteer, null=True, blank=True, on_delete=models.PROTECT)
    event = models.ForeignKey(FoodEvent, null=True, blank=True, on_delete=models.PROTECT)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    isDeleted = models.BooleanField(default=False, null=True, blank=True)

# 17. model to store Information about Notifcations
class Notification(models.Model):
    user = models.ForeignKey(Volunteer, null=True, blank=True, on_delete=models.PROTECT)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    title = models.CharField(max_length=50, default='title', null=True, blank=True)
    message = models.TextField(max_length=1000, default='this is sample message', null=True, blank=True)
    is_unread = models.BooleanField(default=True)
    modifiedAt = models.DateTimeField(null=True, blank=True)  # updated when read
    notificationType = models.CharField(max_length=50, choices=NOTIFICATION_TYPE, default='other', null=True, blank=True)
    isDeleted = models.BooleanField(default=False, null=True, blank=True)