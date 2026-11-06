# Estado da implantação e retomada — estado consolidado

> Estado vigente — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Plano vigente e dependência humana

| Prioridade | Resultado | Próximo passo |
|---|---|---|
| Gate único Kestra | Ativo, revisão2, coleta/política SUCCESS nas duas releases | Aguardar decisões autenticadas |
| GLPI/portal/SNS | GMUD3/API e GMUD4/Worker em Approval10; SNS aceitou ambas | Responsável revisar mudanças e dependências |
| Publisher/Argo | Chave exclusiva, recibos/digest/replay, CI sem chave; signatário alternativo recusado | Exercitar promoção de aplicação autorizada |
| Canary Worker | Componentes e testes isolados, PodMonitor/RBAC preparados/aplicados | Bootstrap de telemetria autorizado; conectar execução Canary normal |
| Rollback/12h | Scheduler persistente ativo; lógica testada com relógio sintético | Validar EKS e cumprir 12h reais sem lacunas |
| LinkedIn | Três diagramas SVG/PNG, seis slides e PDF | Capturas definitivas após os testes integrados |

### Ações exclusivas do responsável

- [Revisar API / GMUD3](https://kestra.cosmotechsolutions.com.br/releases/11532c84f23aaf55829016336d5b7345abbbf6d896484cb2d68325c64f95a37f) — CRITICAL, sempre humana.
- [Revisar Worker / GMUD4](https://kestra.cosmotechsolutions.com.br/releases/2e4f566818a9216a2aaafd91047e6fd7ebc9c133287e1444d3a4eda6a7987bea) — NON_CRITICAL, mas bootstrap altera workflow e dependências; exige revisão preservada pela política.

O agente não aprovou nenhuma release. Aprovação não sobrepõe falha técnica. O coletor revalida evidências após a pausa; alteração de alvo, versão substituída ou falha bloqueia publicação. O bootstrap Worker é pré-requisito explícito, não comprovação de Canary; o código recusa deploy rolling normal quando métricas versionadas já existem, até a ligação Canary ser ativada.

A permissão Actions read anterior está resolvida. Não há dependência de inferência. Não realizar atividades NLB ou CloudTrail.

### Commits e implantações

Pushed: API59990a5/47b408b, Worker0feb8b7/a9dac69, Automatione93bef3/e3b7cad, Infrastructuree608f7b, Observabilityc2c8a44, GitOps4b6d264. CIs finais das três plataformas concluíram success. Host comparado ao commite3b7cad:25 módulos coincidentes. Kestra gate/scheduler revisão2 e controles IAM/SSM/RBAC/Argo implantados. Nenhuma imagem de aplicação promovida; API/Worker permanecem1/1, sem candidata Canary.

### Custos e limites

Cost Explorer: 2026-11-01 a 2026-11-06 exclusivo, UnblendedCost sem créditos/refunds, USD 33.4835982918, estimado. É o total da conta no período, não custo incremental desta implementação. Não foram criados nós/instâncias/volumes adicionais. Chamadas, notificações e ingestão de telemetria têm custo variável ainda não isolado.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# Estado da implantação e retomada

Atualização: 2026-11-06T00:44Z (05/11 no fuso do proprietário).

## Decisão vigente

Kestra deve autorizar por política determinística de criticidade. Esta decisão do
proprietário substitui a exigência anterior de inferência para o Worker.
Bedrock é opcional e desabilitado; quotas zeradas não bloqueiam o desenho
atual. Não fazer novas chamadas enquanto persistirem zeradas.
API HIGH sempre exige humano autorizado; Worker MEDIUM pode ser automático
somente com todas as evidências técnicas verificadas, sem mudança sensível e
com dependências revisadas. Falhas graves não podem ser sobrepostas por humano.
NLB e CloudTrail continuam fora do escopo.

## Resultado desta retomada

| Entrega | Resultado real | Limite |
|---|---|---|
| Política determinística | Default `ai_enabled=false`; CLI, coordinator, verificação Kestra, portal e SNS aceitam ausência de IA | Código dos componentes; não é gate integrado ativo |
| Testes automation | 101 passed; Ruff passou em src/tests | Testes locais; usam mocks, Git/GPG temporários; não são prova integrada |
| Host existente | Seis módulos atualizados, backup local preservado; portal reiniciado, active e healthcheck HTTP200 | Serviço de decisão; sem autoridade de publicação |
| Probe Bedrock | YAML validado sem warnings; revisão2 com `disabled=true` e guarda de execução | Nenhuma execução/inferência nesta retomada |
| Evidências GitHub | App declara Actions read; instalação não concedeu | Token Actions read HTTP422; runs com token contents read HTTP403 nos dois apps |
| Gate/publisher/enforcement | Não ativados | Não foi publicado workflow parcial nem removida credencial do CI antes do cutover |
| Canary/rollback | Não implantados no EKS | Nenhum dado sintético enviado; nenhuma promoção de aplicação |
| SNS | Teste anterior aceito, mailbox continua não verificada | Nenhum novo Publish nesta retomada |

A sequência de atualização do host retornou código7 na primeira leitura imediata
do healthcheck após reinício. A verificação seguinte confirmou active, HTTP200 e
os dois defaults de IA falsos. A atualização do probe já havia sido confirmada;
não foi repetida nem executada inferência.

## Dependência humana confirmada: permissão do GitHub App

App `rlcosmo-cosmotech-gitops`, instalação `178643233`. Os três repositórios
`cosmotech-gitops`, `cosmotech-orders-api` e `cosmotech-orders-worker` já estão
selecionados. O App declara `actions:read`, mas as permissões concedidas à
instalação são apenas `contents:write`, `pull_requests:write`, `metadata:read`.

O proprietário precisa aceitar a atualização **Actions: Read-only** em
[configurações da instalação](https://github.com/settings/installations/178643233).
Não é necessário fornecer chave privada ou token. O cliente runtime pede tokens
por repositório, com Actions read e Contents read para coleta; não usar token
pessoal do proprietário como substituto permanente.

Sem essa aceitação, o coletor não pode verificar diretamente testes/Trivy nos
runs. Não aceitar check enviado pelo CI nem marcar `enforcement_verified=true`
para contornar essa ausência. Nenhuma aprovação de release API foi feita.

## Continuação após a intervenção

1. Revalidar concessão Actions read e consulta autenticada dos runs de ambos os apps.
2. Conectar os adaptadores existentes de GitHub/ECR/diff/Argo/incidentes/observabilidade
   ao fluxo principal `promotion_gate`, sem tarefa Bedrock obrigatória.
3. Integrar portal/SNS, staging/publisher e reconciliação; revisar planos Terraform,
   findings e ativação conjunta. Os documentos SSM/access entry/permissões adicionais
   preparados anteriormente continuam não aplicados nesta retomada.
4. Ativar assinatura verificada no destino, publisher exclusivo, validador/bootstrap
   confiáveis e CI apenas solicitante. Demonstrar tentativa real de bypass bloqueada
   sem interromper as aplicações. Administradores continuam fronteira privilegiada.
5. Instrumentar baseline e ativar Canary somente Worker, sem aumentar nós; verificar
   capacidade, séries reais por digest, amostras/janelas e lease. API aguarda humano real.
6. Demonstrar progressão e rollback com dados sintéticos identificados e drenagem
   comprovada. Atualizar evidências e capturas; não chamar simulação de integração.

## Custos, commits e preservação

Cost Explorer consultado em 06/11 UTC: `UnblendedCost` de 01/11 a 06/11
(exclusivo), excluindo Credit/Refund: **US$33,4835982918**, `Estimated=true`.
É acumulado da conta, com atraso de faturamento; não representa custo incremental
da retomada. Sem inferência, novo SNS Publish, nova instância, controlador, tópico,
chave ou volume. Leituras AWS/Secrets Manager/Cost Explorer e operações SSM podem
ter cobrança; custo incremental exato não apurado.

Commit local automation `e93bef3`; detalhes e validações no índice14. Não houve push, publicação
LinkedIn, alteração dos workflows remotos, apply Terraform ou deploy de aplicação.
O portal conserva ledger/CSRF e o backup de código no host. Nenhuma fila, tabela,
volume, estado Terraform ou histórico Git foi removido. A autorização de execução
anterior e a nova decisão permanecem válidas para a continuação do mesmo escopo.

</details>
