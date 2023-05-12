# Generated by Django 4.2 on 2023-05-01 17:23

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('taggit', '0005_auto_20220424_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('alt', models.FloatField()),
                ('streetAddress', models.TextField(default='', max_length=500)),
                ('city', models.CharField(blank=True, default='', max_length=30, null=True)),
                ('state', models.CharField(blank=True, default='', max_length=30, null=True)),
                ('postalCode', models.CharField(blank=True, default='', max_length=30, null=True)),
                ('formattedAddress', models.CharField(blank=True, default='', max_length=320, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('active', models.BooleanField(blank=True, default=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctype', models.CharField(blank=True, choices=[('profile_photo', 'Profile Photo'), ('event_photo', 'Event Photo'), ('food_photo', 'Food Photo'), ('vehicle_photo', 'Vehicle Photo')], default='profile_photo', max_length=50, null=True)),
                ('document', models.FileField(blank=True, default='', null=True, upload_to='user/documents')),
                ('createdAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('isVerified', models.BooleanField(blank=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('make', models.CharField(blank=True, max_length=100, null=True)),
                ('model', models.CharField(blank=True, max_length=100, null=True)),
                ('plateNumber', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('vehicleColour', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('active', models.BooleanField(blank=True, default=False, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('verified', models.BooleanField(blank=True, default=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('name', models.CharField(default='', max_length=300)),
                ('phoneNumber', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('volunteerType', models.CharField(blank=True, choices=[('driver', 'Driver'), ('food_donor', 'Food Donor'), ('event_organizer', 'Event Organizer'), ('event_volunteer', 'Event Volunteer')], default='donor', max_length=50, null=True)),
                ('verified', models.BooleanField(blank=True, default=False, null=True)),
                ('isDriver', models.BooleanField(blank=True, default=False, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app.address')),
                ('profilePhoto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='volunteer_profile_img', to='app.document')),
            ],
            options={
                'verbose_name': 'Volunteer',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='VolunteerVehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(blank=True, default=False, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('vehicle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='volunteer_vehicle', to='app.vehicle')),
                ('volunteer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='volunteer_profile', to='app.volunteer')),
            ],
        ),
        migrations.CreateModel(
            name='FoodRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foodName', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('ingredients', models.TextField(blank=True, default='', max_length=500, null=True)),
                ('cookingInstructions', models.TextField(default='', max_length=500)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app.category')),
                ('foodImage', models.ManyToManyField(blank=True, null=True, related_name='recipe_photos', to='app.document')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='FoodItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('itemName', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('quantity', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('expiryDate', models.DateTimeField(blank=True, null=True)),
                ('itemType', models.CharField(blank=True, choices=[('food', 'Food'), ('supplies', 'Supplies')], default='food', max_length=50, null=True)),
                ('itemPhotos', models.ManyToManyField(blank=True, null=True, related_name='food_photos', to='app.document')),
            ],
        ),
        migrations.CreateModel(
            name='FoodEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('organizerPhoneNumber', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('pickupDate', models.DateTimeField(blank=True, null=True)),
                ('perishable', models.BooleanField(blank=True, default=False, null=True)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app.address')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app.category')),
                ('eventPhotos', models.ManyToManyField(blank=True, null=True, related_name='event_photos', to='app.document')),
                ('foodItems', models.ManyToManyField(blank=True, null=True, related_name='event_food_items', to='app.fooditem')),
                ('volunteers', models.ManyToManyField(blank=True, null=True, related_name='event_volunteers', to='app.volunteer')),
            ],
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('donationType', models.CharField(blank=True, choices=[('food', 'Food'), ('supplies', 'Supplies')], default='food', max_length=50, null=True)),
                ('quantity', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('pickupDate', models.DateTimeField(blank=True, null=True)),
                ('donorPhoneNumber', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app.address')),
                ('foodItems', models.ManyToManyField(blank=True, null=True, related_name='donation_items', to='app.fooditem')),
                ('volunteers', models.ManyToManyField(blank=True, null=True, related_name='donation_volunteers', to='app.volunteer')),
            ],
        ),
    ]