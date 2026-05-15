from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'room_type', 'created_by', 'member_count', 'created_at')
    list_filter   = ('room_type',)
    search_fields = ('name', 'created_by__email')
    ordering      = ('-created_at',)
    filter_horizontal = ('members',)

    @admin.display(description='Miembros')
    def member_count(self, obj):
        return obj.members.count()


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ('id', 'sender', 'room', 'content_short', 'timestamp')
    list_filter   = ('room',)
    search_fields = ('sender__email', 'content')
    ordering      = ('-timestamp',)
    readonly_fields = ('sender', 'room', 'timestamp')

    @admin.display(description='Mensaje')
    def content_short(self, obj):
        return obj.content[:80]

    actions = ['delete_selected']
