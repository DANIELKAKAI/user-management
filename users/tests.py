from django.test import TestCase

# Create your tests here.

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from users.models import User


def create_user():
    user = User.objects.create_user(
        email="dann@gail.com",
        first_name="dann",
        password="rtsgbdkue",
    )
    user.is_active = True
    user.save()
    token, _ = Token.objects.get_or_create(user=user)
    return user, token


class UserTests(APITestCase):
    def test_create_account(self):
        url = reverse("signup")
        data = {
            "email": "dan2@gmail.com",
            "first_name": "dan2",
            "password": "mylenana",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get().email, "dan2@gmail.com")

    def test_user_login(self):
        user, _ = create_user()
        url = reverse("login")
        data = {"email": "dann@gail.com", "password": "rtsgbdkue"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("token"), None)
        self.assertEqual(User.objects.get().email, "dann@gail.com")

    def test_can_create_profile(self):
        user, token = create_user()
        data = {
            "middle_name": "names",
            "last_name": "last names",
            "dob": "2022-11-11",
            "nationality": "kenya",
            "phone_number": "+254729446777",
        }
        url = reverse("profile")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("middle_name"), None)

    def test_can_create_address(self):
        user, token = create_user()
        data = {
            "country": "kenya",
            "city": "kanairo",
            "state": "kanairo",
            "zip": "99988",
        }
        url = reverse("address")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("country"), None)
