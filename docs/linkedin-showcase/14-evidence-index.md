# Índice de evidências reais

Atualização: 2026-11-05T20:24:29.454115+00:00. Evidências de teste são reais resultados locais com dados simulados; não são evidências de implantação AWS.

| ID | Origem | Resultado | Limite |
|---|---|---|---|
| C01 | STS/config/contexto e Git | Região us-east-1, conta/contexto coincidentes; seis repos inspecionados | Não muda autenticação |
| C02 | Kestra GET autenticado configs/plugins | 2.0.8 OSS; plugin-ai e ChatCompletion presentes | Credenciais somente em memória, sem publicação |
| C03 | Kestra POST flows/validate | Fluxo promotion_risk_assessment aceito, sem warnings | Validação somente; não instalado/executado |
| C04 | Argo GET api/version | v3.6.1 | Não comprova sync/gate atual |
| C05 | GitHub workflow permissions / deploy keys / protections / rulesets | Defaults read; chave GitOps read-only; protections/rulesets403 | Token App explicitamente solicitado ainda pode escrever |
| C06 | Código atual CI e script sync SSM | Caminhos alternativos identificados | Enforcement novo não ativado |
| T01 | automation pytest tests | 86 passaram | Mocks/SQLite/chaves efêmeras; sem LLM/cloud |
| T02 | orders-worker pytest tests | 79 passaram | Inclui mocks/moto; sem alteração SQS/DynamoDB real |
| T03 | gitops unittest discover | 13 passaram | Render e validação local; sem sync |
| T04 | observability teste coletor SQS | 2 passaram | Cliente CloudWatch mockado |
| T05 | Ruff nos 22 arquivos Python alterados/novos do escopo | Passou | Não é scan de vulnerabilidades |
| D01 | demo_promotion_canary.py | APPROVE mock→CANARY_1→CANARY_2→DRAIN_ROLLBACK→ROLLED_BACK | ISOLATED_SIMULATION; nenhum efeito executado |
| K01 | kubectl nodes/pods | Três nós Ready em duas AZs; Worker Running, container de aplicação ready, sem restarts | Snapshot; nenhum canary novo implantado |

## Evidências ainda inexistentes

IA real, e-mail recebido, aprovação humana integrada, bypass runtime bloqueado, efeitos aplicados pelo executor, Canary real e rollback EKS permanecem pendentes. Não capturar teste como se fosse execução dessas integrações.

A01–A08 da investigação NLB anterior estão no relatório histórico09 e no documento do repositório observability. A proposta foi desconsiderada; nenhuma remoção ocorreu. CloudTrail não foi implantado.

## Artefatos de revisão local

Diff completo das alterações canônicas: `/tmp/cosmotech-kestra-canary-review.diff`. Inventário de arquivos com SHA-256: `/tmp/cosmotech-kestra-canary-manifest.json`. São artefatos locais temporários, sem publicação; não são evidências de implantação. Nenhum commit/push foi realizado.


## Revalidação — 2026-11-05T21:04:49.426224+00:00

| ID | Origem | Resultado | Limite |
|---|---|---|---|
| T06 | automation pytest tests/unit | 86 passed | Mocks e Git/GPG temporários; sem cloud writes |
| T07 | Worker pytest | 79 passed | AWS mockado/moto |
| T08 | GitOps unittest / validate_app_manifests | 13 passed; manifests válidos | Sem sync |
| T09 | observability test_sqs_canary_metrics | 2 passed | CloudWatch mockado |
| T10 | Terraform dev fmt-check e validate | Passaram | Não houve plan/apply |
| T11 | Automação Ruff | Passou após correções de imports | Não equivale a scan de dependências |
| T12 | Demo local | CANARY_1 → CANARY_2 → DRAIN_ROLLBACK; inflight1 aguarda; ROLLED_BACK | Nenhum deploy/LLM/SQS real |
| C07 | Bedrock disponibilidade / inference profiles | Nova Micro ativo; disponibilidade para chamador consultada | Sem inferência ou prova da role Kestra |
| C08 | AWS Pricing get-products | Produtos Nova Micro em us-east-1 consultados | Preços incluem variantes; estimativa em10 usa inferência padrão |

A validação remota C03 corresponde à revisão anterior do fluxo ilustrativo. O YAML atual usa Bedrock SDK, permanece inativo e não foi instalado. Nenhum resultado de recebimento de e-mail ou rollback real foi produzido.

Revalidação adicional: Orders API — 65 testes unitários passaram; `bash -n` do sync preparado passou; Ruff do renderer de enforcement passou. Essas verificações não alteraram a aplicação nem seu deploy.


## Implantação autorizada — 2026-11-05T21:26:00.851677+00:00

