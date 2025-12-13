import pytest


@pytest.mark.django_db
class TestBookModel:
    def test_is_available_logic(self, book_factory):
        book = book_factory(available_copies=2, is_active=True)
        assert book.is_available is True
        book.available_copies = 0
        book.save()
        assert book.is_available is False
        book.is_active = False
        book.available_copies = 1
        book.save()
        assert book.is_available is False
