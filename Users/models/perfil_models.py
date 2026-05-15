from django.db import models
from django.conf import settings

class Profile(models.Model):
    user=models.OneToOneField( settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='profile')
    image=models.ImageField(upload_to='imagen/',blank=True,null=True)
    bio=models.TextField(blank=True)
    location=models.CharField(blank=True,max_length=120)
    website=models.URLField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f' perfil de {self.user.email} '

