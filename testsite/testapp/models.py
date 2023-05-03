#Here we store the application's data models

from django.db import models


class System_Admin(models.Model):
    dpt_name = models.CharField(max_length=50)
    hod_name = models.CharField(max_length=50)
    email = models.EmailField(primary_key=True, max_length=50)
    password = models.CharField(max_length=20)
    def __str__(self):
        return self.hod_name


class Student(models.Model):
    name = models.CharField(max_length=50)
    enroll = models.CharField(primary_key=True, max_length=20)
    img = models.ImageField(upload_to='students/')   #here media is our base dir 
    email = models.EmailField(max_length=50, default='abc@example.com')
    mobile = models.CharField(max_length=15, default='+911234567890')
    def __str__(self):
        return self.enroll
    
# need to create an attendance table having Enrll no, subjects as columns


class Team(models.Model):
    name = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    image = models.ImageField(upload_to='team/')
    def __str__(self):
        return self.name
    

class Teacher(models.Model):
    name = models.CharField(max_length=50)
    id = models.CharField(primary_key=True, max_length=20)
    email = models.EmailField(max_length=50, default='abc@example.com')
    mobile = models.CharField(max_length=15, default='+911234567890')
    subjects = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    

class Class(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=15)
    def __str__(self) -> str:
        return self.name


class Classroom(models.Model):
    room = models.CharField(max_length=5, primary_key=True)
    class_id = models.ForeignKey(Class, to_field='id',on_delete=models.CASCADE)
    def __str__(self):
        return self.room


class Subject(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=50)
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    class_id = models.ForeignKey(Class, to_field='id', on_delete=models.CASCADE)
    def __str__(self):
        return self.name


class Camera(models.Model):
    camera_ip = models.CharField(max_length=15, primary_key=True)
    class_id = models.ForeignKey(Class, to_field='id',on_delete=models.CASCADE)
    room_id = models.ForeignKey(Classroom, to_field='room',on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default='0')
    def __str__(self):
        return self.camera_ip


class Schedule(models.Model):
    day_of_week = models.CharField(max_length=10)
    class_id = models.ForeignKey(Class, to_field='id', on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.CharField(max_length=50)
    def __str__(self):
        return self.class_id.__str__()
    

class Second_Year(models.Model):
    enroll_id = models.OneToOneField(Student, to_field='enroll', on_delete=models.CASCADE)
    sub1 = models.IntegerField(default=0)
    sub2 = models.IntegerField(default=0)
    sub3 = models.IntegerField(default=0)
    sub4 = models.IntegerField(default=0)
    sub5 = models.IntegerField(default=0)
    sub6 = models.IntegerField(default=0)
    sub7 = models.IntegerField(default=0)
    sub8 = models.IntegerField(default=0)
    sub9 = models.IntegerField(default=0)
    sub10 = models.IntegerField(default=0)
    def __str__(self):
        return self.enroll_id.__str__()


class Third_Year(models.Model):
    enroll_id = models.OneToOneField(Student, to_field='enroll', on_delete=models.CASCADE)
    sub1 = models.IntegerField(default=0)
    sub2 = models.IntegerField(default=0)
    sub3 = models.IntegerField(default=0)
    sub4 = models.IntegerField(default=0)
    sub5 = models.IntegerField(default=0)
    sub6 = models.IntegerField(default=0)
    sub7 = models.IntegerField(default=0)
    sub8 = models.IntegerField(default=0)
    sub9 = models.IntegerField(default=0)
    sub10 = models.IntegerField(default=0)
    def __str__(self):
        return self.enroll_id


class Final_Year(models.Model):
    enroll_id = models.OneToOneField(Student, to_field='enroll', on_delete=models.CASCADE)
    sub1 = models.IntegerField(default=0)
    sub2 = models.IntegerField(default=0)
    sub3 = models.IntegerField(default=0)
    sub4 = models.IntegerField(default=0)
    sub5 = models.IntegerField(default=0)
    sub6 = models.IntegerField(default=0)
    sub7 = models.IntegerField(default=0)
    sub8 = models.IntegerField(default=0)
    sub9 = models.IntegerField(default=0)
    sub10 = models.IntegerField(default=0)
    def __str__(self):
        return self.enroll_id


class Sub_Tracker(models.Model):
    class_id = models.OneToOneField(Class, to_field='id', on_delete=models.CASCADE)
    sub1 = models.IntegerField(default=0)
    sub2 = models.IntegerField(default=0)
    sub3 = models.IntegerField(default=0)
    sub4 = models.IntegerField(default=0)
    sub5 = models.IntegerField(default=0)
    sub6 = models.IntegerField(default=0)
    sub7 = models.IntegerField(default=0)
    sub8 = models.IntegerField(default=0)
    sub9 = models.IntegerField(default=0)
    sub10 = models.IntegerField(default=0)
    def __str__(self):
        return self.class_id.name