# Generated by Django 4.2 on 2023-09-15 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_location_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='routineexercise',
            name='wait',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
