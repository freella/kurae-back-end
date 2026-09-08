from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class LogoutTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="logout@teste.com", password="Senha@123"
        )
        self.url = reverse("auth-logout")

    def test_logout_sucesso(self):
        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.post(
            self.url, {"refresh": str(refresh)}, format="json"
        )

        self.assertEqual(response.status_code, 205)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Logout realizado com sucesso.")

    def test_logout_sem_token_de_acesso(self):
        response = self.client.post(
            self.url, {"refresh": "qualquer_token"}, format="json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_logout_com_access_token_invalido(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer token_invalido")

        response = self.client.post(
            self.url, {"refresh": "qualquer_token"}, format="json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_logout_sem_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Token é invalido ou expirou.")

    def test_logout_refresh_token_invalido(self):
        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.post(
            self.url, {"refresh": "refresh_invalido"}, format="json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Token é invalido ou expirou.")

    def test_logout_refresh_token_ja_blacklistado(self):
        refresh = RefreshToken.for_user(self.user)
        refresh.blacklist()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.post(
            self.url, {"refresh": str(refresh)}, format="json"
        )

        self.assertEqual(response.status_code, 401)

    def test_logout_nao_permite_get(self):
        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)