import pytest

from catalog.filters import BookFilter


@pytest.mark.django_db
def test_book_filter_available(book_factory):
    book_factory(title="Available Book", available_copies=2, is_active=True)
    book_factory(title="Unavailable Book", available_copies=0, is_active=True)
    qs = BookFilter(data={"available": True}, queryset=book_factory._meta.model.objects.all()).qs
    titles = list(qs.values_list("title", flat=True))
    assert "Available Book" in titles
    assert "Unavailable Book" not in titles


@pytest.mark.django_db
def test_book_filter_search_and_author(book_factory):
    book_factory(title="Django Deep Dive", author="Jane Doe")
    book_factory(title="Flask Basics", author="John Smith")
    qs = BookFilter(
        data={"title": "django", "author": "jane"},
        queryset=book_factory._meta.model.objects.all(),
    ).qs
    titles = list(qs.values_list("title", flat=True))
    assert titles == ["Django Deep Dive"]
