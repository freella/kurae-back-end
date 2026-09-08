# Backend Template

Base arquitetural para projetos backend utilizando Django + Django REST Framework.

---

# 📐 Arquitetura

O projeto segue uma arquitetura modular baseada em apps desacopladas, com separação clara de responsabilidades.

## Estrutura de Diretórios

backend_template/
│
├── apps/
│   ├── auth/
│   ├── common/
│   ├── core/
│   ├── permissions/
│   ├── users
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py

---

# 🧠 Conceitos Arquiteturais

## 1️⃣ Apps Desacopladas

Cada domínio do sistema deve ser isolado dentro de `apps/`.

Regra:

- Um app = Um domínio de negócio
- Nada de lógica espalhada no config
- Nada de dependência  entre apps

---

## 2️⃣ Separação de Settings

As configurações são divididas em:

- base.py → configurações comuns
- dev.py → ambiente de desenvolvimento
- prod.py → ambiente de produção

isso vai facilitar:

- Segurança
- Escalabilidade
- Deploy 

---

## 🗺️ Onde estão as coisas? (Mapa dos Apps)

Atualmente o projeto conta com os seguintes módulos principais:

### 1. `apps/users/`
- **Responsabilidade:** Gerencia o modelo de usuário customizado (`User`).
- **Destaques:** Suporte a múltiplos tipos de usuário (`ADMIN`, `PADRAO`, `GUEST`) e Managers customizados para criação de usuários e guests.

### 2. `apps/auth/`
- **Responsabilidade:** Lógica de autenticação e tokens.
- **Destaques:** Login (JWT), Registro, Logout (Blacklist de tokens), Criação de Guest Users e Serializers de validação.

### 3. `apps/permissions/`
- **Responsabilidade:** Classes de permissão customizadas do DRF.
- **Destaques:** `IsNotGuest` (bloqueia escrita para convidados), `IsGuestUser`, e controle baseado em Roles.

### 4. `apps/core/`
- **Responsabilidade:** Utilitários globais e configurações base.
- **Destaques:** Validadores de senha e nome (`validators.py`), constantes globais e modelos abstratos (`BaseModel`).

---

## 3️⃣ Camadas Internas da App

Cada app deve seguir o padrão:

apps/users/

    models.py
    serializers.py
    views.py
    urls.py
    services.py (opcional)
    selectors.py (opcional)
    tests/

### Responsabilidades

- models → camada de persistência
- serializers → transformação e validação
- views → interface HTTP
- services → regra de negócio
- selectors → queries complexas
- tests → testes unitários

---

## 4️⃣ Banco de Dados

Utilizamos PostgreSQL via Docker.

A configuração é feita via variáveis de ambiente (.env).

Nunca colocar credenciais diretamente no código.

---

## 5️⃣ Docker

O projeto roda em containers:

- web → aplicação Django
- db → PostgreSQL

Motivo:

- Ambiente replicável
- Onboarding rápido
- Compatibilidade entre máquinas

---

# 🚀 Como Rodar o Projeto

## 1. Criar .env

Copiar o exemplo:

cp .env.example .env

## 2. Subir containers

docker compose build
docker compose up

## 3. Rodar migrations

docker compose exec web python manage.py migrate

## 4. Criar superuser

docker compose exec web python manage.py createsuperuser

---

# 🧪 Testes

Executar:

docker compose exec web python manage.py test

---

# 📦 Padrões de Desenvolvimento

- Sempre criar migrations versionadas
- Nunca commitar .env
- Toda nova app deve ser registrada em settings/base.py
- Toda regra de negócio complexa deve ir para services.py


---

# 🔐 Boas Práticas

- Separar lógica de domínio da camada HTTP
- Não acessar banco diretamente dentro de views 
- Usar permissões customizadas na pasta permissions
- Validar tudo via serializer

---

# 🔮 Roadmap & Futuro

O objetivo é evoluir este template para um backend robusto e pronto para produção.

## Próximos Passos (Curto Prazo)
- [ ] **Documentação Automática:** Integrar Swagger/OpenAPI (drf-spectacular) para visualizar os endpoints.
- [ ] **Recuperação de Senha:** Implementar fluxo de "Esqueci minha senha" com envio de e-mail.
- [ ] **Perfil de Usuário:** Criar endpoints para o usuário atualizar seus próprios dados (nome, foto, etc).
- [ ] **Testes de Integração:** Expandir a cobertura de testes para fluxos completos.

## Médio/Longo Prazo
- [ ] **CI/CD:** Configurar GitHub Actions para rodar testes e linter automaticamente.
- [ ] **Deploy:** Configurar arquivos para produção (Gunicorn, Nginx).
- [ ] **Monitoramento:** Adicionar logs estruturados e Sentry.

---

> **Nota:** Este projeto está em evolução constante. Sinta-se livre para contribuir ou sugerir melhorias via Issues.
---
