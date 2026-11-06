# Auditoria atualizada — escopo Kestra/IA e Canary

## Estado vigente — 2026-11-06T00:44Z

Kestra determinístico por criticidade; Bedrock opcional e desabilitado. Probe remoto
disabled=true revisão2, portal atualizado e healthcheck200. 101 testes locais e
Ruff passaram. Gate integrado/publisher/enforcement/Canary e rollback reais
continuam pendentes; instalação do GitHub App requer aceitação de Actions read.
Nenhuma aplicação promovida, nova inferência ou SNS Publish nesta retomada.
Plano em [10](10-action-plan.md), provas em [14](14-evidence-index.md).

Os trechos anteriores de preparação são históricos e não anulam esse estado. NLB e CloudTrail permanecem fora do escopo.


A orientação posterior retirou NLB e CloudTrail da execução ativa. Nenhum recurso dessas fases foi alterado. O relatório original abaixo permanece histórico; seus diagnósticos não são prova de implantação atual.

Leitura atual: Kestra 2.0.8 OSS, plugin-ai/ChatCompletion disponíveis; fluxo novo aceito pela validação sem warnings, porém não instalado/executado. Argo informa v3.6.1. Três nós EKS Ready em duas AZs; Worker Running com container de aplicação ready e sem restarts. Identidade/região/contexto conferidos.

Gate: componentes locais e testes concluídos; o caminho atual App→GitOps e a limitação403 de proteções/rulesets continuam. Defaults de workflow read e deploy key GitOps read-only não eliminam a credencial de escrita explícita do App. Rotina SSM/Argo que executa código/bootstrap do repo mutável precisa entrar no enforcement. Não há novo gate obrigatório em operação.

Canary: código de consumo controlado, métricas, máquina de estados, renderer, PodMonitor e dashboard preparados; nenhum deploy ou executor ativo. Testes mostram comportamento em mocks/moto e simulação; não houve mensagem SQS/DynamoDB real alterada, chamada LLM paga ou e-mail enviado.

Riscos anteriores, inclusive MFA ausente e observabilidade anônima, permanecem abertos e não foram corrigidos. Preservar no relatório interno e não anunciar remediação. Estado atual e pendências:10/13. Evidências sanitizadas:14.

---

# Relatório de auditoria — CosmoTech

**Data:** 05/11/2026. Início da coleta: 19:24:51 UTC (16:24:51 America/Sao_Paulo). Auditoria somente leitura, sem remediação, publicação, instalação de ferramentas, alteração de autenticação ou teste transacional/carga/falha.

## Identificação e limites

Antes das consultas de recursos, `aws configure get region`, `kubectl config current-context`, `kubectl config get-contexts -o name` e `aws sts get-caller-identity --region us-east-1` confirmaram região us-east-1 e conta coincidente entre STS e ARN do contexto EKS esperado. O número da conta e identificadores sensíveis de topologia foram omitidos deste pacote. Nenhum outro contexto foi selecionado.

A identidade é usuário IAM com perfil estático, membro de grupo com AdministratorAccess. O uso foi limitado manualmente a leitura; isso não transforma a identidade em uma role read-only. Não houve leitura de Secrets Manager GetSecretValue, arquivos de credenciais, tokens GitHub ou Secrets Kubernetes. Não houve SendCommand, exec em pods, sessão SSM, terraform plan/apply/destroy, merge, push ou deploy nesta execução.

O nome exato `cosmotech-arquitetura-roadmap(1).pdf` não foi localizado. Foi encontrada a variante `/home/lab/cosmotech-repositories/cosmotech-observability/docs/artifacts/cosmotech-arquitetura-roadmap.pdf`. Não há extrator PDF disponível no host ou venv; conteúdo da variante NÃO VERIFICADO, sem instalar ferramentas. O inventário informado pelo proprietário orientou o escopo, nunca o veredito de saúde.

O AGENTS.md diz que o repositório não provisionou recursos, enquanto as APIs mostram ambiente existente. A constatação atual prevalece para inventário; nenhum provisionamento foi atribuído a este checkout sem evidência. Alterações locais anteriores foram preservadas.

