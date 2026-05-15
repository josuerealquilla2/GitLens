from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class FriendRequest(models.Model):
    STATUS = [
        ('pending',  'Pendiente'),
        ('accepted', 'Aceptado'),
        ('rejected', 'Rechazado'),
    ]
    sender     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status     = models.CharField(max_length=10, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"


class Friendship(models.Model):
    user1      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_as_1')
    user2      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_as_2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1} ↔ {self.user2}"
