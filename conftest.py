import pytest
from rest_framework.test import APIClient

from tests.factories import (
    UserFactory,
    AdminFactory,
    StaffFactory,
    BookFactory,
    LoanFactory,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory():
    return UserFactory


@pytest.fixture
def admin_factory():
    return AdminFactory


@pytest.fixture
def staff_factory():
    return StaffFactory


@pytest.fixture
def member_factory():
    return UserFactory


@pytest.fixture
def book_factory():
    return BookFactory


@pytest.fixture
def loan_factory():
    return LoanFactory
