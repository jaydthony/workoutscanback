# Generated by Django 4.2 on 2023-08-30 18:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_rename_exercises_routine_r_exercises'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routineexercise',
            name='exercise_routine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercise_routine', to='api.exercise'),
        ),
    ]