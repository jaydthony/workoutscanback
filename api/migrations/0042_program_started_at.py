# Generated by Django 4.2 on 2023-11-08 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_program_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
