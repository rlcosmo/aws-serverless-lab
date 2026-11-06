# CosmoTech AWS Lab — arquitetura e estado real — estado consolidado

## Estado vigente de acesso — consulta nativa Kestra

`laboratorio@cosmotechsolutions.com.br` agora entra no formulário original de https://kestra.cosmotechsolutions.com.br/ com a senha operacional existente. Consulta os mesmos17 fluxos do catálogo administrativo, execuções, logs e dashboards. Admin mantém credenciais, sessões e acessos. Regras antigas abaixo que limitavam essa conta ao portal são históricas.

Como o OSS2.0.8 continua com uma conta nativa global, o acesso adicional é um adaptador protegido no Nginx/portal, não RBAC nativo nem compartilhamento da senha administrativa com o navegador. Sessão opaca Secure/HttpOnly/SameSite=Strict; consultas permitidas, alterações/replay/resume/webhooks bloqueados. Aprovação, rejeição e rollback permanecem no portal com identidade e CSRF. Credencial administrativa só no mapa privado root0600, ilegível pelo serviço do portal. Frontend original preservado.

Validação HTTP real: login204, catálogo de17 fluxos idêntico ao admin, execuções/logs200, consulta real de indicador200, tentativas em recursos inexistentes403, logout204 e acesso após logout401. Sem aprovação ou alteração de fluxo real pelo teste. Admin Basic/cookie200 e login204, inclusive durante breve indisponibilidade controlada do adaptador, com recuperação confirmada. Backend Kestra não foi interrompido. Não há captura de navegador: estes resultados são de protocolo HTTP e fonte da versão instalada.

Evidência: `assets/kestra-native-view-evidence.json`. Código80c3657/d910f15/1063c89; infraestrutura131c443. Testes locais219 +4 subtestes. Sem novas versões de aplicações, GMUDs ou recursos AWS nesta alteração; observação12h continua em aberto. Custos variáveis não isolados.

## Acesso operacional e links CD — correção de06/11/2026

Entrar em https://kestra.cosmotechsolutions.com.br/releases/login como `laboratorio@cosmotechsolutions.com.br`, com a senha existente do laboratório. O alias anterior e o admin foram preservados. O login nativo do Kestra OSS permanece administrativo. `Acompanhar esteira CD` abre etapas/evidências autenticadas no portal; o link técnico usa `/ui/main/executions/...`. Links históricos com `/ui/executions/main/...` recebem308. Validação real: dez links CD200, anônimo401 e zero aprovações pelo teste. Evidência: `assets/operational-email-cd-links-evidence.json`; código59f602f e proxy2f9eae5.

## Referências de imagem por tag — atualização de06/11/2026

Por decisão do proprietário, os Deployments usam o endereço completo do ECR com `worker-1.0.5-16` e `api-2.0.3-lab-19`, sem sufixo `@sha256`. Os dois repositórios são integralmente IMMUTABLE. Digest continua verificado na esteira, registrado nas evidências e utilizado internamente por Canary/rollback. A mudança de formato mantém as versões, decisões e prazos das RCL000007/8; não cria aprovação humana ou nova versão. GitOps continua sendo a fonte oficial. Evidência atual: `assets/tag-only-deployment-evidence.json`. Os exemplos anteriores com tag@digest representam o formato anterior.

## Revisão operacional — 06/11/2026

Estado confirmado em 2026-11-06T12:45:28.826367+00:00. API 2.0.3-lab: aprovação humana autenticada registrada; Worker 1.0.5: aprovação automática pela política. Ambos implantados, Argo CD saudável e em observação. Canary exclusivo Worker concluído com progressão 1→2, promoção e drenagem. Nenhuma aprovação pelo agente.

| RCL | Aplicação / versão | GLPI | Kestra principal | Estado |
|---|---|---|---|---|
| RCL000007 | orders-api 2.0.3-lab | 11 | 7jyFluWNV09PrJqsDc3kVb | OBSERVING |
| RCL000008 | orders-worker 1.0.5 | 12 | 50dZBEpEZFcQPNS8qv56rI | OBSERVING |

Portal principal: https://kestra.cosmotechsolutions.com.br/releases/ · Entrada operacional: https://kestra.cosmotechsolutions.com.br/releases/login. Usuário `laboratorio` criado no portal com hash PBKDF2-SHA256; admin preservado. Kestra OSS 2.0.8 mantém autenticação nativa de administrador; não foi concedido acesso administrativo nativo ao operador. Ações continuam sujeitas a autenticação, CSRF, política e prazo. Decisões futuras como laboratorio dependem da interação real desse usuário; esta API foi aprovada pela identidade admin.

