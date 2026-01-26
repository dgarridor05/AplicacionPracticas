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
    
    # --- GUSTOS Y PREFERENCIAS ---
    favorite_song = models.CharField(max_length=100, blank=True, null=True)
    favorite_artist = models.CharField(max_length=100, blank=True, null=True)
    favorite_movie = models.CharField(max_length=100, blank=True, null=True)
    # Nuevo campo para el buscador de lugares
    favorite_place = models.CharField(max_length=255, blank=True, null=True, verbose_name="Lugar favorito", db_column='favorite_place')
    
    motivation = models.TextField(blank=True, null=True)

    # --- NUEVAS PREGUNTAS DE REFLEXIÓN ---
    gratitude = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="¿Por qué estás más agradecido en tu vida?"
    )
    happy_memory = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="¿Cuál es tu recuerdo más feliz?"
    )

    share_with_class = models.BooleanField(default=False)

    # --- CAMPO PARA SPOTIFY ---
    spotify_link = models.URLField(
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name="Enlace de Spotify",
        help_text="Pega aquí el enlace de la canción (Compartir > Copiar enlace de canción)"
    )

    @property
    def spotify_embed_url(self):
        """
        Lógica para transformar el enlace de compartir de Spotify 
        en un enlace de reproductor (embed).
        """
        if self.spotify_link:
            if "track/" in self.spotify_link:
                clean_url = self.spotify_link.split('?')[0]
                if "embed/" not in clean_url:
                    return clean_url.replace("track/", "embed/track/")
                return clean_url
        return None

    def __str__(self):
        return self.username