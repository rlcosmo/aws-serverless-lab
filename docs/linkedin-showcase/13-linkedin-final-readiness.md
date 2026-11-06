# Prontidão para publicação — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

Publicável como relato parcial com evidências. Worker Canary completo nesta release, observação12h aberta; API candidata ainda depende do proprietário. Carrossel/diagramas/PDF atualizados, sem prints simulados. Não anunciar laboratório integralmente concluído, rollback responsável pós-promoção validado ou cinco GMUDs reais bem-sucedidas. Capturas definitivas e12h completas continuam pendentes.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

# Prontidão para publicação — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Prontidão para publicação

Material adequado para relato parcial com limites explícitos; não para anunciar laboratório concluído. Entregues diagramas e carrossel/PDF de revisão. Faltam aprovação do responsável, bootstrap Worker, ligação Canary, testes integrados das duas aplicações e janela real12h, além das capturas sanitizadas de UI.

Aprovações não foram realizadas pelo agente. SNS aceitou mensagens, mas recebimento na caixa postal não foi comprovado. Não se atribui a testes locais a condição de integração validada. Actions read já está resolvido; Bedrock não é pré-requisito.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# Prontidão para publicação

**Gate completo, Canary e rollback integrados ainda não estão validados.**
O texto06 pode ser revisado como relato da evolução, sem alegar integração completa.

- [x] Decisão registrada: Kestra determinístico; Bedrock opcional e desabilitado.
- [x] 101 testes locais da automação e Ruff passaram.
- [x] Probe remoto desabilitado, revisão2; nenhuma inferência nesta retomada.
- [x] Portal atualizado, active e healthcheck200; nenhum humano foi representado pelo agente.
- [ ] Proprietário aceita Actions read na instalação do GitHub App.
- [ ] Adaptadores e fluxo principal integrados; cutover publisher/assinatura/CI validado.
- [ ] Tentativa real de bypass bloqueada no destino.
- [ ] Recebimento SNS confirmado e aprovação humana de release API registrada pelo proprietário.
- [ ] Canary somente Worker, métricas/progressão/rollback reais com dados sintéticos.
- [ ] Capturas sanitizadas e alegações conferidas com evidências.

Liberação de quota Bedrock não é critério de prontidão deste desenho.
Nenhuma publicação LinkedIn ou push ocorreu nesta retomada. Riscos históricos
permanecem documentados; não alegar alta disponibilidade ou prontidão de produção.

</details>

</details>
