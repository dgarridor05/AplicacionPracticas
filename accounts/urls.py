from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('alumno/inicio/', views.student_home, name='student_home'),
    path('profesor/inicio/', views.teacher_home, name='teacher_home'),
    path('alumno/editar/', views.edit_student_profile, name='edit_student_profile'),
    path('alumno/perfil/', views.view_student_profile, name='view_student_profile'),
    path('alumno/clase/', views.public_classmates_list, name='classmates_list'),
    path('alumno/perfil-publico/<int:student_id>/', views.public_student_profile, name='public_student_profile'),
    path('perfil/', views.view_profile, name='view_profile'),
    # NUEVA RUTA
    path('alumno/unirse-clase/', views.join_group_by_code, name='join_group'),
]