> **Atualização real — 06/11/2026:** retenção aplicada por Deployment: API 11→3, Worker 11→3 e Canary 7→3. Vinte ReplicaSets inativos removidos pelo Kubernetes via GitOps assinado; Argo CD Synced/Healthy. Imagens, pods e HPA preservados. Worker atual 1.0.5; candidato 1.0.6 inativo após rollback anterior a esta manutenção. Não anunciar novo Canary validado. Automação `cdedf49`; GitOps `49e0639`/`0efb05d`. [Evidência sanitizada](assets/replicaset-retention-evidence.json). O restante deste documento e o carrossel preservam seus snapshots históricos; não são capturas deste ajuste.

# Estado da implantação e retomada — estado consolidado

## Novas releases — duas réplicas estáveis propostas

CIs reais concluídas: Worker1.0.6 (42230662176) e API2.0.4-lab (42230662459), com testes, Trivy e publicação aprovados. As duas candidatas definem HPA `minReplicas=2`, `maxReplicas=2`; `spec.replicas` permanece sob propriedade exclusiva do HPA. Consulta real:2026-11-06T14:08:19.240108+00:00.

| GMUD | Aplicação / candidata | GLPI | Kestra | Estado |
|---|---|---|---|---|
| [RCL000009](https://kestra.cosmotechsolutions.com.br/releases/4477da31afa7306f609cec5aa3550c4e24fff5a06899bd80254483eedfcfc6fd) | orders-api 2.0.4-lab | 13 | 3wN30fLGZrBmhd214817by | Aprovação humana pendente |
| [RCL000010](https://kestra.cosmotechsolutions.com.br/releases/43e5dc66280aa85c1ec7446d61ec19d93d10ffb06583c87b1e73e918f04db2d8) | orders-worker 1.0.6 | 14 | H7O83ddlbuiIXWI5Izh4L | Aprovação humana pendente |

Ambas aguardam decisão autenticada. API é CRÍTICA; Worker continua NÃO CRÍTICA, mas a mudança de HPA é sensível segundo a política vigente. Não houve reclassificação nem aprovação pelo agente. Nenhuma candidata foi promovida nesta consulta; versões atuais continuam API2.0.3-lab e Worker1.0.5, uma réplica pronta cada.

Executor Canary corrigido para congelar o mínimo aprovado do HPA, em vez de forçar uma réplica, preservando o baseline e a capacidade da candidata na promoção. Após drenagem, restaura o HPA aprovado; rollback restaura a configuração anterior. Testes locais: Worker86, API69, automação222 +4 subtestes. Canary continua exclusivo Worker; novo Canary/dados sintéticos e observação12h aguardam autorização e execução real. Não considerar validação isolada como implantação integrada.

Fonte: `assets/two-replica-release-requests.json`. Commits enviados: Worker3db4ff4, API3ff206a, automação b104c04. Nenhum novo nó/recurso AWS provisionado; custos variáveis CI/ECR/chamadas não isolados. O carrossel existente registra as últimas implantações verificadas RCL000007/8; estas novas GMUDs ainda não podem ser anunciadas como implantadas.

## Estado vigente de acesso — consulta nativa Kestra

`laboratorio@cosmotechsolutions.com.br` agora entra no formulário original de https://kestra.cosmotechsolutions.com.br/ com a senha operacional existente. Consulta os mesmos17 fluxos do catálogo administrativo, execuções, logs e dashboards. Admin mantém credenciais, sessões e acessos. Regras antigas abaixo que limitavam essa conta ao portal são históricas.

Como o OSS2.0.8 continua com uma conta nativa global, o acesso adicional é um adaptador protegido no Nginx/portal, não RBAC nativo nem compartilhamento da senha administrativa com o navegador. Sessão opaca Secure/HttpOnly/SameSite=Strict; consultas permitidas, alterações/replay/resume/webhooks bloqueados. Aprovação, rejeição e rollback permanecem no portal com identidade e CSRF. Credencial administrativa só no mapa privado root0600, ilegível pelo serviço do portal. Frontend original preservado.

Validação HTTP real: login204, catálogo de17 fluxos idêntico ao admin, execuções/logs200, consulta real de indicador200, tentativas em recursos inexistentes403, logout204 e acesso após logout401. Sem aprovação ou alteração de fluxo real pelo teste. Admin Basic/cookie200 e login204, inclusive durante breve indisponibilidade controlada do adaptador, com recuperação confirmada. Backend Kestra não foi interrompido. Não há captura de navegador: estes resultados são de protocolo HTTP e fonte da versão instalada.

Evidência: `assets/kestra-native-view-evidence.json`. Código80c3657/d910f15/1063c89; infraestrutura131c443. Testes locais219 +4 subtestes. Sem novas versões de aplicações, GMUDs ou recursos AWS nesta alteração; observação12h continua em aberto. Custos variáveis não isolados.

## Acesso operacional e links CD — correção de06/11/2026

Entrar em https://kestra.cosmotechsolutions.com.br/releases/login como `laboratorio@cosmotechsolutions.com.br`, com a senha existente do laboratório. O alias anterior e o admin foram preservados. O login nativo do Kestra OSS permanece administrativo. `Acompanhar esteira CD` abre etapas/evidências autenticadas no portal; o link técnico usa `/ui/main/executions/...`. Links históricos com `/ui/executions/main/...` recebem308. Validação real: dez links CD200, anônimo401 e zero aprovações pelo teste. Evidência: `assets/operational-email-cd-links-evidence.json`; código59f602f e proxy2f9eae5.

## Referências de imagem por tag — atualização de06/11/2026

Por decisão do proprietário, os Deployments usam o endereço completo do ECR com `worker-1.0.5-16` e `api-2.0.3-lab-19`, sem sufixo `@sha256`. Os dois repositórios são integralmente IMMUTABLE. Digest continua verificado na esteira, registrado nas evidências e utilizado internamente por Canary/rollback. A mudança de formato mantém as versões, decisões e prazos das RCL000007/8; não cria aprovação humana ou nova versão. GitOps continua sendo a fonte oficial. Evidência atual: `assets/tag-only-deployment-evidence.json`. Os exemplos anteriores com tag@digest representam o formato anterior.

## Revisão operacional — 06/11/2026

Estado confirmado em 2026-11-06T12:45:28.826367+00:00. API 2.0.3-lab: aprovação humana autenticada registrada; Worker 1.0.5: aprovação automática pela política. Ambos implantados, Argo CD saudável e em observação. Canary exclusivo Worker concluído com progressão 1→2, promoção e drenagem. Nenhuma aprovação pelo agente.

| RCL | Aplicação / versão | GLPI | Kestra principal | Estado |
|---|---|---|---|---|
| RCL000007 | orders-api 2.0.3-lab | 11 | 7jyFluWNV09PrJqsDc3kVb | OBSERVING |
| RCL000008 | orders-worker 1.0.5 | 12 | 50dZBEpEZFcQPNS8qv56rI | OBSERVING |

Portal principal: https://kestra.cosmotechsolutions.com.br/releases/ · Entrada operacional: https://kestra.cosmotechsolutions.com.br/releases/login. Usuário `laboratorio` criado no portal com hash PBKDF2-SHA256; admin preservado. Kestra OSS 2.0.8 mantém autenticação nativa de administrador; não foi concedido acesso administrativo nativo ao operador. Ações continuam sujeitas a autenticação, CSRF, política e prazo. Decisões futuras como laboratorio dependem da interação real desse usuário; esta API foi aprovada pela identidade admin.

Uma execução `cosmotech.promotion/release_pipeline` por release, com labels RCL/aplicação/versão; scheduler persistente em `cosmotech.operations`. Dez etapas no portal com fatos, horários, duração e evidências; dados históricos sem horário não recebem duração inventada. Execução principal concluída significa entrega inicial, não GMUD encerrada. Filtrar `execution_type=release` para acompanhamento.

Imagens observadas: `worker-1.0.5-16@sha256:…` e `api-2.0.3-lab-19@sha256:…`, com labels de versão e RCL. O número final vem da CI real; a tag aponta para o mesmo digest testado e a referência continua fixada pelo digest. Pods finais: zero reinícios e nenhum Warning na amostra; startup Istio15021 com atraso de5s.

Carga real com dados sintéticos: 800 respostas202, zero erros HTTP, três pedidos consultados como COMPLETED, estoque1800→1000. Janela Canary300s: candidata185,26 e stable101,05 por Prometheus increase; p95≈0,0986s; falhas, poll, visibility e DLQ zero na amostra. Não são contagens exatas de pedidos nem tráfego de produção.

Observação/rollback até 06/11/2026 às21:41:30 (Worker) e21:44:26 (API), horário de São Paulo; UTC07/11 às00:41:30 e00:44:26. Não houve encerramento antecipado. Rollback humano pós-promoção e conclusão real das12h ainda não validados. Rollback automático real da RCL000005 permanece histórico de falha, nunca sucesso.

Indisponibilidade real breve do GLPI foi controlada e recuperada: histórico autenticado200 permaneceu disponível, ações bloqueadas, decisões e efeitos GitOps preservados, zero GMUDs duplicadas. Cache não autoriza promoção. Autenticação real laboratorio: dez detalhes consultados, anônimo/senha incorreta401, acesso nativo Kestra negado e zero POSTs de aprovação no teste.

Sem novos recursos AWS. Custos variáveis de CI, chamadas, mensagens e telemetria não foram isolados. Bedrock desabilitado, sem inferência; NLB/CloudTrail fora do escopo. Capturas reais de UI/anotações permanecem pendentes; diagramas e placeholders não são prints.

### Evidência e utilização deste documento

Implementação e deploy concluídos nesta rodada. Dependências restantes: decorrer janela12h sem falha/rollback; realizar teste de rollback solicitado por responsável quando autorizado e elegível; obter capturas reais da UI. Não gerar releases extras para contornar observação ou aprovação.

### Commits desta rodada

Automation bb6b9c4; infraestrutura774efd0; Workerdf58807; API8e74c1c. GitOpsAPI ebc0e17; Worker final6a7be69, com etapas intermediárias assinadas registradas na evidência.

<details><summary>Histórico técnico preservado — não representa o estado vigente</summary>

# Estado da implantação e retomada — estado consolidado

## Revisão de execução —06/11/2026

Consulta real: 2026-11-06T11:30:15.400580+00:00. API 2.0.2-lab / RCL000004 / GLPI8: OBSERVING, aprovação humana autenticada pelo responsável. Worker 1.0.4 / RCL000006 / GLPI10: OBSERVING, Canary COMPLETE, aprovação automática condicionada. Nenhuma aprovação da API pelo agente.

Concluídos: correção GLPI, acompanhamento Kestra/Argo, selo Canary por estratégia/etapa e novas releases rastreáveis. Aguardar a observação real12h sem lacunas. Não repetir release para contornar controles nem encerrar GMUD substituída como sucesso; reversão de versão substituída exige análise humana.

Carga real com dados sintéticos: 800 respostas202 e 0 erros HTTP; três pedidos consultados como COMPLETED. API/SQS/DynamoDB reais; pagamento e expedição são simulações explícitas do laboratório. Startup Istio15021 com5s, sem a falha de conexão anterior nos testes desta rodada. Readiness503 pode ocorrer durante drain deliberado; reinícios e eventos estão registrados por teste.

As janelas de12h continuam abertas, sem encerramento antecipado. Rollback solicitado pelo responsável após promoção ainda não foi executado. Capturas reais de UI e suas anotações seguem pendentes; placeholders não são prints. Bedrock permanece opcional/desabilitado, sem inferências. Nenhuma operação NLB/CloudTrail ou recurso AWS novo; custo variável de chamadas/carga/telemetria não isolado.

| RCL | Aplicação / versão | GLPI | Execução Kestra | Estado |
|---|---|---|---|---|
|RCL000001|orders-worker 1.0.1|5|lAvjxmfP9MKrFLukQOWon|ROLLED_BACK / ROLLED_BACK|
|RCL000002|orders-api 2.0.1-lab|6|6F3UA0J7u0LLIVJJxSQxwP|OBSERVING / RollingUpdate|
|RCL000003|orders-worker 1.0.2|7|6EzLdoosy2wpJXqZFJPRWU|OBSERVING / COMPLETE|
|RCL000004|orders-api 2.0.2-lab|8|2wGGXzMxvve2Rv8w0Hokif|OBSERVING / RollingUpdate|
|RCL000005|orders-worker 1.0.3|9|12AXgkuanecQ9CAN4j3MsJ|ROLLED_BACK / ROLLED_BACK|
|RCL000006|orders-worker 1.0.4|10|7kk9GgJSgE5VkTZWcBp60L|OBSERVING / COMPLETE|

[API — acompanhamento](https://kestra.cosmotechsolutions.com.br/releases/6923193b600e17a43510d1749c455af6ae9553efe40c4df6e538a7e4283e46b9) · [GLPI8](https://glpi.cosmotechsolutions.com.br/front/change.form.php?id=8) · [Worker — acompanhamento](https://kestra.cosmotechsolutions.com.br/releases/5477512106ac017183953f2c8b846d1451466fbf1c4888e531aa28c348447518) · [GLPI10](https://glpi.cosmotechsolutions.com.br/front/change.form.php?id=10).

Commits enviados: automation80a1b0c/6d808bc/38427a0/c950e3e; infrastructure16e4555/9f3d137; APIeea8bf9; Worker2595cc9/8cdf74b. API GitOps8fc07c8; preparação Canaryda3d9c5. Demais efeitos GitOps ficam nas evidências finais e no repositório assinado.

Prazos UTC: API 2026-11-06T22:56:10.666817+00:00; Worker 2026-11-06T23:29:37.526989+00:00. As versões anteriores substituídas não recebem encerramento automático como sucesso.

Métrica real da segunda janela Canary (Prometheus increase, não contagem exata de pedidos): candidata 210.53; stable 72.63; p95 0.0982s; erros/poll/visibility/DLQ0; janela300s. Amostra registrada em 2026-11-06T11:26:20.493775+00:00.

GitOps real: RCL000005 preparação da3d9c5, promoção e3eec5d, rollback84f1f73 e restauração HPA8a60364; RCL000006 preparação0906342, promoção8c5c82f e finalização/drenagemabd7ab7. API RCL000004:8fc07c8. Todos pelo publisher exclusivo.

Saldo real dos SKUs sintéticos: RCL000005,1800−900=900; RCL000006,1800−800=1000. Valores lidos no DynamoDB conferem, sem decrementos extras nessas rodadas.

## Histórico preservado desta atualização

<details><summary>Snapshot anterior (não é o estado vigente)</summary>

# Estado da implantação e retomada — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

| RCL | Aplicação/versão | GLPI | Kestra | Estado |
|---|---|---|---|---|
|RCL000001|Worker1.0.1|5|lAvjxmfP9MKrFLukQOWon|ROLLED_BACK, stable preservada|
|RCL000002|API2.0.1-lab|6|6F3UA0J7u0LLIVJJxSQxwP|HUMAN_REVIEW/PAUSED|
|RCL000003|Worker1.0.2|7|6EzLdoosy2wpJXqZFJPRWU|OBSERVING, Canary COMPLETE|

[API — aprovação autenticada](https://kestra.cosmotechsolutions.com.br/releases/33d04c09dea95bb81833b59108cd3266471b2d83da824abae9e099354750227d) · [GLPI6](https://glpi.cosmotechsolutions.com.br/front/change.form.php?id=6).
[Worker — acompanhamento/rollback elegível](https://kestra.cosmotechsolutions.com.br/releases/8e0e93674b858867cd5945864c5ff61fa8f7e885d744fc517251fb7b3da004b9) · [GLPI7](https://glpi.cosmotechsolutions.com.br/front/change.form.php?id=7).

Concluído nesta etapa: sequência RCL, título padrão com versão real, portal pt-BR responsivo, labels Kestra, SNS, metadados GitOps/Prometheus/Grafana, execução Canary Worker1→2 e800 pedidos sintéticos. API atual permanece2.0.0-lab; candidata2.0.1-lab não foi promovida.

Pendências: aprovação humana API; observação Worker até22:04:27Z sem lacunas/erro/versão substituída; rollback responsável pós-promoção ainda não executado; exporter SQS nos painéis; capturas definitivas. GMUD antiga cuja versão foi substituída não fecha como sucesso e requer análise, sem bloquear a observação das demais. Falha/timeout é isolada por release no reconciliador.

Commits enviados: automation19cb384, infrastructured158485, observability4f0b35e; API88f6bc2; Workera1cd2c9/63f8729. Fonte do host comparada ao commit automation:28 módulos coincidentes. Fluxo gate revisão4, scheduler persistente revisão2. Sem recursos AWS novos; plano IAM0 adições/1 atualização/0 destruições e Access Analyzer sem findings. Custo incremental de chamadas/carga/telemetria não isolado; não declarar zero. Bedrock desabilitado, sem inferências. Nenhuma operação NLB/CloudTrail.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

# Estado da implantação e retomada — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Correção após aprovação e deploy

| Aplicação | Versão | GMUD | Estratégia real | Estado |
|---|---|---|---|---|
| orders-api |47b408bd448e |3 |RollingUpdate |OBSERVING até20:45:17Z06/11 |
| orders-worker |a9dac69545cd |4 |Bootstrap rolling de telemetria |OBSERVING até20:46:26Z06/11 |

Nenhum orders-worker-canary ativo. Não anunciar progressão/rollback Canary. Commits de deploy GitOps999f4ad/API e4de7fac/Worker. Nenhuma nova aprovação/release disparada para as correções abaixo.

Infra2e0c30a: atraso inicial5s para startupProbe15021 somente novos pods Orders. A falha anterior ocorreu uma vez por pod, sem restart e com recuperação. Dois pods reais isolados:2/2, zero Warning/restart; removidos após registro. Pods das aplicações e seus eventos antigos preservados.

Automationb02fb01: gate revisão3 validado e fixado; labels application/version/gmud/release antes da aprovação nas próximas releases. Execuções atuais receberam labels via API e readback, sem novo deploy.155 testes e4 subtestes passaram, Ruff passou. Em Executions, exibir coluna Labels se oculta. ID técnico de auditoria permanece imutável.

Canary normal, rollback integrado e janela12h concluída continuam pendentes. Fonte operacional: infrastructure/ops/istio/README.md e automation/docs/gmud-operations.md.

## Plano anterior — snapshot de antes da aprovação

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

</details>

</details>


</details>
