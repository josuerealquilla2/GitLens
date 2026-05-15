import re
import urllib.request
import urllib.parse
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from Users.models import CustomUser
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer

# ── Security constants ────────────────────────────────────────
_MAX_MSG_LEN  = 2000
_ALLOWED_LANGS = {'en', 'fr', 'de', 'pt', 'ca'}

# Basic profanity list (extend as needed; a library like better-profanity is better for production)
_PROFANITY = {
    'puta', 'puto', 'mierda', 'coño', 'joder', 'hostia', 'gilipollas',
    'cabron', 'cabrón', 'idiota', 'imbecil', 'imbécil', 'pendejo',
    'maricón', 'maricon', 'nazi', 'fuck', 'shit', 'bitch', 'asshole',
    'bastard', 'cunt', 'nigger', 'faggot',
}

def _contains_profanity(text: str) -> bool:
    words = re.findall(r'\w+', text.lower())
    return any(w in _PROFANITY for w in words)


# ── Chat rooms ────────────────────────────────────────────────

class ChatRoomListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = ChatRoom.objects.filter(members=request.user).order_by('-created_at')
        return Response(ChatRoomSerializer(rooms, many=True, context={'request': request}).data)

    def post(self, request):
        room_type  = request.data.get('room_type', 'private')
        member_ids = request.data.get('member_ids', [])
        name       = request.data.get('name', '')

        if room_type == 'private' and len(member_ids) == 1:
            existing = ChatRoom.objects.filter(
                room_type='private', members=request.user
            ).filter(members__id=member_ids[0])
            if existing.exists():
                return Response(ChatRoomSerializer(existing.first(), context={'request': request}).data)

        room = ChatRoom.objects.create(
            room_type=room_type,
            name=name if room_type == 'group' else '',
            created_by=request.user,
        )
        room.members.add(request.user)
        for uid in member_ids:
            try:
                room.members.add(CustomUser.objects.get(id=uid))
            except CustomUser.DoesNotExist:
                pass

        return Response(ChatRoomSerializer(room, context={'request': request}).data, status=201)


class GlobalRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        room, created = ChatRoom.objects.get_or_create(
            room_type='global',
            defaults={'name': 'Chat Global OtterHub', 'created_by': request.user},
        )
        room.members.add(request.user)
        return Response(ChatRoomSerializer(room, context={'request': request}).data)


# ── Messages ──────────────────────────────────────────────────

class ChatMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id, members=request.user)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Sala no encontrada'}, status=404)

        # Pagination: ?before=<msg_id>&limit=<n>  (default 50, max 100)
        limit  = min(int(request.query_params.get('limit', 50)), 100)
        before = request.query_params.get('before')

        msgs = room.messages.all()
        if before:
            msgs = msgs.filter(id__lt=before)
        msgs = msgs.order_by('-timestamp')[:limit]
        msgs = list(reversed(msgs))   # back to chronological order

        for msg in [m for m in msgs if m.sender != request.user]:
            msg.read_by.add(request.user)

        return Response(MessageSerializer(msgs, many=True).data)

    def post(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id, members=request.user)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Sala no encontrada'}, status=404)

        content = request.data.get('content', '').strip()
        if not content:
            return Response({'error': 'Mensaje vacío'}, status=400)

        if len(content) > _MAX_MSG_LEN:
            return Response({'error': f'El mensaje no puede superar {_MAX_MSG_LEN} caracteres.'}, status=400)

        if _contains_profanity(content):
            return Response({'error': 'El mensaje contiene lenguaje inapropiado.'}, status=400)

        msg = Message.objects.create(room=room, sender=request.user, content=content)
        return Response(MessageSerializer(msg).data, status=201)


class MessageDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id, msg_id):
        try:
            room = ChatRoom.objects.get(id=room_id, members=request.user)
            msg  = Message.objects.get(id=msg_id, room=room, sender=request.user)
            msg.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (ChatRoom.DoesNotExist, Message.DoesNotExist):
            return Response({'error': 'No encontrado'}, status=404)


class ChatRoomDeleteView(APIView):
    """El usuario abandona la sala; si queda vacía se borra."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id, members=request.user)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Sala no encontrada'}, status=404)
        room.members.remove(request.user)
        if room.members.count() == 0:
            room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClearChatView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id, members=request.user)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Sala no encontrada'}, status=404)

        # Only the room creator can clear all messages.
        # Rooms created before this check existed (created_by=null) allow any member.
        if room.created_by is not None and room.created_by != request.user:
            return Response({'error': 'Solo el creador de la sala puede vaciarla.'}, status=403)

        room.messages.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Translation proxy ─────────────────────────────────────────

class TranslateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q    = request.query_params.get('q', '').strip()
        lang = request.query_params.get('lang', 'en')

        # SSRF: strict whitelist — reject anything not in the allowed set
        if lang not in _ALLOWED_LANGS:
            return Response({'translation': q})

        if not q or lang == 'es':
            return Response({'translation': q})

        def is_real_translation(t, original):
            return bool(t) and t.strip().lower() != original.strip().lower()

        # Attempt 1: lingva.ml (Google Translate proxy, no rate limit)
        try:
            encoded = urllib.parse.quote(q, safe='')
            url = f'https://lingva.ml/api/v1/es/{lang}/{encoded}'
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (compatible; OtterHub/1.0)')
            with urllib.request.urlopen(req, timeout=7) as r:
                data = json.loads(r.read().decode())
            t = data.get('translation', '').strip()
            if is_real_translation(t, q):
                return Response({'translation': t})
        except Exception:
            pass

        # Attempt 2: MyMemory (10 000 words/day with email)
        try:
            params = urllib.parse.urlencode({
                'q': q,
                'langpair': f'es|{lang}',
                'de': 'otterhub.translate@gmail.com',
            })
            url = f'https://api.mymemory.translated.net/get?{params}'
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (compatible; OtterHub/1.0)')
            with urllib.request.urlopen(req, timeout=7) as r:
                data = json.loads(r.read().decode())
            if str(data.get('responseStatus')) == '200':
                t = data['responseData'].get('translatedText', '').strip()
                if is_real_translation(t, q):
                    return Response({'translation': t})
        except Exception:
            pass

        return Response({'translation': q})
