'''import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from chatroom.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "virtual_classroom.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})
'''

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
#from django.urls import path
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from .routing import websocket_urlpatterns


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LMS.settings')  # Update with your project name

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
    AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
        )
    ),
})
