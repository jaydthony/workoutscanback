# Generated by Django 4.2 on 2023-08-26 06:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_location_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.company'),
        ),
    ]