from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auth"
    label = "backend_auth"  # Label alterado para evitar conflito com django.contrib.auth