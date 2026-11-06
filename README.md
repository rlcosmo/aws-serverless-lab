# CosmoTech — Laboratório AWS Serverless e EKS

Este repositório funciona como **índice do laboratório** e preserva snapshots históricos da migração. O desenvolvimento e a operação ativos foram distribuídos entre repositórios especializados. **Não aplique Terraform nem faça deploy a partir dos snapshots congelados daqui.**

## Repositórios oficiais

- [Infraestrutura e Terraform](https://github.com/rlcosmo/cosmotech-infrastructure-iac): único responsável pelo backend e estado Terraform S3 existentes.
- [RBAC Kubernetes](https://github.com/rlcosmo/cosmotech-kubernetes-rbac): permissões por namespace.
- [GitOps e Argo CD](https://github.com/rlcosmo/cosmotech-gitops): configurações declarativas e entrega EKS.
- [Orders API](https://github.com/rlcosmo/cosmotech-orders-api): API, testes e CI.
- [Orders Worker](https://github.com/rlcosmo/cosmotech-orders-worker): consumidor SQS, testes e CI.
- [Observabilidade e backups](https://github.com/rlcosmo/cosmotech-observability): dashboards, telemetria e recuperação.
- [Automação GLPI e Kestra](https://github.com/rlcosmo/cosmotech-automation): orquestração e gestão de mudanças.

Esses sete repositórios foram extraídos com histórico original preservado. Alguns arquivos-fonte permanecem no IaC como snapshots de bootstrap/build Lambda até a migração das referências de artefatos. O projeto MCP independente não foi afetado pela extração.

## Arquitetura e funcionamento

O laboratório combina Python 3.12/Boto3, Terraform, API Gateway HTTP com IAM, AWS Lambda, SQS, DynamoDB, EKS, Istio e observabilidade. O caminho serverless valida pedidos, publica eventos versionados na SQS e grava registros no DynamoDB com idempotência. O caminho EKS possui aplicações Orders independentes.

O Argo CD é executado numa EC2 privada dedicada com K3s e HTTPS autenticado por ALB existente: https://argocd.cosmotechsolutions.com.br/. O GitHub Actions constrói e publica imagens; o Argo CD entrega API e Worker ao EKS. A política DEV atual dessas aplicações permite promoção automática validada sem aprovação humana. Outras políticas de governança estão documentadas separadamente.

GLPI e Kestra operam numa EC2 privada, publicados pelo ALB:
- https://glpi.cosmotechsolutions.com.br/
- https://kestra.cosmotechsolutions.com.br/

O AWS WAF restringe hosts públicos, limita requisições e mantém rotas de observabilidade restritas ao CIDR administrativo. Bancos de dados e portas dos contêineres permanecem privados.

Consulte [arquitetura](docs/architecture.md), [acesso público, DNS e TLS](docs/public-access.md), [auditoria inicial](docs/initial-audit.md), [entrega Orders](docs/orders-worker-delivery.md), [estado da execução](docs/EXECUTION-STATUS.md) e [requisitos de aprovação de mudanças](docs/itsm-change-gates.md).

## Estrutura do repositório

```text
docs/          Arquitetura, operação e roadmap
scripts/       Scripts de desenvolvimento e apoio operacional
src/           Código Python 3.12 e handlers Lambda (snapshot)
terraform/     Definições Terraform (snapshot; não aplicar daqui)
tests/         Testes unitários e de integração
requirements.txt
```

## Pré-requisitos para testes locais

- Ubuntu 24.04 no WSL2 ou Linux compatível
- Python 3.12 com `venv`
- Git
- AWS CLI v2 e Terraform 1.17 apenas para tarefas que os exijam

Não registre chaves AWS, tokens, chaves privadas ou arquivos de segredos preenchidos. Prefira credenciais temporárias IAM Identity Center ou roles.

## Como executar os testes

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
```

Os testes locais usam Moto e não acessam AWS. O produtor usa `ORDERS_QUEUE_URL`; o consumidor usa `ORDERS_TABLE_NAME`, DynamoDB e verificações condicionais de idempotência. O fluxo API → SQS → Lambda → DynamoDB foi testado com pedido sintético e duplicidade, persistindo um único registro. O Lambda implantado registra a entrada com estado `RECEIVED`. O processamento completo simulado foi testado, mas não implantado: veja [processamento de pedidos](docs/orders-processing.md).

## Artefatos Lambda — apenas validação histórica

```bash
python scripts/build_lambda_artifacts.py
python scripts/validate_lambda_artifacts.py
```

Os ZIPs determinísticos incluem apenas arquivos `.py` próprios de `src/`, sem pytest, Moto ou pacotes SDK; usam boto3/botocore do runtime Lambda Python 3.12. `dist/` é ignorado pelo Git. Reconstrua os artefatos após mudanças de código e antes da validação Terraform histórica.

Para validar sintaxe/formatação **sem acessar o estado remoto**:

```bash
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform/environments/dev init -backend=false -input=false
terraform -chdir=terraform/environments/dev validate
```

**Atenção:** os comandos acima são somente para verificação do snapshot. Aplique mudanças reais exclusivamente pelo repositório `cosmotech-infrastructure-iac`. Não versione state, arquivos de plan, credenciais ou backups. O arquivo `.terraform.lock.hcl` deve ser versionado.

## Custos e operação

O laboratório utiliza recursos AWS sujeitos a cobrança, incluindo EKS, nós Spot, NAT, load balancers, CloudWatch e host ITSM privado `t3.large` com gp3 criptografado e AWS Backup. O projeto não possui teto obrigatório de custo; consulte [estado da execução](docs/EXECUTION-STATUS.md) para medições e evidências atualizadas.

## Entrega, aprovações e recuperação

O GitHub Actions valida Python, artefatos Lambda e Terraform. Documentações históricas descrevem um fluxo DEV protegido com quatro aprovações, OIDC e evidências GLPI; **não confunda esse fluxo legado com a política atual de promoção automática da Orders API/Worker**. Integrações de mudança com aprovação podem depender de autenticação Kestra e GitHub App e devem ser verificadas antes do uso.

Cinco componentes de observabilidade utilizam PVCs criptografados com política Retain e restauração isolada testada. Consulte [recuperação de observabilidade](docs/observability-recovery.md) e [roadmap](docs/roadmap.md).

Para deploy, backup e rollback em produção de laboratório, utilize os procedimentos dos **repositórios oficiais**, não os snapshots deste índice.
