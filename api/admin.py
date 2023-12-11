from django.contrib import admin
from .models import Company, RequestingUsers, Subscription, User, Location, Exercise, Routine, RoutineExercise, LocationDays, UserScan
from django.contrib.auth.forms import UserChangeForm
from .models import User
from django import forms


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'alias_name', 'created_date']


# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ['email', 'name', 'company', 'created_date']
#     list_filter = ['company']

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User

class CustomUserAdmin(DefaultUserAdmin):
    model = User
    ordering = ('name',)
    list_display = ('email', 'name', 'company', 'created_date')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'name', 'company')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

# Register your custom user model with the custom admin class
admin.site.register(User, CustomUserAdmin)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['company', 'created_at']


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']

@admin.register(RequestingUsers)
class RequestingUsereAdmin(admin.ModelAdmin):
    list_display = ['name', "email",'created_at']


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ['company', 'name',  'created_at']


@admin.register(RoutineExercise)
class RoutineExerciseAdmin(admin.ModelAdmin):
    list_display = ['routine_exercise', 'exercise_routine', 'duration', 'reps', 'sets']


@admin.register(LocationDays)
class LocationDaysAdmin(admin.ModelAdmin):
    list_display = ['location', 'day']


@admin.register(Subscription)
class LocationDaysAdmin(admin.ModelAdmin):
    list_display = ['location', 'started_at']


from .models import Program, ProgramPhase, ProgramPhaseRoutine

class ProgramPhaseInline(admin.TabularInline):
    model = ProgramPhase
    extra = 1  # The number of empty forms to display

class ProgramPhaseRoutineInline(admin.TabularInline):
    model = ProgramPhaseRoutine
    extra = 1  # The number of empty forms to display

@admin.register(UserScan)
class UserScanAdmin(admin.ModelAdmin):
    list_display = ('user_ip', )
    # inlines = [ProgramPhaseInline]

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'weeks')
    inlines = [ProgramPhaseInline]

@admin.register(ProgramPhase)
class ProgramPhaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'program', 'duration_weeks')
    inlines = [ProgramPhaseRoutineInline]

@admin.register(ProgramPhaseRoutine)
class ProgramPhaseRoutineAdmin(admin.ModelAdmin):
    list_display = ('phase', 'routine')