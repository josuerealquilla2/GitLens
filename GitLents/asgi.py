import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GitLents.settings')

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from Chat.routing import websocket_urlpatterns
from GitLents.token_auth_middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    'http':      django_asgi_app,
    'websocket': JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
})
