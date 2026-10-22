from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileGetTest(APITestCase):
    """Testes de integração para GET /api/users/me/"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="perfil@teste.com",
            password="Senha@123",
            first_name="João",
            last_name="Silva",
        )
        self.url = reverse("user-profile")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_retorna_perfil_do_usuario_autenticado(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["first_name"], "João")
        self.assertEqual(response.data["last_name"], "Silva")

    def test_nao_retorna_senha(self):
        response = self.client.get(self.url)
        self.assertNotIn("password", response.data)

    def test_sem_token_retorna_401(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_guest_nao_pode_acessar_perfil(self):
        guest = User.objects.create_guest_user()
        guest_refresh = RefreshToken.for_user(guest)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {guest_refresh.access_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


class UserProfilePatchTest(APITestCase):
    """Testes de integração para PATCH /api/users/me/"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="patch@teste.com",
            password="Senha@123",
            first_name="Maria",
            last_name="Souza",
        )
        self.url = reverse("user-profile")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_atualiza_first_name(self):
        response = self.client.patch(self.url, {"first_name": "Ana"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "Ana")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Ana")

    def test_atualiza_last_name(self):
        response = self.client.patch(self.url, {"last_name": "Costa"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["last_name"], "Costa")

    def test_sem_token_retorna_401(self):
        self.client.credentials()
        response = self.client.patch(self.url, {"first_name": "Ana"}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_ignora_campos_protegidos_e_atualiza_nome(self):
        response = self.client.patch(
            self.url,
            {
                "first_name": "Ana",
                "is_staff": True,
                "is_active": False,
                "is_superuser": True,
                "password": "OutraSenha@123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Ana")
        self.assertFalse(self.user.is_staff)
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_superuser)
        self.assertTrue(self.user.check_password("Senha@123"))
        for field in ("is_staff", "is_active", "is_superuser", "password"):
            self.assertNotIn(field, response.data)

    def test_nao_pode_alterar_email(self):
        response = self.client.patch(
            self.url, {"email": "novo@email.com"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        # email deve permanecer o original (campo read_only)
        self.assertEqual(response.data["email"], self.user.email)

    def test_nao_pode_alterar_role(self):
        response = self.client.patch(
            self.url, {"role": "ADMIN"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, "PADRAO")

    def test_first_name_invalido_retorna_400(self):
        response = self.client.patch(self.url, {"first_name": "A"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Dados inválidos"})

    def test_guest_nao_pode_atualizar_perfil(self):
        guest = User.objects.create_guest_user()
        guest_refresh = RefreshToken.for_user(guest)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {guest_refresh.access_token}")
        response = self.client.patch(self.url, {"first_name": "Hack"}, format="json")
        self.assertEqual(response.status_code, 403)
