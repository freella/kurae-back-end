from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.conf import settings # Importa as configurações do Django
import logging
from django_ratelimit.exceptions import Ratelimited

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Handler de exceções customizado para padronizar as respostas de erro da API.
    Captura erros de validação, banco de dados e exceções inesperadas.
    """
    # Chama o handler padrão do DRF para obter a resposta inicial
    response = exception_handler(exc, context)

    # Captura a exceção de rate limit
    if isinstance(exc, Ratelimited):
        logger.warning(f"Rate limit exceeded: {exc}")
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # Se o DRF já gerou uma resposta (ex: para APIException, ValidationError)
    if response is not None:
        # Erro de validação (400 Bad Request)
        if isinstance(exc, ValidationError):
            if settings.TESTING: # Loga de forma mais concisa durante os testes
                logger.warning(f"Validation Error (test): {exc.detail}")
            else: # Loga o traceback completo em outros ambientes
                logger.warning(f"Validation Error: {exc} - Details: {exc.detail}", exc_info=True)
            response.data = {"error": "Dados inválidos"}
            response.status_code = status.HTTP_400_BAD_REQUEST
            return response
        
        # Erros internos do servidor (5xx)
        if response.status_code >= 500:
            logger.exception(f"Internal Server Error (DRF): {exc}", exc_info=True)
            response.data = {"error": "Erro interno do servidor"}
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return response
        
        # Para outras exceções do DRF (401, 403, 404, etc.), mantemos a resposta padrão do DRF
        return response

    # Se o DRF não gerou uma resposta (ex: exceções Python genéricas, DatabaseError)
    logger.exception(f"Unhandled Exception: {exc}", exc_info=True)
    return Response(
        {"error": "Erro interno do servidor"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
