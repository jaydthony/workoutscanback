# Generated by Django 4.2 on 2023-10-24 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_rename_user_subscription_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programphase',
            name='duration_weeks',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
