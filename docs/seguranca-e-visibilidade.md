# Segurança e visibilidade dos repositórios Kurae

Os repositórios da aplicação podem permanecer públicos enquanto isso for necessário para o
deploy. Código, histórico Git, mensagens de commit, branches, arquivos de workflow e logs de
Actions ficam visíveis para qualquer pessoa. Não coloque segredos, dados pessoais ou informação
comercial confidencial no Git, em mensagens de commit ou em logs.

## Verificações antes de manter o código público

- Mantenha `.env`, chaves privadas, tokens e credenciais fora do repositório. Use o gerenciador
  de segredos da plataforma de deploy.
- Revise o conteúdo versionado e o histórico completo, incluindo branches e pull requests.
- Se uma credencial real for exposta, revogue ou rotacione-a no serviço emissor. Apagar o arquivo
  ou reescrever o histórico não invalida uma credencial já exposta.
- Use a política em [SECURITY.md](../SECURITY.md) para receber relatos sem divulgar detalhes
  publicamente.

## Plano para voltar a repositórios privados

Execute este plano quando o plano Vercel da organização permitir conectar o frontend privado:

1. Confirme que o projeto Vercel da organização consegue acessar o repositório privado do
   frontend e que o deploy de produção está ligado à branch correta.
2. Confirme que a integração GitHub do Render tem acesso ao repositório privado do backend e
   que um deploy de produção pode ser executado a partir dele.
3. Verifique os forks públicos existentes e os requisitos de acesso da equipe. Tornar o
   repositório privado não torna privados os forks públicos: o GitHub os separa da rede original.
4. Alinhe a janela de mudança com a equipe e altere a visibilidade de cada repositório para
   privado nas configurações da organização.
5. Confirme os webhooks e integrações, execute os deploys de produção e valide frontend, API,
   CI e rollback antes de encerrar a mudança.

Clones locais, cópias baixadas, caches e forks públicos podem continuar existindo após a mudança
de visibilidade. Tornar o repositório privado restringe o acesso futuro ao repositório original,
mas não recolhe cópias já feitas.
