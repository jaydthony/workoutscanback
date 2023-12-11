from django.core.validators import FileExtensionValidator
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
import qrcode
import uuid
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.utils import timezone
from django.db import models
from django.core.files.base import ContentFile
from io import BytesIO
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Company(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    alias_name = models.CharField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name or str(self.id)

    def save(self, *args, **kwargs):
        is_new_company = self.pk is None
        super().save(*args, **kwargs)


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        # extra_fields.setdefault('username', '')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        company = extra_fields.pop('company', None)
        if company:
            # company = Company.objects.get(id= idc)
            extra_fields['company'] = Company.objects.get(pk=company)

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    # Your existing fields

    # Add related_name to the groups field
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='custom_user_set',  # Change this to a unique name
        related_query_name='user',
    )

    # Add related_name to the user_permissions field
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # Change this to a unique name
        related_query_name='user',
    )

    name = models.CharField(max_length=255,  null=False, blank=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    username = None
    profile_picture =  models.ImageField(upload_to='barcode_images/', null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'company']

    def __str__(self):
        return self.email

    objects = CustomUserManager()


class RequestingUsers(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2000, null=True, blank=True)
    email = models.EmailField()
    processed = models.BooleanField(default=False)
    accepted = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Exercise(models.Model):
    company = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    video_upload = models.FileField(
        upload_to='exercise_videos/',
        blank=True, null=True,
        verbose_name='Video Upload (Max 20MB)',
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov']),
        ]
    )
    youtube_link = models.URLField(
        blank=True, null=True, verbose_name='YouTube Link')
    thumb_image = models.ImageField(upload_to='exercise_thumbnails/', blank=True, null=True)
    thumb_image_tube = models.URLField(
        blank=True, null=True, verbose_name='YouTube Link Thumb')
    
    is_upload = models.BooleanField(default=False)


    def __str__(self):
        return self.name


class Routine(models.Model):
    company = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2000, null=True, blank=True)
    r_exercises = models.ManyToManyField(Exercise, through='RoutineExercise')
    created_at = models.DateTimeField(auto_now_add=True)
    private = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    


class RoutineExercise(models.Model):
    routine_exercise = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name="routine_exercise")
    exercise_routine = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="exercise_routine")
    duration = models.PositiveIntegerField(null=True, blank=True)
    reps = models.PositiveIntegerField(null=True, blank=True)
    sets = models.PositiveIntegerField(null=True, blank=True)
    wait  = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

class Program(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    weeks = models.PositiveIntegerField(default=1)
    show_all = models.BooleanField(default=True)
    default = models.BooleanField(default=False)
    started_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    managername = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location')
    barcode_image = models.ImageField(upload_to='barcode_images/', blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company.name

    def save(self, *args, **kwargs):

                # Check if a program with the same name and company exists
        existing_program = Program.objects.filter(name=self.name, user=self.company, default=True).first()

        # If no program exists, create a new program
        if not existing_program:
            current_date = datetime.now().date()
            today_time = datetime.combine(current_date, time(0, 0))
            new_program = Program.objects.create(
                user=self.company,
                name=self.name,
                default=True,
                started_at=today_time
            )

        

        if not self.barcode_image:  # Generate QR code image only if not already generated
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def generate_qr_code(self):
        url = f"https://workoutscanner.com/loc/{str(self.id)}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Create an in-memory buffer to hold the image data
        buffer = BytesIO()
        img.save(buffer, format='PNG')

        # Create a ContentFile from the buffer and save to barcode_image field
        self.barcode_image.save(f"barcode_{self.id}.png", ContentFile(
            buffer.getvalue()), save=False)


class LocationDays(models.Model):
    DAY_CHOICES = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, blank=True, null=True)







class ProgramPhase(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    duration_weeks = models.PositiveIntegerField(default=1)
    routines = models.ManyToManyField('Routine', related_name='routinesPhases',through='ProgramPhaseRoutine')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='phasesProgram')  # Update related_name here

    def __str__(self):
        return f"{self.program.name} - Phase {self.name}"

class ProgramPhaseRoutine(models.Model):
    phase = models.ForeignKey(ProgramPhase, on_delete=models.CASCADE)
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.phase.program.name} - Phase {self.phase.name} - {self.routine.name}"



from datetime import datetime, time
class Subscription(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    defualt = models.BooleanField(default=False)
    started_at = models.DateTimeField()


    def __str__(self):
        return self.location.name
    def save(self, *args, **kwargs):
        if self.started_at:
            # Set the started_at field to 12 midnight (00:00) if it's not provided
           
            self.started_at = datetime.combine(self.started_at, time(0, 0))
        else:
            # Set the started_at field to the current day at 12 midnight (00:00)
            current_date = datetime.now().date()
            self.started_at = datetime.combine(current_date, time(0, 0))
        super(Subscription, self).save(*args, **kwargs)


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class UserScan(models.Model):
    user_ip = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user_ip} - {self.created_at}"


@receiver(post_save, sender=User)
def create_location(sender, instance, created, **kwargs):
    if created:
        Location.objects.create(name=instance.company.name, company=instance)

# Signal to create LocationDays instances for each day of the week on Location creation
@receiver(post_save, sender=Location)
def create_location_days(sender, instance, created, **kwargs):
    if created:
        for day_value, day_label in LocationDays.DAY_CHOICES:
            LocationDays.objects.create(location=instance, day=day_value)



# Automatically create LocationDays instances for existing Location instances
# for location in Location.objects.all():
#     for day_value, day_label in LocationDays.DAY_CHOICES:
#         LocationDays.objects.get_or_create(location=location, day=day_value)
