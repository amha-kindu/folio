import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_default_role_member(self, user_factory):
        user = user_factory()
        assert user.role == User.Roles.MEMBER
        assert user.is_staff is False

    def test_staff_role_sets_is_staff(self, staff_factory):
        staff = staff_factory()
        assert staff.role == User.Roles.STAFF
        assert staff.is_staff is True

    def test_superuser_sets_admin_role(self):
        admin = User.objects.create_superuser(username="super", password="password123")
        assert admin.role == User.Roles.ADMIN
        assert admin.is_staff is True
        assert admin.is_superuser is True
