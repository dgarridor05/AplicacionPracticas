from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'share_with_class')
    list_filter = ('role', 'share_with_class')
    search_fields = ('user__username', 'nickname')