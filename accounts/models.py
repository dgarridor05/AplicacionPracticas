from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField

class UserProfile(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Alumno'),
        ('teacher', 'Profesor')
    )
    GENDER_CHOICES = (
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro')
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    full_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre completo")
    profile_picture = CloudinaryField('image', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    residence_area = models.CharField(max_length=100, blank=True, null=True)
    celebrate_birthday = models.BooleanField(default=True)
    learning_style = models.CharField(max_length=100, blank=True, null=True)
    emotional_reinforcement = models.CharField(max_length=100, blank=True, null=True)
    favorite_song = models.CharField(max_length=100, blank=True, null=True)
    favorite_artist = models.CharField(max_length=100, blank=True, null=True)
    favorite_movie = models.CharField(max_length=100, blank=True, null=True)
    motivation = models.TextField(blank=True, null=True)

    share_with_class = models.BooleanField(default=False)

    def __str__(self):
        return self.username