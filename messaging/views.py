from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from accounts.models import UserProfile
from teachers.models import ClassGroup
from .models import Conversation, ConversationMember, Message


@login_required
def conversation_list(request):
    user = request.user
    conversations = Conversation.objects.filter(participants=user).order_by('-updated_at')

    unread_chats_count = 0
    for conv in conversations:
        conv.unread_count_for_user = conv.unread_count(user)
        if conv.unread_count_for_user > 0:
            unread_chats_count += 1

        # Agregar información del otro participante para chats privados
        if not conv.is_group:
            other_participant = conv.participants.exclude(id=user.id).first()
            if other_participant:
                conv.other_username = other_participant.username
                conv.other_nickname = other_participant.nickname
                conv.other_profile_picture = other_participant.profile_picture
                conv.other_full_name = other_participant.full_name
            else:
                conv.other_username = 'Usuario desconocido'
                conv.other_nickname = None
                conv.other_profile_picture = None
                conv.other_full_name = None

    return render(request, 'messaging/conversation_list.html', {
        'conversations': conversations,
        'unread_chats_count': unread_chats_count,
    })


@login_required
def conversation_detail(request, conversation_id):
    user = request.user
    conversation = get_object_or_404(Conversation.objects.filter(participants=user), id=conversation_id)

    # Obtener todas las conversaciones para la lista lateral
    conversations = Conversation.objects.filter(participants=user).order_by('-updated_at')
    for conv in conversations:
        conv.unread_count_for_user = conv.unread_count(user)
        if not conv.is_group:
            other_participant = conv.participants.exclude(id=user.id).first()
            if other_participant:
                conv.other_username = other_participant.username
                conv.other_nickname = other_participant.nickname
                conv.other_profile_picture = other_participant.profile_picture
                conv.other_full_name = other_participant.full_name

    # Obtener información del otro participante para chats privados
    other_participant = None
    if not conversation.is_group:
        other_participant = conversation.participants.exclude(id=user.id).first()

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            message_obj = Message.objects.create(
                conversation=conversation,
                sender=user,
                text=text
            )
            message_obj.read_by.add(user)
            conversation.updated_at = message_obj.created_at
            conversation.save(update_fields=['updated_at'])
            return redirect('conversation_detail', conversation_id=conversation.id)
        messages.error(request, 'No se puede enviar un mensaje vacío.')

    chat_messages = conversation.messages.select_related('sender').all()
    for msg in chat_messages:
        if user not in msg.read_by.all():
            msg.read_by.add(user)

    return render(request, 'messaging/conversation_detail.html', {
        'conversation': conversation,
        'chat_messages': chat_messages,
        'other_participant': other_participant,
        'conversations': conversations,
    })


@login_required
def start_private_conversation(request, student_id):
    user = request.user
    if user.role != 'student':
        messages.error(request, 'Solo alumnos pueden iniciar conversaciones privadas entre alumnos.')
        return redirect('student_home')

    other = get_object_or_404(UserProfile, id=student_id, role='student')

    if other == user:
        messages.warning(request, 'No puedes iniciar un chat contigo mismo.')
        return redirect('conversation_list')

    # Verificar que compartan grupo
    shared = ClassGroup.objects.filter(students=user).filter(students=other).exists()
    if not shared:
        messages.error(request, 'Solo se puede chatear con compañeros de clase compartidos.')
        return redirect('classmates_list')

    conversation = Conversation.objects.filter(is_group=False, participants=user).filter(participants=other).first()

    if not conversation:
        conversation = Conversation.objects.create(is_group=False, name=f"Chat {user.username} & {other.username}")
        ConversationMember.objects.bulk_create([
            ConversationMember(conversation=conversation, user=user),
            ConversationMember(conversation=conversation, user=other),
        ])

    return redirect('conversation_detail', conversation_id=conversation.id)
