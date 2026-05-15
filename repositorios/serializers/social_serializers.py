from rest_framework import serializers
from repositorios.models import RepoComment


class ReplySerializer(serializers.ModelSerializer):
    autor = serializers.SerializerMethodField()

    class Meta:
        model = RepoComment
        fields = ['id', 'autor', 'body', 'created_at']

    def get_autor(self, obj):
        return {
            'nombre': obj.user.nombre,
            'email': obj.user.email,
        }


class RepoCommentSerializer(serializers.ModelSerializer):
    autor = serializers.SerializerMethodField()
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = RepoComment
        fields = ['id', 'autor', 'body', 'parent', 'replies', 'created_at']
        read_only_fields = ['id', 'autor', 'replies', 'created_at']

    def get_autor(self, obj):
        return {
            'nombre': obj.user.nombre,
            'email': obj.user.email,
        }
