from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.permissions.base import IsNotGuest
from apps.users.serializers import UserProfileSerializer
from apps.users.services import UserService


class UserProfileView(APIView):
    """
    GET  /api/users/me/  → Retorna os dados do perfil do usuário autenticado.
    PATCH /api/users/me/ → Atualiza parcialmente os dados de perfil.

    Requer autenticação JWT. Usuários guest não têm acesso (IsNotGuest).
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsNotGuest]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        user = UserService.update_profile(request.user, serializer.validated_data)
        return Response(UserProfileSerializer(user).data, status=status.HTTP_200_OK)
