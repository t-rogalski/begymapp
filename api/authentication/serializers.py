from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from fitness.models import AppUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
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

