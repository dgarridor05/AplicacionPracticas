from django.contrib import admin
from .models import Conversation, ConversationMember, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_group', 'class_group', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(ConversationMember)
class ConversationMemberAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'user', 'joined_at')
    search_fields = ('conversation__name', 'user__username')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'created_at', 'text_short')
    search_fields = ('sender__username', 'text')

    def text_short(self, obj):
        return obj.text[:60]
    text_short.short_description = 'Texto'
