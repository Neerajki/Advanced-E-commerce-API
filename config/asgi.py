# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator
# from apps.orders.middleware import JWTAuthMiddleware
# import apps.orders.routing

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AllowedHostsOriginValidator(
#         JWTAuthMiddleware(
#             URLRouter(
#                 apps.orders.routing.websocket_urlpatterns
#             )
#         )
#     ),
# })





import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from apps.orders.middleware import JWTAuthMiddleware
import apps.orders.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(
                apps.orders.routing.websocket_urlpatterns
            )
        )
    ),
})
