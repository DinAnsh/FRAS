from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/face_recognize/', views.face_recognize, name='face_recognize'),
    path('students/', views.student, name='students'),
    path('students/get-student-data/', views.get_student_data, name='get_student_data'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('students/sort/', views.sort, name='sort'),
    path('teachers/', views.teacher, name='teachers'),
    path('classes/', views.schedule, name='classes'),
    path('cameras/', views.camera, name='cameras'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/update_profile/', views.update_profile, name='update_profile'),
]