Uma execução `cosmotech.promotion/release_pipeline` por release, com labels RCL/aplicação/versão; scheduler persistente em `cosmotech.operations`. Dez etapas no portal com fatos, horários, duração e evidências; dados históricos sem horário não recebem duração inventada. Execução principal concluída significa entrega inicial, não GMUD encerrada. Filtrar `execution_type=release` para acompanhamento.

Imagens observadas: `worker-1.0.5-16@sha256:…` e `api-2.0.3-lab-19@sha256:…`, com labels de versão e RCL. O número final vem da CI real; a tag aponta para o mesmo digest testado e a referência continua fixada pelo digest. Pods finais: zero reinícios e nenhum Warning na amostra; startup Istio15021 com atraso de5s.

Carga real com dados sintéticos: 800 respostas202, zero erros HTTP, três pedidos consultados como COMPLETED, estoque1800→1000. Janela Canary300s: candidata185,26 e stable101,05 por Prometheus increase; p95≈0,0986s; falhas, poll, visibility e DLQ zero na amostra. Não são contagens exatas de pedidos nem tráfego de produção.

Observação/rollback até 06/11/2026 às21:41:30 (Worker) e21:44:26 (API), horário de São Paulo; UTC07/11 às00:41:30 e00:44:26. Não houve encerramento antecipado. Rollback humano pós-promoção e conclusão real das12h ainda não validados. Rollback automático real da RCL000005 permanece histórico de falha, nunca sucesso.

Indisponibilidade real breve do GLPI foi controlada e recuperada: histórico autenticado200 permaneceu disponível, ações bloqueadas, decisões e efeitos GitOps preservados, zero GMUDs duplicadas. Cache não autoriza promoção. Autenticação real laboratorio: dez detalhes consultados, anônimo/senha incorreta401, acesso nativo Kestra negado e zero POSTs de aprovação no teste.

Sem novos recursos AWS. Custos variáveis de CI, chamadas, mensagens e telemetria não foram isolados. Bedrock desabilitado, sem inferência; NLB/CloudTrail fora do escopo. Capturas reais de UI/anotações permanecem pendentes; diagramas e placeholders não são prints.

### Evidência e utilização deste documento

Arquitetura preservada: GLPI oficial, Kestra gate único, publisher assinado exclusivo, GitOps/Argo CD, EKS/Istio, SQS/DynamoDB e observabilidade. Portal persistente é uma projeção operacional, sem autoridade própria de promoção.

### Commits desta rodada

Automation bb6b9c4; infraestrutura774efd0; Workerdf58807; API8e74c1c. GitOpsAPI ebc0e17; Worker final6a7be69, com etapas intermediárias assinadas registradas na evidência.

<details><summary>Histórico técnico preservado — não representa o estado vigente</summary>

# CosmoTech AWS Lab — arquitetura e estado real — estado consolidado

## Revisão de execução —06/11/2026

Consulta real: 2026-11-06T11:30:15.400580+00:00. API 2.0.2-lab / RCL000004 / GLPI8: OBSERVING, aprovação humana autenticada pelo responsável. Worker 1.0.4 / RCL000006 / GLPI10: OBSERVING, Canary COMPLETE, aprovação automática condicionada. Nenhuma aprovação da API pelo agente.

A arquitetura foi preservada: EKS, SQS/DLQ, DynamoDB, GLPI Change, Kestra, publisher GitOps assinado, Argo CD e observabilidade. Canary exclusivo do Worker; API usa rolling.

Carga real com dados sintéticos: 800 respostas202 e 0 erros HTTP; três pedidos consultados como COMPLETED. API/SQS/DynamoDB reais; pagamento e expedição são simulações explícitas do laboratório. Startup Istio15021 com5s, sem a falha de conexão anterior nos testes desta rodada. Readiness503 pode ocorrer durante drain deliberado; reinícios e eventos estão registrados por teste.

As janelas de12h continuam abertas, sem encerramento antecipado. Rollback solicitado pelo responsável após promoção ainda não foi executado. Capturas reais de UI e suas anotações seguem pendentes; placeholders não são prints. Bedrock permanece opcional/desabilitado, sem inferências. Nenhuma operação NLB/CloudTrail ou recurso AWS novo; custo variável de chamadas/carga/telemetria não isolado.

## Histórico preservado desta atualização

<details><summary>Snapshot anterior (não é o estado vigente)</summary>

# CosmoTech AWS Lab — arquitetura e estado real — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

A arquitetura foi reutilizada: GLPI Change nativo, Kestra como gate, publisher exclusivo e Argo com assinatura exigida; Canary apenas Worker/SQS. RCL global é reservado atomicamente no ledger persistente protegido antes do POST GLPI, sem contador no CI/portal. API mantém estratégia rolling e autorização humana.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

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

</details>

</details>


</details>
