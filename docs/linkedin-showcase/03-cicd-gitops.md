# CI/CD, gate único e criticidade — estado consolidado

> Estado vigente — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

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
