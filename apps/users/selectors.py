from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_by_id(user_id):
    """
    Retorna o usuário pelo ID ou None se não encontrado.
    """
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


def get_user_by_email(email: str):
    """
    Retorna o usuário pelo email (case-insensitive) ou None.
    """
    try:
        return User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return None
