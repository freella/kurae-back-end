import json
import logging
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from django.conf import settings
from .models import Lead

logger = logging.getLogger(__name__)

TURNSTILE_VERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
HUBSPOT_CONTACTS_URL = 'https://api.hubapi.com/crm/v3/objects/contacts'


class LeadService:
    """
    Serviço com regras de negócio para o domínio de leads:
    validação antispam (Turnstile), persistência mínima e envio opcional ao HubSpot CRM.
    """

    @staticmethod
    def verify_turnstile(token: str, remote_ip: str | None = None) -> bool:
        """
        Valida o token do Cloudflare Turnstile no servidor.
        Quando TURNSTILE_SECRET_KEY não está configurada (ex.: dev local), retorna True.
        """
        secret_key = getattr(settings, 'TURNSTILE_SECRET_KEY', '')
        if not secret_key:
            return True

        if not token or not token.strip():
            return False

        payload = {
            'secret': secret_key,
            'response': token.strip(),
        }
        if remote_ip:
            payload['remoteip'] = remote_ip

        encoded_data = urllib_parse.urlencode(payload).encode('utf-8')
        req = urllib_request.Request(
            TURNSTILE_VERIFY_URL,
            data=encoded_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            method='POST',
        )

        try:
            with urllib_request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read().decode('utf-8'))
                return bool(body.get('success', False))
        except (urllib_error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            logger.warning('Falha ao validar token Turnstile: %s', exc.__class__.__name__)
            return False

    @staticmethod
    def sync_to_hubspot(lead: Lead) -> bool:
        """
        Envia apenas os dados mínimos do lead para o HubSpot CRM (coordenado com a KSS-53).
        Credenciais ficam exclusivamente no servidor (HUBSPOT_ACCESS_TOKEN ou Forms API).
        """
        access_token = getattr(settings, 'HUBSPOT_ACCESS_TOKEN', '')
        portal_id = getattr(settings, 'HUBSPOT_PORTAL_ID', '')
        form_guid = getattr(settings, 'HUBSPOT_FORM_GUID', '')

        if portal_id and form_guid:
            return LeadService._submit_hubspot_form(lead, portal_id, form_guid)

        if access_token:
            return LeadService._create_hubspot_contact(lead, access_token)

        return False

    @staticmethod
    def _create_hubspot_contact(lead: Lead, access_token: str) -> bool:
        parts = lead.name.strip().split(' ', 1)
        firstname = parts[0]
        lastname = parts[1] if len(parts) > 1 else ''

        properties = {
            'email': lead.email,
            'firstname': firstname,
            'lastname': lastname,
            'message': lead.message,
        }
        if lead.phone:
            properties['phone'] = lead.phone

        req = urllib_request.Request(
            HUBSPOT_CONTACTS_URL,
            data=json.dumps({'properties': properties}).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        try:
            with urllib_request.urlopen(req, timeout=5) as resp:
                return 200 <= resp.status < 300
        except (urllib_error.URLError, TimeoutError) as exc:
            logger.error('Erro ao sincronizar lead %s com HubSpot CRM: %s', lead.id, exc.__class__.__name__)
            return False

    @staticmethod
    def _submit_hubspot_form(lead: Lead, portal_id: str, form_guid: str) -> bool:
        parts = lead.name.strip().split(' ', 1)
        fields = [
            {'name': 'email', 'value': lead.email},
            {'name': 'firstname', 'value': parts[0]},
            {'name': 'message', 'value': lead.message},
        ]
        if len(parts) > 1:
            fields.append({'name': 'lastname', 'value': parts[1]})
        if lead.phone:
            fields.append({'name': 'phone', 'value': lead.phone})

        url = f'https://api.hsforms.com/submissions/v3/integration/submit/{portal_id}/{form_guid}'
        req = urllib_request.Request(
            url,
            data=json.dumps({'fields': fields}).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        try:
            with urllib_request.urlopen(req, timeout=5) as resp:
                return 200 <= resp.status < 300
        except (urllib_error.URLError, TimeoutError) as exc:
            logger.error('Erro ao enviar lead %s para HubSpot Forms: %s', lead.id, exc.__class__.__name__)
            return False

    @staticmethod
    def create_lead(validated_data: dict) -> Lead:
        """
        Cria e retorna um novo lead apenas com os campos mínimos persistíveis
        e dispara a sincronização com o HubSpot quando configurada.
        """
        lead_data = {
            'name': validated_data['name'],
            'email': validated_data['email'],
            'phone': validated_data.get('phone', ''),
            'message': validated_data['message'],
            'privacy_accepted': validated_data.get('privacy_accepted', False),
            'privacy_policy_version': validated_data.get('privacy_policy_version', ''),
        }
        lead = Lead.objects.create(**lead_data)
        LeadService.sync_to_hubspot(lead)
        return lead
