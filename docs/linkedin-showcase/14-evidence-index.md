# Índice de evidências reais — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

| ID | Fonte | Evidência real |
|---|---|---|
|RCL01|GLPI5 / lAvjxmfP9MKrFLukQOWon|RCL000001; autoaprovação; Canary abortado por evidência inicial insuficiente; candidata drenada e stable mantida; native Cancelled14|
|RCL02|GLPI6 /6F3UA0J7u0LLIVJJxSQxwP|RCL000002; titlev2.0.1-lab; HUMAN_REVIEW/PAUSED, sem decisão humana|
|RCL03|GLPI7 /6EzLdoosy2wpJXqZFJPRWU|RCL000003; policy-engine; Worker1.0.2;1→2→promoção→drain; OBSERVING/Review8 até22:04:27Z|
|RCL04|CIs42196287796/42196288505/42197528788|Testes, Trivy, publicação e solicitação reais aprovados; não confundir com API implantada|
|RCL05|SSMd013d61a-2e8a-4e43-91d7-6a2443587ca8|Flow4 validado sem warnings, backup privado, zero GMUD histórica renumerada|
|RCL06|SSM7b45de21-b869-41cd-9ce7-a1dce434f6b1|Portal GET200 autenticado/401 anônimo nas três RCLs, correspondência de identidade, nenhum POST de aprovação pelo agente|
|RCL07|SSMde5d2167-7462-4a87-aab1-875229ecd7dd|28 módulos do host coincidem com19cb384; sequência3/3; RCL000003 na série Prometheus stable|
|RCL08|assets/rcl-live-evidence.json|Estados consultados e janela real de300s: increase≈203,16 candidatos/83,16 estáveis, p95≈0,099s, erros/retries/DLQ0 naquela amostra|
|RCL09|Carga limitada + GET/Orders|800 pedidos sintéticos HTTP202, zero erros de envio; amostras0/399/799 COMPLETED, pagamento SIMULATED_CAPTURED|
|RCL10|Grafana API|Dashboard orders-worker-canary instalado/lido;12 painéis. Painéis exporter SQS ainda parciais SEM DADOS|
|RCL12|GitOps assinados|98cab14/f41651f: candidata e capacidade da RCL000001;3e19c1f/df1c979/09e52d1: preparação, promoção e drenagem/capacidade da RCL000003|
|RCL13|CIs plataforma|Automation42200997321 e observability42201001293 concluídos success; validação Terraform local passou|
|RCL11|pytest/Ruff|168 passed,4 subtests; Ruff passou. Concorrência/retry/restore/CSRF/rollback/janelas isolados; não são prova de12h reais|

Evidências que permanecem ausentes: aprovação API candidata, deploy desta API, observação12h concluída, rollback responsável pós-promoção e capturas de UI definitivas. Artefatos visuais são diagramas/editorial, não prints.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

# Índice de evidências reais — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Evidência após as aprovações

| ID | Origem | Resultado real |
|---|---|---|
| P01 |SSMd49b7dac-43f2-43c4-b59a-63d3a7ee2575 |Duas decisões autenticadas; Kestra SUCCESS; GMUD3/4 Review8/OBSERVING, errors[] |
| P02 |GitOps999f4ad e4de7fac |Release API e bootstrap Worker promovidos pelo publisher controlado; ambos RollingUpdate, sem Canary |
| P03 |kubectl pods/events |Uma falha startup15021 em cada pod, ambos2/2 sem restart. Origem: proxy Istio nativo com atraso0s |
| P04 |Injector patch server dry-run/replace |Atraso5s somente app orders-api/orders-worker; outras probes e workloads preservados; sem rollout das aplicações |
| P05 |Dois pods reais isolados em default |Proxy injetado5s, ambosReady, zero Warning e zero restart. Evidência sanitizada em infrastructure/ops/istio/startup-probe-evidence-20261106.json; pods de teste removidos |
| P06 |SSM1a75aa4f-3096-40f6-8004-5df38bc64153 |Flow revision3 validado sem warnings e labels instalados; execuções3/4 identificadas por aplicação, commit12 e GMUD |
| P07 |Automation pytest/Ruff |155 passed,4 subtests; Ruff passou após mudança de apresentação |

