> **Atualização real — 06/11/2026:** retenção aplicada por Deployment: API 11→3, Worker 11→3 e Canary 7→3. Vinte ReplicaSets inativos removidos pelo Kubernetes via GitOps assinado; Argo CD Synced/Healthy. Imagens, pods e HPA preservados. Worker atual 1.0.5; candidato 1.0.6 inativo após rollback anterior a esta manutenção. Não anunciar novo Canary validado. Automação `cdedf49`; GitOps `49e0639`/`0efb05d`. [Evidência sanitizada](assets/replicaset-retention-evidence.json). O restante deste documento e o carrossel preservam seus snapshots históricos; não são capturas deste ajuste.

# Canary real de consumidor SQS — código local, ativação pendente — estado consolidado

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

WorkerRCL8: Canary1→2→promoção→drenagem→COMPLETE. Candidate0 após finalização; stable1 saudável. Lease, idempotência, visibility e digest preservados. API usa RollingUpdate, sem Canary. Encerramento12h e rollback humano ainda pendentes.

### Commits desta rodada

Automation bb6b9c4; infraestrutura774efd0; Workerdf58807; API8e74c1c. GitOpsAPI ebc0e17; Worker final6a7be69, com etapas intermediárias assinadas registradas na evidência.

<details><summary>Histórico técnico preservado — não representa o estado vigente</summary>

# Canary real de consumidor SQS — código local, ativação pendente — estado consolidado

## Revisão de execução —06/11/2026

Consulta real: 2026-11-06T11:30:15.400580+00:00. API 2.0.2-lab / RCL000004 / GLPI8: OBSERVING, aprovação humana autenticada pelo responsável. Worker 1.0.4 / RCL000006 / GLPI10: OBSERVING, Canary COMPLETE, aprovação automática condicionada. Nenhuma aprovação da API pelo agente.

RCL000005/Worker1.0.3 sofreu dois reinícios por AccessDenied em ChangeMessageVisibility e rollback após oldest175s exceder120s. A candidata drenou, stable1.0.2 e HPA foram restaurados. A correção IAM tem escopo na fila exata;1.0.4 trata devolução negada sem crash e expõe erros próprios. Poll/visibility errors ou reinícios agora bloqueiam progressão; lease300s já dentro do teto do consumidor acomoda propagação do ConfigMap. RCL000001 abortou por missing_metrics antes da correção de aquecimento. RCL000003 concluiu1→2→promoção→drenagem; a mensagem antiga de coleta não significava rollback dessa release. O runtime agora arquiva erros por etapa/horário e limpa o erro ativo somente após coleta válida, sem reduzir controles. A nova release exercita novamente o fluxo com dados sintéticos reais. A regra de qualidade manteve janela300s,50/10 amostras,p95≤5s e backlog≤120s.

Carga real com dados sintéticos: 800 respostas202 e 0 erros HTTP; três pedidos consultados como COMPLETED. API/SQS/DynamoDB reais; pagamento e expedição são simulações explícitas do laboratório. Startup Istio15021 com5s, sem a falha de conexão anterior nos testes desta rodada. Readiness503 pode ocorrer durante drain deliberado; reinícios e eventos estão registrados por teste.

As janelas de12h continuam abertas, sem encerramento antecipado. Rollback solicitado pelo responsável após promoção ainda não foi executado. Capturas reais de UI e suas anotações seguem pendentes; placeholders não são prints. Bedrock permanece opcional/desabilitado, sem inferências. Nenhuma operação NLB/CloudTrail ou recurso AWS novo; custo variável de chamadas/carga/telemetria não isolado.

## Histórico preservado desta atualização

<details><summary>Snapshot anterior (não é o estado vigente)</summary>

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

</details>


</details>
