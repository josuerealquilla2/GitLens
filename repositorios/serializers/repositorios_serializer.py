from rest_framework import serializers

class RepoFilterSerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True)
    language = serializers.CharField(required=False, allow_blank=True)
    stars = serializers.IntegerField(required=False)  # 🔥 ahora opcional
    page = serializers.IntegerField(required=False, default=1)

    #  VALIDACIÓN PERSONALIZADA
    def validate_stars(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El número de estrellas debe ser mayor que 0"
            )
        return value

    def validate(self, data):
        if data.get('language') and data.get('q'):
            return data  # ok

        if not data.get('stars'):
            raise serializers.ValidationError({
                "stars": "Debes ingresar estrellas"
            })

        return data