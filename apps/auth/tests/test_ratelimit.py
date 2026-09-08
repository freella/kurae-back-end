from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.test import override_settings

from django.core.cache import cache

@override_settings(TESTING=False) # Temporariamente define TESTING como False para ativar o rate limiting

class RateLimitTest(APITestCase):
    """
    Testa a funcionalidade de Rate Limiting nos endpoints públicos.
    """
    def setUp(self):
      cache.clear() # Limpa o cache antes de cada teste para resetar o contador de rate limit
      # get_ratelimit_rate agora retornará "10/m" porque TESTING é False para esta classe de teste

    def test_rate_limit_no_endpoint_de_registro(self):
        """
        Verifica se o endpoint de registro bloqueia após exceder o limite de requisições.
        """
        url = reverse("auth-register")
        base_data = {
            "password": "StrongPassword@123",
            "password_confirm": "StrongPassword@123", # Adicionado para validação
            "first_name": "Test",
            "last_name": "User",
        }

        # Faz 10 requisições que devem ser bem-sucedidas
        for i in range(10):
            data = {**base_data, "email": f"test{i}@test.com"}
            response = self.client.post(url, data, format="json")
            # Espera 201 Created para registro bem-sucedido
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"Requisição {i} falhou com {response.status_code}: {response.data}")

        # A 11ª requisição deve ser bloqueada com status 429
        data = {**base_data, "email": "test10@test.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.data["error"], "Limite de requisições excedido. Tente novamente mais tarde.")

    def test_rate_limit_no_endpoint_de_password_reset(self):
        """
        Verifica se o endpoint de password-reset bloqueia após exceder o limite.
        """
        url = reverse("auth-password-reset")

        # Faz 10 requisições que devem ser bem-sucedidas
        for i in range(10):
            response = self.client.post(url, {"email": f"user{i}@test.com"}, format="json")
            # A resposta deve ser 200, não 429
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # A 11ª requisição deve ser bloqueada com status 429
        response = self.client.post(url, {"email": "user10@test.com"})
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.data["error"], "Limite de requisições excedido. Tente novamente mais tarde.")