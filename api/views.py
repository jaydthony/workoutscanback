from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render

from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from dotenv import load_dotenv
from api.models import User
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BaseAuthentication
from api.serializers import UserAuthSerializer, UserSerializer
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status

from api.serializers import ExerciseSerializer
from api.models import Exercise
from .permissions import IsSuperuserOrReadOnly, IsSuperuserOrReadOnlyExceptPOST
from .getThumb import generate_thumbnail, get_youtube_thumbnail

from .authentication.JWTAuthentication import CustomAuthentication


class LoginAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return None

# Create your views here.


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class LoginView(APIView):
    authentication_classes = [LoginAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        print(email, password)

        user = User.objects.filter(email=email).first()
        response = Response()
        

        if user is None:
            raise AuthenticationFailed("User not found")

        if not user.check_password(password):
            raise AuthenticationFailed("incorrect Password")

        if user is not None:
            if user.is_active:
                data = get_tokens_for_user(user)

                response.data = {"Success": "Login successfully", "data": data}
                return response
            else:
                return Response({"No active": "This account is not active!!"}, status=status.HTTP_404_NOT_FOUND)

        return response


class UserView(APIView):
    def get(self, request):

        user = request.user

        # print(user, "the user")

        serializer = UserSerializer(user)
        return Response(serializer.data)


class RegisterView(APIView):
    authentication_classes = [LoginAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from django.db.models import Q


class ExamplePagination2(PageNumberPagination):
    page_size = 20

class ExamplePagination3(PageNumberPagination):
    page_size = 40
class ExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter,  filters.OrderingFilter]
    
    search_fields = ['id', "name"]
    
    pagination_class = ExamplePagination2
    
    def get_queryset(self):
        # Get the currently logged in user
        user = self.request.user

        if user.is_superuser:
            return Exercise.objects.all()

        # Define a query to get exercises based on user and admin criteria
        queryset = Exercise.objects.filter(
            Q(company=user) | Q(company__is_superuser=True)
        )

        return queryset
    
    def perform_create(self, serializer):
        # Automatically set the company to the currently logged in user
        serializer.save(company=self.request.user)

    def perform_create(self, serializer):
        video_file = self.request.FILES.get('video_upload')
        youtube_url = serializer.validated_data.get('youtube_link')

        # print(video_file, youtube_url)

        if video_file:
            
            thumbnail_content = generate_thumbnail(video_file.read())
            if not thumbnail_content:
                raise ValidationError("Unable to generate thumbnail for video")
            if thumbnail_content:
                instance = serializer.save(company=self.request.user)
                instance.thumb_image.save("thumbnail.jpg", ContentFile(thumbnail_content.read()), save=False)
                instance.save()
                # print(instance, instance.pk)
        elif youtube_url:
            
            thumbnail_path = get_youtube_thumbnail(youtube_url)  # Update this line
            # print(thumbnail_path)
            if not thumbnail_path:
                raise ValidationError("Unable to generate thumb for video")
            if thumbnail_path:
                instance = serializer.save(company=self.request.user)
                instance.thumb_image_tube = thumbnail_path
                instance.save()
        else:
            raise ValidationError("You must provide either a video file or a YouTube URL.")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.company != self.request.user:
            raise PermissionDenied("You don't have permission to edit this exercise.")

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.company != self.request.user:
            raise PermissionDenied("You don't have permission to edit this exercise.")

        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Ensure that only the user who created the RoutineExercise can delete it
        if instance.company != request.user:
            raise PermissionDenied("You don't have permission to delete this Exercise.")
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    



from .models import LocationDays, ProgramPhaseRoutine, RequestingUsers, Routine, RoutineExercise,  Subscription, UserScan
from .serializers import LocationDaysSerializer, PasswordChangeSerializer, ProgramMoreSerializer, ProgramPhaseRoutineSerializer, RequestingUsersSerializer, RoutineExerciseSerializer, RoutineSerializer, SubscribedUserSerializer, SubscriptionMoreSerializer, SubscriptionSerializer, UserDetailsSerializer, UserProfilePictureSerializer
from django.db.models import F, Case, When, Value, BooleanField

class RoutineViewSet(viewsets.ModelViewSet):
    serializer_class = RoutineSerializer
    permission_classes = [permissions.IsAuthenticated]  # Default authentication and permission
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter,  filters.OrderingFilter]
    
    search_fields = ['id', "name"]

    pagination_class = ExamplePagination3
    
    
    def get_queryset(self):
        # Retrieve routines linked to the currently logged in company (user)
        # Order by a custom expression that places routines with the user's company first
        return Routine.objects.annotate(
            is_user_company=Case(
                When(company=self.request.user, then=Value(1)),
                default=Value(0),
                output_field=BooleanField()
            )
        ).order_by('-is_user_company', 'private', 'name')
    
    def perform_create(self, serializer):
        # Automatically set the company to the currently logged in user
        serializer.save(company=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.company != self.request.user:
            raise PermissionDenied("You don't have permission to edit this Workout.")

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.company != self.request.user:
            raise PermissionDenied("You don't have permission to edit this Workout.")

        return super().partial_update(request, *args, **kwargs)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Ensure that only the user who created the RoutineExercise can delete it
        if instance.company != request.user:
            raise PermissionDenied("You don't have permission to delete this Workout.")
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoutineExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = RoutineExerciseSerializer

    
    def get_queryset(self):
        # Only return routine exercises linked to the company (user)
        return RoutineExercise.objects.filter()
    
    def perform_create(self, serializer):
        # Ensure the exercise is linked to the user's company
        exercise_id = serializer.validated_data.get('exercise_routine')
        routine_id = serializer.validated_data.get('routine_exercise')
       
        
        try:
            routine = Routine.objects.get(pk=routine_id.id, company=self.request.user)
        except Routine.DoesNotExist:
            raise PermissionDenied("You don't have permission to add this exercise to the Workout.")
        
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Ensure that only the user who created the RoutineExercise can delete it
        if instance.routine_exercise.company != request.user:
            raise PermissionDenied("You don't have permission to delete this Workout Exercise.")
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class RoutineExerciseViewSet2(viewsets.ModelViewSet):
    serializer_class = RoutineExerciseSerializer

    
    def get_queryset(self):
        # Only return routine exercises linked to the company (user)
        return RoutineExercise.objects.filter()
    
    def perform_create(self, serializer):
        # Ensure the exercise is linked to the user's company
        exercise_id = serializer.validated_data.get('exercise_routine')
        routine_id = serializer.validated_data.get('routine_exercise')
       
        
        try:
            routine = Routine.objects.get(pk=routine_id.id, company=self.request.user)
        except Routine.DoesNotExist:
            raise PermissionDenied("You don't have permission to add this exercise to the Workout.")
        
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Ensure that only the user who created the RoutineExercise can delete it
        if instance.routine_exercise.company != request.user:
            raise PermissionDenied("You don't have permission to delete this Workout Exercise.")
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


from .models import Location
from .serializers import LocationSerializer
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser

class LocationViewSet(viewsets.ModelViewSet):
   
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter,  filters.OrderingFilter]
    
    search_fields = ['id', "name"]
    
    def get_queryset(self):
        # Only return routines linked to the currently logged in company (user)
        
        if self.request.user.is_superuser:
            return Location.objects.filter(active=True)
        return Location.objects.filter(company=self.request.user)
    
    def perform_create(self, serializer):
        # Automatically set the company to the currently logged in user
        if self.request.user.is_superuser:
            
            company = self.request.data.get('company', False)
            original_conpany = get_object_or_404(User, pk=company)
        
            serializer.save(company=original_conpany)
        else:
            serializer.save(company=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.company != self.request.user:
            raise PermissionDenied("You don't have permission to edit this routine.")

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.company != self.request.user:
            raise PermissionDenied("You don't have permission to edit this routine.")

        return super().partial_update(request, *args, **kwargs)
    
    @action(detail=True, methods=['POST'], url_path='generate_qr_code')
    def generate_qr_code(self, request, pk=None):
        location = self.get_object()
        location.generate_qr_code()  # Call the generate_qr_code method
        location.save()  # Save the Location model to store the updated QR code image

        return Response({'status': 'QR code generated successfully'})

    @action(detail=True, methods=['DELETE'])
    def delete_qr_picture(self, request, pk=None):
        location = self.get_object()
        location.barcode_image.delete()  # Delete the existing QR picture

        return Response({'status': 'QR picture deleted successfully'})



class LocationDaysViewSet(viewsets.ModelViewSet):
   
    serializer_class = LocationDaysSerializer
    
    def get_queryset(self):
        # Only return routines linked to the currently logged in company (user)
        return LocationDays.objects.filter(location__company=self.request.user)
    
    def perform_create(self, serializer):
        # Automatically set the company to the currently logged in user
        serializer.save()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.location.company != self.request.user:
            raise PermissionDenied("You don't have permission to edit this routine.")

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.location.company != self.request.user:
            raise PermissionDenied("You don't have permission to edit this routine.")

        return super().partial_update(request, *args, **kwargs)



from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import datetime

from .models import Location, LocationDays
from .serializers import RoutineSerializer, LocationMoreSerializer  # Import your RoutineSerializer here
from django.http import JsonResponse
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # print(x_forwarded_for, "xxfor")
    # print(request.META.get('REMOTE_ADDR'))
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@csrf_exempt
def get_routine_for_current_day(request, location_id):
    # Determine the current day of the week (e.g., 'mon', 'tue', etc.)
    current_day = datetime.datetime.now().strftime('%A')

    # Get the Location object
    location = get_object_or_404(Location, id=location_id)

    if location:
        location_serializer = LocationMoreSerializer(location, context={'request': request})
        location_data = location_serializer.data
    else:
        location_data = None
    
    if location:
        default_program = Program.objects.filter(name=location.name, default=True).first()
        default_data =ProgramMoreSerializer(default_program).data
    else:
        default_data = None

    if location:
        # Get the user's IP address
        user_ip = get_client_ip(request)

        # Get the current date
        current_date = timezone.now().date()

        # Check if a UserScan with the same user_ip and created_at (today's date) exists
        existing_user_scan = UserScan.objects.filter(user_ip=user_ip, created_at__date=current_date, location=location).first()
        print(current_day, )
        if not existing_user_scan:
            # If no existing UserScan found, create a new one
            user_scan = UserScan.objects.create(user_ip=user_ip, day_of_week=current_day, location=location)
            # Additional logic if needed...
        else:
            # Handle the case where a UserScan for the same IP and date already exists
            pass
            # print("UserScan already exists for this IP and today's date.")

    # Return the routine data as JSON response
    response_data = {
        'location': location_data,
        'default': default_data
    }

    return JsonResponse(response_data)


class SubscriptionViewSet(viewsets.ModelViewSet):
   
    serializer_class = SubscriptionSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter,  filters.OrderingFilter]
    
    search_fields = ['id']
    
    def get_queryset(self):
        # Only return routines linked to the currently logged in company (user)
        
        if self.request.user.is_superuser:
            return Subscription.objects.filter(active=True)
        return Subscription.objects.filter(location__company=self.request.user)


