# Generated by Django 4.2 on 2023-11-18 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0043_alter_location_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
