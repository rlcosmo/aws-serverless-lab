# Canary real de consumidor SQS — código local, ativação pendente — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

Integração real Canary Worker concluída para RCL000003:1→2 consumidores,300s/amostras por etapa, promoção de1.0.2, drenagem comprovada e candidata escalada a0. SQS distribui consumo; não há pesos HTTP prometidos. Observações persistidas no journal do controller, lease180s e reconciliação por agendamento Kestra.

RCL000001 comprovou aborto/drenagem da candidata preservando stable, não reversão de uma stable já promovida. O fluxo de rollback responsável exige autenticação, justificativa, prazo, digest atual e inflight zero. Retomada da versão restaurada exige imageID do manifest correto em pod realmente Running; imagem de configuração não é aceita como digest de deploy. Isso tem testes isolados; reversão responsável pós-promoção ainda precisa de execução real autorizada.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

# Canary real de consumidor SQS — código local, ativação pendente — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Limite atual Canary e rollback

Canary é exclusivo do Orders Worker, por consumidores da mesma SQS; não são percentuais de tráfego HTTP. Controller/lease/drain/limites e métricas têm testes isolados. Ainda não há candidata ativa no EKS, progressão real ou rollback integrado. Nenhuma carga sintética foi enviada nesta etapa.

Rollback preparado: responsável autenticado informa justificativa; até 12h após validação; controle de versão atual/CAS, idempotência e exclusão concorrente. Worker deve parar novos polls e comprovar inflight zero antes de restaurar; sem comprovação, bloqueia. Versão substituída ou resultado ambíguo exige análise humana. Após 12h, nova GMUD.

Scheduler persistente Kestra verifica a observação; não há processo temporário esperando 12h. Lacunas de amostragem acima de180s, incidentes, falha ou mudança de digest impedem fechar como sucesso. A janela real não começou.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# Canary real de consumidor SQS — código local, ativação pendente

## Estado vigente — 2026-11-06T00:44Z

Kestra determinístico por criticidade; Bedrock opcional e desabilitado. Probe remoto
disabled=true revisão2, portal atualizado e healthcheck200. 101 testes locais e
Ruff passaram. Gate integrado/publisher/enforcement/Canary e rollback reais
continuam pendentes; instalação do GitHub App requer aceitação de Actions read.
Nenhuma aplicação promovida, nova inferência ou SNS Publish nesta retomada.
Plano em [10](10-action-plan.md), provas em [14](14-evidence-index.md).

Os trechos anteriores de preparação são históricos e não anulam esse estado. NLB e CloudTrail permanecem fora do escopo.


## Escolha

Stable e canary competem na mesma fila, cada pod processando uma mensagem por vez. Controlar capacidade e medir resultados é mais simples do que criar fila/roteador novos. Filas separadas dariam roteamento explícito, porém mudariam produtor, IAM, custos e operação. Pesos HTTP Istio não distribuem mensagens SQS. Não instalar Argo Rollouts para simular esse controle.

Runtime mantém long poll20s, visibility180s e DLQ/retries existentes. Usa ApproximateReceiveCount para medir reentregas. Checkpoints e transação de estoque existentes preservam idempotência dos efeitos simulados. Não alterar contrato, tabela ou lease de negócio nesta fase. Teste moto comprova duplicidade entre dois processadores sem repetir reserva; falha real de nó/Spot continua possível.

## Etapas propostas

| Etapa | Capacidade | Condições |
|---|---|---|
| Baseline | Stable instrumentado; canary 0 | Release própria aprovada; métricas e contrato compatíveis; folga de capacidade |
| Canary1 | Stable1 + canary 1 | Gate válido; lease renovada; aguardar capacidade antes de analisar |
| Observação1 | Mesma capacidade | Pelo menos300s,50 tentativas canary e 10 stable; fontes atuais |
| Canary2 | Stable1 + canary 2 | Nova janela exclusiva da etapa e mesmos critérios |
| Promoção | Atualizar stable ao digest candidato via publisher | Confirmar revisão/digest e Argo Synced/Healthy; manter proteção contra regressão |
| Finalização | Drain canary e depois0 | Provar inflight 0 e stable candidato disponível/sincronizado; restaurar política HPA original via configuração revisada |

Os limites são iniciais de laboratório: qualquer falha de processamento/ack/persistência, DLQ crescendo, P95 > 5s, idade > 120s, retries > 10%, versão errada, disponibilidade insuficiente ou dados ausentes/stale interrompem a progressão. Sem amostras suficientes, esperar até 30 min e então drenar; nunca promover só por tempo decorrido. Os thresholds precisam ser calibrados após teste autorizado.

## Rollback

Máquina persiste DRAIN_ROLLBACK e emite modo drain, restauração do stable original e notificação. Não emite replicas0 imediatamente. Só finaliza ROLLED_BACK após prova fresca de canary drenado, inflight 0 e stable original disponível/sincronizado. Falta de prova mantém drain e pede intervenção; não mata uma mensagem para cumprir timeout.

O código canary exige lease JSON renovada: expiração180s, máximo300s aceito. Se coordenador parar, o consumidor deixa de iniciar polls quando observar expiração. Um receive já aberto pode retornar; sua mensagem não iniciada é devolvida com visibility0, sem ack. A mensagem já processando termina. Liveness não força restart durante drain/trabalho. Renovador e orçamento de atraso de ConfigMap ainda precisam ser implantados/medidos.

## Recursos preparados

Renderer gitops/scripts/render_worker_canary.py gera bundle fora da árvore observada, com canary 0 e lease expirada. Selectors stable/canary são distintos; Service atual não passa a misturar seus pods. HPA stable temporariamente min=max 1; nenhum HPA controla canary. O executor será o dono da capacidade temporária, e Argo precisa ignorar apenas replicas canary e campo de lease; self-heal não pode competir.

PodMonitor e dashboard estão em observability. O coletor SQS é read-only. Ainda falta ligar o executor idempotente de efeitos ao GitOps/Argo, renovação de lease, notificação e queries reais. A máquina hoje emite dados; não executa mudanças no cluster.

## Evidência disponível e pendente

Disponível: testes unitários de progressão, falhas, drain, restart e rollback; runtime testado com mocks/moto; simulação explicitamente rotulada, sem AWS ou LLM. Pendente: stable/canary reais processando dados sintéticos autorizados, distribuição medida por digest, painel válido, rollback observado e registro correspondente no Kestra/Argo. Estratégia da API não foi alterada.


## Atualização desta revisão — 2026-11-05T21:04:49.426224+00:00

O executor local aplica somente efeitos vinculados ao ledger confiável, com journal por geração e lease limitada. Resposta de deploy ambígua exige reconciliação, não retry cego. Callbacks de staging/promoção/restauração precisam ser ligados ao publisher exclusivo e ao estado Argo antes de ativar. O mock de rollback não comprova efeitos Kubernetes.

</details>

</details>
