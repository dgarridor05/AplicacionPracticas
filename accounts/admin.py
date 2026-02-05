from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Fusionado: ID y Role (seguridad) + Username, Full Name y Nickname (nombres)
    list_display = ('id', 'username', 'full_name', 'nickname', 'role', 'share_with_class')
    
    # Filtros laterales
    list_filter = ('role', 'share_with_class')
    
    # Buscador habilitado (ahora que sabemos los nombres exactos de los campos)
    search_fields = ('username', 'full_name', 'nickname')
    
    # Ordenar por ID descendente para ver los últimos registros arriba
    ordering = ('-id',)