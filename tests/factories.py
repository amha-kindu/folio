import factory
from django.contrib.auth import get_user_model

from catalog.models import Book, Loan

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    role = User.Roles.MEMBER

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        pwd = extracted or "password123"
        self.set_password(pwd)
        if create:
            self.save()


class AdminFactory(UserFactory):
    role = User.Roles.ADMIN
    is_staff = True
    is_superuser = True


class StaffFactory(UserFactory):
    role = User.Roles.STAFF
    is_staff = True


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f"Book {n}")
    author = "Author"
    isbn = factory.Sequence(lambda n: f"{1000000000000 + n}")
    page_count = 100
    total_copies = 2
    available_copies = 2


class LoanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Loan

    borrower = factory.SubFactory(UserFactory)
    book = factory.SubFactory(BookFactory)
