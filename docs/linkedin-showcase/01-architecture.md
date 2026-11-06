# CosmoTech AWS Lab — arquitetura e estado real — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Arquitetura atual

EKS executa Orders API → SQS/DLQ → Orders Worker → DynamoDB. Reutilizamos os serviços de observabilidade e ITSM existentes. O gate de promoção pertence ao Kestra; criticidade protegida não pode ser alterada por CI/IA. GLPI usa o objeto nativo Change, com vínculo imutável de release/commit/digest/aplicação/ambiente/execução.

A assinatura GPG é exigida no projeto Argo. O CI perdeu a chave de escrita GitOps, mantém publicação ECR e solicita promoção por documento SSM fixo. A fronteira administrativa privilegiada permanece; isso não equivale a impedir um administrador de alterar políticas.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# CosmoTech AWS Lab — arquitetura e estado real

## Estado vigente — 2026-11-06T00:44Z

Kestra determinístico por criticidade; Bedrock opcional e desabilitado. Probe remoto
disabled=true revisão2, portal atualizado e healthcheck200. 101 testes locais e
Ruff passaram. Gate integrado/publisher/enforcement/Canary e rollback reais
continuam pendentes; instalação do GitHub App requer aceitação de Actions read.
Nenhuma aplicação promovida, nova inferência ou SNS Publish nesta retomada.
Plano em [10](10-action-plan.md), provas em [14](14-evidence-index.md).

Os trechos anteriores de preparação são históricos e não anulam esse estado. NLB e CloudTrail permanecem fora do escopo.


Escopo vigente: integrar Kestra determinístico e Canary somente do Orders Worker, com Bedrock opcional desabilitado. NLB e CloudTrail foram retirados da execução ativa por orientação posterior do proprietário. Propostas anteriores permanecem históricas, sem execução.

## Ambiente observado

Região us-east-1; EKS aws-eks-istio-lab-dev ACTIVE, versão 1.37. A leitura atual confirmou três nós Ready em duas AZs e um pod Worker Running, com seu container de aplicação pronto e sem restarts. Conta STS e ARN do contexto coincidem. Seis repositórios foram inspecionados; alterações anteriores do checkout /opt foram preservadas. Não houve mudança de autenticação.

A arquitetura de referência usa instâncias privadas, ALB com ACM/WAF, EKS para aplicações e ferramentas, Argo em K3s separado e Kestra em host de gestão. O fluxo de negócio é API→SQS→Worker→DynamoDB, com fila/DLQ EKS distintas do fluxo serverless. Os dados da auditoria inicial continuam em 09 como histórico com janela de coleta própria. Não revalidamos todos os componentes nessa execução restrita.

A leitura autenticada confirmou Kestra 2.0.8 OSS e plugin-ai instalado, inclusive ChatCompletion. Argo /api/version informou v3.6.1. Os workflows atuais ainda publicam no GitOps via GitHub App. Eles não foram modificados ou publicados nesta execução; a API em operação ainda não tem o novo gate humano obrigatório.

## Implementação local acrescentada

O repositório automation contém motor determinístico de promoção, schema da IA, classificação conservadora de manifests, assinaturas Ed25519, ledger SQLite, construção de notificação e verificação de identidade/challenge. O fluxo nativo de avaliação foi validado pelo parser do Kestra, mas continua em arquivo .disabled. Não possui publisher nem credenciais GitOps.

O Worker recebeu consumo controlado por lease/drain, métricas reais no código por digest/channel e tratamento separado de falha de processamento, persistência e ack. O renderer GitOps prepara stable 1, HPA fixado1 e canary inicialmente0; a progressão proposta é uma e depois duas instâncias canary, com janelas de observação. O bundle é produzido fora do diretório observado pelo Argo. Nenhum recurso ou estratégia de deploy da API foi alterado.

## Fronteiras e pendências

IA opcional não concede autoridade; somente política determinística e identidade humana autorizada podem liberar. As entradas do motor devem vir de adapters de evidência e identidade confiáveis. Um booleano enviado pelo solicitante não comprova enforcement. Assinatura de recibo não substitui proteção do caminho GitOps.

Faltam conectar e validar os transports de solicitação/evidência/publicação, a aprovação humana no endpoint autenticado, SNS e executor de efeitos/lease. Não há Canary ativo, nova métrica implantada ou rollback real demonstrado.

O laboratório continua sendo ambiente de aprendizado, com Spot, capacidade limitada, pontos únicos e riscos de MFA e observabilidade anônima ainda abertos. Não afirmar alta disponibilidade, produção, CloudTrail persistente ou gate obrigatório funcionando.


## Histórico da preparação — anterior à implantação parcial

Bedrock regional Nova Micro foi escolhido para recomendação; publisher GPG e portal autenticado foram implementados localmente. O runtime AWS existente não foi modificado. Plano e fronteiras em10/11.

Na retomada atual, seis módulos foram atualizados no host; o portal segue decision-only. O bloqueio vigente é Actions read não concedido à instalação do App; quota Bedrock não é requisito.

</details>
