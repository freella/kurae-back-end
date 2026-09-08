from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    GuestAuthView,
    LoginView,
    LogoutView,
    RegisterView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("guest/", GuestAuthView.as_view(), name="auth-guest"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="auth-password-reset"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="auth-password-reset-confirm"),
]