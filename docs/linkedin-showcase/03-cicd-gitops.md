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
