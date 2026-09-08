class UserService:
    """
    Serviço com regras de negócio para o domínio de usuários.
    """

    @staticmethod
    def update_profile(user, validated_data: dict):
        """
        Atualiza os campos de perfil do usuário com os dados validados.
        Retorna o usuário atualizado.
        """
        for field, value in validated_data.items():
            setattr(user, field, value)

        user.save(update_fields=list(validated_data.keys()))
        return user
