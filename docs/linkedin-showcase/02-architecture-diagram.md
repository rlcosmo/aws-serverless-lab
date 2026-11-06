# Arquitetura atual e extensão preparada

## Estado vigente — 2026-11-06T00:44Z

Kestra determinístico por criticidade; Bedrock opcional e desabilitado. Probe remoto
disabled=true revisão2, portal atualizado e healthcheck200. 101 testes locais e
Ruff passaram. Gate integrado/publisher/enforcement/Canary e rollback reais
continuam pendentes; instalação do GitHub App requer aceitação de Actions read.
Nenhuma aplicação promovida, nova inferência ou SNS Publish nesta retomada.
Plano em [10](10-action-plan.md), provas em [14](14-evidence-index.md).

Os trechos anteriores de preparação são históricos e não anulam esse estado. NLB e CloudTrail permanecem fora do escopo.


Linhas contínuas: arquitetura de referência/estado observado nas consultas documentadas. Linhas pontilhadas: componentes preparados localmente, sem ativação. Cada vínculo continua sujeito ao escopo e à janela do relatório09.

```mermaid
flowchart TB
  subgraph entrada[Entrada HTTPS]
    U[Cliente] --> ALB[ALB — TLS ACM / WAF]
  end
  subgraph rede[Rede AWS]
    VPC[VPC privada — duas AZs / NAT único]
    NLB[NLB interno — 443 unhealthy; proposta não executada]
  end
  subgraph kube[Kubernetes]
    EKS[EKS 1.37 — três nós Ready]
    Istio[Gateway Istio — HTTP]
    Argo[Argo CD — gestão K3s]
  end
  subgraph apps[Aplicações]
    API[Orders API — estratégia preservada]
    Stable[Worker stable — runtime atual]
    Canary[Worker canary — preparado, inativo]
    ALB --> API
    ALB --> Istio
    ALB --> Stable
    EKS --- API
    EKS --- Stable
    EKS -.-> Canary
  end
  subgraph dados[Mensageria e persistência]
    SQS[SQS EKS]
    DLQ[DLQ EKS]
    DB[DynamoDB — checkpoints / inventário]
    API --> SQS
    SQS --> Stable --> DB
    SQS -. consumidores concorrentes .-> Canary
    Canary -.-> DB
    SQS --> DLQ
  end
  subgraph entrega[CI/CD e GitOps]
    CI[Actions — testes / build / Trivy / ECR]
    Git[GitOps — caminho atual de escrita]
    Kestra[Kestra 2.0.8 OSS]
    AI[Bedrock opcional — desabilitado]
    Gate[Política / identidade / recibo — código local]
    CI --> Git --> Argo --> EKS
    CI -. solicitação futura .-> Kestra
    Kestra -. política determinística .-> Gate
    Kestra -. opcional desabilitado .-> AI
    Gate -. único publisher a integrar .-> Git
  end
  subgraph obs[Observabilidade]
    P[Prometheus / Grafana existentes]
    Traces[Loki / Tempo / OpenTelemetry existentes]
    New[PodMonitor / painel comparativo — preparados]
    Lease[Lease e drenagem — código local]
    Stable --> Traces
    Canary -. métricas por versão .-> New -.-> P
    Gate -.-> Lease -.-> Canary
  end
  subgraph seguranca[Segurança e operação]
    IDs[IAM / Pod Identity / Secrets Manager]
    Audit[CloudTrail persistente — não implementado nesta execução]
    Risk[MFA e telemetria anônima — riscos preservados]
    IDs --- EKS
    VPC --- EKS
    Risk --- P
    Audit --- VPC
  end
```

O caminho atual CI→GitOps continua existindo: o diagrama não apresenta o gate novo como obrigatório. A versão final pós-ativação deve remover esse caminho direto somente após enforcement demonstrado. Pesos HTTP do Istio não controlam consumo SQS e não são usados para representar Canary.


## Integração pretendida após a decisão determinística

```mermaid
flowchart LR
  CI[Actions: testes / Trivy / ECR] -. solicitação SSM .-> K[Kestra: gate único pretendido]
  K -. evidências verificadas .-> P[Política determinística]
  K -. opcional desabilitado .-> B[Bedrock Nova Micro regional]
  P -. API ou revisão .-> H[Portal HTTPS / identidade Kestra / CSRF]
  H -. decisão vinculada .-> K
  P -. Worker elegível .-> K
  K -. recibo Ed25519 .-> G[Publisher exclusivo / commit GPG]
  G -. assinatura exigida .-> A[GitOps / Argo CD]
  A -. API sem mudança de estratégia .-> API[Orders API]
  A -. staging Worker .-> W[Stable + Canary SQS]
  W -. métricas / lease / drain .-> R[Análise e rollback]
  R -. observação .-> O[Prometheus / Grafana]
```
Todas as linhas deste complemento representam a integração preparada/pretendida, ainda sem ativação ponta a ponta. Não são evidência de implantação.


## Componentes implantados e histórico do probe

```mermaid
flowchart LR
  U[Identidade humana autorizada] --> TLS[HTTPS existente]
  TLS --> N[Proxy nginx existente]
  N --> P[Portal de decisão / loopback / usuário dedicado]
  P --> A[Autenticação Kestra]
  P --> DB[Ledger privado de decisões]
  T[Teste explícito sem deploy] --> SNS[SNS + KMS existentes]
  SNS --> M[Assinatura de e-mail confirmada]
  K[Histórico: probe real, agora desabilitado] --> B[Bedrock regional / role EC2]
  B --> Q[Quota zero / ThrottlingException]
  Q --> F[BLOCK: sem publisher]
```

O envio foi aceito pelo SNS; entrega no mailbox e decisão humana de release continuam não verificadas. O fluxo principal de promoção, publisher/GPG no destino e Canary EKS continuam preparados ou pendentes, conforme10.
