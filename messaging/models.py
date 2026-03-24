from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import UserProfile
from teachers.models import ClassGroup


class Conversation(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    participants = models.ManyToManyField(
        UserProfile,
        through='ConversationMember',
        related_name='conversations'
    )
    class_group = models.ForeignKey(
        ClassGroup,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            return self.name
        members = list(self.participants.values_list('username', flat=True))
        return f"Chat: {', '.join(members)}"

    def clean(self):
        if self.class_group and not self.is_group:
            raise ValidationError('Una conversación de grupo debe marcar is_group=True.')

    def unread_count(self, user):
        return self.messages.exclude(read_by=user).count()


class ConversationMember(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='conversation_memberships'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('conversation', 'user')

    def __str__(self):
        return f"{self.user} en {self.conversation}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(
        UserProfile,
        related_name='read_messages',
        blank=True
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.text[:50]}{'...' if len(self.text) > 50 else ''}"
