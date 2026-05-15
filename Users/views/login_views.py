from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from Users.serializers.login_serializer import Loginserializer

_MAX_ATTEMPTS = 5
_WINDOW_SECS  = 60


def _get_client_ip(request) -> str:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR', 'unknown')


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        ip  = _get_client_ip(request)
        key = f'login_rate:{ip}'

        attempts = cache.get(key, 0)
        if attempts >= _MAX_ATTEMPTS:
            return Response(
                {'error': 'Demasiados intentos. Espera 1 minuto e inténtalo de nuevo.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = Loginserializer(data=request.data)
        if serializer.is_valid():
            cache.delete(key)   # reset counter on success
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        cache.set(key, attempts + 1, timeout=_WINDOW_SECS)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
