from django.urls import path

from .views import (
    OverviewView,
    BooksView,
    LoansView,
    UsersView,
    MarkLoanReturnedView,
    BookCreateView,
    BookDetailView,
    BookDeleteView,
    UserCreateView,
    UserDeleteView,
    DashboardLoginView,
    DashboardLogoutView,
    SettingsView,
)

urlpatterns = [
    path("login/", DashboardLoginView.as_view(), name="dashboard_login"),
    path("logout/", DashboardLogoutView.as_view(), name="dashboard_logout"),
    path("", OverviewView.as_view(), name="dashboard_overview"),
    path("books/", BooksView.as_view(), name="dashboard_books"),
    path("books/new/", BookCreateView.as_view(), name="dashboard_book_create"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="dashboard_book_detail"),
    path("books/<int:pk>/delete/", BookDeleteView.as_view(), name="dashboard_book_delete"),
    path("loans/", LoansView.as_view(), name="dashboard_loans"),
    path("loans/<int:pk>/return/", MarkLoanReturnedView.as_view(), name="dashboard_mark_returned"),
    path("users/", UsersView.as_view(), name="dashboard_users"),
    path("users/new/", UserCreateView.as_view(), name="dashboard_user_create"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="dashboard_user_delete"),
    path("settings/", SettingsView.as_view(), name="dashboard_settings"),
]
