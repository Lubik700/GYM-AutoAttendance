
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("home/",views.home, name="home"),
    #  path('login/', auth_views.LoginView.as_view(template_name='app/login.html'), name='login'),
     path('password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='app/password_reset.html'
        ),
        name='password_reset',
    ),
   path('register/', views.register_view, name='register'),
path('register/success/', views.registration_success_view, name='registration_success'),
path('', views.login_view, name='login'),
    path('notices/', views.notices_view, name='notices'),
path('membership/', views.membership_view, name='membership'),
path('equipment/', views.equipment_view, name='equipment'),
path('trainers/', views.trainers_view, name='trainers'),
path('feedback/', views.feedback_view, name='feedback'),
path('profile/', views.profile_view, name='profile'),
path('settings/', views.settings_view, name='settings'),
path('logout/',views.logout_view, name='logout'),
path('notice_create/',views.logout_view, name='notice_create'),

path('workout-plan/', views.workout_plan_view, name='workout_plan'),
path('workout-plan/suggest/', views.suggest_workout_plan, name='suggest_workout_plan'),
path('workout-plan/day/add/<str:day_key>/', views.add_workout_day, name='add_workout_day'),
path('workout-plan/day/<int:day_id>/edit/', views.edit_workout_day, name='edit_workout_day'),
path('workout-plan/day/<int:day_id>/delete/', views.delete_workout_day, name='delete_workout_day'),
path('workout-plan/day/<int:day_id>/exercise/add/', views.add_exercise, name='add_exercise'),
path('workout-plan/exercise/<int:exercise_id>/delete/', views.delete_exercise, name='delete_exercise'),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)