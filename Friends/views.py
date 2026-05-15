from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from Users.models import CustomUser
from .models import FriendRequest, Friendship
from .serializers import UserSearchSerializer, FriendRequestSerializer, FriendshipSerializer


class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if len(q) < 2:
            return Response([])
        qs = CustomUser.objects.filter(
            Q(nombre__icontains=q) | Q(apellidos__icontains=q) | Q(email__icontains=q)
        ).exclude(id=request.user.id)[:20]
        return Response(UserSearchSerializer(qs, many=True).data)


class FriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pending = FriendRequest.objects.filter(receiver=request.user, status='pending')
        return Response(FriendRequestSerializer(pending, many=True).data)

    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        try:
            receiver = CustomUser.objects.get(id=receiver_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)

        if receiver == request.user:
            return Response({'error': 'No puedes enviarte una solicitud a ti mismo'}, status=400)

        already = Friendship.objects.filter(
            Q(user1=request.user, user2=receiver) | Q(user1=receiver, user2=request.user)
        ).exists()
        if already:
            return Response({'error': 'Ya sois amigos'}, status=400)

        req, created = FriendRequest.objects.get_or_create(
            sender=request.user, receiver=receiver, defaults={'status': 'pending'}
        )
        if not created:
            return Response({'error': 'Solicitud ya enviada'}, status=400)
        return Response(FriendRequestSerializer(req).data, status=201)


class FriendRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            req = FriendRequest.objects.get(id=pk, receiver=request.user, status='pending')
        except FriendRequest.DoesNotExist:
            return Response({'error': 'No encontrada'}, status=404)

        action = request.data.get('action')
        if action == 'accept':
            req.status = 'accepted'
            req.save()
            u1, u2 = sorted([request.user, req.sender], key=lambda u: u.id)
            Friendship.objects.get_or_create(user1=u1, user2=u2)
            return Response({'status': 'accepted'})
        elif action == 'reject':
            req.status = 'rejected'
            req.save()
            return Response({'status': 'rejected'})
        return Response({'error': 'Acción inválida'}, status=400)


class FriendsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fs = Friendship.objects.filter(Q(user1=request.user) | Q(user2=request.user))
        return Response(FriendshipSerializer(fs, many=True, context={'request': request}).data)


class FriendDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            friendship = Friendship.objects.get(
                Q(user1=request.user) | Q(user2=request.user), id=pk
            )
            friendship.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Friendship.DoesNotExist:
            return Response({'error': 'Amistad no encontrada'}, status=404)


class FriendCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count   = Friendship.objects.filter(Q(user1=request.user) | Q(user2=request.user)).count()
        pending = FriendRequest.objects.filter(receiver=request.user, status='pending').count()
        return Response({'friend_count': count, 'pending_requests': pending})


class FriendStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            other = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'status': 'not_found'})

        if Friendship.objects.filter(
            Q(user1=request.user, user2=other) | Q(user1=other, user2=request.user)
        ).exists():
            return Response({'status': 'friends'})

        sent = FriendRequest.objects.filter(sender=request.user, receiver=other, status='pending').first()
        if sent:
            return Response({'status': 'pending_sent'})

        received = FriendRequest.objects.filter(sender=other, receiver=request.user, status='pending').first()
        if received:
            return Response({'status': 'pending_received', 'request_id': received.id})

        return Response({'status': 'none'})
