from django.contrib.auth.models import BaseUserManager
import uuid


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")

        return self.create_user(email, password, **extra_fields)

    def create_guest_user(self):
        email = f"guest-{uuid.uuid4()}@guest.local"

        user = self.model(
            email=email,
            role="GUEST",
            is_guest=True,
            is_active=True,
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user