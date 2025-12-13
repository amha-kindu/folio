from django.conf import settings
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    page_count = models.PositiveIntegerField()
    published_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title", "author"]

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"

    @property
    def is_available(self) -> bool:
        return self.is_active and self.available_copies > 0


class Loan(models.Model):
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loans",
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="loans")
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-borrowed_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["borrower", "book"],
                condition=models.Q(returned_at__isnull=True),
                name="unique_active_loan_per_user_book",
            )
        ]

    def __str__(self) -> str:
        return f"{self.borrower} -> {self.book}"
