from django.contrib import admin

from .models import Book, Loan


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "available_copies", "total_copies", "is_active")
    search_fields = ("title", "author", "isbn")
    list_filter = ("is_active",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("book", "borrower", "borrowed_at", "due_at", "returned_at")
    search_fields = ("book__title", "borrower__username")
    list_filter = ("returned_at",)
