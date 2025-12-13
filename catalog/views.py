from django.utils import timezone
from rest_framework import permissions, viewsets, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdminRole, IsAdminOrStaffRole
from .pagination import BookPagination
from .filters import BookFilter
from .models import Book, Loan
from .serializers import BookSerializer, LoanSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_class = BookFilter
    pagination_class = BookPagination
    search_fields = ["title", "author", "isbn"]
    ordering_fields = ["title", "author", "created_at"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and getattr(user, "role", None) == "admin":
            return qs
        return qs.filter(is_active=True)


class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAdminOrStaffRole]
    filter_backends = [OrderingFilter]
    ordering_fields = ["borrowed_at", "due_at"]

    def get_queryset(self):
        qs = Loan.objects.select_related("book", "borrower")
        user = self.request.user
        if getattr(user, "role", None) in {"admin", "staff"}:
            return qs
        return qs.none()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        loan = self.get_object()
        if loan.returned_at:
            return Response({"detail": "Book already returned."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(loan, data={"returned_at": timezone.now()}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
