from django.db import models
from django.contrib.auth.models import User

# Create your models here.

from django.db import models

class Person(models.Model):
    CARD_TYPE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('teacher', 'Teacher'),
        ('visitor', 'Visitor'),
    )
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        
    )
    fname=models.CharField(max_length=255,null=False)
    lname=models.CharField(max_length=255)
    card_id = models.CharField(max_length=100, unique=True)
    card_type = models.CharField(max_length=10, choices=CARD_TYPE_CHOICES)

    serial_number = models.CharField(max_length=100, unique=True)
    gender=models.CharField(max_length=255,null=True)
    img=models.ImageField(upload_to='media',null=True,blank=True)
    qr_code=models.ImageField(upload_to='qrcodes',null=True,blank=True)
    city=models.CharField(max_length=255)
    phone=models.CharField(max_length=255,null=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    serial_number = models.CharField(max_length=100,null=True)
    brand=models.CharField(max_length=255,null=True)
    class Meta:
        ordering=['-updated','-created']

    def __str__(self):
        return self.fname

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='media/profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-timestamp']  


class Entry(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    card_id = models.CharField(max_length=100,null=True)
    entry_date = models.DateTimeField(auto_now_add=True)
    # Add other entry fields as needed

    def __str__(self):
        return f"{self.person.fname}'s entry on {self.entry_date}"





