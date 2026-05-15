from rest_framework import serializers

from Users.models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    nombre=serializers.CharField(min_length=2,max_length=25,required=True,allow_blank=False,allow_null=False)
    apellidos=serializers.CharField(min_length=2,max_length=25,required=True,allow_blank=False,allow_null=False)
    email=serializers.EmailField(min_length=5,max_length=25,required=True,allow_blank=False,allow_null=False)
    password1=serializers.CharField(min_length=6, required=True,allow_blank=False,allow_null=False)
    password2=serializers.CharField(min_length=6,write_only=True,allow_blank=False,allow_null=False)

    class Meta:
        model=CustomUser
        fields=("nombre","apellidos","email","password1","password2")

    def validate_email(self,email):
        if "@" not in email:
            raise serializers.ValidationError("el email debe de tener un @ ")
        return email

    def validate_password(self,password):
        if len(password) < 6:
            raise serializers.ValidationError("la contraseña no puede ser menos de 6 caracteres")
        if not any (n.isdigit() for n in password):
            raise serializers.ValidationError("la contraseña debe de tener digitos ")
        return password
    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError("las contraseñas deben de conincidir")
        return attrs


    def create(self,validated_data):
        password = validated_data.pop("password1")
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(
            nombre=validated_data["nombre"],
            apellidos=validated_data["apellidos"],
            email=validated_data["email"],
        )
        user.set_password(password)
        user.save()
        return user





