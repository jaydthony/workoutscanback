# Generated by Django 4.2 on 2023-10-27 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0038_routine_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='show_all',
            field=models.BooleanField(default=True),
        ),
    ]