# Generated by Django 4.2 on 2023-09-23 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_alter_user_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='barcode_images/'),
        ),
    ]