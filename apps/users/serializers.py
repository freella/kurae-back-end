from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para leitura e atualização do perfil do usuário autenticado.
    Expõe campos básicos — estender conforme necessidade do projeto.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
        ]
        read_only_fields = ["id", "email", "role"]

    def validate_first_name(self, value):
        from apps.core.validators import validar_nome
        if value:
            validar_nome(value)
        return value

    def validate_last_name(self, value):
        from apps.core.validators import validar_nome
        if value:
            validar_nome(value)
        return value
