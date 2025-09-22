from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User, Group
from datetime import date
from PIL import Image


phone_regex = RegexValidator(
    regex=r'^0[5-7][0-9]{8}$',
    message='Please enter a valid phone number starting with 05, 06 or 07 and has 10 digits in total'
)

class Client(models.Model):
    GENDERS =[
        ('M','Male'),
        ('F','Female')
    ]
    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ]
    user = models.OneToOneField(User, primary_key = True, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10,validators=[phone_regex])
    gender = models.CharField(max_length = 1 ,choices = GENDERS)
    address = models.CharField(max_length=50)
    policy = models.BooleanField(default = False)
    profile_pic = models.ImageField(default="default.png", upload_to="profile_pics")
    date_of_birth = models.DateField(default='2003-03-08')
    tests_made = models.PositiveIntegerField(default=0)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES,null=True,blank=True)

    
    class Meta():
        db_table = 'auth_client'
        
    def __str__(self):
        return f'{self.user.username}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        img_url = self.profile_pic.path
        img = Image.open(img_url)
        
        if img.height > 320 or img.width > 320 :
            prefered_image_size = (320,320)
            img.thumbnail(prefered_image_size)
            img.save(img_url)
            
    @property
    def age(self):
        today = date.today()
        age = today.year - self.date_of_birth.year
        
        return age
    
    