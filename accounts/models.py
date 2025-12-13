from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        STAFF = "staff", "Staff"
        MEMBER = "member", "Member"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.MEMBER)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Roles.ADMIN
        if self.role in {self.Roles.ADMIN, self.Roles.STAFF}:
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
