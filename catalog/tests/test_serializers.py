import pytest

from catalog.serializers import BookSerializer, LoanSerializer


@pytest.mark.django_db
class TestBookSerializer:
    def test_book_serializer_fields(self, book_factory):
        book = book_factory()
        data = BookSerializer(book).data
        assert data["title"] == book.title
        assert data["is_available"] is True


@pytest.mark.django_db
class TestLoanSerializer:
    def test_create_decrements_available_and_prevents_duplicate_active(self, member_factory, book_factory, rf):
        book = book_factory(total_copies=2, available_copies=2)
        request = rf.post("/api/loans/")
        request.user = member_factory()
        serializer = LoanSerializer(data={"book": book.id}, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        loan = serializer.save()
        book.refresh_from_db()
        assert loan.borrower == request.user
        assert book.available_copies == 1

        serializer2 = LoanSerializer(data={"book": book.id}, context={"request": request})
        assert serializer2.is_valid() is False

    def test_return_updates_available_copies(self, member_factory, book_factory, rf):
        book = book_factory(total_copies=2, available_copies=2)
        request = rf.post("/api/loans/")
        request.user = member_factory()

        loan_serializer = LoanSerializer(data={"book": book.id}, context={"request": request})
        loan_serializer.is_valid(raise_exception=True)
        loan = loan_serializer.save()
        book.refresh_from_db()
        assert book.available_copies == 1

        update_serializer = LoanSerializer(
            instance=loan,
            data={"returned_at": loan.borrowed_at},
            partial=True,
            context={"request": request},
        )
        assert update_serializer.is_valid(), update_serializer.errors
        update_serializer.save()
        book.refresh_from_db()
        assert book.available_copies == 2
