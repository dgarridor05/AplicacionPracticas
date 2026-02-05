from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Usamos campos que existen seguro en el modelo User y Profile
    list_display = ('id', 'get_username', 'role', 'share_with_class')
    list_filter = ('role', 'share_with_class')
    # Buscamos por el username del usuario relacionado
    search_fields = ('user__username',)

    # Función auxiliar para mostrar el username en la lista
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'