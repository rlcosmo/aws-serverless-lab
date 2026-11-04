# GitHub App para propostas de GitOps

A App cria branches e pull requests no GitOps. Não aprova GMUD, não faz merge e não sincroniza o Argo CD.

1. Na conta `rlcosmo`, abra https://github.com/settings/apps/new.
2. Nome: `rlcosmo-cosmotech-gitops` (precisa ser único). Homepage: `https://github.com/rlcosmo`. Deixe Callback URL vazio; desmarque Webhook → Active. Não habilite OAuth nem Device Flow.
3. Repository permissions: **Contents: Read and write**, **Pull requests: Read and write**, **Metadata: Read-only**. Sem permissões de administração ou aprovação.
4. Selecione **Only on this account** e crie a App. Anote o **App ID**, não o Client ID.
5. Em Private keys, clique **Generate a private key**. Guarde o `.pem` fora dos repositórios; não envie seu conteúdo pelo chat.
6. Em **Install App**, instale em `rlcosmo`, escolhendo **Only select repositories → cosmotech-gitops**.
7. Em `cosmotech-orders-api → Settings → Secrets and variables → Actions`:
   - Variables: `GITOPS_APP_ID` = App ID.
   - Secrets: `GITOPS_APP_PRIVATE_KEY` = conteúdo completo do `.pem`, incluindo BEGIN/END e as quebras de linha.
8. Informe somente “App configurada”. A integração será verificada por criação de PR, sem merge ou deploy automático.

Links diretos: [variáveis](https://github.com/rlcosmo/cosmotech-orders-api/settings/variables/actions), [secrets](https://github.com/rlcosmo/cosmotech-orders-api/settings/secrets/actions).

Proteção de branch privada está disponível em Pro/Team/Enterprise. Entretanto, **required reviewers de ambientes privados não está disponível em Free, Pro ou Team**; esse recurso exige Enterprise. Portanto, Pro sozinho não resolve os quatro gates configurados. A App não resolve essa limitação. O fluxo de release permanece bloqueado enquanto os quatro gates reais e a autorização GLPI/GMUD não estiverem comprovados. O proprietário informou que não alterou o plano. Não foi alterada cobrança nem visibilidade dos repositórios.

Referências: [registro da App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app), [token de instalação no Actions](https://github.com/actions/create-github-app-token).

Referências de proteções: [branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), [required reviewers](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments#required-reviewers).
