import re
import unicodedata
from pathlib import Path

from django.conf import settings
from rest_framework.exceptions import ValidationError




def normalizar_nome(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z]", "", texto)
    return texto.lower()


def normalizar_senha(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    return texto.lower()





def validar_nome(nome: str) -> str:
    if not nome or len(nome.strip()) < 2:
        raise ValidationError("Nome inválido.")

    if not re.match(r"^[A-Za-zÀ-ÿ\s'\-]+$", nome):
        raise ValidationError("O nome deve conter apenas letras.")

    nome_normalizado = normalizar_nome(nome)

    if len(nome_normalizado) < 2:
        raise ValidationError("Nome inválido.")



    return nome

def validar_senha(senha: str | None) -> None:

    if senha is None:
        raise TypeError("Senha não pode ser None.")

  
    if not isinstance(senha, str):
        raise TypeError("Senha inválida.")

  
    if senha == "":
        raise ValidationError("A senha não pode ser vazia.")

    if len(senha) < 8:
        raise ValidationError("A senha deve ter pelo menos 8 caracteres.")

    if " " in senha:
        raise ValidationError("A senha não pode conter espaços.")

    if not re.search(r"[A-Z]", senha):
        raise ValidationError("A senha deve conter pelo menos uma letra maiúscula.")

    if not re.search(r"[a-z]", senha):
        raise ValidationError("A senha deve conter pelo menos uma letra minúscula.")

    if not re.search(r"\d", senha):
        raise ValidationError("A senha deve conter pelo menos um número.")

    if not re.search(r"[^A-Za-z0-9]", senha):
        raise ValidationError("A senha deve conter pelo menos um caractere especial.")

    senha_normalizada = normalizar_senha(senha)
