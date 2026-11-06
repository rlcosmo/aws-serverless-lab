# Observabilidade do Worker — implementação local — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

Canary observado com Prometheus por versão/canal/RCL. A janela qualificada de300s teve increase estimado≈203,16 sucessos candidatos e≈83,16 estáveis, p95≈0,099s; falhas/retries/erros de ack/DynamoDB e DLQ em0 naquela amostra. Esses contadores são estimativas increase do Prometheus, não contagem exata de pedidos únicos. Fonte integral em assets/rcl-live-evidence.json. Dashboard12 painéis instalado em https://grafana.cosmotechsolutions.com.br/d/orders-worker-canary; os painéis do exporter SQS permanecem parcialmente SEM DADOS. O gate consulta SQS/CW diretamente e não trata ausência como zero.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

# Observabilidade do Worker — implementação local — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Observabilidade efetivamente verificada

Os alertas críticos de scheduler/controller-manager expuseram uma lacuna de scrape no EKS. Foram conectados os endpoints oficiais de métricas do plano de controle, preservando as regras e validação TLS: quatro targets ficaram up e os alertas resolveram. Não houve supressão para liberar o gate.

PodMonitor do Worker foi aplicado, mas séries por versão, amostras, p95 e progressão da candidata dependem do bootstrap autorizado. Dashboard preparado não é dashboard integrado validado. Capturas reais de UI continuam pendentes; os arquivos screenshots são placeholders explícitos.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# Observabilidade do Worker — implementação local

## Estado vigente — 2026-11-06T00:44Z

Kestra determinístico por criticidade; Bedrock opcional e desabilitado. Probe remoto
disabled=true revisão2, portal atualizado e healthcheck200. 101 testes locais e
Ruff passaram. Gate integrado/publisher/enforcement/Canary e rollback reais
continuam pendentes; instalação do GitHub App requer aceitação de Actions read.
Nenhuma aplicação promovida, nova inferência ou SNS Publish nesta retomada.
Plano em [10](10-action-plan.md), provas em [14](14-evidence-index.md).

Os trechos anteriores de preparação são históricos e não anulam esse estado. NLB e CloudTrail permanecem fora do escopo.


A observabilidade já existente continua documentada no relatório histórico09. Nesta execução foram preparados código de métricas, PodMonitor e dashboard, sem importação ou deploy. Não afirmar que as novas queries já retornam séries no Prometheus atual.

## Métricas novas no código

| Série | Significado |
|---|---|
| cosmotech_worker_messages_total | Resultado por digest/channel: success após ack, error ou ack_error |
| cosmotech_worker_processing_seconds_bucket/count/sum | Histograma real de tentativa de processamento e ack |
| cosmotech_worker_retries_total | Recebimentos com ApproximateReceiveCount maior que 1 |
| cosmotech_worker_dynamodb_errors_total | Erros AWS na etapa de persistência |
| cosmotech_worker_poll_errors_total | Falhas da chamada SQS receive |
| cosmotech_worker_inflight / draining | Prova operacional para drenagem |
| cosmotech_worker_heartbeat_timestamp_seconds | Frescor do processo de exposição |
| cosmotech_sqs_visible / oldest_age_seconds / dlq_visible | Gauges CloudWatch para fila/DLQ EKS |
| cosmotech_sqs_collection_success / data_timestamp_seconds | Validade e timestamp do dado de fila |

O endpoint /metrics permanece privado e não foi acrescentado ao Ingress público. Labels não incluem IDs de pedido ou receipt handles. Logs/traces preexistentes não foram substituídos. Não inferir sucesso de negócio de health checks ou traces sintéticos.

O coletor de fila é uma função de leitura com cliente injetável; falta conectá-la ao timer/exporter existente e validar permissões. Dado ausente/atrasado é coleta inválida, nunca zero. O PodMonitor seleciona somente Worker por label de componente, separando stable/canary por labels emitidos na aplicação.

## Dashboard preparado

observability/ops/grafana/dashboards/orders-worker-canary.json contém12 painéis com datasource parametrizado: throughput por versão/resultado, P95, retries, persistência, inflight/drain, backlog, idade, DLQ, freshness, amostras e disponibilidade. Json/YAML e métricas foram verificados localmente; fontes/queries instaladas continuam NÃO VERIFICADAS porque não foram implantadas.

Após aprovação, validar cada query com janela e versão corretas, confirmar histogramas e cardinalidade e registrar datasource/revisão. Só então produzir captura real. Um dashboard vazio não é prova de ausência de falhas.

A máquina Canary exige5min por etapa,50 amostras canary e 10 stable, ausência de falhas e fontes atuais. A política inicial limita P95 a 5s, idade a 120s e retries a 10%; esses limites são propostas conservadoras de laboratório, não SLOs calibrados por carga real.

A exposição anônima preexistente de telemetria e MFA ausente continuam no relatório interno, sem correção nesta execução. Não divulgar URLs administrativas ou métricas financeiras pessoais.


## Atualização desta revisão — 2026-11-05T21:04:49.426224+00:00

Revalidação local: dois testes do coletor CloudWatch passaram. Métricas por digest/canal, heartbeat, inflight e draining continuam sem comprovação de séries no cluster. O executor recusa progressão com métricas ausentes; zero inventado não substitui coleta.

</details>

</details>
