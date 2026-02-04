from django.contrib.auth.base_user import BaseUserManager


class CustomUser(BaseUserManager):
    email=models.EmailField(max_length=250,unique=True)

