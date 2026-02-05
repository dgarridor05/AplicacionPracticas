from django.contrib import admin
from .models import ClassGroup

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'invite_code', 'get_student_count')
    search_fields = ('name', 'teacher__user__username')
    filter_horizontal = ('students',)
    
    # Para ver cuántos alumnos hay sin entrar al grupo
    def get_student_count(self, obj):
        return obj.students.count()
    get_student_count.short_description = 'Nº Alumnos'