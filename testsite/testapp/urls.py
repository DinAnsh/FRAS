from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('students/', views.student, name='students'),
<<<<<<< HEAD
    path('students/get-student-data/', views.get_student_data, name='get_student_data'),
=======
    path('upload_image/', views.upload_image, name='upload_image'),
>>>>>>> 7d6dfd007dd500511fd13f0652dc12b7f4d7b5a3
    path('teachers/', views.teacher, name='teachers'),
    path('classes/', views.schedule, name='classes'),
    path('cameras/', views.camera, name='cameras'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/update_profile/', views.update_profile, name='update_profile'),
]