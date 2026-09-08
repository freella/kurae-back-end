# Custom JWT tokens

from rest_framework_simplejwt.tokens import RefreshToken

class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        
        # Adiciona claims customizados automaticamente
        token['role'] = user.role
        token['is_guest'] = bool(user.is_guest)
        token['sub'] = str(user.id)
        
        return token