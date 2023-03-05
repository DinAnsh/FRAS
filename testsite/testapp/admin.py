#We can register our models here which Django will use them with Django's admin interface. 

from django.contrib import admin
from .models import System_Admin, Student, Team

#username: admin
#password: adminhubae

admin.site.register(System_Admin)
admin.site.register(Student)
admin.site.register(Team)