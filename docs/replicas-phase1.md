# CosmoTech — padronização de réplicas: diagnóstico e plano

> **Escopo corrigido pelo proprietário:** a demanda atual é retenção de ReplicaSets no Argo CD, não escala de pods. Este plano de escala fica como diagnóstico histórico e não deve ser executado para essa finalidade. Ver [plano corrigido](replicaset-retention-plan.md).

**Fase 1 concluída. A Fase 2 não foi executada e exige aprovação.** Snapshot de workloads: `2026-11-06T14:31:01.453432+00:00`. As consultas foram somente de leitura. Não houve alteração de manifests, deploy iniciado pelo agente, tráfego sintético, Terraform apply ou recurso AWS criado nesta fase. Foram criados apenas este documento e o [inventário sanitizado](evidence/replicas-phase1-2026-11-06.json), localmente.

## Resumo e escopo recomendado

Foram encontrados **13 namespaces, 20 Deployments, 4 HPAs, 7 releases Helm e 2 Applications Argo CD destinadas ao EKS**. O cluster usa Kubernetes 1.37 e três nós Spot em duas zonas. Quatorze Deployments de infraestrutura/suporte devem ficar fora da escala automática proposta.

- **Orders API:** versão 2.0.4-lab em 2/2, já distribuída entre dois nós/zonas. Resultado da GMUD anterior, não desta fase.
- **Orders Worker stable:** versão 1.0.5 em 1/1. A candidata 1.0.6 está em 1/1, na etapa CANARY_1 da GMUD anterior, cujo alvo aprovado é HPA 2/2.
- **OTel Collector e Loki Gateway:** candidatos stateless à escala 2, mediante validação e adoção GitOps dos charts existentes.
- **Grafana:** não escalar indiscriminadamente. SQLite e PVC RWO foram confirmados; é necessário um plano de banco/armazenamento compartilhado e preservação de dados antes de distribuir duas instâncias.
- **Canary:** precisa de exceção controlada para 0→1→2→0. Fixar o candidato permanentemente em 2 conflita com preservar a estratégia, a drenagem e o rollback.

O padrão recomendado para aplicações novas é `Deployment.spec.replicas: 2`, sem HPA desnecessário. A retirada dos HPAs Orders exige migrar contratos do CI, publisher e Canary; mantê-los em 2/2 é uma alternativa transitória compatível com a arquitetura atual.

## Inventário completo

### Namespaces

| Namespace | Deployments |
|---|---|
| cosmotech-recovery | 0 |
| default | 0 |
| external-integration | 0 |
| istio-system | 2 |
| kube-node-lease | 0 |
| kube-public | 0 |
| kube-system | 6 |
| kyverno | 4 |
| loki | 1 |
| observability | 4 |
| orders-api | 1 |
| orders-worker | 2 |
| platform-system | 0 |

Namespaces sem Deployments podem conter outros recursos. `cosmotech-recovery`, por exemplo, possui PVCs de recuperação; não excluir seus dados.

### Deployments

| Namespace | Deployment | Desejadas | Prontas | Gestão observada | Tratamento |
|---|---|---|---|---|---|
| istio-system | istio-ingressgateway | 1 | 1 | Helm | Infraestrutura/suporte: preservar |
| istio-system | istiod | 1 | 1 | Helm | Infraestrutura/suporte: preservar |
| kube-system | aws-load-balancer-controller | 2 | 2 | aws-load-balancer-controller | Infraestrutura/suporte: preservar |
| kube-system | cluster-autoscaler | 1 | 1 | manifest/add-on | Infraestrutura/suporte: preservar |
| kube-system | coredns | 2 | 2 | manifest/add-on | Infraestrutura/suporte: preservar |
| kube-system | ebs-csi-controller | 2 | 2 | EKS | Infraestrutura/suporte: preservar |
| kube-system | metrics-server | 1 | 1 | manifest/add-on | Infraestrutura/suporte: preservar |
| kube-system | snapshot-controller | 2 | 2 | manifest/add-on | Infraestrutura/suporte: preservar |
| kyverno | kyverno-admission-controller | 1 | 1 | kyverno | Infraestrutura/suporte: preservar |
| kyverno | kyverno-background-controller | 1 | 1 | kyverno | Infraestrutura/suporte: preservar |
| kyverno | kyverno-cleanup-controller | 1 | 1 | kyverno | Infraestrutura/suporte: preservar |
| kyverno | kyverno-reports-controller | 1 | 1 | kyverno | Infraestrutura/suporte: preservar |
| loki | loki-gateway | 1 | 1 | loki | Ferramenta stateless: avaliar |
| observability | otel-collector-opentelemetry-collector | 1 | 1 | otel-collector | Ferramenta stateless: avaliar |
| observability | prometheus-grafana | 1 | 1 | prometheus | Bloqueio de armazenamento/HA |
| observability | prometheus-kube-prometheus-operator | 1 | 1 | prometheus | Infraestrutura/suporte: preservar |
| observability | prometheus-kube-state-metrics | 1 | 1 | prometheus | Infraestrutura/suporte: preservar |
| orders-api | orders-api | 2 | 2 | Argo CD | Aplicação estável |
| orders-worker | orders-worker | 1 | 1 | Argo CD | Aplicação estável |
| orders-worker | orders-worker-canary | 1 | 1 | Argo CD | Exceção Canary |

