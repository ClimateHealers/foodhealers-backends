# Generated by Django 4.2 on 2023-10-10 09:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_category_categoryimage_customtoken_expopushtoken_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventvolunteer',
            name='volunteers',
        ),
        migrations.AddField(
            model_name='eventvolunteer',
            name='fromDate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='eventvolunteer',
            name='toDate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='eventvolunteer',
            name='volunteer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app.volunteer'),
        ),
        migrations.AddField(
            model_name='foodevent',
            name='requiredVolunteers',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='foodevent',
            name='volunteers',
            field=models.ManyToManyField(blank=True, null=True, related_name='food_event_volunteers', to='app.volunteer'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notificationType',
            field=models.CharField(blank=True, choices=[('event', 'Event'), ('donation', 'Donation'), ('volunteer', 'Volunteer'), ('other', 'Other')], default='other', max_length=50, null=True),
        ),
    ]
