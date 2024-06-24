from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Students(models.Model):
    fname=models.CharField(max_length=255,null=False)
    lname=models.CharField(max_length=255)
    postion=models.CharField(max_length=255)
    gender=models.CharField(max_length=255,null=True)
    img=models.TextField(max_length=500, blank=True, null=True)
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
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Entry(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    
    entry_date = models.DateTimeField(auto_now_add=True)
    # Add other entry fields as needed

    def __str__(self):
        return f"{self.student.name}'s entry on {self.entry_date}"




