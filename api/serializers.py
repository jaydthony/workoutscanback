from rest_framework import serializers
from .models import PasswordResetToken, RequestingUsers,  Subscription, User, Company, Exercise
from rest_framework.exceptions import ValidationError as ValidationError1
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.core.exceptions import ValidationError


from .validators import MaxFileSizeValidator


class ExerciseSerializer(serializers.ModelSerializer):
    # thumb_image = serializers.SerializerMethodField()
    video_upload = serializers.FileField(
        max_length=None,
        allow_empty_file=False,
        required=False,
        validators=[MaxFileSizeValidator(max_size=20 * 1024 * 1024)]
    )
    class Meta:
        model = Exercise
        # fields = ['id', "company", "name", "description", "created_at", "video_upload", "youtube_link", "thumb_image", "thumb_image_tube", "is_upload"]
        fields = "__all__"
        extra_kwargs = {
            'company': {'required': False}
        }

    # def get_thumb_image(self, obj):
    #     if obj.thumb_image:
    #         request = self.context.get('request')
    #         thumb_image_url = obj.thumb_image.url
    #         return request.build_absolute_uri(thumb_image_url)
    #     return None






class UserAuthSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        max_length=255, write_only=True, required=False)
    alias_name = serializers.CharField(
        max_length=255, write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id',  "name", 'email', 'password',
                  'company_name', 'alias_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'company_name': {'required': False},
            'alias_name': {'required': False},

        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        company_name = validated_data.pop('company_name', None)
        alias_name = validated_data.pop('alias_name', None)

        company = Company.objects.create(
            name=company_name, alias_name=alias_name, created_date=timezone.now())

        validated_data['company'] = company

        instance = self.Meta.model(**validated_data)

        if password is not None:
            try:
                validate_password(password)  # Validate the password
            except ValidationError as e:
                error_messages = [str(error) for error in e]
                # Raise the error as a field-specific error
                raise serializers.ValidationError({'password': error_messages})

            instance.set_password(password)

        instance.save()

        return instance


class UserSerializer(serializers.ModelSerializer):
    # company = CompanySerializer(read_only=True)
    # company_department = CompanyDepartmentSerializer(read_only=True)
    date_joined = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    location_count= serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "name", "email", 'password',
                  "profile_picture", "date_joined", 'is_superuser', "count", "location_count"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_date_joined(self, obj):
        return obj.date_joined.strftime("%d, %B %Y")

    def get_count(self, obj):
        if not obj.is_superuser:
            return 0
        return RequestingUsers.objects.filter(processed=False).count()
    def get_location_count(self, obj):
        
        return len(obj.location.all())
    





from .models import Routine, RoutineExercise

class RoutineExerciseSerializer(serializers.ModelSerializer):
    exercise_info = serializers.SerializerMethodField()
    
    class Meta:
        model = RoutineExercise
        fields = "__all__"
        # fields = ["id", "duration", "reps", "sets", "notes", "exercise_routine"]  # Adjust this based on your RoutineExercise model
    def get_exercise_info(self, obj):
        
        return_data = ExerciseSerializer(obj.exercise_routine, context={'request': self.context.get('request')}).data
        return return_data



class RoutineSerializer(serializers.ModelSerializer):
    # r_exercises = RoutineExerciseSerializer(many=True, read_only=True)  # To serialize the related exercises
    exercises = serializers.SerializerMethodField()
    class Meta:
        model = Routine
        fields = '__all__'
        extra_kwargs = {
            'company': {'required': False}
        }

    
    def get_exercises(self, obj):
        routine_exercises = obj.routine_exercise.all()  # Access related RoutineExercise instances
        routine_exercise_data = RoutineExerciseSerializer(routine_exercises, many=True, context={'request': self.context.get('request')}).data
        return routine_exercise_data



from .models import Location, LocationDays


class LocationDaysSerializer(serializers.ModelSerializer):
    day_display = serializers.SerializerMethodField()
    routine_name = serializers.CharField(source='routine.name', read_only=True)  # Name of the linked Routine
    routine_id = serializers.PrimaryKeyRelatedField(source='routine', read_only=True)  # ID of the linked Routine
    
    class Meta:
        model = LocationDays
        fields = '__all__'

    def get_day_display(self, obj):
        # Get the full day name corresponding to the day abbreviation
        for abbreviation, full_name in LocationDays.DAY_CHOICES:
            if obj.day == abbreviation:
                return full_name
        return obj.day # Fallback to abbreviation if no match found
    
from datetime import date

from .models import Program, ProgramPhase, ProgramPhaseRoutine


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
    

class UserProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_picture']


class RequestingUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestingUsers
        fields = ('id', 'name', 'description', 'email', 'created_at')



class ProgramCreateSerializer(serializers.Serializer):
    programName = serializers.CharField(max_length=100)
    days = serializers.IntegerField()
    phases = serializers.IntegerField()



class ProgramPhaseSerializer(serializers.ModelSerializer):
    # routines = RoutineSerializer(many=True, read_only=True)
    class Meta:
        model = ProgramPhase
        fields = '__all__'

class ProgramPhaseSerializer(serializers.ModelSerializer):
    # routines = RoutineSerializer(many=True, read_only=True)
    class Meta:
        model = ProgramPhase
        fields = '__all__'

class ProgramPhaseRoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramPhaseRoutine
        fields = '__all__'






class ProgramWithPhasesSerializer(serializers.ModelSerializer):
    phasesProgram = ProgramPhaseSerializer(many=True, read_only=True)
    days_since_subscription_start = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = '__all__'

    def get_days_since_subscription_start(self, obj):
        
        if obj.started_at:
            start_date = obj.started_at.date()
            current_date = date.today()
            days_passed = (current_date - start_date).days
          
            return days_passed
        return None





class ProgramSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Program
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    days_since_subscription_start = serializers.SerializerMethodField()
    program_length = serializers.SerializerMethodField()
   

    class Meta:
        model = Subscription
        fields = '__all__'

    def get_days_since_subscription_start(self, obj):
        
        if obj:
            start_date = obj.started_at.date()
            current_date = date.today()
            days_passed = (current_date - start_date).days
            # print(days_passed, "passsed")
            return days_passed
        return None
    
    def get_program_length(self, obj):
        
        if obj.program:
            value = obj.program.phasesProgram.all()
            
            return len(value)
        return None
    


class LocationSerializer(serializers.ModelSerializer):
    latest_active_subscription = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = '__all__'

    def get_latest_active_subscription(self, location):
        latest_subscription = Subscription.objects.filter(location=location, active=True).order_by('-started_at').first()
        if latest_subscription:
            return SubscriptionSerializer(latest_subscription).data
        return None
    
    def get_company(self, location):
        
        if location:
            return UserSerializer(location.company).data
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Rename the field for better naming
        data['latest_active_subscription'] = data.pop('latest_active_subscription')
        return data
    

class SubscribedUserSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    days_since_subscription_start = serializers.SerializerMethodField()
    program_length = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['id', 'location', 'program', 'active', 'started_at', "days_since_subscription_start", "program_length"]

    def get_location(self, obj):
        location = Location.objects.get(id=obj.location.id)  # Retrieve the user object
        return LocationSerializer(location).data

    def get_days_since_subscription_start(self, obj):
        
        if obj:
            start_date = obj.started_at.date()
            current_date = date.today()
            days_passed = (current_date - start_date).days

            return days_passed
        return None
    
    def get_program_length(self, obj):
        
        if obj.program:
            value = obj.program.phasesProgram.all()
         
            return len(value)
        return None
    

    
    
class ProgramPhaseDetailsSerializer(serializers.ModelSerializer):
    routines = RoutineSerializer(many=True, read_only=True)
    class Meta:
        model = ProgramPhase
        fields = '__all__'

class ProgramMoreSerializer(serializers.ModelSerializer):
    phases = ProgramPhaseDetailsSerializer(many=True, read_only=True, source='phasesProgram')
    class Meta:
        model = Program
        fields = '__all__'


class SubscriptionMoreSerializer(serializers.ModelSerializer):
    days_since_subscription_start = serializers.SerializerMethodField()
    program_length = serializers.SerializerMethodField()
    program = ProgramMoreSerializer()

    class Meta:
        model = Subscription
        fields = '__all__'

    def get_days_since_subscription_start(self, obj):
        
        if obj:
            start_date = obj.started_at.date()
            current_date = date.today()
            days_passed = (current_date - start_date).days
            # print(days_passed, "passsed")
            return days_passed
        return None
    
    def get_program_length(self, obj):
        
        if obj.program:
            value = obj.program.phasesProgram.all()
            
            return len(value)
        return None

class LocationMoreSerializer(serializers.ModelSerializer):
    subscription = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = '__all__'

    def get_subscription(self, location):
        latest_subscription = Subscription.objects.filter(location=location, active=True).order_by('-started_at')
        if latest_subscription:
            return SubscriptionMoreSerializer(latest_subscription, many=True).data
        return []
    
    def get_company(self, location):
        
        if location:
            return UserSerializer(location.company).data
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Rename the field for better naming
        data['subscription'] = data.pop('subscription')
        return data



class UserDetailsSerializer(serializers.ModelSerializer):
    # company = CompanySerializer(read_only=True)
    # company_department = CompanyDepartmentSerializer(read_only=True)
    date_joined = serializers.SerializerMethodField()
    locations = LocationSerializer(many=True, read_only=True, source='location') 

    

    class Meta:
        model = User
        fields = ["id", "name", "email", 'password',
                  "profile_picture", "date_joined", 'is_superuser', "locations"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_date_joined(self, obj):
        return obj.date_joined.strftime("%d, %B %Y")
    

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    


from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

User = get_user_model()

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    """
    token = serializers.CharField()
    new_password = serializers.CharField(style={'input_type': 'password'})

    def validate_token(self, value):
        # Check if the provided token is valid
        try:
            user = PasswordResetToken.objects.get(token=value).user
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError(_("Invalid or expired token."))

        if not default_token_generator.check_token(user, value):
            raise serializers.ValidationError(_("Invalid or expired token."))

        return value

    def save(self):
        # Set the new password for the user
        user = PasswordResetToken.objects.get(token=self.validated_data['token']).user
        user.set_password(self.validated_data['new_password'])
        user.save()

        # Delete the used password reset token
        PasswordResetToken.objects.filter(user=user).delete()

        return user
