from django.contrib.auth.hashers import check_password
from django.core import signing
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from fitness.models import AppUser

from .serializers import (
    LoginResponseSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserResponseSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserResponseSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserResponseSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: LoginResponseSerializer},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = AppUser.objects.get(username=serializer.validated_data['username'])
        except AppUser.DoesNotExist:
            return Response(
                {'detail': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_password(serializer.validated_data['password'], user.password):
            return Response(
                {'detail': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = signing.dumps({'user_id': user.id})
        return Response({
            'token': token,
            'user': UserResponseSerializer(user).data,
        })