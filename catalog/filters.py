import django_filters

from .models import Book


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    author = django_filters.CharFilter(field_name="author", lookup_expr="icontains")
    isbn = django_filters.CharFilter(field_name="isbn", lookup_expr="exact")
    available = django_filters.BooleanFilter(method="filter_available")

    class Meta:
        model = Book
        fields = ["title", "author", "isbn", "available", "is_active"]

    def filter_available(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(is_active=True, available_copies__gt=0)
        return queryset.filter(available_copies__lte=0)
