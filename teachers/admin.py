from django.contrib import admin
from .models import ClassGroup

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    # Esto muestra columnas claras en la lista
    list_display = ('name', 'teacher', 'invite_code')
    # Esto crea un buscador por nombre de grupo o profesor
    search_fields = ('name', 'teacher__username')
    # Esto crea la herramienta de "dos columnas" para mover alumnos fácilmente
    filter_horizontal = ('students',)