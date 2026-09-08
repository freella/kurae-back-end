from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken


class GuestAuthTest(APITestCase):
    def setUp(self):
        self.guest_url = reverse("auth-guest")
        self.logout_url = reverse("auth-logout")

    def _get_guest_token(self):
        """Helper para obter token de guest"""
        response = self.client.post(self.guest_url)
        return response.data["token"]

    def test_criar_guest(self):
        """Testa criação de guest via POST"""
        response = self.client.post(self.guest_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertIn("expires_in", response.data)

    def test_token_guest_eh_valido(self):
        """Verifica se o token contém os claims corretos"""
        token = self._get_guest_token()
        access = AccessToken(token)

        self.assertTrue(access)
        self.assertTrue(access.get("is_guest"))
        self.assertEqual(access.get("role"), "GUEST")
        self.assertIsNotNone(access.get("sub"))

    def test_token_guest_tem_expiracao(self):
        """Verifica se o token tem expiração"""
        token = self._get_guest_token()
        access = AccessToken(token)
        self.assertIsNotNone(access.get("exp"))

    def test_guest_pode_fazer_get_em_endpoint_publico(self):
        """Guest pode fazer GET no endpoint guest (público)"""
        token = self._get_guest_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.guest_url)
        self.assertEqual(response.status_code, 200)

    def test_guest_nao_pode_fazer_post_em_endpoint_protegido(self):
        """Guest não pode fazer POST em logout (protegido com IsNotGuest)"""
        token = self._get_guest_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post(self.logout_url, {})
        # IsNotGuest retorna 403 Forbidden porque guest está autenticado mas sem permissão
        self.assertEqual(response.status_code, 403)

    def test_token_guest_invalido(self):
        """Token inválido retorna 401"""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer token_falso")

        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 401)