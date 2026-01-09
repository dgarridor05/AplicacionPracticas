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
            'nickname', 'favorite_song', 'favorite_artist', 'favorite_movie',
            'motivation', 'share_with_class'
        ]
        labels = {
            'full_name': 'Nombre completo',
            'profile_picture': 'Foto de perfil',
            'date_of_birth': 'Fecha de nacimiento',
            'gender': 'Género',
            'residence_area': '¿Dónde vives?',
            'celebrate_birthday': '¿Te gusta celebrar tu cumpleaños?',
            'nickname': '¿Cual es tu apodo o como te gusta que te llamen?',
            'favorite_song': '¿Cúal es tu cancion favorita?',
            'favorite_artist': '¿Cúal es tu artista favorito?',
            'favorite_movie': '¿Qué pelicula verías una y otra vez?',
            'motivation': '¿Cual es tu mayor motivación?',
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
            'favorite_artist': forms.TextInput(attrs={'class': 'form-control'}),
            'favorite_movie': forms.TextInput(attrs={'class': 'form-control'}),
            'motivation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }    
