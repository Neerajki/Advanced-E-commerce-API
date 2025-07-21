# # apps/accounts/urls.py
# from django.urls import path
# from .views import UserRegistrationView, UserProfileView
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# urlpatterns = [
#     path('register/', UserRegistrationView.as_view(), name='register'),
#     path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('profile/', UserProfileView.as_view(), name='profile'),
# ]

from django.urls import path
from .views import UserRegistrationView, UserProfileView, CustomTokenObtainPairView,UserDeleteView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
     path('profile/delete/', UserDeleteView.as_view(), name='delete_profile'),
]
