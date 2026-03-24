from django.urls import path
from . import views

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('nuevo/<int:student_id>/', views.start_private_conversation, name='start_private_conversation'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
]