CoreDNS, CNI, CSI, Istio, controladores, operadores e suporte de métricas não devem ser escalados pela política de aplicações. Argo CD, GLPI e Kestra de gestão estão fora deste EKS; o Argo no host/k3s existente administra as duas Applications acima.

Há também **4 StatefulSets e 7 DaemonSets**, preservados. Nenhum Job/CronJob foi encontrado no EKS nesta consulta; isso não exclui schedulers externos do Kestra/systemd. Loki, Tempo, Prometheus e Alertmanager mantêm seus StatefulSets e PVCs.

### HPAs e demais mecanismos

| Namespace | HPA | Mínimo | Máximo |
|---|---|---|---|
| istio-system | istio-ingressgateway | 1 | 5 |
| istio-system | istiod | 1 | 5 |
| orders-api | orders-api | 2 | 2 |
| orders-worker | orders-worker | 1 | 1 |

O Worker está temporariamente em HPA 1/1 porque o Canary congela a capacidade da versão antiga. A candidata aprovada propõe 2/2. Não tratar esse estado transitório como edição manual de escala.

Não foram encontradas CRDs de KEDA, VPA ou Karpenter. EKS Auto Mode está desabilitado. O `cluster-autoscaler` está ativo e descobre o ASG por tags; o nodegroup tem mínimo 1, desejado 3 e máximo 3. Já está no teto: falta de capacidade pode resultar em Pods Pending, não em um quarto nó permitido pela configuração atual.

### Helm e Kustomize

| Namespace | Release | Chart | Estado |
|---|---|---|---|
| observability | alloy | alloy-1.15.0 | deployed |
| kube-system | aws-load-balancer-controller | aws-load-balancer-controller-3.6.2 | deployed |
| kyverno | kyverno | kyverno-3.9.2 | deployed |
| loki | loki | loki-20.2.1 | deployed |
| observability | otel-collector | opentelemetry-collector-0.178.2 | deployed |
| observability | prometheus | kube-prometheus-stack-92.17.0 | deployed |
| observability | tempo | tempo-3.2.1 | deployed |

Istio tem rótulos Helm, mas nenhuma release registrada em `helm list`; a documentação local indica instalação com `istioctl`. Os caminhos Orders reconciliados pelo Argo usam manifests JSON, sem Kustomization.

Somente Orders tem reconciliação Argo ativa observada no EKS. Os values de observabilidade estão em `cosmotech-observability`, mas ter configuração em Git não equivale a um reconciliador GitOps ativo para essas releases Helm.

## Fontes de verdade e conflitos

