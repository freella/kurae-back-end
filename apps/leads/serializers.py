import re
from django.conf import settings
from rest_framework import serializers
from .models import Lead


PHONE_DIGITS_RE = re.compile(r'\D+')


class LeadSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de leads com validação de coleta mínima,
    telefone opcional (BR), mensagem obrigatória e ciência/aceite de privacidade.
    Campos de proteção antispam (website, turnstile_token) são write_only e não são persistidos.
    """
    name = serializers.CharField(
        min_length=2,
        max_length=120,
        trim_whitespace=True,
        error_messages={
            'blank': 'O nome é obrigatório.',
            'required': 'O nome é obrigatório.',
            'min_length': 'O nome deve ter pelo menos 2 caracteres.',
            'max_length': 'O nome deve ter no máximo 120 caracteres.',
        },
    )
    email = serializers.EmailField(
        max_length=255,
        error_messages={
            'blank': 'O e-mail é obrigatório.',
            'required': 'O e-mail é obrigatório.',
            'invalid': 'Digite um e-mail válido.',
        },
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20,
        default='',
    )
    message = serializers.CharField(
        min_length=10,
        max_length=2000,
        trim_whitespace=True,
        error_messages={
            'blank': 'A mensagem é obrigatória.',
            'required': 'A mensagem é obrigatória.',
            'min_length': 'A mensagem deve ter pelo menos 10 caracteres.',
            'max_length': 'A mensagem deve ter no máximo 2000 caracteres.',
        },
    )
    privacy_accepted = serializers.BooleanField(required=False, default=False)
    privacy_policy_version = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=32,
        default='',
    )
    # Campos antispam (não persistidos no modelo)
    website = serializers.CharField(required=False, allow_blank=True, write_only=True, default='')
    turnstile_token = serializers.CharField(required=False, allow_blank=True, write_only=True, default='')

    class Meta:
        model = Lead
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'message',
            'privacy_accepted',
            'privacy_policy_version',
            'website',
            'turnstile_token',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_phone(self, value: str) -> str:
        if not value or not value.strip():
            return ''
        digits = PHONE_DIGITS_RE.sub('', value)
        if len(digits) not in (10, 11):
            raise serializers.ValidationError('Digite um telefone válido com DDD (10 ou 11 dígitos).')
        return digits

    def validate_privacy_accepted(self, value: bool) -> bool:
        if getattr(settings, 'LEAD_PRIVACY_CONSENT_REQUIRED', True) and not value:
            raise serializers.ValidationError(
                'É necessário confirmar a ciência da Política de Privacidade para enviar o formulário.'
            )
        return value
