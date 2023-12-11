from django.urls import include, path

from django.conf import settings

from api import views

from django.conf.urls.static import static
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework.routers import DefaultRouter

# Exercise ViewSet URLs
default_router = DefaultRouter()
default_router.register(r'exercises', views.ExerciseViewSet, basename='exercise')


default_router.register(r'users', views.UsersViewSet, basename='users')

default_router.register(r'routines', views.RoutineViewSet, basename='routine')

# RoutineExercise ViewSet URLs

default_router.register(r'routine-exercises', views.RoutineExerciseViewSet, basename='routine-exercise')
default_router.register(r'routine-exercises2', views.RoutineExerciseViewSet2, basename='routine-exercise2')

default_router.register(r'locations', views.LocationViewSet, basename='location')

default_router.register(r'location-days', views.LocationDaysViewSet, basename='locationDays')

default_router.register(r'requesting-users', views.RequestingUsersViewSet)

default_router.register(r'programs', views.ProgramViewSet)

default_router.register(r'programs2', views.ProgramViewSet2)

default_router.register(r'programphase', views.ProgramPhaseViewSet)


default_router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscriptions')

default_router.register(r'programphaseroutine', views.ProgramPhaseRoutineViewSet)
 

urlpatterns = [

     path('', include(default_router.urls)),

    # path('create-vector-index/', create_vector_index.as_view(), name='create_vector_index'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('user/', views.UserView.as_view(), name='user'),

    path('locations/<uuid:location_id>/get_routine_for_current_day/', views.get_routine_for_current_day, name='get_routine_for_current_day'),
    path('locations/<uuid:location_id>/get_subscriptions/', views.get_subscriptions, name='get_subscriptions'),
    path('unsubscribe/<uuid:location_id>/', views.unsubscribe, name='unsubscribe'),
    path('makedefault/<uuid:location_id>/', views.makeDefault, name='makedefault'),
    path('change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    path('update-profile-picture/', views.UserProfilePictureUpdateView.as_view(), name='update-profile-picture'),
     path('count-unprocessed-requesting-users/', views.CountUnprocessedRequestingUsers.as_view(), name='count-unprocessed-requesting-users'),
    path('accept-user/<id>/', views.ProcessRequestingUser.as_view(), name='accept-user'),
    path('add-user/', views.Add_user, name='Add_user'),
    path('reject-user/<id>/', views.RejectRequestingUser.as_view(), name='reject-user'),
    path('create_program/', views.ProgramCreateView.as_view(), name='create_program'),
    # path('programs/', views.ProgramList.as_view(), name='program-list'),
    path('phase/<int:pk>/', views.ProgramPhaseDetail.as_view(), name='program-phase-detail'),
    path('programphase/<int:programphase_id>/add_routines/', views.add_routines_to_programphase, name='add_routines_to_programphase'),
     path('programphase/<int:programphase_id>/remove_routines/', views.remove_routines_from_programphase, name='remove_routines_from_programphase'),
     # Create a new subscription
    path('subscription/create/', views.SubscriptionCreateView.as_view(), name='create-subscription'),

    path('program/<int:program_id>/subscribed_users/', views.SubscribedUsersListView.as_view(), name='subscribed-users-list'),
    path('duplicate-routine/<int:routine_id>/', views.duplicate_routine, name='duplicate_routine'),
    path('createroutines/', views.createroutine, name='createroutines'),

     path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/<str:uidb64>/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('dashboard-data/', views.dashboard_data, name='dashboard_data'),
] 


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