1. **GitOps Orders:** `rlcosmo/cosmotech-gitops`, caminhos `gitops/apps/orders-api/dev` e `gitops/apps/orders-worker/dev`. A revisão conferida no remoto e no Argo foi `11051addb5283190af516779ba3b126ab65d47d6`. Ambas Applications estavam Synced/Healthy; isso não significa que a GMUD Canary tenha concluído.
2. **Origem das releases:** os diretórios `deploy/dev` dos repositórios de aplicação são lidos pelo coletor Kestra. Editar somente a cópia publicada permite que uma promoção futura restaure a configuração anterior.
3. **Argo ignora réplicas:** há `ignoreDifferences` para `/spec/replicas` em todos os Deployments e `RespectIgnoreDifferences=true`. No modo estático, remover essa omissão dos estáveis; para Worker, restringi-la ao nome exato `orders-worker-canary`. Preservar as exceções de lease e modo dos ConfigMaps.
4. **Prune desabilitado:** remover `hpa.json` de Git não remove o HPA vivo. A migração exige pruning seletivo, autenticado e auditado, exclusivamente dos HPAs aprovados. Não habilitar prune global nem apagar ReplicaSets, PVCs ou Secrets.
5. **Contratos atuais exigem HPA:** os validadores rejeitam `spec.replicas`, exigem cinco arquivos incluindo HPA e permitem limites de 1 a 4. O executor Canary acessa diretamente `resources['hpa.json']`. Apagar os arquivos antes de adaptar esses pontos quebra o fluxo.
6. **Preservar imagens exige caminho de configuração:** os workflows atuais também constroem/publicam imagem em mudanças de `deploy/**`, com label OCI do commit. A Fase 2 precisa reutilizar o digest instalado e produzir evidência/GMUD de configuração, distinguindo seu commit do commit da imagem. Não forjar evidência anterior nem reaproveitar aprovação para um bundle diferente.
7. **Terraform:** `/opt/aws-eks-istio-lab/terraform/ephemeral/eks.tf` define o nodegroup e seu teto, com desired size controlado pelo autoscaler. A integração Terraform define Argo/IAM/documentos SSM que embarcam validadores. Não foi encontrado `helm_release` dono da escala Orders nos diretórios consultados. Não criar um segundo dono da escala ou executar apply nesta fase.
8. **Worktrees:** existem alterações não relacionadas e arquivos não rastreados. Nenhum foi editado, staged, sobrescrito, rebaseado ou publicado nesta fase.

## Plano de padronização

### Dono único da escala

Preferência para aplicações stateless: manifest final com `spec.replicas: 2`, sem HPA. Templates Helm devem definir `replicaCount: 2` e desabilitar autoscaling; Kustomize deve renderizar 2. Os charts existentes exigem suas chaves reais: `replicaCount` no OTel, `gateway.replicas` no Loki e `grafana.replicas` no kube-prometheus-stack.

Enquanto os contratos antigos forem necessários, manter HPA 2/2 é uma opção transitória. Não manter simultaneamente controles com valores divergentes. A remoção do HPA deve ser coordenada com a migração de ownership, o publisher e o rollback.

### Aplicações futuras e admissão

O onboarding deve cadastrar aplicação, namespace, dono, criticidade e origem CI em configuração protegida. CI não escolhe sua criticidade nem cria sua própria exceção. Em namespaces mistos, como `observability`, selecionar nomes explicitamente; não atingir seus operadores por engano.

Reutilizar Kyverno 1.19.2, já instalado, com `policies.kyverno.io/v1 ValidatingPolicy`. Validar Deployments e o subresource `scale`; exigir HPA 2/2 enquanto esse modo for permitido. A política atual somente audita limites de recursos de Pods e não bloqueia divergências de réplicas.

Iniciar em Audit, testar o escopo e depois habilitar Deny. A exceção Canary precisa de nomes/atores protegidos e compatibilidade com o executor; um rótulo livre não é autorização. Tipos não Deployment e componentes essenciais permanecem fora do match. Kubernetes também oferece ValidatingAdmissionPolicy; não é necessário instalar outro controlador.

### Adoção GitOps das ferramentas

Adotar releases Helm existentes com o mesmo nome, chart, versão e values, sem reinstalação. Conferir diff sem mudanças fora dos alvos. Preservar Secrets existentes: renderização de chart com senha aleatória pode rotacionar credenciais se a referência atual não for mantida.

O kube-prometheus-stack e o Loki incluem recursos fora do alvo de réplica; sua adoção precisa manter StatefulSets, operadores e volumes intactos. Não colocar um mesmo recurso sob duas Applications ou continuar executando upgrades Helm imperativos depois da adoção.

