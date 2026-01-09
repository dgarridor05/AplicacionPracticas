from django.urls import path
from . import views

urlpatterns = [
    path('adivina/', views.face_guess_game, name='face_guess_game'),
    path('adivina-imagen/', views.name_to_face_game, name='name_to_face_game'),
    path('adivina-gustos/', views.student_interests_game, name='student_interests_game'),
    path('adivina-tests/', views.quiz_results_game, name='quiz_results_game'),
    path('perfil-completo/', views.student_complete_profile_game, name='student_complete_profile_game'),
    path('ahorcado/', views.hangman_game, name='hangman_game'),
]