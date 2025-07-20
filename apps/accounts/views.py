# from rest_framework import generics, permissions
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import UserRegistrationSerializer, UserProfileSerializer
# from rest_framework_simplejwt.tokens import RefreshToken
# from .models import User

# class UserRegistrationView(generics.CreateAPIView):
#     """
#     POST: Register a new user and return user data with JWT tokens
#     """
#     serializer_class = UserRegistrationSerializer
#     permission_classes = [permissions.AllowAny]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()

#         # Generate tokens for the new user
#         refresh = RefreshToken.for_user(user)
#         tokens = {
#             'refresh': str(refresh),
#             'access': str(refresh.access_token)
#         }

#         response_data = {
#             'user': UserProfileSerializer(user).data,
#             'tokens': tokens
#         }

#         return Response(response_data, status=status.HTTP_201_CREATED)

# class UserProfileView(generics.RetrieveUpdateAPIView):
#     """
#     GET: View your own profile
#     PUT/PATCH: Update your own profile
#     """
#     serializer_class = UserProfileSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self):
#         return self.request.user  # Always return the logged-in user


from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserProfileSerializer, CustomTokenObtainPairSerializer
from .models import User

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

        response_data = {
            'user': UserProfileSerializer(user).data,
            'tokens': tokens
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