O Grafana usa SQLite, PVC `grafana-data` de 5 GiB RWO e estratégia Recreate. RWO restringe montagem a um nó; dois pods no mesmo nó não entregam a distribuição desejada. Para duas instâncias distribuídas, planejar banco compartilhado, backup, retorno e eventual orçamento. Não criar RDS ou migrar dados automaticamente nesta fase.

### Canary e rollback

O candidato permanece em 0 quando inativo, progride 1→2, promove, drena e retorna a 0. Com stable 2 e candidate 2, há quatro pods Worker; com API 2, seis pods Orders, sem contar surge/terminação. Manter dois candidatos permanentemente acrescenta consumo em espera e muda o fluxo, portanto não é recomendado.

Os Deployments Orders têm `maxSurge: 1` e `maxUnavailable: 0`. Desejado 2 não significa limite físico de dois pods em todo instante de rollout. Não alterar essa estratégia ou pesos de tráfego apenas para impor um teto físico.

A GMUD9 está em observação até `2026-11-07T02:12:36.340917+00:00`, ou 23:12:36 de 06/11 em São Paulo. A GMUD10 ainda está em CANARY_1, sem janela de observação iniciada. Sua última amostra lida tem zero sucessos de negócio e p95 ausente: não valida progressão. Nenhuma carga sintética foi enviada nesta Fase 1.

Não modificar bundles assinados, renumerar RCLs, abreviar observação ou aprovar pelo responsável. Uma política Deny que exija 2 durante o congelamento atual em 1 bloquearia o executor. Remover HPA também pode invalidar rollbacks que dependem do formato anterior. Aguardar a conclusão/decisão da esteira e das janelas, ou aprovar uma migração compatível e testada antes do cutover. Não inserir uma política nova silenciosamente em um recibo antigo.

## Capacidade e custos

Requests efetivos dos pods incluem sidecars e init containers. Uso é uma amostra instantânea de `kubectl top`; não é benchmark nem simulação de scheduling. Os nomes dos nós foram anonimizados.

| Nó | Zona | CPU alocável/solicitada (m) | RAM alocável/solicitada (MiB) | RAM em uso (MiB) | Folga de requests RAM (MiB) |
|---|---|---|---|---|---|
| node-01 | us-east-1a | 1930/950 | 3141.8/1282 | 2207 | 1859.8 |
| node-02 | us-east-1a | 1930/1290 | 3141.8/3040 | 2068 | 101.8 |
| node-03 | us-east-1b | 1930/1400 | 3141.8/2318 | 2249 | 823.8 |

A folga é desigual: um nó tem pouca memória disponível por requests. Há folga agregada para a réplica adicional Orders na amostra, mas scheduling depende também de zona, volumes, afinidade e margem para Canary/surge. Não aumentar o teto de nós sem aprovação financeira.

| Cenário de escala estável | Pods adicionais | CPU adicional solicitada | RAM adicional solicitada |
|---|---|---|---|
| Orders estáveis em 2/2 | 1 | 150m | 192 MiB |
| Orders + OTel + Loki Gateway | 3 | 250m | 320 MiB |
| Incluindo Grafana: hipótese bloqueada | 4 | 350m | 448 MiB |

Os deltas consideram estáveis e não descontam a futura remoção do candidato já ativo. Loki Gateway não declara requests: zero no somatório não significa consumo real zero. Dois candidatos Worker acrescentam estimativamente 300m e 384 MiB ao cenário sem candidatos. Surge e pods em terminação exigem margem adicional.

Com os mesmos três nós, a escala de pods não acrescenta cobrança EC2 por nó. Pode aumentar logs, métricas, transferência e armazenamento; não afirmar custo total zero. As APIs oficiais AWS forneceram as cotações abaixo para us-east-1, com 730 h/mês e disco raiz gp3 de 20 GiB confirmado no launch template ativo.

| Hipótese de nó adicional, não autorizada | Compute USD/mês | Disco USD/mês | Total parcial USD/mês |
|---|---|---|---|
| c7i-flex.large Spot | 22.48 | 1.60 | 24.08 |
| c7i-flex.large On-Demand | 61.90 | 1.60 | 63.50 |

Spot varia: equivalência mensal não é preço garantido nem fatura observada. Valores não incluem impostos, câmbio, banco do Grafana, telemetria ou tráfego adicional. Nenhum nó foi provisionado e o limite atual não permite um quarto nó. Não houve atividade NLB, CloudTrail ou Bedrock.

