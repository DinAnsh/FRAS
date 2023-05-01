#We can register our models here which Django will use them with Django's admin interface. 

from django.contrib import admin
from .models import *

#username: admin
#password: adminhubae

admin.site.register(System_Admin)
admin.site.register(Student)
admin.site.register(Team)
admin.site.register(Teacher)
admin.site.register(Classroom)
admin.site.register(Subject)
admin.site.register(Class)
admin.site.register(Camera)
admin.site.register(Schedule)
admin.site.register(Second_Year)
admin.site.register(Third_Year)
admin.site.register(Final_Year)