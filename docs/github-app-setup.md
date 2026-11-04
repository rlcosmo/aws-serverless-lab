# GitHub App para propostas de GitOps

A App cria branches e pull requests no GitOps. Não aprova GMUD, não faz merge e não sincroniza o Argo CD.

1. Na conta `rlcosmo`, abra https://github.com/settings/apps/new.
2. Nome: `rlcosmo-cosmotech-gitops` (precisa ser único). Homepage: `https://github.com/rlcosmo`. Deixe Callback URL vazio; desmarque Webhook → Active. Não habilite OAuth nem Device Flow.
3. Repository permissions: **Contents: Read and write**, **Pull requests: Read and write**, **Metadata: Read-only**. Sem permissões de administração ou aprovação.
4. Selecione **Only on this account** e crie a App. Anote o **App ID**, não o Client ID.
5. Em Private keys, clique **Generate a private key**. Guarde o `.pem` fora dos repositórios; não envie seu conteúdo pelo chat.
6. Em **Install App**, instale em `rlcosmo`, escolhendo **Only select repositories → cosmotech-gitops**.
7. Em `cosmotech-orders-api → Settings → Secrets and variables → Actions`:
   - Variables: `GITOPS_APP_ID` = App ID. O workflow também aceita esse ID como Secret, como configurado pelo proprietário.
   - Secrets: `GITOPS_APP_PRIVATE_KEY` = conteúdo completo do `.pem`, incluindo BEGIN/END e as quebras de linha.
8. Configuração validada em 2026-11-04: token de instalação restrito ao GitOps, leitura/escrita e criação do PR #1 aprovadas. Não há merge ou deploy automático.

Links diretos: [variáveis](https://github.com/rlcosmo/cosmotech-orders-api/settings/variables/actions), [secrets](https://github.com/rlcosmo/cosmotech-orders-api/settings/secrets/actions).

Proteção de branch privada está disponível em Pro/Team/Enterprise. Entretanto, **required reviewers de ambientes privados não está disponível em Free, Pro ou Team**; esse recurso exige Enterprise. Portanto, Pro sozinho não resolve os quatro gates configurados. A App não resolve essa limitação. O fluxo de release permanece bloqueado enquanto os quatro gates reais e a autorização GLPI/GMUD não estiverem comprovados. O proprietário informou que não alterou o plano. Não foi alterada cobrança nem visibilidade dos repositórios.

Referências: [registro da App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app), [token de instalação no Actions](https://github.com/actions/create-github-app-token).

Referências de proteções: [branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), [required reviewers](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments#required-reviewers).

## Validação efetiva e bloqueio atual

- O ID e a chave estão em repository Secrets. Nenhuma chave foi regenerada ou exposta. `orders-ci.yml` aceita ID via Variable ou Secret; a chave permanece exclusivamente Secret.
- Execuções `41885072665` e `41885793878`: somente proposta, reutilizando imagem da execução aprovada `41875936763`. Sem novo build/scan. A segunda confirmou que o token vê somente `rlcosmo/cosmotech-gitops` e não lê o repositório privado de infraestrutura.
- Token solicitado com Contents/Pull requests write e Metadata read; sem permissão de administração/checks/AWS. A falha na autenticação encerra o job antes do checkout/escrita, sem `continue-on-error` ou fallback para PAT. Tokens são revogados no pós-job; a chave persistente não é rotacionada pelo workflow.
- [PR #1](https://github.com/rlcosmo/cosmotech-gitops/pull/1), autor `app/rlcosmo-cosmotech-gitops`, está aberto, sem reviews aprovadas. Tag SHA e digest imutável conferidos; server dry-run aprovado. O check verify-protections falhou e os quatro gates foram pulados. O PR #2 propõe corrigir também o check terminal: se qualquer gate falhar/pular, release-approved deve terminar em FAILURE (teste negativo confirmado), em vez de SKIPPED. Essa correção ainda não foi mergeada.
- **Isso bloqueia os jobs, mas não impõe bloqueio de merge no GitHub:** main tem `protected=false`; branch protection e rulesets retornam 403. Revisões e checks podem existir sem serem obrigatórios. Argo auto-sync desabilitado também não equivale a aprovação técnica. Nenhum merge, sync ou deploy foi executado.

## Alternativas de governança — propostas, não implementadas

| Opção | Imposição técnica necessária | Custo/licenciamento e limites |
|---|---|---|
| A — Privados com controles nativos | Organização Enterprise Cloud; branch/ruleset sem bypass, reviews/checks obrigatórios e quatro Environments com required reviewers reais | Enterprise: US$21/usuário/mês no preço público, antes de impostos/uso. Exige autorização de organização/transferência, ajustes de URLs, instalação App e confiança OIDC. Pro pessoal ou Team não habilitam required reviewers de Environments privados. |
| B — Privados na conta pessoal com verificador externo | Pro para impedir merge sem status obrigatório, emitido somente por uma App verificadora separada. GLPI fornece quatro decisões humanas reais, vinculadas a PR/head SHA/digest/hash dos manifests; novos commits invalidam aprovações. Credencial verificadora separada da App propositora, auditoria, expiração e falha fechada. RBAC/admission no destino impede deploy fora do release aprovado | Pro: referência pública US$4/mês na FAQ histórica; confirmar checkout. Acrescenta implementação/manutenção e consumo de serviços existentes. Native reviewers privados continuam indisponíveis, mas as aprovações seriam efetivamente impostas pelo verificador + status exigido e controle de deploy. Nada disso está implementado. |
| C — Usar os gates nativos do índice público existente | O índice aws-serverless-lab já é público e tem os quatro Environments com rlcosmo como reviewer. Um workflow controlado ali poderia aprovar somente metadados (PR/head SHA/digest), emitir um check por App verificadora separada e liberar o GitOps privado somente após as quatro aprovações. Pro ainda é necessário para tornar esse check obrigatório no merge privado; RBAC/admission protege o destino | Pro + uso de CI. Não transforma nenhum dos seis privados em público nem publica código privado, mas exige proteger o workflow de controle e evitar vazamento nos logs. Reutiliza gates existentes; precisa de autorização de desenho/implementação. |

Com o plano atual sem proteção de branch privada, um verificador externo/admission pode negar **deploy**, mas não impedir tecnicamente o **merge** no GitHub. Isso não atende à exigência completa e não é equivalente a branch protegida. A alternativa imediata segura é manter a entrega parada. Nenhum upgrade, transferência, alteração de visibilidade ou substituição de mecanismo foi realizado.

Fontes: [preços Enterprise/Team](https://github.com/pricing), [referência Pro na FAQ](https://docs.github.com/en/get-started/learning-about-github/faq-about-changes-to-githubs-plans), [planos pessoais/organização](https://docs.github.com/en/get-started/learning-about-github/githubs-plans), [rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets), [status de serviço externo](https://docs.github.com/en/rest/commits/statuses), [branches protegidas](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
