from messaging.models import Conversation, Message

def unread_messages_count(request):
    """Context processor para mostrar el contador de chats sin leer en la navegación"""
    if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'student':
        # Optimización: contar conversaciones con mensajes no leídos en una sola consulta
        unread_conversations = Conversation.objects.filter(
            participants=request.user,
            messages__isnull=False
        ).exclude(
            messages__read_by=request.user
        ).distinct().count()

        return {'unread_chats_count': unread_conversations}
    return {'unread_chats_count': 0}