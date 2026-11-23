from django.conf import settings
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LeadSerializer
from .services import LeadService


def get_leads_ratelimit_rate(group=None, request=None):
    if getattr(settings, 'TESTING', False):
        return None
    return getattr(settings, 'LEAD_RATELIMIT_RATE', '5/m')


def _get_client_ip(request) -> str | None:
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class LeadCreateView(APIView):
    """
    POST /api/leads/ → Captura um lead enviado pelo formulário da landing page.

    Endpoint público (AllowAny) com proteção contra spam:
    - Rate limiting por IP (django-ratelimit)
    - Honeypot silencioso (campo `website`)
    - Verificação Cloudflare Turnstile quando configurada no servidor
    """
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate=get_leads_ratelimit_rate, method='POST', block=True))
    def post(self, request):
        # Honeypot: bots preenchem campos ocultos; descarta silenciosamente sem persistir
        honeypot_value = str(request.data.get('website', '') or '').strip()
        if honeypot_value:
            return Response(
                {'message': 'Lead registrado com sucesso'},
                status=status.HTTP_201_CREATED,
            )

        serializer = LeadSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error_details = {}
            for field, err_list in e.detail.items():
                if isinstance(err_list, list) and len(err_list) > 0:
                    error_details[field] = str(err_list[0])
                else:
                    error_details[field] = str(err_list)

            return Response(
                {
                    'error': 'Dados inválidos',
                    'details': error_details,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        turnstile_token = serializer.validated_data.get('turnstile_token', '')
        if not LeadService.verify_turnstile(turnstile_token, _get_client_ip(request)):
            return Response(
                {
                    'error': 'Falha na verificação de segurança. Recarregue e tente novamente.',
                    'details': {'turnstile_token': 'Verificação antispam inválida ou expirada.'},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        LeadService.create_lead(serializer.validated_data)
        return Response({'message': 'Lead registrado com sucesso'}, status=status.HTTP_201_CREATED)