@csrf_exempt
def get_subscriptions(request, location_id):
    # Determine the current day of the week (e.g., 'mon', 'tue', etc.)
    current_day = datetime.datetime.now().strftime('%a').lower()

    # Get the Location object
    location = get_object_or_404(Location, id=location_id)
    subscription = Subscription.objects.filter(location__id = location_id, active=True, defualt=True).order_by('-started_at')

    if location:
        location_serializer = LocationMoreSerializer(location, context={'request': request})
        location_data = location_serializer.data
    
    else:
        location_data = None

    if location:
        default_program = Program.objects.filter(name=location.name, default=True).first()
        default_data =ProgramWithPhasesSerializer(default_program).data
    else:
        default_data = None

    if len(subscription)>0:
        sub_default = True
    else:
        sub_default = False

    

    # Return the routine data as JSON response
    response_data = {
        'location': location_data,
        'sub_default': sub_default,
        "default": default_data
    }

    return JsonResponse(response_data)

class PasswordChangeView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data.get('old_password')
            new_password = serializer.validated_data.get('new_password')

            if not user.check_password(old_password):
                return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserProfilePictureUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfilePictureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user



class RequestingUsersViewSet(viewsets.ModelViewSet):
    queryset = RequestingUsers.objects.all()
    serializer_class = RequestingUsersSerializer
    permission_classes = [IsSuperuserOrReadOnlyExceptPOST]   
    authentication_classes = [LoginAuthentication]


    def get_queryset(self):
        # Filter the queryset to only include users with processed=True
        return RequestingUsers.objects.filter(processed=False)



