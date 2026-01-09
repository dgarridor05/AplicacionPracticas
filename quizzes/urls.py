from django.urls import path
from . import views

urlpatterns = [
    path('vark/', views.take_vark_quiz, name='take_vark_quiz'),
    path('vark/resultado/', views.vark_result, name='vark_result'),
    path('chapman/', views.take_chapman_quiz, name='take_chapman_quiz'),
    path('chapman/resultado/', views.chapman_result, name='chapman_result'),
]