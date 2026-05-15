from django.urls import path
from .views import (
    ChatRoomListView, ChatMessagesView, GlobalRoomView, TranslateView,
    MessageDeleteView, ClearChatView, ChatRoomDeleteView,
)

urlpatterns = [
    path('rooms/',                                      ChatRoomListView.as_view()),
    path('rooms/global/',                               GlobalRoomView.as_view()),
    path('rooms/<int:room_id>/',                        ChatRoomDeleteView.as_view()),
    path('rooms/<int:room_id>/messages/',               ChatMessagesView.as_view()),
    path('rooms/<int:room_id>/messages/<int:msg_id>/',  MessageDeleteView.as_view()),
    path('rooms/<int:room_id>/clear/',                  ClearChatView.as_view()),
    path('translate/',                                  TranslateView.as_view()),
]
