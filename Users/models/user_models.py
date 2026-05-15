from django.db import models
from django.contrib.auth.models import BaseUserManager,PermissionsMixin, AbstractBaseUser


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('el usuario debe de tener un correo')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        from Users.models.perfil_models import Profile
        Profile.objects.get_or_create(user=user)
        return user


    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


ROLE_CHOICES = [
    ('user',      'Usuario'),
    ('vip',       'VIP'),
    ('moderator', 'Moderador'),
]

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email       = models.EmailField(max_length=50, unique=True, blank=False)
    nombre      = models.CharField(max_length=25, blank=False, null=False)
    apellidos   = models.CharField(max_length=25, blank=False, null=False)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    role        = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    date_joined = models.DateTimeField(auto_now_add=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellidos']

    def __str__(self):
        return f"{self.email}"





