from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from fitness.models import AppUser


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        exclude = ['password']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = AppUser
        fields = [
            'username',
            'password',
            'birth_year',
            'height_cm',
            'experience_level',
            'goal',
            'available_equipment',
            'injuries',
        ]
        extra_kwargs = {
            'available_equipment': {'required': False},
            'injuries': {'required': False},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return AppUser.objects.create(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = UserResponseSerializer()