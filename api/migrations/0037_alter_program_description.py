# Generated by Django 4.2 on 2023-10-25 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_alter_programphase_duration_weeks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='program',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
