# Generated by Django 4.2 on 2023-10-18 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_alter_user_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('weeks', models.PositiveIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='ProgramPhase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('duration_weeks', models.PositiveIntegerField()),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phasesProgram', to='api.program')),
                ('routines', models.ManyToManyField(blank=True, related_name='routinesPhases', to='api.routine')),
            ],
        ),
        migrations.CreateModel(
            name='ProgramPhaseRoutine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.programphase')),
                ('routine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.routine')),
            ],
        ),
        migrations.AddField(
            model_name='program',
            name='phases',
            field=models.ManyToManyField(blank=True, related_name='programs', to='api.programphase'),
        ),
    ]
