# Generated by Django 4.2 on 2023-08-30 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_exercise_thumb_image_tube'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='routines',
            field=models.ManyToManyField(through='api.RoutineExercise', to='api.routine'),
        ),
    ]
