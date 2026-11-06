# Demonstração reproduzível — estado consolidado

## Revisão de execução —06/11/2026

Consulta real: 2026-11-06T11:30:15.400580+00:00. API 2.0.2-lab / RCL000004 / GLPI8: OBSERVING, aprovação humana autenticada pelo responsável. Worker 1.0.4 / RCL000006 / GLPI10: OBSERVING, Canary COMPLETE, aprovação automática condicionada. Nenhuma aprovação da API pelo agente.

Acompanhar as GMUDs pelos links abaixo. Aprovar/rejeitar somente quando a UI indicar revisão humana; concluídas são leitura. Rollback só com identidade autorizada, justificativa, prazo válido e versão atual; após12h usar nova GMUD. Não executar rollback de release já substituída nem aprovar a API em nome do proprietário.

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

## Histórico preservado desta atualização

<details><summary>Snapshot anterior (não é o estado vigente)</summary>

# Demonstração reproduzível — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

1. Abrir GLPI5/6/7 e conferir os mesmos RCLs nos títulos/labels Kestra/portal.
2. Mostrar API RCL000002 pausada; o agente não opera Aprovar/Rejeitar em nome do responsável.
3. Mostrar RCL000001 revertida e RCL000003 em observação, sem esconder falha inicial.
4. Consultar série Prometheus por cosmotech_io_gmud_id=RCL000003 e dashboard, distinguindo SEM DADOS.
5. Conferir carga sintética800 aceitos e amostras COMPLETED; explicitar simulação de pagamento da aplicação.
6. Depois da aprovação humana real, acompanhar API pelo publisher/Argo e cumprir12h reais. Não acelerar relógio/encerrar artificialmente.
7. Revalidar elegibilidade/digest atual antes de rollback, preservar drenagem/journal e exigir nova GMUD após o prazo. Só então produzir capturas definitivas sanitizadas.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

# Demonstração reproduzível — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Runbook de demonstração atual

1. Consultar GMUD3/4 e execuções Kestra vinculadas; demonstrar CI/Trivy/digest verificados, pausa e decisão ainda ausente.
2. Mostrar configuração protegida das três políticas e testes isolados. Não criar histórico falso no GLPI.
3. Mostrar controle assinado e evidência real de signatário recusado. Não disparar nova promoção para capturar print.
4. Responsável decide no portal autenticado. O agente não opera o formulário em seu nome.
5. Após autorização e validação do bootstrap, concluir ligação Canary Worker e testar dados sintéticos rastreáveis, métricas, progressão e drenagem.
6. Validar API somente com autorização humana real; observar12h reais. Não comprimir relógio do ambiente integrado.
7. Capturar UI sanitizada e substituir placeholders; reexportar slides/PDF somente com evidência correspondente.

Rollback fora do prazo exige nova GMUD; concorrente/duplicado/versão substituída bloqueia. Em falha GLPI/Kestra, preservar intent/ledger e reconciliar o efeito real antes de repetir. Não apagar journal, GMUDs ou dados.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# Demonstração reproduzível

Estado atual em10/14. Não executar novamente o probe histórico: está desabilitado. A quota não é pré-requisito do gate determinístico.

## Histórico executado antes da decisão determinística, sem promoção de aplicação

1. Conferir STS, us-east-1, contexto EKS e Git.
2. Validar Terraform, revisar plano direcionado e aplicar somente policy Bedrock/SNS/KMS.
3. Preparar runtime Python isolado; confirmar Converse disponível.
4. Implantar portal decision-only, usuário Linux dedicado, dados privados e rota no HTTPS existente. Testar healthcheck200, anônimo401, autenticado200 e POST com origem inválida403.
5. Criar registro explicitamente de validação, com enforcementfalse/checks negativos, sem autoridade de promoção. Enviar um e-mail TESTE SEM DEPLOY via tópico confirmado. SNS aceitou; não repetir automaticamente.
6. Validar/instalar/executar `ops/promotion/bedrock-probe.yaml`. A execução real falhou por quota0; fail_closed concluiu sem invocar publisher. Esse probe é diagnóstico, não o gate principal.
7. Confirmar API e Worker atuais1/1. Nenhuma imagem/aplicação promovida.

Resultados e IDs sanitizados em14. Código de instalação do portal, unit e snippet nginx estão em `cosmotech-automation/ops/promotion/`. A chave CSRF e configuração operacional ficam fora do Git.

## Simulação local de Canary já executada

No checkout cosmotech-automation, com o ambiente Python existente:

```bash
PYTHONPATH=src /opt/aws-serverless-lab/.venv/bin/python scripts/demo_promotion_canary.py
```

Saída identificada ISOLATED_SIMULATION: Worker autoaprovado com mocks, CANARY_1, CANARY_2, falha, DRAIN_ROLLBACK, aguarda inflight1 e ROLLED_BACK após drenagem. Não acessa AWS, não invoca LLM e não executa deploy.

## Demonstração completa pendente

Após aceitação de Actions read na instalação do GitHub App, concluir as ligações operacionais do gate e validar assinatura/isolamento no destino. Só então iniciar:

1. Releases stable/candidata por digest e evidências verificadas diretamente.
2. Política determinística, Bedrock desabilitado; API aguardando humano; Worker elegível à liberação automática somente com provas completas.
3. Recibo consumido uma vez, staging assinado e Argo sincronizado na revisão esperada.
4. Canary1, observação com amostras mínimas e métricas frescas, Canary2 e nova observação.
5. Dados sintéticos identificados, sem alterar pedidos reais; medir participação efetiva por versão, sem percentuais prometidos.
6. Falha controlada, interrupção de novos polls, conclusão da mensagem em processamento, stable preservada/restaurada e candidata0 somente após prova de drenagem.
7. Registrar incidente/notificação, sync/health final e capturas reais sanitizadas.

Não usar credenciais humanas armazenadas para aprovar em nome do proprietário. Não registrar a demonstração completa como executada antes de haver provas. NLB e CloudTrail não fazem parte dessa sequência.

</details>

</details>

</details>