**Estados:** FUNCIONAL significa sucesso na verificação limitada indicada; FUNCIONAL COM RESSALVAS tem evidência positiva com limites materiais; PROBLEMA IDENTIFICADO tem desvio observado; NÃO VERIFICADO indica falta de evidência direta suficiente. Uma linha não certifica todo o componente. Dados de coletores existentes são identificados como indiretos.

## Matriz

| Componente | Estado | Evidência | Problema | Recomendação | Prioridade |
|---|---|---|---|---|---|
| VPC, AZs e NAT | FUNCIONAL COM RESSALVAS | E01: VPC available; duas AZs; NAT available | NAT único; failover não testado | Documentar limitação e custo | P1 |
| EC2 | FUNCIONAL | E02: seis running; checks system/instance ok; sem IP público | Saúde do SO não decorre dos checks EC2 | Manter monitoramento de host | P1 |
| SSM | FUNCIONAL COM RESSALVAS | E03: três hosts de gestão Online | Nós EKS não aparecem na lista SSM; sessão não testada | Explicitar escopo; usar roles temporárias | P1 |
| EKS control plane | FUNCIONAL COM RESSALVAS | E04: ACTIVE 1.37; API kubectl acessível | Endpoint público 0.0.0.0/0; logs desabilitados | Revisar acesso e auditoria com estimativa | P1 |
| Node group e nós | FUNCIONAL COM RESSALVAS | E05: Spot ACTIVE sem issues; três Ready em duas AZs | Um tipo Spot; desejado=máximo=3 | Revisar folga e distribuição sem alegar HA | P1 |
| Pods e deployments EKS | FUNCIONAL | E06: nenhum pod com condição problemática/restarts na listagem | Fotografia não mede estabilidade histórica | Guardar janela e evidências sanitizadas | P1 |
| CPU, memória e PVCs | FUNCIONAL COM RESSALVAS | E07: CPU 6–8%; RAM 61–70%; PVCs com uso baixo | Requests de memória até 96.7592% em nó segundo CA | Revisar requests com histórico; não reduzir por CPU baixa | P1 |
| HPA | FUNCIONAL COM RESSALVAS | E06: API/Worker CPU 1%/70%; min1/max4 | Escala por CPU; evento real de escala não testado | Backlog scaling como evolução | P2 |
| Cluster Autoscaler | FUNCIONAL COM RESSALVAS | E08: Healthy; NoCandidates; imagem v1.36.1 | Minor difere do cluster 1.37; teto já atingido | Validar matriz e propor versão compatível | P1 |
| K3s e Argo atual | NÃO VERIFICADO | E09: coletor reporta serviços ativos; API Argo 401 | Sem contexto K3s nem leitura autenticada das Applications | Consultar diretamente sem trocar autenticação existente | P1 |
| Orders API/Worker readiness | FUNCIONAL COM RESSALVAS | E10: HTTP 200 e TGs healthy; pods 2/2 | Uma réplica de cada no mesmo nó; readiness não prova pedido | Validar negócio após autorização | P1 |
| SQS/DLQ EKS | FUNCIONAL COM RESSALVAS | E11: 0 visible/inflight; DLQ 0; visibility180; maxReceive5 | Idade e histórico de consumo não verificados | Correlacionar com métricas e contrato do Worker | P1 |
| DynamoDB | FUNCIONAL COM RESSALVAS | E12: tabelas ACTIVE, KMS, PAY_PER_REQUEST | ItemCount é metadado aproximado; transação não validada | Validar persistência e PITR separadamente | P1 |
| Fluxo de pedido ponta a ponta | NÃO VERIFICADO | E13: código/configuração inspecionados; sem envio de pedido | Nenhum teste transacional autorizado executado | Aprovar teste mínimo controlado antes de alegar sucesso | P0 |
| Fluxo Lambda separado | FUNCIONAL COM RESSALVAS | E14: producer/consumer Python3.12 listados | Execução atual das funções não validada | Distinguir claramente de EKS no case | P1 |
| DLQ serverless | PROBLEMA IDENTIFICADO | E11/E15: 1 visible; alarme ALARM | Mensagem não inspecionada; causa desconhecida | Investigar; não purgar nem redrive automaticamente | P1 |
| ALB e targets | FUNCIONAL COM RESSALVAS | E16: active; targets app/gestão/Istio healthy | TLS policy 2016-08; disponibilidade pontual | Propor política atual após compatibilidade | P1 |
| NLB porta 443 | PROBLEMA IDENTIFICADO | E17: três unhealthy Target.FailedHealthChecks; TG TCP | Gateway só HTTP 80; Service aponta a 8443 | Fechar causa e decidir necessidade com consumidores | P1 |
| ACM | FUNCIONAL | E18: ISSUED; expira 19/05/2027 | Renovação futura não testada | Monitorar expiração e validação | P1 |
| WAF e SG | FUNCIONAL COM RESSALVAS | E19: WAF associado, default Block e regras host/rate; SGs LBs 80/443 públicos | WAF permite hosts de telemetria; não autentica | Conter telemetria antes de divulgar | P0 |
| Telemetria pública | PROBLEMA IDENTIFICADO | E20: Prometheus query/targets, Alertmanager alerts/status, Tempo search HTTP200 anônimo | Exposição de metadados, sinais financeiros e operacionais | Restringir acesso com mudança aprovada e validar consumidores | P0 |
| MFA e administração | PROBLEMA IDENTIFICADO | E21: MFADevices=0; AccountMFAEnabled=0; grupo AdministratorAccess | Identidade IAM administrativa sem MFA cadastrado; perfil estático | Planejar MFA/credenciais temporárias e recuperação segura | P0 |
| IAM Identity Center | NÃO VERIFICADO | E22: list-instances vazio em us-east-1 | Não exclui configuração em outra região | Confirmar região administrativa e desenho de acesso | P1 |
| OIDC CI e IAM consultado | FUNCIONAL COM RESSALVAS | E23: trust main+aud+IDs; ECR por repo; SSM por documento/host | Não é revisão de todas as roles/policies da conta | Completar mínimo privilégio por workload | P1 |
| Pod Identity | FUNCIONAL COM RESSALVAS | E24: seis associações incluindo API e Worker | Credenciais efetivas de cada pod e policies não exaustivamente validadas | Revisar roles e evidência de chamadas | P1 |
| Secrets Manager/KMS | FUNCIONAL COM RESSALVAS | E25: metadados de secrets; EBS criptografado; DynamoDB KMS | Rotação não indicada nos metadados; políticas de chave não auditadas | Revisar ciclo de vida sem ler valores | P1 |
| Kyverno | PROBLEMA IDENTIFICADO | E26: controllers disponíveis; ClusterPolicies items vazio | Presença do controller não prova enforcement; policies namespaced não consultadas | Definir controles necessários e validar cobertura | P1 |
| NetworkPolicies | PROBLEMA IDENTIFICADO | E27: somente isolate-recovery no namespace de recuperação | Sem NetworkPolicy listada em Orders/observabilidade; enforcement CNI não validado | Propor isolamento com mapa de dependências | P1 |
| CloudTrail | PROBLEMA IDENTIFICADO | E28: describe-trails retorna [] | Sem trail retornado; não significa ausência do Event History ou Lake | Revisar cobertura, destino e retenção; estimar custo | P1 |
| Auditoria EKS/SSM | PROBLEMA IDENTIFICADO | E04/E29: logs EKS disabled; documento SessionManagerRunShell InvalidDocument | Retenção de sessões SSM NÃO VERIFICADA | Planejar auditoria e custo; não afirmar sessões gravadas | P1 |
| EBS e AWS Backup | FUNCIONAL COM RESSALVAS | E30: volumes criptografados; vault 22 pontos; jobs consultados COMPLETED; plano 14 dias | Backups concluídos não comprovam restore e consistência | Verificar cobertura, dumps e restauração aprovada | P1 |
| Volumes disponíveis | FUNCIONAL COM RESSALVAS | E30: seis available, total47GiB | Podem ser retenção/recuperação, não lixo comprovado | Mapear PVC/PV/backup/owner antes de propor limpeza | P1 |
| Bancos em EC2 | NÃO VERIFICADO | E09: coletor reporta postgres/glpi-db/kestra-db/clickhouse ativos; RDS vazio | Versão, integridade, retenção e compatibilidade não consultadas diretamente | Leitura do runtime e banco por acesso aprovado existente | P1 |
| Zabbix versão e saúde | FUNCIONAL COM RESSALVAS | E31: apiinfo.version=8.0.0; TG healthy; coletor serviços=1 | Versão do server/binário e estabilidade prolongada NÃO VERIFICADAS | Confirmar runtime antes de propor upgrade | P1 |
| Zabbix AWS discovery e problemas | FUNCIONAL COM RESSALVAS | E32: coletor espelha dois problemas NLB de severidades2/3 | Evidência indireta de integração ELB; descoberta ampla/ações/agentes não validados | Auditar itens unsupported, freshness, agentes e destinatários | P1 |
| Zabbix APM/ClickHouse | NÃO VERIFICADO | E09: coletor diz serviços telemetry/clickhouse ativos | Não prova ingestão APM, tabelas ou compatibilidade de versões | Verificar configuração e consulta autenticada; sem upgrade | P1 |
| GitHub Actions/ECR/GitOps | FUNCIONAL COM RESSALVAS | E33: runs/etapas success; ECR IMMUTABLE; DEV_AUTO_PROMOTE true | Histórico não equivale ao estado atual Argo | Consolidar SHA/digest/revisão e artifact sanitizado | P1 |
| Proteções GitHub | NÃO VERIFICADO | E34: três endpoints de branch protection retornam 403; seis repos privados | Limitação de plano; security_and_analysis null inconclusivo | Revisar controles sem alterar branches/visibilidade | P1 |
| Kestra evidências | FUNCIONAL COM RESSALVAS | E33: steps de reporte success; API anônima401 | Persistência/UI e retenção das evidências NÃO VERIFICADAS diretamente | Conferir execução correlacionada autenticada | P1 |
| Prometheus/Grafana | FUNCIONAL COM RESSALVAS | E35: targets ativos up, queries reais; Grafana database ok | Sem targets/séries Orders/SQS; painéis instalados não validados | Completar evidências e evitar zero artificial | P1 |
| Alertmanager/SNS | FUNCIONAL COM RESSALVAS | E36: receiver SNS configurado; email confirmado; três alertas roteados null | Sem teste de recebimento; Watchdog não valida canal externo | Revisar intenção, runbooks e dependências; teste só aprovado | P1 |
| Regras de alerta | FUNCIONAL COM RESSALVAS | E36:161 regras;6 sem runbook; Scheduler/ControllerDown firing | Falsos positivos prováveis para endpoints gerenciados; dois problemas NLB correlatos | Ajustar aplicabilidade e correlação após aprovação | P1 |
| Logs/traces | FUNCIONAL COM RESSALVAS | E37: JSON trace_id/span_id; Loki labels; Tempo synthetic.cycle | Ingestão Loki Orders e trace transacional completo não comprovados | Validar um pedido e separar sintético do negócio | P1 |
| Custos | FUNCIONAL COM RESSALVAS | E38: coletor existente com snapshot custos success e freshness | Estimativa/cached; sem consulta nova ao faturamento | Revisar bruto/serviço, NAT, LBs, EBS, EC2 e retenção | P1 |

