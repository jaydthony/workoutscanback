# Generated by Django 4.2 on 2023-08-29 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_exercise_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='thumb_image',
            field=models.ImageField(blank=True, null=True, upload_to='exercise_thumbnails/'),
        ),
    ]