| ID | Origem | Resultado real | Limite |
|---|---|---|---|
| R01 | STS/região/contexto e Git | Ambiente esperado conferido antes de alterações | Conta/IPs não reproduzidos neste material |
| R02 | Terraform planos/apply direcionados | Uma policy IAM criada; atualização KMS aplicada, sem destruição | Nenhum outro recurso do plano foi aplicado |
| R03 | Runtime isolado EC2 | boto3/botocore1.43.122; cryptography50.0.2; Converse disponível | Python dos serviços existentes preservado |
| R04 | Bedrock Converse real | ThrottlingException por tokens/dia | Inferência/recomendação não obtida |
| R05 | Service Quotas get/list | TPD/TPM/RPM Nova Micro0; TPD não ajustável | Proprietário solicitará liberação à AWS |
| R06 | Kestra validação/create/execution | Flow promotion_bedrock_probe validado sem warnings e instalado; execução `4e5JaUBxhUeP1nx5tQGkuq` FAILED | Teste de conectividade; não é gate principal |
| R07 | Logs reais do probe | request_id `a177d8ec-924e-4256-bb96-a731d8a7e7e4`; fail_closed SUCCESS, decision BLOCK | Nenhum publisher acionado |
| R08 | systemd / loopback / nginx | Portal active; healthcheck200; nginx -t passou | Decisor humano não tem chave/publisher |
| R09 | HTTPS portal | Anônimo401; autenticado200; POST origem inválida403 | Nenhuma decisão humana registrada |
| R10 | SNS Publish real após correção KMS | MessageId `c3586903-b6c6-5b4b-9c75-0a6543232494`; assunto TESTE SEM DEPLOY | Aceitação SNS; recebimento mailbox NÃO VERIFICADO |
| R11 | EKS após alterações | Orders API1/1 e Worker1/1 | Imagens e estratégia não alteradas; sem canary novo |
| R12 | IAM Access Analyzer validate-policy | findings vazio na policy aplicada | Não é auditoria completa IAM da conta |
| T13 | Automação pytest + Ruff | 92 testes passaram; Ruff passou | Inclui coletor confiável e notificação claramente identificada como teste |
| T14 | Worker pytest + Ruff | 79 testes passaram; Ruff passou | Sem mensagens SQS ou dados DynamoDB reais alterados |
| T15 | Terraform fmt-check/validate | Passaram | Planos adicionais preparados não equivalem a apply |

Evidências privadas de reconciliação/notificação e execução ficam na EC2 em diretório do serviço, sem credenciais em Git. O e-mail contém um registro de validação com enforcementfalse e checks negativos; não autoriza deploy e não foi aprovado por uma identidade humana. Nenhum teste foi apresentado como release real.


## Retomada determinística — 2026-11-06T00:44Z

Decisão do proprietário substitui Bedrock obrigatório: política determinística por
criticidade; Bedrock opcional e desabilitado. As seções anteriores registram o
histórico; IA real não é mais requisito de autorização do Worker.

| ID | Origem | Resultado real | Limite |
|---|---|---|---|
| R13 | STS/contexto + EKS leitura | Ambiente esperado; três nós Ready; API1/1 e Worker1/1, sem canary | Snapshot anterior à atualização do serviço de portal; nenhuma aplicação alterada |
| R14 | GitHub App GET app/installations/repositories | App declara actions:read; instalação178643233 concede somente contents:write, pull_requests:write, metadata:read; três repos selecionados | Metadados autenticados; não é concessão Actions |
| R15 | Tokens restritos por repo + Actions runs | API e Worker: contents read token201; leitura runs403; solicitação actions read422, “The permissions requested are not granted to this installation.” | Dependência humana: aceitar atualização da instalação; sem token pessoal runtime |
| T16 | automation pytest tests/unit | 101 passed em3,48s | Mocks/SQLite/Git/GPG temporários; não integração cloud |
| T17 | automation Ruff src/tests + YAML | Ruff passou; dois YAMLs Bedrock disabled=true | Não comprova segurança integral ou ativação do gate |
| R16 | SSM atualização do host + Kestra validate/PUT/GET | Seis módulos atualizados com backup; probe disabled=true revisão2; sem warnings | Não houve POST executions nem inferência; gate principal não instalado |
| R17 | systemd/healthcheck/imports no host | Portal active, HTTP200; defaults PromotionGate/evaluate ai_enabled=false | Primeira leitura imediata pós-restart recusou conexão; verificação posterior bem-sucedida |
| R18 | Cost Explorer get-cost-and-usage | 01/11–06/11 exclusivo, sem Credit/Refund: USD33,4835982918; Estimated=true | Acumulado da conta, sujeito a atraso; não custo incremental da retomada |

Comandos SSM: atualização `8e24f1d3-5c55-4364-8135-d4a4230973c5` (falha7 apenas
no healthcheck imediato após update/restart; probe já confirmado); verificação
`71aef2a0-c54b-4761-a11f-945cf60abf51` SUCCESS. Backups de módulos preservados no
host. Nenhum SNS Publish novo, apply Terraform, criação de recursos, alteração
remota CI, promoção de aplicação, Canary EKS ou rollback real nesta retomada.
Nenhuma decisão humana de API registrada pelo agente; nenhum push/publicação.

Aceitação necessária: [Actions Read-only na instalação do App](https://github.com/settings/installations/178643233).
O endpoint de token não pode conceder permissão ausente da instalação. Não
substituir as fontes verificadas por claims do CI. Evidência sanitizada adicional
local: `/tmp/cosmotech-actions-permission-evidence.json`, sem tokens ou chaves.

Commit local automation: `e93bef3 feat(promotion): default to deterministic approval with optional Bedrock`. Registra componentes existentes reutilizados e ajustes determinísticos; sem push. O checkout automation ficou limpo. Workflows preparados nos demais repos continuam locais; não foram publicados ou ativados.
