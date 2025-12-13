import pytest
from django.urls import reverse
from rest_framework.test import APIClient


def login(client: APIClient, username: str, password: str):
    resp = client.post(reverse("auth_login"), {"username": username, "password": password}, format="json")
    assert resp.status_code == 200
    return resp.json()["access"]


@pytest.mark.django_db
class TestAuthAndBooksFlow:
    def test_register_login_and_list_books(self, book_factory):
        client = APIClient()
        seeded_book = book_factory()
        register_resp = client.post(
            reverse("auth_register"),
            {"username": "newuser", "password": "password123", "email": "new@example.com"},
            format="json",
        )
        assert register_resp.status_code == 201

        access = login(client, "newuser", "password123")

        list_resp = client.get(reverse("book-list"))
        assert list_resp.status_code == 200
        auth_client = APIClient()
        auth_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        list_resp_auth = auth_client.get(reverse("book-list"))
        assert list_resp_auth.status_code == 200
        titles = [item.get("title") for item in list_resp_auth.data.get("results", list_resp_auth.data)]
        assert seeded_book.title in titles


@pytest.mark.django_db
class TestLoanFlowAdminOnly:
    def test_admin_can_create_and_return_loan(self, api_client, admin_factory, book_factory):
        token = login(api_client, admin_factory().username, "password123")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        book = book_factory(total_copies=2, available_copies=2)

        create_resp = api_client.post(reverse("loan-list"), {"book": book.id}, format="json")
        assert create_resp.status_code == 201
        loan_id = create_resp.data["id"]
        book.refresh_from_db()
        assert book.available_copies == 1

        return_resp = api_client.post(reverse("loan-return-book", args=[loan_id]))
        assert return_resp.status_code == 200
        book.refresh_from_db()
        assert book.available_copies == 2

    def test_member_cannot_create_loan(self, api_client, member_factory, book_factory):
        token = login(api_client, member_factory().username, "password123")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = api_client.post(reverse("loan-list"), {"book": book_factory().id}, format="json")
        assert resp.status_code in (401, 403)
