from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.core.validators import validar_nome, validar_senha


class ValidarNomeTest(TestCase):
    def test_nome_simples_valido(self):
        resultado = validar_nome("Pedro")
        self.assertEqual(resultado, "Pedro")

    def test_nome_composto_valido(self):
        resultado = validar_nome("Pedro Silva")
        self.assertEqual(resultado, "Pedro Silva")

    def test_nome_com_maiusculas(self):
        resultado = validar_nome("MARIA")
        self.assertEqual(resultado, "MARIA")

    def test_nome_vazio(self):
        with self.assertRaises(ValidationError):
            validar_nome("")

    def test_nome_apenas_espacos(self):
        with self.assertRaises(ValidationError):
            validar_nome("   ")

    def test_nome_muito_curto(self):
        with self.assertRaises(ValidationError):
            validar_nome("A")


class SenhaValidatorTest(TestCase):
    def test_senha_forte_valida(self):
        validar_senha("Senha@123")

    def test_senha_forte_com_simbolos_diferentes(self):
        validar_senha("Teste#Senha9")

    def test_senha_forte_com_varios_numeros(self):
        validar_senha("Senha@12345")

    def test_senha_curta(self):
        with self.assertRaises(ValidationError):
            validar_senha("S@1")

    def test_senha_exatamente_8_caracteres_valida(self):
        validar_senha("Aa1@aaaa")

    def test_senha_sem_numero(self):
        with self.assertRaises(ValidationError):
            validar_senha("Senha@aaa")

    def test_senha_sem_maiuscula(self):
        with self.assertRaises(ValidationError):
            validar_senha("senha@123")

    def test_senha_sem_minuscula(self):
        with self.assertRaises(ValidationError):
            validar_senha("SENHA@123")

    def test_senha_sem_caractere_especial(self):
        with self.assertRaises(ValidationError):
            validar_senha("Senha1234")

    def test_senha_apenas_numeros(self):
        with self.assertRaises(ValidationError):
            validar_senha("12345678")

    def test_senha_apenas_letras(self):
        with self.assertRaises(ValidationError):
            validar_senha("SenhaTeste")

    def test_senha_com_espacos(self):
        with self.assertRaises(ValidationError):
            validar_senha("Senha @123")

    def test_senha_vazia(self):
        with self.assertRaises(ValidationError):
            validar_senha("")

    def test_senha_none(self):
        with self.assertRaises(TypeError):
            validar_senha(None)