from django.urls import path
from . import views
from .views import edit_group
from .views import delete_group
from .views import student_detail

urlpatterns = [
    path('crear/', views.create_group, name='create_group'),
    path('mis-grupos/', views.view_groups, name='view_groups'),
    path('grupo/<int:group_id>/', views.group_detail, name='group_detail'),
    path('grupo/<int:group_id>/estadisticas/', views.group_statistics, name='group_statistics'),
    path('grupo/<int:group_id>/editar/', edit_group, name='edit_group'),
    path('grupo/<int:group_id>/eliminar/', delete_group, name='delete_group'),
    path('alumno/<int:student_id>/', student_detail, name='student_detail'),
]