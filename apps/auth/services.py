from rest_framework_simplejwt.tokens import RefreshToken

from apps.auth.token import CustomRefreshToken

class AuthService:
    @staticmethod
    def generate_tokens_for_user(user):
        refresh = CustomRefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
