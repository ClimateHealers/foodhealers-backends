# Generated by Django 4.2 on 2023-10-27 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_eventvolunteer_volunteers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverydetail',
            name='dropOtp',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='deliverydetail',
            name='pickupOtp',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='donation',
            name='active',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
        migrations.AddField(
            model_name='request',
            name='status',
            field=models.CharField(blank=True, choices=[('approved', 'Approved'), ('rejected', 'Rejected'), ('pending', 'Pending')], default='pending', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='message',
            field=models.TextField(blank=True, default='this is sample message', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notificationType',
            field=models.CharField(blank=True, choices=[('event', 'Event'), ('donation', 'Donation'), ('volunteer', 'Volunteer'), ('request', 'Request'), ('other', 'Other')], default='other', max_length=50, null=True),
        ),
    ]
