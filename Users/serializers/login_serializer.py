from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from Users.models import CustomUser


class Loginserializer(serializers.ModelSerializer):

    email=serializers.EmailField(max_length=100, allow_null=True, allow_blank=True, required=False)
    password=serializers.CharField(required=True, allow_blank=False, allow_null=False, min_length=5)
    class Meta:
        model = CustomUser
        fields = ('email', 'password')

    def validate_password(self, password):
        if not any(n.isdigit() for n in password):
            raise serializers.ValidationError("La contraseña es incorrecta.")
        return password

    def validate(self,attrs):
        email = attrs.get('email', )
        password = attrs.get('password', )

        _INVALID = 'Credenciales incorrectas.'

        if not email:
            raise serializers.ValidationError(_INVALID)

        user=CustomUser.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError(_INVALID)

        if not user.check_password(password):
            raise serializers.ValidationError(_INVALID)

        refresh = RefreshToken.for_user(user)
        refresh['nombre']=user.nombre
        refresh['email']=user.email

        return {
            'success': True,
            'data': {
                'id': user.id,
                'nombre': user.nombre,
                'apellidos': user.apellidos,
                'email': user.email,
                'refreshToken': str(refresh),
                'token': str(refresh.access_token),
            }
        }