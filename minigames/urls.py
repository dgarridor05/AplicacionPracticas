from django.urls import path
from . import views

urlpatterns = [
    # 1. Ahorcado (Hangman)
    path('ahorcado/', views.hangman_game, name='hangman_game'),
    path('ahorcado/<int:group_id>/', views.hangman_game, name='hangman_game'),

    # 2. Adivina quién es (Face Guess - Foto a Nombre)
    path('adivina/', views.face_guess_game, name='face_guess_game'),
    path('adivina/<int:group_id>/', views.face_guess_game, name='face_guess_game'),

    # 3. Adivina imagen (Name to Face - Nombre a Foto)
    path('adivina-imagen/', views.name_to_face_game, name='name_to_face_game'),
    path('adivina-imagen/<int:group_id>/', views.name_to_face_game, name='name_to_face_game'),

    # 4. Adivina Gustos (Intereses personales)
    path('adivina-gustos/', views.student_interests_game, name='student_interests_game'),
    path('adivina-gustos/<int:group_id>/', views.student_interests_game, name='student_interests_game'),

    # 5. Adivina Tests (Resultados de cuestionarios)
    path('adivina-tests/', views.quiz_results_game, name='quiz_results_game'),
    path('adivina-tests/<int:group_id>/', views.quiz_results_game, name='quiz_results_game'),

    # 6. Perfil Completo (El desafío total)
    path('perfil-completo/', views.student_complete_profile_game, name='student_complete_profile_game'),
    path('perfil-completo/<int:group_id>/', views.student_complete_profile_game, name='student_complete_profile_game'),

    # 7. NUEVO: Spotify Mystery (Adivina la canción)
    path('spotify/', views.spotify_guess_game, name='spotify_guess_game'),
    path('spotify/<int:group_id>/', views.spotify_guess_game, name='spotify_guess_game'),

    # 8. Dino-Reto (Juego de habilidad)
    path('dino-reto/', views.dino_game, name='dino_game'),

    # 9. El Impostor (Juego de deducción social)
    path('impostor/', views.impostor_game, name='impostor_game'),
    path('impostor/<int:group_id>/', views.impostor_game, name='impostor_game'),

    # 10. Charadas (Adivina la palabra en la frente)
    path('charadas/', views.charadas_game, name='charadas_game'),
    path('charadas/<int:group_id>/', views.charadas_game, name='charadas_game'),
]