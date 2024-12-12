from knox.views import LoginView as KnoxLoginView
from django.contrib.auth import login
from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer


class RegisterView(generics.CreateAPIView):
    """
    API view for user registration.
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(KnoxLoginView):
    """
    API view for user login.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        """
        Handles user login and returns a Knox token.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super().post(request, format=None)

class LoginView(KnoxLoginView):
    """
    API view for user login.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        """
        Handles user login and returns a Knox token.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return super().post(request, format=None)