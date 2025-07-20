# from rest_framework import serializers
# from rest_framework_simplejwt.tokens import RefreshToken
# from .models import User

# class UserRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)
#     access = serializers.CharField(read_only=True)
#     refresh = serializers.CharField(read_only=True)

#     class Meta:
#         model = User
#         fields = ('id', 'username', 'email', 'password', 'phone', 'address', 'access', 'refresh')
#         extra_kwargs = {
#             'username': {'required': True},
#             'email': {'required': True}
#         }

#     def validate_email(self, value):
#         """
#         Ensure email is unique (case-insensitive)
#         """
#         value = value.lower()
#         if User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("A user with this email already exists.")
#         return value

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()

#         # Generate JWT tokens
#         refresh = RefreshToken.for_user(user)
#         user.access = str(refresh.access_token)
#         user.refresh = str(refresh)

#         return user

# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'email', 'phone', 'address')
#         read_only_fields = ('id', 'email')  # Email cannot be updated, but username can


from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'phone', 'address', 'access', 'refresh')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        user.access = str(refresh.access_token)
        user.refresh = str(refresh)

        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'address')
        read_only_fields = ('id', 'email')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extend the JWT login serializer to include user data in the response
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email
        }
        return data