## Evidências e reprodução

Os IDs E01–E38 referenciam os resultados resumidos abaixo e nas linhas da matriz. Todas as chamadas AWS usaram região explícita us-east-1, timeouts de conexão/leitura e paginação padrão da CLI. As consultas são pontuais; recursos criados/alterados durante a janela podem produzir fotografias diferentes. Não há teste de continuidade.

| Evidências | Origem / comandos ou método | Resultado preservado |
|---|---|---|
| E01–E03 | ec2 describe-vpcs/describe-nat-gateways/describe-instances/describe-instance-status; ssm describe-instance-information | VPC disponível; NAT único;6 EC2 com checks OK;3 hosts SSM Online |
| E04–E08 | eks describe-cluster/describe-nodegroup; kubectl get nodes,pods,deployments,services,ingresses,hpa,pvc -A; top nodes; get configmap cluster-autoscaler-status; logs deployment/cluster-autoscaler --tail=30 | Versão1.37, nós Ready e estado CA Healthy; incompatibilidade minor a revisar; reservas impedem scale-down |
| E09–E10 | PromQL lab_ec2_application_service_status/lab_ec2_host_probe_up; GET health/ready; API Argo e Kestra anônimas | Indicadores indiretos de gestão positivos; readiness200; APIs protegidas401 |
| E11–E15 | sqs list-queues/get-queue-attributes (sem ReceiveMessage); dynamodb describe-table; lambda list-functions; cloudwatch describe-alarms | Quatro filas; só DLQ serverless com mensagem; tabelas ACTIVE; alarme correspondente ALARM |
| E16–E18 | elbv2 describe-load-balancers/describe-target-groups/describe-target-health/describe-listeners; acm list-certificates | ALB healthy; NLB 443 unhealthy; TLS termina no ALB |
| E17 | kubectl get endpointslices -A; get gateways,virtualservices -A; get service istio-ingressgateway | Gateway HTTP 80; Service 443→31146→8443; EndpointSlice não comprova listener |
| E19–E20 | wafv2 list-web-acls/get-web-acl/list-resources-for-web-acl; ec2 describe-security-groups; HTTP GET sem credenciais | WAF defaultBlock, rate 1200/300s e allow hosts; consultas de telemetria públicas200 |
| E21–E25 | iam get-account-summary/list-mfa-devices/list-groups-for-user/list-attached-group-policies/get-role/list-role-policies/get-role-policy; eks list-pod-identity-associations; secretsmanager list-secrets | MFA ausente; grupo admin; trust CI restrito;6 associações; só metadados secrets |
| E26–E29 | kubectl get clusterpolicies/networkpolicies -A; cloudtrail describe-trails; sso-admin list-instances; ssm get-document SSM-SessionManagerRunShell | ClusterPolicies vazias;1 NetworkPolicy;trails[];Identity Center[] regional;documento SSM ausente |
| E30 | ec2 describe-volumes; backup list-backup-vaults/list-backup-plans/get-backup-plan/list-backup-jobs | Criptografia; retenção 14 dias;22 recovery points; jobs listados completos |
| E31–E32 | POST JSON-RPC apiinfo.version sem credenciais (método de leitura); PromQL lab_zabbix_problem_active/lab_zabbix_problem_count | API 8.0.0;dois problemas correlatos NLB via coletor |
| E33–E34 | gh run list/run view --json jobs; gh api repos/.../contents/...; actions/variables; branches/main/protection; ecr describe-repositories | Steps success;workflows locais iguais a main remoto;proteção403;ECR imutável |
| E35–E36 | Prometheus GET /api/v1/targets?state=active, /rules?type=alert, /label/__name__/values, /query; Alertmanager /api/v2/alerts e /status; sns list-subscriptions sem destinatários | Targets up;161 regras;6 sem runbook;receivers null específicos;SNS confirmado |
| E37 | kubectl logs API/Worker --tail=20; proxy Kubernetes para Loki /loki/api/v1/labels; Tempo /api/search?limit=3 | Logs JSON sintéticos;labels Loki;traces disponíveis;sem prova de pedido |
| E38 | PromQL lab_aws_cost_mtd_* e lab_collection_* | Snapshot existente com indicador de sucesso;sem novas chamadas Cost Explorer |

