from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterTest(APITestCase):
    def setUp(self):
        self.url = reverse("auth-register")
        self.valid_data = {
            "email": "teste@teste.com",
            "first_name": "Pedro",
            "last_name": "Silva",
            "password": "Senha@123",
            "password_confirm": "Senha@123",
        }

    def test_registro_sucesso(self):
        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        self.assertTrue(User.objects.filter(email=self.valid_data["email"]).exists())

    def test_email_duplicado(self):
        User.objects.create_user(
            email=self.valid_data["email"], password="Senha@123"
        )

        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_email_invalido(self):
        data = self.valid_data.copy()
        data["email"] = "email-invalido"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_senhas_nao_conferem(self):
        data = self.valid_data.copy()
        data["password_confirm"] = "Senha@1234"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_senha_fraca(self):
        data = self.valid_data.copy()
        data["password"] = "123"
        data["password_confirm"] = "123"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_senha_nao_eh_retornada_na_resposta(self):
        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertNotIn("password", response.data)
        self.assertNotIn("password_confirm", response.data)

    def test_first_name_invalido(self):
        data = self.valid_data.copy()
        data["first_name"] = "A"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_last_name_invalido(self):
        data = self.valid_data.copy()
        data["last_name"] = "123"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_campo_email_obrigatorio(self):
        data = self.valid_data.copy()
        data.pop("email")

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_campo_password_obrigatorio(self):
        data = self.valid_data.copy()
        data.pop("password")

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})