## Arquivos previstos para a Fase 2

Nenhum dos arquivos abaixo foi modificado nesta fase. A lista distingue cópias publicadas, origens das aplicações e validadores externos; alterar só uma cópia não resolve o padrão.

| Repositório | Arquivos | Mudança prevista |
|---|---|---|
| `cosmotech-orders-api` | `deploy/dev/deployment.json`, `deploy/dev/hpa.json` | Static 2 após migração ou HPA 2/2 transitório, preservando imagem/configuração |
| `cosmotech-orders-worker` | `deploy/dev/deployment.json`, `deploy/dev/hpa.json` | Mesmo padrão estável; preservar estratégia e controles do Worker |
| Ambos os apps | `scripts/validate_deployment.py`, `.github/workflows/orders-ci.yml` ou `worker-ci.yml`, testes | Validar capacidade final; tratar configuração sem reconstruir/promover outra imagem; manter controles técnicos |
| `cosmotech-gitops` | `gitops/apps/orders-api/dev/deployment.json`, `hpa.json`; equivalentes Worker | Publicação assinada pelo writer exclusivo; nenhuma edição direta em main |
| `cosmotech-gitops` | `gitops/apps/orders-worker/dev/canary-deployment.json`, `canary-control.json`, `stable-control.json` | Preservar escala dinâmica e lease; não fixar 2 no candidato |
| `cosmotech-gitops` | `gitops/bootstrap/orders-application.yaml`, `orders-worker-application.json` | Remover ignore de réplicas estáveis no modo estático; manter exceção Canary/controles |
| `cosmotech-gitops` | `scripts/validate_app_manifests.py`, `validate_dev_image.py`, `tests/test_configuration_bundle.py` | Migrar contrato de cinco arquivos/HPA sem enfraquecer digest, hash ou limites de paths |
| `cosmotech-automation` | `src/automation/trusted_evidence.py`, `gitops_publisher.py`, `controlled_publisher.py`, `gate_runner.py` | Vincular alteração de configuração à imagem instalada e à aprovação correta; deleção limitada ao HPA autorizado |
| `cosmotech-automation` | `src/automation/canary_delivery.py`, `delivery_runtime.py`, testes de Canary/publisher/rollback | Compatibilidade com escala estática, baseline, drenagem e históricos HPA |
| `cosmotech-infrastructure-iac` | `ops/argocd/validate_app_manifests.py`, `sync-orders-gitops.sh`, `apply-worker-control-ignore.py`, `promotion-enforcement.yaml` | Validação, sync e bootstrap compatíveis; pruning seletivo, sem prune global |
| `cosmotech-infrastructure-iac` | `terraform/environments/dev/orders_gitops_sync.tf`, `promotion_stage.tf`, `ops/promotion/flows/release_pipeline.yaml` | Atualizar contratos embarcados somente se necessário; revisar planos e pins, sem invalidar execuções pendentes |
| `cosmotech-observability` | `ops/helm/values/otel-collector.json` | `replicaCount: 2`, após validação OTLP e adoção GitOps |
| `cosmotech-observability` | `ops/helm/values/loki.json` | `gateway.replicas: 2`, preservando Loki StatefulSet/storage |
| `cosmotech-observability` | `ops/helm/values/prometheus.json` | `grafana.replicas: 2` somente após plano HA; preservar operadores, Prometheus, Alertmanager e Secrets |
| Novos em `cosmotech-gitops` | `gitops/environments/dev/replica-policy.json`, `gitops/policies/application-replicas.yaml`, `gitops/bootstrap/observability-application*.yaml` | Registro protegido, admissão seletiva e adoção sem reinstalação |
| Novos em `cosmotech-gitops` | `templates/application/deployment.yaml`, `templates/application/kustomization.yaml`, `charts/cosmotech-application/values.yaml`, validação CI | Default 2 no resultado renderizado e onboarding obrigatório |
| Legados | `/opt/aws-serverless-lab/scripts/deploy_eks.sh`, `ops/kubernetes/orders/*-deployment.yaml`; `/opt/aws-eks-istio-lab/kubernetes/namespaces/*-deployment.yaml` | Reconciliar ou documentar descontinuação para não reintroduzir 1 por bootstrap; não executá-los em paralelo ao GitOps |

