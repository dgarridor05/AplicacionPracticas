from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class RegisterForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password1', 'password2', 'role']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'full_name', 'profile_picture', 'date_of_birth', 'gender', 'residence_area', 'celebrate_birthday',
            'nickname', 'favorite_song', 'spotify_link', 'favorite_artist', 'favorite_movie',
            'favorite_place',  # <--- AÑADIDO
            'motivation', 'gratitude', 'happy_memory', 'share_with_class'
        ]
        labels = {
            'full_name': 'Nombre completo',
            'profile_picture': 'Foto de perfil',
            'date_of_birth': 'Fecha de nacimiento',
            'gender': 'Género',
            'residence_area': '¿Dónde vives?',
            'celebrate_birthday': '¿Te gusta celebrar tu cumpleaños?',
            'nickname': '¿Cuál es tu apodo o cómo te gusta que te llamen?',
            'favorite_song': 'Nombre de tu canción favorita',
            'spotify_link': 'Enlace de la canción en Spotify',
            'favorite_artist': '¿Cuál es tu artista favorito?',
            'favorite_movie': '¿Qué película verías una y otra vez?',
            'favorite_place': '¿Cuál es tu lugar favorito en el mundo?', # <--- AÑADIDO
            'motivation': '¿Cuál es tu mayor motivación?',
            'gratitude': '¿Por qué estás más agradecido en tu vida?',
            'happy_memory': '¿Cuál es tu recuerdo más feliz?',
            'share_with_class': '¿Quieres compartir esta información con la clase?',
        }
        widgets = {
            'full_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Escribe tu nombre completo'
                }
            ),
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'Selecciona tu fecha de nacimiento'
                }
            ),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'residence_area': forms.TextInput(attrs={'class': 'form-control'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'favorite_song': forms.TextInput(attrs={'class': 'form-control'}),
            'spotify_link': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Pega el enlace de Spotify aquí'
                }
            ),
            'favorite_artist': forms.TextInput(attrs={'class': 'form-control'}),
            'favorite_movie': forms.TextInput(attrs={'class': 'form-control'}),
            'favorite_place': forms.TextInput(
                attrs={
                    'class': 'form-control', 
                    'placeholder': 'Busca un país, ciudad o monumento...'
                }
            ), # <--- AÑADIDO
            'motivation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gratitude': forms.Textarea(
                attrs={
                    'class': 'form-control', 
                    'rows': 3, 
                    'placeholder': 'Describe brevemente qué agradeces hoy...'
                }
            ),
            'happy_memory': forms.Textarea(
                attrs={
                    'class': 'form-control', 
                    'rows': 3, 
                    'placeholder': 'Cuéntanos un momento que te haga sonreír...'
                }
            ),
        }