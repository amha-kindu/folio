import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestAuthViews:
    def setup_method(self):
        self.client = APIClient()

    def test_register_view_creates_user(self):
        url = reverse("auth_register")
        payload = {
            "username": "apiuser",
            "email": "api@example.com",
            "password": "password123",
        }
        resp = self.client.post(url, payload, format="json")
        assert resp.status_code == 201

    def test_login_view_returns_jwt(self, admin_factory):
        user = admin_factory(username="apitest")
        url = reverse("auth_login")
        resp = self.client.post(url, {"username": user.username, "password": "password123"}, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert "access" in data and "refresh" in data
        assert data["user"]["username"] == user.username
