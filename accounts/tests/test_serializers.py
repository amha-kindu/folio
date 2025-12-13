import pytest
from django.contrib.auth import get_user_model

from accounts.serializers import LoginSerializer, UserRegistrationSerializer

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    def test_registration_sets_member_role_and_hashes_password(self):
        data = {
            "username": "newuser",
            "email": "user@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.role == User.Roles.MEMBER
        assert user.check_password("password123")
        assert user.email == "user@example.com"


@pytest.mark.django_db
class TestLoginSerializer:
    def test_login_serializer_returns_tokens_and_user(self, admin_factory):
        user = admin_factory(username="loginuser")
        serializer = LoginSerializer(data={"username": user.username, "password": "password123"})
        assert serializer.is_valid(), serializer.errors
        data = serializer.validated_data
        assert "access" in data and "refresh" in data
        assert data["user"]["username"] == user.username
        assert data["user"]["role"] == user.role
