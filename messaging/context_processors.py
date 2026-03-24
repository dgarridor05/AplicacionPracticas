from messaging.models import Conversation

def unread_messages_count(request):
    """Context processor para mostrar el contador de chats sin leer en la navegación"""
    if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'student':
        conversations = Conversation.objects.filter(participants=request.user)
        unread_chats_count = sum(1 for conv in conversations if conv.unread_count(request.user) > 0)
        return {'unread_chats_count': unread_chats_count}
    return {'unread_chats_count': 0}