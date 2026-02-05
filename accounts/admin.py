from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Usamos solo 'id' y 'role' que son campos estándar
    list_display = ('id', 'role', 'share_with_class')
    list_filter = ('role', 'share_with_class')
    # Eliminamos search_fields por ahora para evitar conflictos de nombres