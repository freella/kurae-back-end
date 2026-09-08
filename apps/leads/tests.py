from rest_framework.test import APITestCase
from django.urls import reverse

from apps.leads.models import Lead


class LeadCreateTest(APITestCase):
    """Testes de integração para POST /api/leads/"""

    def setUp(self):
        self.url = reverse('lead-create')

    def test_cria_lead_com_dados_validos(self):
        data = {'name': 'João Silva', 'email': 'joao@teste.com'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Lead registrado com sucesso')
        self.assertEqual(Lead.objects.count(), 1)

    def test_sem_name_retorna_400(self):
        data = {'email': 'joao@teste.com'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('error'), 'Dados inválidos')
        self.assertIn('name', response.data.get('details', {}))

    def test_nome_curto_retorna_400(self):
        data = {'name': 'A', 'email': 'joao@teste.com'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('error'), 'Dados inválidos')
        self.assertIn('name', response.data.get('details', {}))

    def test_sem_email_retorna_400(self):
        data = {'name': 'João Silva'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('error'), 'Dados inválidos')
        self.assertIn('email', response.data.get('details', {}))

    def test_email_invalido_retorna_400(self):
        data = {'name': 'João Silva', 'email': 'nao-e-email'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('error'), 'Dados inválidos')
        self.assertIn('email', response.data.get('details', {}))

    def test_get_nao_permitido(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