Respostas brutas locais temporárias foram mantidas em `/tmp/cosmotech-audit-*.json`, fora do Git, e podem desaparecer com o ambiente. Contêm identificadores operacionais, metadados e amostras de logs; **não publicar esses arquivos**. O registro permanente neste pacote é resumido e sanitizado. Não é um acervo forense imutável. Para uma auditoria reproduzível futura, exportar apenas evidências revisadas e registrar hashes antes de compartilhar.

## NLB: diagnóstico e decisão pendente

O inventário chamou o TG de HTTPS, mas a API informa **TCP**: listener 443 → TG TCP 31146 → NodePort 31146 → pod 8443. Todos os três targets falham no health check TCP de traffic-port. Os TGs de HTTP e status estão healthy; o TG do ALB aponta diretamente ao IP do ingress gateway:8080, usando readiness 15021. Não há encadeamento ALB→NLB nos targets observados.

A única configuração Gateway listada expõe HTTP 80. A hipótese mais forte é ausência de listener TLS efetivo 8443. Security Groups e endpoints foram lidos, mas ausência de listener não foi confirmada no config dump Envoy e conectividade interna não foi testada. Não atribuir causa exclusivamente ao SG nem substituir por health check sempre verde.

**Necessidade:** aparentemente redundante para as rotas públicas auditadas; uso privado/legado NÃO VERIFICADO. Ainda é recurso gerenciado pelo Service LoadBalancer. Antes de propor remoção, ler DNS privado, consumers/configuração e tráfego histórico com escopo definido. Se necessário, projetar TLS e readiness corretos; se legado, apresentar diff declarativo, impacto e estimativa de economia. Nenhuma remoção foi feita.

