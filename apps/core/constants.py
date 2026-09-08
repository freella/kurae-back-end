class UserRoles:
    ADMIN = "ADMIN"
    GUEST = "GUEST"
    MANAGER = "MANAGER"

    CHOICES = [
        (ADMIN, "Admin"),
        (GUEST, "Guest"),
        (MANAGER, "Manager"),
    ]