class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailsSerializer
    permission_classes = [IsSuperuserOrReadOnly]   
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter,  filters.OrderingFilter]
    
    search_fields = ['id', "name"]

    


class CountUnprocessedRequestingUsers(APIView):
    def get(self, request):
        # Count requesting users with processed=False
        count = RequestingUsers.objects.filter(processed=False).count()
        return Response({'count': count}, status=status.HTTP_200_OK)
    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
import secrets
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags  # Import to strip HTML tags from the message

from .models import RequestingUsers, User  # Assuming this is your custom User model
from .serializers import RequestingUsersSerializer, UserAuthSerializer  # Import the serializer

class ProcessRequestingUser(APIView):
    permission_classes = [IsSuperuserOrReadOnly]

    def post(self, request, id):
        # Get the requesting user data
        user_data = request.data.get('user_data', {})

        try:
            user = RequestingUsers.objects.get(id=id)
            print(user, "here is the user")
        except RequestingUsers.DoesNotExist:
            return Response({'error': 'Requesting user not found'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a random password
        password = secrets.token_hex(8)  # You can adjust the password length as needed

        print(password)

        # # Use the UserAuthSerializer to create a new User instance
        serializer = UserAuthSerializer(data={
            'name': user.name,
            'email': user.email,
            'password': password,
            'company_name': user.name,  # Assuming 'company' is the company name field
        })

        if serializer.is_valid():
            new_user = serializer.save()   

            # Create an EmailMessage
            subject = 'Welcome to Workout Scanner!'
            text_message = 'Your Gym Has Been Added'
            from_email = 'workoutscanner@gmail.com'  # Replace with your email address
            recipient_list = [user.email]  # User's email address

            # Render the HTML email template with email and password as context
            html_message = render_to_string('registration_email.html', {
                'email': user.email,
                'password': password,
            })

            email = EmailMultiAlternatives(
                subject,
                text_message,  # Plain text version of the email
                from_email,
                recipient_list,
            )

            # Attach the HTML email template as an alternative
            email.attach_alternative(html_message, "text/html")

            # Send the email
            email.send()

            if user:
                user.processed = True
                user.accepted = True
                user.save()

            return Response({'message': 'Requesting user processed successfully'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # # Mark the requesting user as processed
            # requesting_user_id = user_data.get('id')



class RejectRequestingUser(APIView):
    permission_classes = [IsSuperuserOrReadOnly]

    def post(self, request, id):
        # Get the requesting user data
        user_data = request.data.get('user_data', {})

        try:
            user = RequestingUsers.objects.get(id=id)
            print(user, "here is the user")
        except RequestingUsers.DoesNotExist:
            return Response({'error': 'Requesting user not found'}, status=status.HTTP_404_NOT_FOUND)

        if user:
            user.processed = True
            user.accepted = False
            user.save()

            return Response({'message': 'Requesting Rejected user processed successfully'})
        




from rest_framework.views import APIView
from .models import Program, ProgramPhase
from .serializers import ProgramCreateSerializer

class ProgramCreateView(APIView):
    def post(self, request):
        serializer = ProgramCreateSerializer(data=request.data)
        if serializer.is_valid():
            program_name = serializer.validated_data['programName']
            days= serializer.validated_data['days']

            # Create the program
            program = Program(name=program_name, weeks=days, user=self.request.user)
            program.save()

            # Calculate weeks per phase
           

            
            for days_num in range(1, days + 1):
                phase_name = f'Day {days_num}'
                phase = ProgramPhase(name=phase_name, program=program)
                phase.save()
                # print(phase_name, "names")

            return Response(ProgramWithPhasesSerializer(program).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from .serializers import ProgramSerializer, ProgramPhaseSerializer, ProgramWithPhasesSerializer, ProgramPhaseDetailsSerializer

# class ProgramList(generics.ListAPIView):
#     queryset = Program.objects.all()
#     serializer_class = ProgramSerializer

#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return ProgramSerializer
#         return ProgramSerializer
    


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramWithPhasesSerializer
    def get_queryset(self):
        # Only return routines linked to the currently logged in company (user)
        return Program.objects.filter(user=self.request.user, default=False)
    
class ProgramViewSet2(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramWithPhasesSerializer
    def get_queryset(self):
        # Only return routines linked to the currently logged in company (user)
        return Program.objects.filter()


class ProgramPhaseViewSet(viewsets.ModelViewSet):
    queryset = ProgramPhase.objects.all()
    serializer_class = ProgramPhaseSerializer

class ProgramPhaseRoutineViewSet(viewsets.ModelViewSet):
    queryset = ProgramPhaseRoutine.objects.all()
    serializer_class = ProgramPhaseRoutineSerializer




class ProgramPhaseDetail(generics.RetrieveAPIView):
    queryset = ProgramPhase.objects.all()
    serializer_class = ProgramPhaseDetailsSerializer


from rest_framework.decorators import api_view

@api_view(['POST'])
def remove_routines_from_programphase(request, programphase_id):
    programphase = get_object_or_404(ProgramPhase, id=programphase_id)
    
    # Get routine IDs to remove from the request data
    routine_ids = request.data.get('routines', [])
    
    # Remove routines from the ProgramPhase
    programphase.routines.remove(*routine_ids)

    # Serialize and return the updated ProgramPhase
    serializer = ProgramPhaseSerializer(programphase)
    return Response(serializer.data)


@api_view(['POST'])
def createroutine(request):
    # Get routine IDs to remove from the request data
    routine_exercise_data = request.data.get('routineexercise', [])
    workoutName = request.data.get('name', None)
    private = request.data.get('private', None)
    description = request.data.get('description', None)
    programphase_id = request.data.get('programphase_id', None)
    print(workoutName, private, description, "pag", programphase_id)
    

    print("user", private)

    newroutine = Routine()
    newroutine.company = request.user
    newroutine.name = workoutName
    newroutine.description = description
    newroutine.private = private
    newroutine.save()

    # programphase.routines.add(newroutine)

    if private:
        programphase = get_object_or_404(ProgramPhase, id=programphase_id)
        programphase.routines.add(*[str(newroutine.pk)])


    


    # Assuming 'routine_exercise_data' is a list of dictionaries containing routine exercise data
    for exercise_data in routine_exercise_data:
        # print(exercise_data)
        # routine_exercise=theroutine.data.id
        newroutineexercise  =  RoutineExercise()
        try:
            exercise = Exercise.objects.get(id=exercise_data.get("exerciseId", None))
        except Exercise.DoesNotExist:
            # Skip to the next iteration if the exercise does not exist
            continue
        newroutineexercise.routine_exercise = newroutine
        newroutineexercise.exercise_routine = exercise
        newroutineexercise.duration = exercise_data.get("duration", None)
        newroutineexercise.reps = exercise_data.get("reps", None)
        newroutineexercise.sets = exercise_data.get("sets", None)
        newroutineexercise.notes = exercise_data.get("notes", None)
        newroutineexercise.wait = exercise_data.get("wait", None)
        newroutineexercise.save()

    return Response(RoutineSerializer(newroutine).data)





@api_view(['POST'])
def add_routines_to_programphase(request, programphase_id):
    programphase = get_object_or_404(ProgramPhase, id=programphase_id)
    
    # Get routine IDs to add from the request data
    routine_ids = request.data.get('routines', [])

    
    # Add routines to the ProgramPhase
    programphase.routines.add(*routine_ids)

    # Serialize and return the updated ProgramPhase
    serializer = ProgramPhaseSerializer(programphase)
    return Response(serializer.data)



    
class SubscriptionCreateView(generics.CreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def create(self, request, *args, **kwargs):
        user = request.user  # Assuming you have authentication set up
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        location_id = serializer.validated_data['location']
        program_id = serializer.validated_data['program']

        # Check if an active subscription with the same program already exists for the location
        existing_subscription = Subscription.objects.filter(
            location=location_id,
            program=program_id,
            active=True
        ).first()

        if existing_subscription:
            # If an active subscription already exists, return an error response
            return Response({'error': f'Subscription with the same program already exists for {location_id.name}.'}, status=status.HTTP_400_BAD_REQUEST)

        # # Deactivate existing subscriptions for the user
        # Subscription.objects.filter(location=location_id, active=True)

        # Create a new subscription
        serializer.save() 

        return Response(serializer.data, status=status.HTTP_201_CREATED)



class SubscribedUsersListView(generics.ListAPIView):
    serializer_class = SubscribedUserSerializer

    def get_queryset(self):
        program_id = self.kwargs['program_id']

        # Retrieve users subscribed to the active program
        return Subscription.objects.filter(program_id=program_id, active=True)


from django.http import JsonResponse
from rest_framework import status
from .models import Routine
from .serializers import RoutineSerializer


@api_view(['POST'])
@csrf_exempt
def duplicate_routine(request, routine_id):
    # Step 1: Retrieve the original routine
    original_routine = get_object_or_404(Routine, pk=routine_id)

    private = request.data.get('private', False)
    print("privte", private)

    # Step 2: Create a new routine as a duplicate
    new_routine = Routine(
        company=original_routine.company,
        name=f"{original_routine.name} (Copy)",
        description=original_routine.description,
        created_at=original_routine.created_at,
        private=private,
    )
    new_routine.save()

    # Step 3: Iterate over routine exercises and create duplicates
    original_exercises = original_routine.routine_exercise.all()
    for original_exercise in original_exercises:
        # Step 4: Create corresponding routine exercise for the new routine
        new_exercise = RoutineExercise(
            routine_exercise=new_routine,
            exercise_routine=original_exercise.exercise_routine,
            duration=original_exercise.duration,
            reps=original_exercise.reps,
            sets=original_exercise.sets,
            wait=original_exercise.wait,
            notes=original_exercise.notes,
        )
        new_exercise.save()

    serializer = RoutineSerializer(new_routine)
        
    return JsonResponse({
            'message': 'Routine duplicated successfully',
           'routine': serializer.data
        })



@api_view(['POST'])
@csrf_exempt
def unsubscribe(request, location_id):
    # Step 1: Retrieve the original routine
    sub_id = request.data.get('sub_id', False)
    subscription = Subscription.objects.filter(id=sub_id, location__id = location_id, active=True).update(active=False)

        
    return JsonResponse({
            'message': 'Subscribed',
        })


@api_view(['POST'])
@csrf_exempt
def makeDefault(request, location_id):
    # Step 1: Retrieve the original routine

    makehome = request.data.get('makehome', False)
    subscription_id = request.data.get('subscription', False)
    

    # Step 1: Retrieve the original routine
    if makehome:
        Subscription.objects.filter(location__id = location_id, active=True).update(defualt=False)
    else:
        Subscription.objects.filter(location__id = location_id, active=True).update(defualt=False)
        Subscription.objects.filter(id=subscription_id, location__id = location_id, active=True).update(defualt=True)
        
    return JsonResponse({
            'message': 'made main',
        })



@api_view(['POST'])
@csrf_exempt
def Add_user(request):
        # Generate a random password
    company_name = request.data.get('company_name', False)
    company_email = request.data.get('company_email', False)
    password = secrets.token_hex(8)  # You can adjust the password length as needed

    print(password)

    # # Use the UserAuthSerializer to create a new User instance
    serializer = UserAuthSerializer(data={
        'name': company_name,
        'email': company_email,
        'password': password,
        'company_name': company_name,  # Assuming 'company' is the company name field
    })

    if serializer.is_valid():
        new_user = serializer.save()   

        # Create an EmailMessage
        subject = 'Welcome to Workout Scanner!'
        text_message = 'Your Gym Has Been Added'
        from_email = 'workoutscanner@gmail.com'  # Replace with your email address
        recipient_list = [company_email]  # User's email address

        # Render the HTML email template with email and password as context
        html_message = render_to_string('registration_email.html', {
            'email': company_email,
            'password': password,
        })

        email = EmailMultiAlternatives(
            subject,
            text_message,  # Plain text version of the email
            from_email,
            recipient_list,
        )

        # Attach the HTML email template as an alternative
        email.attach_alternative(html_message, "text/html")

        # Send the email
        email.send()


        return Response({'message': 'Requesting user processed successfully'})
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # # Mark the requesting user as processed
            # requesting_user_id = user_data.get('id')

# def duplicate_routine(request, routine_id):
#     try:
#         original_routine = Routine.objects.get(pk=routine_id)
#         private = request.POST.get('private')
#         print("privte", private)
#         # Create a duplicate of the original routine
#         duplicated_routine = Routine.objects.create(
#             company=original_routine.company,
#             name=f"{original_routine.name} (Copy)",  # You can customize the name
#             description=original_routine.description,
#             created_at=original_routine.created_at,
#             private=private,
#         )
#         # Copy the routine exercises from the original routine to the duplicate
#         for original_exercise in original_routine.r_exercises.all():
#             duplicated_routine.r_exercises.add(original_exercise)
        
#         # Serialize the duplicated routine
#         serializer = RoutineSerializer(duplicated_routine)
        
#         return JsonResponse({
#             'message': 'Routine duplicated successfully',
#             'routine': serializer.data
#         })
#     except Routine.DoesNotExist:
#         return JsonResponse(
#             {'message': 'Original routine not found'},
#             status=status.HTTP_404_NOT_FOUND
#         )
#     except Exception as e:
#         return JsonResponse(
#             {'message': 'Failed to duplicate routine', 'error': str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


# views.py
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, status
from rest_framework.response import Response
from .models import PasswordResetToken
from .serializers import PasswordResetRequestSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string

class PasswordResetRequestView(generics.CreateAPIView):
    serializer_class = PasswordResetRequestSerializer
    authentication_classes = [LoginAuthentication]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # email = request.data.get('email')
        
        

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')

        print(email)

        user = User.objects.filter(email=email).first()
        
        if user:
            # Create a password reset token
            token = default_token_generator.make_token(user)
            PasswordResetToken.objects.create(user=user, token=token)

            # Send the reset email
            self.send_reset_email(user, token)

            return Response({'detail': 'Password reset email sent'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'User with this email not found'}, status=status.HTTP_404_NOT_FOUND)

    def send_reset_email(self, user, token):
        
                # Create an EmailMessage
        subject = 'Password Reset Request'
        text_message = 'You Requested a password change'
        from_email = 'workoutscanner@gmail.com'  # Replace with your email address
        recipient_list = [user.email]  # User's email address

        # Render the HTML email template with email and password as context
        html_message = render_to_string('password_reset_email.html', {
            'user': user,
            'link': f'https://workoutscanner.com/change-password/{token}/{urlsafe_base64_encode(force_bytes(user.pk))}',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token,
        })
        email = EmailMultiAlternatives(
            subject,
            text_message,  # Plain text version of the email
            from_email,
            recipient_list,
        )

        # Attach the HTML email template as an alternative
        email.attach_alternative(html_message, "text/html")

        # Send the email
        email.send()


# views.py
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str as force_text

from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.response import Response
from .models import PasswordResetToken
from .serializers import PasswordResetConfirmSerializer
from django.utils import timezone

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    authentication_classes = [LoginAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')
        password = request.data.get('password')

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            # Check if the token is still valid (e.g., within a certain time limit)
            token_obj = PasswordResetToken.objects.filter(user=user, token=token).first()
            if token_obj and self.is_token_valid(token_obj):
                # Reset the user's password
                user.set_password(password)
                user.save()

                # Delete the password reset token
                token_obj.delete()

                return Response({'detail': 'Password reset successful'}, status=status.HTTP_200_OK)
        
        return Response({'detail': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)

    def is_token_valid(self, token_obj):
        # Check if the token is still valid (e.g., within a certain time limit)
        expiration_time = timezone.now() - token_obj.created_at
        return expiration_time.total_seconds() < 3600  # Adjust the time limit as needed




from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import UserScan, Location, Program
@api_view(['GET'])
@csrf_exempt
def dashboard_data(request):
    # Total Programs by the user (request.user)
    total_programs = Program.objects.filter(user=request.user).count()

    # Total Scanned Today
    today = timezone.now().date()
    total_scanned_today = UserScan.objects.filter(
        location__company=request.user,
        created_at__date=today
    ).count()
    last_30_days_start = timezone.now() - timedelta(days=30)

    # Total scanned count for the last 30 days
    total_scanned_last_30_days = UserScan.objects.filter(
         location__company=request.user,
        created_at__gte=last_30_days_start
    ).count()
    # Total Scanned Last 7 Days
    last_7_days = today - timedelta(days=6)
    total_scanned_last_7_days = UserScan.objects.filter(
        location__company=request.user,
        created_at__date__range=[last_7_days, today]
    ).count()

    # Total Branches (by request.user)
    total_branches = Location.objects.filter(company=request.user).count()

    # Total Visitors (est) (use the total scan by all locations under the user)
    total_visitors = UserScan.objects.filter(location__company=request.user).count()
    total_subscribed_programs = Subscription.objects.filter(location__company=request.user, active=True).count()

# 
    low_days_query = UserScan.objects.filter(location__company=request.user).annotate(scans_count=Count('id')).order_by('scans_count').first()
    # low_days_query = UserScan.objects.filter(location__company=request.user).order_by( 'created_at__date').first()
    
    # Convert the queryset to a list of dictionaries
    low_days_list = None
    if low_days_query:
        low_days_list= low_days_query.day_of_week

    response_data = {
    'total_programs': total_programs,
    'total_scanned_today': total_scanned_today,
    'total_scanned_last_7_days': total_scanned_last_7_days,
    'total_scanned_last_30_days': total_scanned_last_30_days,
    'total_branches': total_branches,
    'total_visitors': total_visitors,
    'low_days': low_days_list,
    'total_subscribed_programs': total_subscribed_programs
}

    return JsonResponse(response_data)
