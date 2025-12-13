import pytest
from django.urls import reverse
from django.test import Client


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestDashboardAccess:
    def test_redirects_to_login_when_anonymous(self, client):
        resp = client.get(reverse("dashboard_overview"))
        assert resp.status_code == 302
        assert reverse("dashboard_login") in resp.url

    def test_forbidden_for_staff_role(self, client, staff_factory):
        client.force_login(staff_factory())
        resp = client.get(reverse("dashboard_overview"))
        assert resp.status_code == 403

    def test_admin_can_access_overview(self, client, admin_factory):
        client.force_login(admin_factory())
        resp = client.get(reverse("dashboard_overview"))
        assert resp.status_code == 200
        assert b"Overview" in resp.content

    def test_admin_can_access_books_page(self, client, admin_factory):
        client.force_login(admin_factory())
        resp = client.get(reverse("dashboard_books"))
        assert resp.status_code == 200
        assert b"Books" in resp.content

    def test_admin_can_access_settings_page(self, client, admin_factory):
        client.force_login(admin_factory())
        resp = client.get(reverse("dashboard_settings"))
        assert resp.status_code == 200
        assert b"Settings" in resp.content
