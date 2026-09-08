import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    PADRAO = "PADRAO"
    ADMIN = "ADMIN"
    GUEST = "GUEST"

    USER_ROLES = (
        (PADRAO, "Padrão"),
        (ADMIN, "Admin"),
        (GUEST, "Guest"),
    )

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
    )
    first_name = models.CharField(
        max_length=30, 
        blank=True)
    last_name = models.CharField(
        max_length=30, 
        blank=True)

    role = models.CharField(
        max_length=10,
        choices=USER_ROLES,
        default=PADRAO,
    )

    is_guest = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):

        if self.is_guest:
            self.role = self.GUEST
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)

    def __str__(self):
        if self.email:
            return self.email
        return f"guest-{self.pk}"
