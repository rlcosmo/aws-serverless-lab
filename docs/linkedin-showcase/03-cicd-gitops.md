# CI/CD, gate único e criticidade — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

CI real API42196287796, Worker42196288505 e42197528788: testes/Trivy/publicação e solicitação aprovados. API permanece aguardando humano; CI verde não é deploy. Worker aprovou por policy-engine com dependências revisadas, diff não sensível e controles verificados. GitOps assinado inclui RCL corporativo, ID GLPI nativo, execução, commit/digest e efeito; o CI continua sem chave de escrita.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

# CI/CD, gate único e criticidade — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## CI/CD com GMUD

CI aprovado → GMUD única → criticidade protegida → autorização Kestra → publisher GitOps → Argo CD → validação → observação por 12h → encerramento. API sempre humana; Worker automático apenas quando os controles técnicos e de mudanças sensíveis permitem. Esta primeira release Worker altera workflow/dependências e requer humano.

As CIs reais passaram após correção de apt/libapt-pkg7.0 apontada pelo Trivy; o scan não foi relaxado. Fonte fixada por hash do workflow, commit e digest; recibo assinado e journal durável precedem publicação. Um signatário alternativo foi realmente recusado no Argo, sem operação de sync da aplicação diagnóstica. O publisher assinou apenas o commit de controle, sem mudar os manifests das aplicações.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# CI/CD, gate único e criticidade

A decisão vigente usa Kestra e política determinística. Bedrock é opcional,
desabilitado e não é pré-requisito para Worker. API HIGH exige humano real;
Worker MEDIUM elegível pode seguir automaticamente após evidências e enforcement.

Fluxo de destino: Actions → testes/build/Trivy → ECR por digest → solicitação
SSM → Kestra → política determinística → portal/SNS quando necessário → recibo
único → publisher GPG → Argo com assinatura obrigatória → EKS.

Os CIs locais já estão preparados como solicitantes. Os workflows remotos ainda
usam GitHub App para escrita/merge GitOps; não foram alterados nesta retomada.
A credencial explícita do App não é limitada pelo default Contents read do
Actions. O cutover de CI, publisher, assinatura no destino e SSM confiável deve
ser conjunto, depois de validação; não habilitar `enforcement_verified` antes.

Portal autenticado e SNS existente serão reutilizados; SNS aceitou um teste
anterior, sem comprovação de recebimento. E-mail não aprova. O portal registra
identidade/CSRF vinculados à release, sem publicar. API não foi aprovada pelo
agente e nenhuma aplicação foi promovida nesta retomada.

A instalação GitHub App não concedeu Actions read declarado no App: token com
essa permissão retorna422; consulta aos runs sem ela retorna403. É necessária
aceitação pelo proprietário, conforme [10](10-action-plan.md). O coletor não
aceita claims de checks vindos do solicitante.

101 testes locais e Ruff passaram; isso não demonstra enforcement no destino,
Canary ou rollback real. Consulte [11](11-ai-approval-architecture.md) e
[14](14-evidence-index.md) para fronteiras e provas.

</details>

</details>
