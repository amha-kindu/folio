from django.db import transaction
from rest_framework import serializers

from .models import Book, Loan


class BookSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "page_count",
            "published_date",
            "description",
            "total_copies",
            "available_copies",
            "is_active",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_available"]


class LoanSerializer(serializers.ModelSerializer):
    borrower = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Loan
        fields = [
            "id",
            "borrower",
            "book",
            "borrowed_at",
            "due_at",
            "returned_at",
        ]
        read_only_fields = ["id", "borrower", "borrowed_at"]

    def validate(self, attrs):
        book = attrs.get("book")
        user = self.context["request"].user
        if book and not book.is_available:
            raise serializers.ValidationError("Book is not available for borrowing.")
        if book and user and Loan.objects.filter(borrower=user, book=book, returned_at__isnull=True).exists():
            raise serializers.ValidationError("You already have this book borrowed.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        book = validated_data["book"]
        with transaction.atomic():
            locked_book = Book.objects.select_for_update().get(pk=book.pk)
            if not locked_book.is_available:
                raise serializers.ValidationError("Book is not available for borrowing.")
            locked_book.available_copies -= 1
            locked_book.save(update_fields=["available_copies", "updated_at"])
            loan = Loan.objects.create(borrower=user, **validated_data)
        return loan

    def update(self, instance, validated_data):
        validated_data.pop("borrower", None)
        validated_data.pop("book", None)
        was_returned = instance.returned_at is not None
        loan = super().update(instance, validated_data)
        now_returned = loan.returned_at is not None
        if not was_returned and now_returned:
            book = loan.book
            book.available_copies = min(book.total_copies, book.available_copies + 1)
            book.save(update_fields=["available_copies", "updated_at"])
        return loan
