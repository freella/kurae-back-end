from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class LoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="login@teste.com", password="Senha@123"
        )
        self.url = reverse("token_obtain_pair")

    def test_login_sucesso(self):
        data = {"email": "login@teste.com", "password": "Senha@123"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_retorna_tokens_validos(self):
        data = {"email": "login@teste.com", "password": "Senha@123"}

        response = self.client.post(self.url, data, format="json")

        self.assertIsInstance(response.data["access"], str)
        self.assertIsInstance(response.data["refresh"], str)
        self.assertGreater(len(response.data["access"]), 50)

    def test_login_senha_incorreta(self):
        data = {"email": "login@teste.com", "password": "errada"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_login_email_inexistente(self):
        data = {"email": "naoexiste@teste.com", "password": "Senha@123"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_login_sem_email(self):
        data = {"password": "Senha@123"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_login_sem_senha(self):
        data = {"email": "login@teste.com"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_login_payload_vazio(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_login_metodo_get_nao_permitido(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)