## Zabbix: limites da confirmação

A API web responde 8.0.0; isso não confirma versão do binário server nem que todos os containers usam release final. O coletor reporta server/web/postgres/clickhouse/telemetry ativos e problemas AWS ELB, sem provar suporte do banco, ingestão APM, cobertura da descoberta, agentes ou ações de notificação. Sem login ou acesso direto ao runtime por mecanismo read-only já configurado, esses itens permanecem NÃO VERIFICADOS.

Não propor upgrade com base em 8.0.0rc3 desatualizado. Comparar imagem/digest/binário e versão do banco às [exigências oficiais8.0](https://www.zabbix.com/documentation/8.0/en/manual/installation/requirements) e à [política de suporte](https://www.zabbix.com/life_cycle_and_release_policy). A [documentação8.0](https://www.zabbix.com/documentation/8.0/en/manual/whatsnew) contempla ClickHouse para histórico/telemetria; isso não comprova que a integração deste laboratório está operacional. Não sugerir downgrade de schema sem caminho suportado, backup e restauração validados.

## Segurança e impacto operacional

Os riscos prioritários são acesso anônimo à telemetria e ausência de MFA no root/administrador. As consultas expõem inclusive séries financeiras e métricas pessoais do coletor. Não foi encontrado vazamento de senha nestas verificações; também não houve scan integral de segredos ou histórico Git, portanto não há atestado de ausência de credenciais expostas.

A listagem sem trails evidencia falta de trail retornado, não ausência de toda auditoria AWS. A resposta vazia do Identity Center é regional. Secrets com Rotation=null não provam credencial comprometida. A política TLS antiga, controle público do EKS e isolamento limitado merecem revisão proporcional ao laboratório. Nenhuma alteração de IAM, WAF, SG, autenticação ou auditoria foi feita.

## Custos e retenção

Não foram criados recursos nem feitas chamadas novas ao Cost Explorer: consultas paginadas têm cobrança segundo a [documentação AWS](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html). Usou-se o snapshot já exportado pelo coletor. Ele é estimado, sujeito a atraso de faturamento, e não representa projeção mensal confiável.

Snapshot de custos coletado em 2026-11-05T15:16:19.333329+00:00: bruto acumulado USD 27.90. Crédito aplicado é praticamente igual ao bruto; o líquido exportado tem pequeno resíduo negativo de precisão. Não interpretar como economia estrutural, ambiente gratuito ou crédito futuro garantido. Esses valores são privados e devem ser removidos de capturas públicas.

Seis volumes available somam 47 GiB, mas podem ser restaurações e retenção intencional; não são desperdício comprovado. Os custos a investigar incluem EC2 de gestão, nodes Spot, EKS control plane, EBS/snapshots, NAT/hora/bytes, ALB/NLB/hora/capacidade, WAF, logs/traces e backup. Não houve orçamento novo, ativação de recomendadores ou limpeza. Nenhuma cifra de economia foi inventada.

## Limitações que impedem conclusões adicionais

Sem contexto K3s/autorização autenticada de portais disponível nesta sessão, não foram confirmados diretamente Applications Argo, dashboards/fontes Grafana, execuções persistidas Kestra, problemas/itens/ações Zabbix, binários/bancos EC2 e APM. Não foram acessados valores secretos para contornar essas limitações. Pod logs, recursos Kubernetes e métricas públicas foram usados quando suficientes para uma verificação limitada.

Também NÃO VERIFICADOS: rollback real, entrega efetiva SNS, restauração atual, PITR/TTL das tabelas, retenção efetiva Loki/Tempo/ClickHouse/S3, política e rotação KMS, grants IAM de toda a conta, enforcement do CNI, estabilidade histórica, auditoria de sessões, varredura integral Git e vulnerabilidades completas das imagens. Esses itens exigem coleta complementar; não classificá-los como funcionais por associação.

## Resultado para publicação

**Prontidão: pendente.** O laboratório tem evidência real de infraestrutura disponível e entrega automatizada DEV. O texto e o carrossel são rascunhos utilizáveis após revisão, mas segurança de exposição e alegações transacionais precisam ser tratadas. Ver [plano de ação](10-action-plan.md). Achados não foram corrigidos nesta execução.

## Validação dos documentos

Dez arquivos Markdown conferidos quanto a links locais, fechamento de blocos de código, espaços finais e padrões de conta/chaves/tokens. Nenhum padrão de credencial foi encontrado nos documentos criados; essa checagem limitada não substitui revisão de segurança. Mermaid não foi renderizado por ferramenta nesta sessão. Testes de aplicação e Terraform não foram reexecutados: não houve mudança de código ou infraestrutura.

Workflows locais coincidem com main remoto no momento da coleta (SHA-256 do conteúdo):

- `cosmotech-orders-api/orders-ci.yml`: `2b6775e21d4b82b6013afbe3bf83036543c8a3d39fde76247678b7ebc1db1fd3`.
- `cosmotech-orders-worker/worker-ci.yml`: `c559566d657a95c5a751a3100ae6e4fb7535bf9d631a8562ce6811f9b97453e2`.
- `cosmotech-gitops/deliver-dev.yml`: `4ff9f88f7cb2296c5f5f4eeb76dd038c23f7a9737edf6ed8094ba17a136415f8`.

Fechamento da revisão documental: 2026-11-05T19:35:00.131815+00:00. As respostas de cada serviço refletem os instantes de consulta ao longo da janela.

## Atualização V1.0 — Fase A (investigação atual)

A configuração efetiva Envoy foi consultada: listeners 8080, 15021, 15090; não há 8443. A ausência do destino TLS do Service é agora confirmada, substituindo a hipótese anterior. NLB 443 continua unhealthy; nenhuma correção/desativação foi executada. ALB termina TLS e encaminha diretamente ao pod;68 amostras por métrica de tráfego NLB retornaram zero; PrivateLink vazio. Decisão proposta: desativar o NLB redundante mediante aprovação, com ressalva de consumidores externos não documentados. Plano, diff, custos e rollback: [relatório da fase](/home/lab/cosmotech-repositories/cosmotech-observability/docs/istio-nlb-retirement.md). Esse checkout privado não é um link público.

Os riscos anteriores de MFA e observabilidade pública permanecem abertos e fora do escopo de correção desta execução. CloudTrail continua sem trails/shadow trails retornados, e list-event-data-stores retornou vazio em us-east-1; implantação não iniciada.


## Atualização desta revisão — 2026-11-05T21:04:49.426224+00:00

| Componente | Estado | Evidência | Problema | Recomendação | Prioridade |
|---|---|---|---|---|---|
| Bedrock | FUNCIONAL COM RESSALVAS na consulta de disponibilidade; inferência NÃO VERIFICADA | get-foundation-model-availability; testes mockados | Role de execução não validada | Autorizar permissão/custo e teste limitado | P0 |
| Publisher assinado | FUNCIONAL em testes locais; runtime NÃO VERIFICADO | Git/GPG efêmeros reais | Argo/SSM ainda sem enforcement novo | Cutover atômico e teste de bypass | P0 |
| Portal / SNS | FUNCIONAL em mocks; runtime NÃO VERIFICADO | testes de autenticação/CSRF/subscriber policy | Sem endpoint/e-mail integrado | Ativar após revisão de identidade | P0 |
| Canary / rollback | FUNCIONAL em simulação; EKS NÃO VERIFICADO | 86 testes automação; 79 Worker; demo isolada | Coleta/execução integrada não demonstrada | Fechar bindings antes de deploy | P0 |

Os riscos históricos de MFA ausente e observabilidade anônima não foram corrigidos. NLB e CloudTrail permanecem adiados.
