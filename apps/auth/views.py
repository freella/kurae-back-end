from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.auth.serializers import ( RegisterSerializer,PasswordResetRequestSerializer,PasswordResetConfirmSerializer,
)
from apps.auth.services import AuthService
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from apps.permissions.base import IsNotGuest
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
# botei 
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit


def get_ratelimit_rate(group=None, request=None):
    from django.conf import settings
    if getattr(settings, 'TESTING', False):
        return None
    return "10/m"


# Views de autenticação: registro, login e logout

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key="ip", rate=get_ratelimit_rate, method="POST", block=True))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        tokens = AuthService.generate_tokens_for_user(user)

        return Response(
            {
                "user_id": user.id,
                "email": user.email,
                "access": tokens["access"],
                "refresh": tokens["refresh"],
            },
            status=status.HTTP_201_CREATED,
        )
        
        
class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)




class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsNotGuest]  
    
    def post(self, request):
        refresh_token = request.data.get("refresh")
        try:
            if not refresh_token: # yapf: disable
                raise TokenError("Token de atualização não fornecido.")
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (TokenError, AttributeError, TypeError, ValueError):
            return Response(
                {"detail": "Token é invalido ou expirou."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(
            {"detail": "Logout realizado com sucesso."},
            status=status.HTTP_205_RESET_CONTENT,
        )

        
#guest view

User = get_user_model()

class GuestAuthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request):
        """Permite GET para qualquer um (público)"""
        return Response(
            {
                "message": "Endpoint de convidado",
                "info": "Use POST para criar um token de convidado",
            },
            status=status.HTTP_200_OK
        )
    
    def post(self, request):
        """Cria um novo usuário guest"""
        guest_user = User.objects.create_guest_user()
        tokens = AuthService.generate_tokens_for_user(guest_user)
        
        return Response(
            {
                "guest_id": str(guest_user.id),
                "token": tokens["access"],
                "expires_in": "3h",
            },
            status=status.HTTP_200_OK,
        )


# ──────────────────────────────────────────────
# Recuperação de Senha / slk fazer isso foi uma droga pqp
# ──────────────────────────────────────────────

password_reset_token_generator = PasswordResetTokenGenerator()


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @method_decorator(ratelimit(key="ip", rate=get_ratelimit_rate, method="POST", block=True))
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email__iexact=email, is_guest=False).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = password_reset_token_generator.make_token(user)
            reset_link = (
                f"{django_settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            )

            send_mail(
                subject="Recuperação de senha",
                message=f"Acesse o link para redefinir sua senha: {reset_link}",
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response(
            {"detail": "Se o email estiver cadastrado, você receberá as instruções."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise ValidationError({"detail": "Link inválido ou expirado."})

        token = serializer.validated_data["token"]
        if not password_reset_token_generator.check_token(user, token):
            raise ValidationError({"detail": "Link inválido ou expirado."})

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        return Response(
            {"detail": "Senha redefinida com sucesso."},
            status=status.HTTP_200_OK,
        )