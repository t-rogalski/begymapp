from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from fitness.models import AppUser
from .validators import (
    validate_birth_year,
    validate_height_cm,
    validate_password,
    validate_username,
    validate_weight_kg,
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    username = serializers.CharField(validators=[validate_username, UniqueValidator(
        queryset=AppUser.objects.all(), message="This username is already taken.")])
    birth_year = serializers.IntegerField(validators=[validate_birth_year])
    height_cm = serializers.IntegerField(validators=[validate_height_cm])
    weight_kg = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[validate_weight_kg],
    )

    class Meta:
        model = AppUser
        fields = [
            'id',
            'username',
            'password',
            'birth_year',
            'height_cm',
            'weight_kg',
            'experience_level',
            'goal',
            'available_equipment',
            'injuries',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        password = validated_data.pop('password')
        return AppUser.objects.create_user(
            password=password,
            **validated_data,
        )


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        self.user.last_login = timezone.now()
        self.user.save(update_fields=['last_login'])
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        try:
            self.token = RefreshToken(value)
        except TokenError:
            raise serializers.ValidationError('Invalid or expired token.')
        return value

    def save(self):
        self.token.blacklist()