Essas provas não são validação de Canary/rollback ou conclusão das12h. As linhas G04/G05/G13/G16 abaixo registram o snapshot anterior às aprovações.

## Evidências vigentes desta etapa

| ID | Execução/artefato | Resultado real e limite |
|---|---|---|
| G01 | API CI42147727518 / commit47b408b | Testes/Trivy/publicação ECR e solicitação Kestra verdes; sem deploy |
| G02 | Worker CI42147729148 / commita9dac69 | Testes/Trivy/publicação ECR e solicitação verdes; sem deploy |
| G03 | CIs iniciais42145824882/42145826639 | Trivy recusou apt3.0.3/libapt-pkg7.0; corrigidos para pacote apt3.0.4 disponível |
| G04 | Kestra5hHDHAD5Edszef1FQbH4Cy / GLPI3 | Revisão2; coleta e política SUCCESS; PAUSED; native Approval10; sem decisão humana |
| G05 | KestraMKVIJ36d4wfJrsh1jml1J / GLPI4 | Revisão2; coleta e política SUCCESS; PAUSED; native Approval10; bootstrap sensível exige humano |
| G06 | SNS | Duas notificações aceitas, IDs nos ledgers privados; mailbox não comprovada |
| G07 | GitOps4b6d264cf5c027570387aa0daebf777360ae5770 | Anchor assinado de controle; árvore gitops/apps idêntica ao pai; sem promoção |
| G08 | Argo verificação negativa | GIT/GPG recusou revisão com outro signatário; zero operações de sync da aplicação diagnóstica |
| G09 | EKS control-plane ServiceMonitor | Quatro targets up; alertas scheduler/controller-manager resolvidos sem supressão |
| G10 | Automação pytest/Ruff | 155 passed e4 subtests; Ruff passou. Isolados, mocks/Git/relógio sintético |
| G11 | API/Worker testes locais | 65/81 passaram; não são testes integrados EKS |
| G12 | GLPI Change2 | Protocolo nativo testado, sintético e cancelado, sem deploy; nunca conta nos cinco sucessos |
| G13 | SSM1c087168-8121-4173-80b9-b4b322201981 | Leitura direta das duas execuções confirma pausa, native10 e ausência de decisão |
| G14 | SSM9d6cd34d-b81e-4415-a7fc-b332c561e1af | Patch de semântica nativa/histórico aplicado; sem publicação de aplicação |
| G16 | SSMedb1e812-4b72-42d2-91b3-9eaa8a849466 | Leitura real confirmou zero sucessos encerrados; retries GMUD3/4 retornaram IDs existentes, com create bloqueado e zeroPOST |
| G15 | Kit visual | Diagramas/carrossel/PDF exportados; placeholders explícitos, nenhuma captura de UI fabricada |

| G17 | SSMfd13787e-50ab-400d-8538-335af398ea3d | Os25 módulos Python no host coincidem com automatione3b7cad; portal active/health200, sem autoridade de publicação no portal |
| G18 | Automation CI42152132774 / e3b7cad | Workflow validate-cluster-pipelines concluído success; não equivale aos155 testes pytest locais |
| G19 | Infrastructure CI42152134245 / e608f7b | Workflow terraform concluído success; controles aplicados previamente com planos revisados |
| G20 | Observability CI42152137542 / c2c8a44 | Workflow validate-observability concluído success; dashboard novo continua preparado, não integrado |
| G21 | kubectl deployments | API1/1 e Worker1/1, sem deployment orders-worker-canary; nenhuma imagem promovida nesta etapa |

Não existentes: cinco GMUDs reais encerradas com sucesso, aprovação humana registrada, deploy integrado desta release, Canary/rollback EKS, janela real12h concluída e capturas definitivas. Valores de custo: ver10. Manifesto de hashes dos arquivos públicos em assets/artifact-manifest.json.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

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

</details>

</details>
