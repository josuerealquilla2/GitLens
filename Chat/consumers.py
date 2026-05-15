import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id    = self.scope['url_route']['kwargs']['room_id']
        self.room_group = f'chat_{self.room_id}'
        user = self.scope.get('user')

        if not user or not user.is_authenticated:
            await self.close()
            return

        if not await self.check_membership(user, self.room_id):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data    = json.loads(text_data)
        content = data.get('message', '').strip()
        if not content:
            return

        user = self.scope['user']
        msg  = await self.save_message(user, self.room_id, content)

        await self.channel_layer.group_send(
            self.room_group,
            {
                'type':             'chat_message',
                'message':          content,
                'sender_id':        user.id,
                'sender_nombre':    user.nombre,
                'sender_apellidos': user.apellidos,
                'message_id':       msg.id,
                'timestamp':        str(msg.timestamp),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def check_membership(self, user, room_id):
        from Chat.models import ChatRoom
        return ChatRoom.objects.filter(id=room_id, members=user).exists()

    @database_sync_to_async
    def save_message(self, user, room_id, content):
        from Chat.models import ChatRoom, Message
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(room=room, sender=user, content=content)
