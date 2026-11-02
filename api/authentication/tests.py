from django.contrib.auth.hashers import identify_hasher
from rest_framework import status
from rest_framework.test import APITestCase

from fitness.models import AppUser


class AuthEndpointTests(APITestCase):
    register_url = '/api/auth/register/'
    login_url = '/api/auth/login/'

    def register_user(self):
        return self.client.post(self.register_url, {
            'username': 'jan',
            'password': 'bezpieczne-haslo',
            'birth_year': 1990,
            'height_cm': 180,
            'experience_level': 'beginner',
            'goal': 'strength',
        }, format='json')

    def test_register_hashes_password_with_argon2(self):
        response = self.register_user()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = AppUser.objects.get(username='jan')
        self.assertNotEqual(user.password, 'bezpieczne-haslo')
        self.assertEqual(identify_hasher(user.password).algorithm, 'argon2')

    def test_login_returns_token_for_valid_password(self):
        self.register_user()

        response = self.client.post(self.login_url, {
            'username': 'jan',
            'password': 'bezpieczne-haslo',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['token'])

    def test_login_rejects_invalid_password(self):
        self.register_user()

        response = self.client.post(self.login_url, {
            'username': 'jan',
            'password': 'bledne-haslo',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)