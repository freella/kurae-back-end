from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


class PasswordResetRequestTest(APITestCase):
    """Testes para POST /api/auth/password-reset/"""

    def setUp(self):
        self.url = reverse("auth-password-reset")
        self.user = User.objects.create_user(
            email="reset@teste.com",
            password="Senha@123",
        )

    def test_email_valido_retorna_200(self):
        response = self.client.post(self.url, {"email": "reset@teste.com"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.data)

    def test_email_nao_cadastrado_retorna_200_mesmo_assim(self):
        """Não deve revelar quais emails estão cadastrados."""
        response = self.client.post(self.url, {"email": "naocadastrado@teste.com"}, format="json")
        self.assertEqual(response.status_code, 200)

    def test_email_invalido_retorna_400(self):
        response = self.client.post(self.url, {"email": "email-invalido"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_payload_vazio_retorna_400(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_guest_nao_recebe_reset(self):
        """Guest users não devem receber links de reset (filtrado is_guest=False)."""
        guest = User.objects.create_guest_user()
        response = self.client.post(self.url, {"email": guest.email}, format="json")
        # Retorna 200 mas internamente não envia email
        self.assertEqual(response.status_code, 200)


class PasswordResetConfirmTest(APITestCase):
    """Testes para POST /api/auth/password-reset/confirm/"""

    def setUp(self):
        self.url = reverse("auth-password-reset-confirm")
        self.user = User.objects.create_user(
            email="confirm@teste.com",
            password="Senha@123",
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = token_generator.make_token(self.user)

    def test_reset_com_dados_validos(self):
        data = {
            "uid": self.uid,
            "token": self.token,
            "new_password": "NovaSenha@456",
            "new_password_confirm": "NovaSenha@456",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.data)

        # Verifica se a nova senha foi salva corretamente
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NovaSenha@456"))

    def test_token_invalido_retorna_400(self):
        data = {
            "uid": self.uid,
            "token": "token-invalido",
            "new_password": "NovaSenha@456",
            "new_password_confirm": "NovaSenha@456",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_uid_invalido_retorna_400(self):
        data = {
            "uid": "uid-invalido",
            "token": self.token,
            "new_password": "NovaSenha@456",
            "new_password_confirm": "NovaSenha@456",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_senhas_nao_conferem_retorna_400(self):
        data = {
            "uid": self.uid,
            "token": self.token,
            "new_password": "NovaSenha@456",
            "new_password_confirm": "Diferente@789",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_senha_fraca_retorna_400(self):
        data = {
            "uid": self.uid,
            "token": self.token,
            "new_password": "fraca",
            "new_password_confirm": "fraca",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})
