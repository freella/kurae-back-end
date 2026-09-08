#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path
from decouple import config


def main():
    """Run administrative tasks."""

    # Adiciona o diretório raiz do projeto ao sys.path
    # Isso garante que pacotes como 'config' e 'apps' sejam encontrados.
    sys.path.append(str(Path(__file__).resolve().parent))

    '''Define o módulo de settings padrão para o Django.
    O comando 'test' irá sobrescrever isso para o ambiente de testes.
    Para outros ambientes.'''
    settings_module = config("DJANGO_SETTINGS_MODULE", default="config.settings.dev")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    
       # Define uma variável de ambiente para indicar que estamos em modo de teste
    if 'test' in sys.argv:
        os.environ['DJANGO_TESTING'] = 'True'

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? "
            "Did you forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()