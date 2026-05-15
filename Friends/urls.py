from django.urls import path
from .views import (
    UserSearchView, FriendRequestView, FriendRequestDetailView,
    FriendsListView, FriendCountView, FriendStatusView,
)

urlpatterns = [
    path('search/',            UserSearchView.as_view()),
    path('requests/',          FriendRequestView.as_view()),
    path('requests/<int:pk>/', FriendRequestDetailView.as_view()),
    path('',                   FriendsListView.as_view()),
    path('count/',             FriendCountView.as_view()),
    path('status/<int:user_id>/', FriendStatusView.as_view()),
]
