from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class ChatRoom(models.Model):
    ROOM_TYPES = [('private', 'Privado'), ('group', 'Grupo'), ('global', 'Global')]
    room_type  = models.CharField(max_length=10, choices=ROOM_TYPES)
    name       = models.CharField(max_length=100, blank=True, null=True)
    members    = models.ManyToManyField(User, related_name='chat_rooms')
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='owned_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Room #{self.pk}"


class Message(models.Model):
    room      = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender    = models.ForeignKey(User, on_delete=models.CASCADE)
    content   = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by   = models.ManyToManyField(User, related_name='read_messages', blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender}: {self.content[:40]}"
