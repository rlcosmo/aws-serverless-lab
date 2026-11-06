# Carrossel de seis páginas — estado consolidado

## Revisão de execução —06/11/2026

Consulta real: 2026-11-06T11:30:15.400580+00:00. API 2.0.2-lab / RCL000004 / GLPI8: OBSERVING, aprovação humana autenticada pelo responsável. Worker 1.0.4 / RCL000006 / GLPI10: OBSERVING, Canary COMPLETE, aprovação automática condicionada. Nenhuma aprovação da API pelo agente.

O carrossel tem seis páginas1080×1350 e PDF vetorial. Inclui GMUDs atuais, aprovação humana/automática, links CD e selo Canary. Ilustrações editoriais são identificadas e não imitam prints reais.

Carga real com dados sintéticos: 800 respostas202 e 0 erros HTTP; três pedidos consultados como COMPLETED. API/SQS/DynamoDB reais; pagamento e expedição são simulações explícitas do laboratório. Startup Istio15021 com5s, sem a falha de conexão anterior nos testes desta rodada. Readiness503 pode ocorrer durante drain deliberado; reinícios e eventos estão registrados por teste.

As janelas de12h continuam abertas, sem encerramento antecipado. Rollback solicitado pelo responsável após promoção ainda não foi executado. Capturas reais de UI e suas anotações seguem pendentes; placeholders não são prints. Bedrock permanece opcional/desabilitado, sem inferências. Nenhuma operação NLB/CloudTrail ou recurso AWS novo; custo variável de chamadas/carga/telemetria não isolado.

## Histórico preservado desta atualização

<details><summary>Snapshot anterior (não é o estado vigente)</summary>

# Carrossel de seis páginas — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

Carrossel reexportado: seis páginas1080×1350 SVG/PNG e [PDF6 páginas](carousel/cosmotech-carousel-review.pdf), com identidade CosmoTech e RCLs reais. Fonte: scripts/build_rcl_review_kit.py, reutilizando o renderizador existente. [Contato visual](carousel/contact-sheet.png). Revisão parcial; não anunciar fechamento12h nem aprovação API. Capturas reais de UI continuam pendentes e os placeholders explícitos não são prova operacional.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

# Carrossel de seis páginas — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Carrossel entregue para revisão

Seis páginas 1080 × 1350 em SVG/PNG e [PDF de seis páginas](carousel/cosmotech-carousel-review.pdf). [Contato visual](carousel/contact-sheet.png). Roteiro: experiência Azure/AKS e AWS; arquitetura; três políticas; fluxo GMUD; Canary ainda pendente; resultados reais e limites.

Ver [README do kit](README.md). Exportações são diagramas e conteúdo editorial, não screenshots. Não inserir números de desempenho inventados ou apresentar testes sintéticos como deploy real.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# Carrossel de seis páginas

| Página | Conteúdo | Captura real necessária |
|---|---|---|
| 1. CosmoTech AWS Lab | Objetivo profissional, AWS/Azure e limites de laboratório | Capa/diagrama sanitizado, sem selo de produção ou alta disponibilidade |
| 2. Arquitetura AWS | EKS, entrada, aplicação assíncrona e persistência | Nós e deployments atuais; diagrama com preparado versus implantado |
| 3. Kestra determinístico | Política por criticidade; IA opcional e desabilitada | 101 testes locais; probe remoto desabilitado. Gate integrado depende de Actions read no App |
| 4. Criticidade | API humana; Worker condicional no desenho | Portal autenticado e e-mail TESTE SEM DEPLOY; não apresentar como aprovação real de release |
| 5. Canary Worker | Concorrência controlada, lease e drenagem | Por enquanto, execução local legendada SIMULAÇÃO. Captura EKS/Grafana/rollback depende de implantação futura |
| 6. Observabilidade e aprendizado | Evidência, métricas por versão e limites | Dashboards existentes somente com fontes/queries validadas; novo dashboard continua preparado |

Nunca reproduzir credenciais, IDs de conta, IPs, cabeçalhos, e-mail pessoal, rotas administrativas ou chave privada. Cortar ou mascarar antes de exportar. Não gerar capturas falsas. Não anunciar o carrossel como demonstração completa de Canary operacional enquanto13 estiver pendente.

</details>

</details>

</details>
