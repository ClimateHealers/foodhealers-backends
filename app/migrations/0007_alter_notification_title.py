# Generated by Django 4.2 on 2023-11-10 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_deliverydetail_dropotp_deliverydetail_pickupotp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='title',
            field=models.CharField(blank=True, default='title', max_length=100, null=True),
        ),
    ]
