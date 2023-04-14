#Here we store the application's data models

from django.db import models
import numpy as np
import json
from django.contrib.postgres.fields import ArrayField

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
    encoding = models.CharField(max_length=384050)
    def __str__(self):
        return self.enroll

    # def save_encoding(self, float_array):
    #     # Convert the numpy array to JSON and save to JSONField
    #     self.encoding = json.dumps(float_array)
    #     self.save()

    # def getencoding(self):
    #     # Retrieve the JSON from JSONField and convert to numpy array
    #     return np.array(json.loads(self.encoding))
    
# need to create an attendance table having Enrll no, subjects as columns


class Team(models.Model):
    name = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    image = models.ImageField(upload_to='team/')
    def __str__(self):
        return self.name