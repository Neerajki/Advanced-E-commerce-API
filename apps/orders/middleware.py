# from rest_framework_simplejwt.tokens import AccessToken
# from django.contrib.auth.models import AnonymousUser
# from django.conf import settings
# from channels.db import database_sync_to_async
# import jwt


# @database_sync_to_async
# def get_user_from_token(token):
#     try:
#         # Decode the JWT token
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#         user_id = payload.get("user_id")
#         print(f"Decoded JWT: user_id={user_id}")
#         # Fetch user from database
#         from django.contrib.auth import get_user_model
#         User = get_user_model()
#         user = User.objects.get(id=user_id)
#         print(f"User fetched: {user}")
#         return user
#     except jwt.InvalidTokenError as e:
#         print(f"Invalid JWT token: {e}")
#         return AnonymousUser()
#     except User.DoesNotExist:
#         print(f"User with id={user_id} does not exist")
#         return AnonymousUser()

# class JWTAuthMiddleware:
#     def __init__(self, app):
#         self.app = app

#     async def __call__(self, scope, receive, send):
#         print("JWTAuthMiddleware: Processing WebSocket connection")
#         # Extract token from query string
#         query_string = scope.get("query_string", b"").decode()
#         token = None
#         for param in query_string.split("&"):
#             if param.startswith("token="):
#                 token = param.split("=")[1]
#                 break

#         # Alternatively, check headers for token (e.g., Sec-WebSocket-Protocol)
#         if not token and "headers" in scope:
#             for header in scope["headers"]:
#                 if header[0].decode().lower() == "sec-websocket-protocol":
#                     token = header[1].decode()
#                     break

#         print(f"Extracted token: {token}")
#         # Authenticate user
#         if token:
#             scope["user"] = await get_user_from_token(token)
#         else:
#             print("No token provided")
#             scope["user"] = AnonymousUser()

#         print(f"User set in scope: {scope['user']}")
#         # Call the next application in the ASGI stack
#         return await self.app(scope, receive, send)




import jwt
from channels.db import database_sync_to_async

@database_sync_to_async
def get_user_from_token(token):
    try:
        from django.conf import settings
        from django.contrib.auth import get_user_model

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")

        User = get_user_model()
        user = User.objects.get(id=user_id)
        return user
    except Exception as e:
        print(f"Token decode error: {e}")
        from django.contrib.auth.models import AnonymousUser
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        token = None

        for param in query_string.split("&"):
            if param.startswith("token="):
                token = param.split("=")[1]
                break

        if not token and "headers" in scope:
            for header in scope["headers"]:
                if header[0].decode() == "authorization":
                    token = header[1].decode().split(" ")[1]  # Bearer <token>
                    break

        scope["user"] = await get_user_from_token(token) if token else AnonymousUser()
        return await self.app(scope, receive, send)
