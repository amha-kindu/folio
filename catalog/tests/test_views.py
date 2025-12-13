import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestBookViewSet:
    def test_anonymous_can_list_books(self, book_factory):
        book_factory()
        client = APIClient()
        resp = client.get(reverse("book-list"))
        assert resp.status_code == 200

    def test_member_cannot_create_book(self, member_factory):
        client = APIClient()
        client.force_authenticate(member_factory())
        resp = client.post(
            reverse("book-list"),
            {"title": "X", "author": "Y", "isbn": "1111111111111", "page_count": 10, "total_copies": 1, "available_copies": 1},
        )
        assert resp.status_code in (401, 403)

    def test_admin_can_create_book(self, admin_factory):
        client = APIClient()
        client.force_authenticate(admin_factory())
        resp = client.post(
            reverse("book-list"),
            {"title": "X", "author": "Y", "isbn": "1111111111112", "page_count": 10, "total_copies": 1, "available_copies": 1},
        )
        assert resp.status_code == 201


@pytest.mark.django_db
class TestLoanViewSet:
    def test_admin_can_create_and_return_loan(self, admin_factory, book_factory):
        client = APIClient()
        client.force_authenticate(admin_factory())
        book = book_factory(total_copies=2, available_copies=2)

        create_resp = client.post(reverse("loan-list"), {"book": book.id})
        assert create_resp.status_code == 201
        book.refresh_from_db()
        assert book.available_copies == 1

        loan_id = create_resp.data["id"]
        return_resp = client.post(reverse("loan-return-book", args=[loan_id]))
        assert return_resp.status_code == 200
        book.refresh_from_db()
        assert book.available_copies == 2

    def test_member_cannot_create_loan(self, member_factory, book_factory):
        client = APIClient()
        client.force_authenticate(member_factory())
        book = book_factory()
        resp = client.post(reverse("loan-list"), {"book": book.id})
        assert resp.status_code in (401, 403)
