# Generated by Django 4.2 on 2023-09-14 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_location_active_location_managername'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
