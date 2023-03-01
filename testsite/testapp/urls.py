from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    # path('dashboard/edit_student/<table>', views.edit_student, name='edit_student'),
    # path('dashboard/remove_student', views.remove_student, name='remove_student'),
]