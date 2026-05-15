from rest_framework import serializers
from .models import ChatRoom, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_id        = serializers.IntegerField(source='sender.id',        read_only=True)
    sender_nombre    = serializers.CharField(source='sender.nombre',        read_only=True)
    sender_apellidos = serializers.CharField(source='sender.apellidos',     read_only=True)

    class Meta:
        model  = Message
        fields = ('id', 'sender_id', 'sender_nombre', 'sender_apellidos', 'content', 'timestamp')


class ChatRoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    members_info = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    class Meta:
        model  = ChatRoom
        fields = ('id', 'room_type', 'name', 'display_name',
                  'members_info', 'last_message', 'unread_count', 'created_at')

    def get_last_message(self, obj):
        msg = obj.messages.last()
        if not msg:
            return None
        return {'content': msg.content, 'timestamp': str(msg.timestamp), 'sender': msg.sender.nombre}

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.exclude(read_by=user).exclude(sender=user).count()

    def get_members_info(self, obj):
        return [{'id': m.id, 'nombre': m.nombre, 'apellidos': m.apellidos} for m in obj.members.all()]

    def get_display_name(self, obj):
        if obj.room_type == 'group':
            return obj.name or 'Grupo sin nombre'
        user = self.context['request'].user
        other = obj.members.exclude(id=user.id).first()
        return f"{other.nombre} {other.apellidos}" if other else 'Chat privado'
