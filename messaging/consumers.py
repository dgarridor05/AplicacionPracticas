import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Conversation
from accounts.models import UserProfile


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']

        # Verificar que el usuario tiene acceso a esta conversación
        has_access = await self.check_conversation_access()
        if not has_access:
            await self.close()
            return

        # Unirse al grupo WebSocket
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Abandonar el grupo WebSocket
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()

        if not message_text:
            return

        # Guardar el mensaje en la BD
        message_obj = await self.save_message(message_text)

        # Enviar el mensaje a todos en el grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender': self.user.username,
                'sender_nickname': self.user.nickname or self.user.username,
                'sender_id': self.user.id,
                'timestamp': message_obj.created_at.strftime('%d/%m/%Y %H:%M'),
                'message_id': message_obj.id,
            }
        )

    async def chat_message(self, event):
        # Enviar mensaje a WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
            'sender_nickname': event['sender_nickname'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))

    @database_sync_to_async
    def check_conversation_access(self):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.participants.filter(id=self.user.id).exists()
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message_text):
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            text=message_text
        )
        message.read_by.add(self.user)
        return message
