from unittest.mock import MagicMock, patch
from urllib import error as urllib_error

from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.leads.models import Lead
from apps.leads.services import HubSpotUnavailableError, LeadService


class LeadCreateTest(APITestCase):
    """Testes de integração para POST /api/leads/"""

    def setUp(self):
        self.url = reverse('lead-create')
        self.valid_payload = {
            'name': 'João Silva',
            'email': 'joao@teste.com',
            'phone': '(11) 98765-4321',
            'message': 'Gostaria de conversar sobre um projeto com a equipe.',
            'privacy_accepted': True,
            'privacy_policy_version': '2026-01',
        }

    def test_cria_lead_com_dados_validos(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Lead registrado com sucesso')
        self.assertEqual(Lead.objects.count(), 1)
        lead = Lead.objects.first()
        self.assertEqual(lead.phone, '11987654321')
        self.assertTrue(lead.privacy_accepted)

    def test_cria_lead_sem_telefone_opcional(self):
        payload = {**self.valid_payload}
        payload.pop('phone')
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lead.objects.first().phone, '')

    def test_sem_name_retorna_400(self):
        data = {**self.valid_payload, 'name': ''}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('error'), 'Dados inválidos')
        self.assertIn('name', response.data.get('details', {}))

    def test_nome_curto_retorna_400(self):
        data = {**self.valid_payload, 'name': 'A'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data.get('details', {}))

    def test_sem_email_retorna_400(self):
        data = {**self.valid_payload}
        data.pop('email')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data.get('details', {}))

    def test_email_invalido_retorna_400(self):
        data = {**self.valid_payload, 'email': 'nao-e-email'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data.get('details', {}))

    def test_telefone_invalido_retorna_400(self):
        data = {**self.valid_payload, 'phone': '12345'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data.get('details', {}))

    def test_mensagem_curta_retorna_400(self):
        data = {**self.valid_payload, 'message': 'Oi'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data.get('details', {}))

    def test_sem_aceite_privacidade_retorna_400(self):
        data = {**self.valid_payload, 'privacy_accepted': False}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('privacy_accepted', response.data.get('details', {}))

    def test_honeypot_preenchido_descarta_silenciosamente(self):
        data = {**self.valid_payload, 'website': 'https://spam-bot.example'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lead.objects.count(), 0)

    @override_settings(TURNSTILE_SECRET_KEY='secret-test-key')
    @patch('apps.leads.services.LeadService.verify_turnstile', return_value=False)
    def test_turnstile_invalido_retorna_400(self, _mock_verify):
        data = {**self.valid_payload, 'turnstile_token': 'invalid-token'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('turnstile_token', response.data.get('details', {}))
        self.assertEqual(Lead.objects.count(), 0)

    def test_get_nao_permitido(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch('apps.leads.services.LeadService.sync_to_hubspot', side_effect=HubSpotUnavailableError('down'))
    def test_hubspot_indisponivel_retorna_503(self, _mock_sync):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('temporariamente indisponível', response.data.get('error', ''))

    @override_settings(HUBSPOT_ACCESS_TOKEN='test-token', HUBSPOT_PORTAL_ID='', HUBSPOT_FORM_GUID='')
    @patch('apps.leads.services.urllib_request.urlopen')
    def test_hubspot_409_faz_patch_sem_duplicar(self, mock_urlopen):
        conflict = urllib_error.HTTPError(
            url='https://api.hubapi.com/crm/v3/objects/contacts',
            code=409,
            msg='Conflict',
            hdrs=None,
            fp=None,
        )
        patch_resp = MagicMock()
        patch_resp.__enter__.return_value.status = 200
        mock_urlopen.side_effect = [conflict, patch_resp]

        lead = Lead.objects.create(
            name='João Silva',
            email='joao@teste.com',
            message='Mensagem de atualização para contato existente.',
            privacy_accepted=True,
        )
        synced = LeadService.sync_to_hubspot(lead)
        self.assertTrue(synced)
        self.assertEqual(mock_urlopen.call_count, 2)
        second_req = mock_urlopen.call_args_list[1].args[0]
        self.assertEqual(second_req.get_method(), 'PATCH')
        self.assertIn('idProperty=email', second_req.full_url)


@override_settings(TESTING=False, LEAD_RATELIMIT_RATE='5/m')
class LeadRateLimitTest(APITestCase):
    """Testa limitação efetiva de envios em POST /api/leads/"""

    def setUp(self):
        window_patch = patch('django_ratelimit.core._get_window', return_value=0)
        window_patch.start()
        self.addCleanup(window_patch.stop)
        cache.clear()
        self.url = reverse('lead-create')

    def test_rate_limit_bloqueia_apos_limite(self):
        payload = {
            'name': 'Maria Souza',
            'email': 'maria@teste.com',
            'message': 'Mensagem válida para testar o limite de envios.',
            'privacy_accepted': True,
        }

        for i in range(5):
            response = self.client.post(self.url, payload, format='json')
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                f'Requisição {i} falhou: {response.status_code} {response.data}',
            )

        blocked = self.client.post(self.url, payload, format='json')
        self.assertEqual(blocked.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(
            blocked.data['error'],
            'Limite de requisições excedido. Tente novamente mais tarde.',
        )
