from django.conf import settings
from django.db import models


class ModerationLog(models.Model):
    ACTION_CHOICES = [
        ('ban',            'Baneo'),
        ('unban',          'Desbaneo'),
        ('suspend',        'Suspensión'),
        ('verify',         'Verificación'),
        ('unverify',       'Quitar verificación'),
        ('role_change',    'Cambio de rol'),
        ('delete_comment', 'Eliminar comentario'),
        ('delete_message', 'Eliminar mensaje'),
    ]
    moderator   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name='mod_actions')
    action      = models.CharField(max_length=30, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='mod_events')
    detail      = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.moderator} → {self.action}"


class MaintenanceMode(models.Model):
    is_active    = models.BooleanField(default=False)
    message      = models.CharField(max_length=300, blank=True,
                                    default='Sitio en mantenimiento. Vuelve pronto.')
    activated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                     on_delete=models.SET_NULL)
    activated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Modo mantenimiento'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
