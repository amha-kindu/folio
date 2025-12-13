from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from django.db.models import Q
from django.core.paginator import Paginator

from accounts.models import User
from catalog.models import Book, Loan


class AdminRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy("dashboard_login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if getattr(request.user, "role", None) != User.Roles.ADMIN:
            return HttpResponseForbidden("You do not have access to the dashboard.")
        return super().dispatch(request, *args, **kwargs)


class OverviewView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["nav"] = "overview"
        context["query"] = self.request.GET.get("q", "")
        context.update(
            {
                "stats": {
                    "total_books": Book.objects.count(),
                    "available_books": Book.objects.filter(is_active=True, available_copies__gt=0).count(),
                    "active_loans": Loan.objects.filter(returned_at__isnull=True).count(),
                    "overdue_loans": Loan.objects.filter(returned_at__isnull=True, due_at__lt=now).count(),
                },
                "recent_loans": Loan.objects.select_related("book", "borrower")
                .order_by("-borrowed_at")[:10],
                "low_stock_books": Book.objects.filter(is_active=True, available_copies__lte=0)
                .order_by("available_copies", "title")[:10],
                "recent_books": Book.objects.filter(is_active=True).order_by("-created_at")[:6],
                "pending_staff": User.objects.filter(role=User.Roles.STAFF, is_active=False)[:6],
                "now": now,
            }
        )
        return context


class MarkLoanReturnedView(AdminRequiredMixin, View):
    def post(self, request, pk):
        loan = Loan.objects.select_related("book").get(pk=pk)
        if loan.returned_at:
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse_lazy("dashboard_overview")))
        with transaction.atomic():
            loan.returned_at = timezone.now()
            loan.save(update_fields=["returned_at"])
            book = loan.book
            book.available_copies = min(book.total_copies, book.available_copies + 1)
            book.save(update_fields=["available_copies", "updated_at"])
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse_lazy("dashboard_overview")))


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "isbn",
            "page_count",
            "published_date",
            "description",
            "total_copies",
            "available_copies",
            "is_active",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class BookDetailView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/book_detail.html"

    def get_object(self):
        pk = self.kwargs.get("pk")
        return Book.objects.select_related().get(pk=pk)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        form = BookForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy("dashboard_books"))
        context = self.get_context_data(form=form, book=instance)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = kwargs.get("book") or self.get_object()
        form = kwargs.get("form") or BookForm(instance=book)
        active_loan = (
            Loan.objects.select_related("borrower")
            .filter(book=book, returned_at__isnull=True)
            .order_by("-borrowed_at")
            .first()
        )
        context.update(
            {
                "nav": "books",
                "book": book,
                "form": form,
                "active_loan": active_loan,
            }
        )
        return context


class BookCreateView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/book_detail.html"

    def post(self, request, *args, **kwargs):
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy("dashboard_books"))
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get("form") or BookForm()
        context.update({"nav": "books", "form": form, "book": None, "active_loan": None})
        return context


class BookDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        book = Book.objects.get(pk=pk)
        book.delete()
        return HttpResponseRedirect(reverse_lazy("dashboard_books"))


class BooksView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/books.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Book.objects.all()
        search = self.request.GET.get("q", "").strip()
        availability = self.request.GET.get("availability")
        author = self.request.GET.get("author", "").strip()
        order = self.request.GET.get("order", "-created_at")

        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(author__icontains=search)
                | Q(isbn__icontains=search)
            )
        if author:
            qs = qs.filter(author__icontains=author)
        if availability == "available":
            qs = qs.filter(available_copies__gt=0, is_active=True)
        elif availability == "unavailable":
            qs = qs.filter(Q(available_copies__lte=0) | Q(is_active=False))

        if order in ["title", "author", "page_count", "-page_count", "-created_at"]:
            qs = qs.order_by(order)
        else:
            qs = qs.order_by("-created_at")

        paginator = Paginator(qs, 20)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        params = self.request.GET.copy()
        params.pop("page", True)

        context.update(
            {
                "nav": "books",
                "page_obj": page_obj,
                "books": page_obj,
                "search": search,
                "availability": availability or "",
                "author": author,
                "order": order,
                "base_query": params.urlencode(),
            }
        )
        return context


class LoansView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/loans.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Loan.objects.select_related("book", "borrower")
        status_filter = self.request.GET.get("status")
        user_q = self.request.GET.get("user", "").strip()
        book_q = self.request.GET.get("book", "").strip()
        start = self.request.GET.get("start")
        end = self.request.GET.get("end")

        if status_filter == "active":
            qs = qs.filter(returned_at__isnull=True)
        elif status_filter == "returned":
            qs = qs.filter(returned_at__isnull=False)
        elif status_filter == "overdue":
            qs = qs.filter(returned_at__isnull=True, due_at__lt=timezone.now())

        if user_q:
            qs = qs.filter(
                Q(borrower__username__icontains=user_q) | Q(borrower__email__icontains=user_q)
            )
        if book_q:
            qs = qs.filter(Q(book__title__icontains=book_q) | Q(book__isbn__icontains=book_q))
        if start:
            qs = qs.filter(borrowed_at__date__gte=start)
        if end:
            qs = qs.filter(borrowed_at__date__lte=end)

        paginator = Paginator(qs.order_by("-borrowed_at"), 20)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        params = self.request.GET.copy()
        params.pop("page", True)

        context.update(
            {
                "nav": "loans",
                "loans": page_obj,
                "page_obj": page_obj,
                "status_filter": status_filter or "",
                "user_q": user_q,
                "book_q": book_q,
                "start": start or "",
                "end": end or "",
                "now": timezone.now(),
                "base_query": params.urlencode(),
            }
        )
        return context


class UsersView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/users.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = User.objects.all()
        search = self.request.GET.get("q", "").strip()
        role = self.request.GET.get("role")
        active = self.request.GET.get("active")

        if search:
            qs = qs.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        if role:
            qs = qs.filter(role=role)
        if active == "true":
            qs = qs.filter(is_active=True)
        elif active == "false":
            qs = qs.filter(is_active=False)

        paginator = Paginator(qs.order_by("-date_joined"), 20)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        params = self.request.GET.copy()
        params.pop("page", True)

        context.update(
            {
                "nav": "users",
                "users": page_obj,
                "page_obj": page_obj,
                "search": search,
                "role": role or "",
                "active": active or "",
                "base_query": params.urlencode(),
            }
        )
        return context


class SettingsView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav"] = "settings"
        return context


class DashboardLoginView(LoginView):
    template_name = "dashboard/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("dashboard_overview")


class DashboardLogoutView(LogoutView):
    next_page = reverse_lazy("dashboard_login")


class UserForm(forms.ModelForm):
    password = forms.CharField(required=True, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class UserCreateView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/user_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get("form") or UserForm()
        context.update({"nav": "users", "form": form})
        return context

    def post(self, request, *args, **kwargs):
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy("dashboard_users"))
        return self.render_to_response(self.get_context_data(form=form))


class UserDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        # Avoid deleting self or superusers via dashboard quick action
        if user.is_superuser or user == request.user:
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse_lazy("dashboard_users")))
        user.delete()
        return HttpResponseRedirect(reverse_lazy("dashboard_users"))
