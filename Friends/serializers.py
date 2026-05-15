from rest_framework import serializers
from Users.models import CustomUser
from .models import FriendRequest, Friendship


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CustomUser
        fields = ('id', 'nombre', 'apellidos', 'email')


class FriendRequestSerializer(serializers.ModelSerializer):
    sender_nombre    = serializers.CharField(source='sender.nombre',    read_only=True)
    sender_apellidos = serializers.CharField(source='sender.apellidos', read_only=True)
    sender_email     = serializers.CharField(source='sender.email',     read_only=True)
    sender_id        = serializers.IntegerField(source='sender.id',     read_only=True)

    class Meta:
        model  = FriendRequest
        fields = ('id', 'sender_id', 'sender_nombre', 'sender_apellidos',
                  'sender_email', 'receiver', 'status', 'created_at')
        read_only_fields = ('sender', 'status', 'created_at')


class FriendshipSerializer(serializers.ModelSerializer):
    friend_id        = serializers.SerializerMethodField()
    friend_nombre    = serializers.SerializerMethodField()
    friend_apellidos = serializers.SerializerMethodField()
    friend_email     = serializers.SerializerMethodField()

    class Meta:
        model  = Friendship
        fields = ('id', 'friend_id', 'friend_nombre', 'friend_apellidos', 'friend_email', 'created_at')

    def _friend(self, obj):
        user = self.context['request'].user
        return obj.user2 if obj.user1_id == user.id else obj.user1

    def get_friend_id(self, obj):        return self._friend(obj).id
    def get_friend_nombre(self, obj):    return self._friend(obj).nombre
    def get_friend_apellidos(self, obj): return self._friend(obj).apellidos
    def get_friend_email(self, obj):     return self._friend(obj).email