Não modificar nodegroup, CoreDNS, CSI, CNI, Istio, Argo de gestão ou arquivos não relacionados apenas para uniformizar números.

## Ordem de implementação após aprovação

1. Confirmar aplicações incluídas, exceção Canary, abordagem Grafana e modo estático versus HPA transitório.
2. Reconciliar a esteira anterior e a compatibilidade das janelas de rollback. Capturar imagem, digest, configuração, owners e históricos; preservar backups e aprovações.
3. Preparar PRs dos contratos, configuração e templates. Renderizar charts pinados e testar saídas. A mudança de capacidade não deve publicar outra imagem.
4. Pelo Kestra/GLPI/publisher exclusivo, estabelecer um dono da escala e publicar o estado 2. No modo estático, retirar somente os HPAs selecionados após a migração, com pruning controlado. Não substituir Deployments ou apagar ReplicaSets.
5. Adotar ferramentas Helm com diff sem efeitos nos demais recursos. Grafana permanece bloqueado para escala até aprovação do plano de banco/armazenamento e custos.
6. Validar admissão em Audit, depois Deny, incluindo 1/2/3, `scale`, HPA, labels e exceções. Preservar namespaces de infraestrutura e impedir autoisenção por CI.
7. Criar um Deployment isolado pelo fluxo oficial para demonstrar o default 2 em uma aplicação nova. Usar GMUD e imagem aprovadas, sem alegar validação integrada antes da execução.
8. Validar 2 desejadas/2 prontas, distribuição entre nós, Argo Synced/Healthy e ausência de deriva. Se necessário, propor spread preferencial; uma alteração de agendamento deve ter diff e aprovação, sem isolamento rígido que cause indisponibilidade em falha Spot.
9. Testar Canary/rollback com dados sintéticos autorizados na Fase 2. Parar em Pods Pending, incompatibilidade de PVC, divergência de imagem ou necessidade de nó/banco não autorizado.

## Critérios de aceite e decisões pendentes

- Todos os estáveis incluídos: desejadas 2 e prontas 2 após estabilização. Candidatos seguem a exceção explícita. A saída Helm/Kustomize/GitOps deve comprovar o padrão.
- Nenhum autoscaler altera estáveis para fora de 2. No modo estático, o HPA deixa de reconciliar de fato, não apenas desaparece do Git.
- Imagens/digests, env, Secrets, ConfigMaps, Services, PVCs e estratégia preservados. Não apagar ReplicaSets. Mudanças de agendamento, se necessárias, ficam explícitas no escopo aprovado.
- Aplicação nova prova 2/2 pelo pipeline oficial; entradas 1/3 e alterações de scale fora do padrão são recusadas no escopo. Nenhum bypass ou aprovação em nome de usuário.
- Infraestrutura segue saudável e inalterada pelo padrão. Argo está Synced/Healthy e os campos estáveis deixam de ser ignorados no modo estático.
- Três políticas de aprovação, assinatura, replay protection, publisher exclusivo e rollback preservados. Não abreviar observação de 12h nem apresentar testes isolados como integrados.

**Aprovação pendente:** recomenda-se avançar com aplicações estáveis e ferramentas stateless, exceção Canary controlada e migração coordenada dos contratos. Grafana exige aprovação adicional de seu plano HA antes da escala. Exigir Canary permanentemente em 2 ou Grafana distribuído sem migração conflita com preservar o rollout e os dados. Esses pontos precisam ser resolvidos antes da Fase 2; este relatório não autoriza mudanças sozinho.

## Referências

- [Kubernetes: HPA e propriedade de réplicas](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/).
- [Argo CD: RespectIgnoreDifferences](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/).
- [Grafana: alta disponibilidade com banco compartilhado](https://grafana.com/docs/grafana/latest/setup-grafana/set-up-for-high-availability/).
- [Kyverno: ValidatingPolicy CEL](https://kyverno.io/docs/policy-types/validating-policy/).
- [AWS: preços Spot](https://aws.amazon.com/ec2/spot/pricing/) e [EBS](https://aws.amazon.com/ebs/pricing/). Cotações deste relatório obtidas pelas APIs AWS; não representam fatura ou compromisso de preço.
