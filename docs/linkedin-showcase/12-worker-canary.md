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
