# Desafios técnicos reais — estado consolidado

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

Troubleshooting desta rodada: visibilidade da versão no pod, separação de execuções técnicas, identidade de aprovador, acompanhamento durante indisponibilidade real do GLPI e tag ECR independente. Causa histórica de rollbackRCL5: backlog175s>120s após falha de permissão/propagação da drenagem; correção já preservada e CanaryRCL8 concluído.

### Commits desta rodada

Automation bb6b9c4; infraestrutura774efd0; Workerdf58807; API8e74c1c. GitOpsAPI ebc0e17; Worker final6a7be69, com etapas intermediárias assinadas registradas na evidência.

<details><summary>Histórico técnico preservado — não representa o estado vigente</summary>

# Desafios técnicos reais — estado consolidado

## Revisão de execução —06/11/2026

Consulta real: 2026-11-06T11:30:15.400580+00:00. API 2.0.2-lab / RCL000004 / GLPI8: OBSERVING, aprovação humana autenticada pelo responsável. Worker 1.0.4 / RCL000006 / GLPI10: OBSERVING, Canary COMPLETE, aprovação automática condicionada. Nenhuma aprovação da API pelo agente.

GLPI falhava no login lembrar-me por INSERT duplicado de token_uid. O patch guardado por imagem/SHA256 preserva UID apenas em Auth::COOKIE; login explícito gera UID novo. Dois logins reais com a conta técnica passaram, com rotação; auto-login por cookie manteve UID. Perfil técnico continua sem acesso à Change UI (403), sem ampliar autorização. Leitura REST das GMUDs assinadas validou IDs/títulos/estados. A senha administrativa armazenada foi recusada; nenhuma credencial foi alterada.

Carga real com dados sintéticos: 800 respostas202 e 0 erros HTTP; três pedidos consultados como COMPLETED. API/SQS/DynamoDB reais; pagamento e expedição são simulações explícitas do laboratório. Startup Istio15021 com5s, sem a falha de conexão anterior nos testes desta rodada. Readiness503 pode ocorrer durante drain deliberado; reinícios e eventos estão registrados por teste.

As janelas de12h continuam abertas, sem encerramento antecipado. Rollback solicitado pelo responsável após promoção ainda não foi executado. Capturas reais de UI e suas anotações seguem pendentes; placeholders não são prints. Bedrock permanece opcional/desabilitado, sem inferências. Nenhuma operação NLB/CloudTrail ou recurso AWS novo; custo variável de chamadas/carga/telemetria não isolado.

Canary: permissão ausente em ChangeMessageVisibility gerou dois reinícios na RCL000005 e backlog175s, superior ao limite120s. Rollback automático restaurou stable1.0.2/HPA. Corrigidos IAM com escopo na fila, tratamento de devolução negada, métricas de controle, bloqueio de reinícios e lease300s. A rodada corretiva1.0.4 completou Canary sem reinícios; evento preservado como falha, sem reescrever o histórico.

## Histórico preservado desta atualização

<details><summary>Snapshot anterior (não é o estado vigente)</summary>

# Desafios técnicos reais — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

A primeira tentativa RCL000001 foi abortada antes de evidências suficientes dos pods; a stable permaneceu disponível. Corrigida espera inicial limitada a90s por etapa, sem renovar lease sem prova ou reduzir janelas/amostras obrigatórias. A nova tentativa possui alteração rastreável no health e versão1.0.2; o RCL anterior não foi reaproveitado. A API inicialmente falhou na leitura do arquivo opcional de versão legado:404 agora tem tipo explícito, com fallback AST;403/rede continuam bloqueando. Retomada a mesma execução, sem GMUD duplicada.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

# Desafios técnicos reais — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Troubleshooting comprovado

1. Trivy barrou apt/libapt-pkg7.0 vulnerável: atualização na imagem base fixada, novas CIs verdes.
2. Validação de URL rejeitava o separador legítimo `compare/a...b`: correção mantém bloqueio de traversal, com regressões.
3. API Kestra 2.0.8 usa `/actions/restart` e `/actions/resume`: corrigido e retomadas as mesmas execuções, sem nova GMUD.
4. EKS access entry já existia: preservada e ampliada de forma aditiva, sem importação duplicada ou substituição.
5. Argo: verificação negativa corrigiu a asserção para o erro GIT/GPG real; zero sync na aplicação diagnóstica.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# Desafios técnicos reais

## SDK Bedrock sem Converse — corrigido no host

**Sintoma:** AttributeError ao chamar Converse. **Impacto:** impossibilidade de avaliar risco com o SDK de sistema. **Investigação:** comparação da versão do SDK no host com o runtime existente de automação. **Causa:** boto3 de sistema antigo. **Correção aplicada:** suporte Python3.12-venv e ambiente isolado com boto3/botocore1.43.122. **Validação:** a chamada passou a alcançar a API e recebeu erro de quota, em vez de método inexistente. **Aprendizado:** disponibilidade do serviço e compatibilidade do cliente são verificações distintas. Os pacotes Python dos serviços existentes foram preservados.

## Portal sem permissão de execução — corrigido

**Sintoma:** systemd203/EXEC. **Impacto:** portal reiniciando sem atender. **Investigação:** journal e namei nos diretórios pais. **Causa:** usuário dedicado sem travessia no caminho do runtime. **Correção aplicada:** travessia dos pais e dados privados do serviço, sem tornar legíveis os diretórios de credenciais. **Validação:** active, healthcheck200; HTTPS401/200/403 nos casos esperados. **Aprendizado:** validar sob a identidade efetiva do serviço e incluir caminhos pais na análise de permissões.

## SNS criptografado — corrigido

**Sintoma:** KMSAccessDenied no Publish. **Impacto:** notificação recusada antes da aceitação. **Investigação:** chave associada ao tópico e policy do publicador. **Causa:** ausência de GenerateDataKey/Decrypt na role de execução. **Correção aplicada:** policy Terraform limitada à chave existente, SNS regional e encryption context do tópico. **Validação:** Publish aceito com MessageId; Access Analyzer sem findings. Recebimento no mailbox não foi confirmado. **Aprendizado:** permissão Publish no tópico não cobre automaticamente sua dependência KMS. A rejeição explícita foi reconciliada antes de repetir; não houve reenvio após aceitação.

## Quota Bedrock zero — não resolvido

**Sintoma:** ThrottlingException, Too many tokens per day. **Impacto histórico:** nenhuma recomendação IA real. Na decisão atual, Bedrock é opcional/desabilitado; a quota não é requisito da promoção determinística. **Investigação:** chamada da EC2, probe no Kestra e Service Quotas. **Causa identificada:** quotas aplicadas TPD/TPM/RPM iguais a zero, apesar de entitlement disponível; motivo administrativo da restrição não determinado. **Correção aplicada:** nenhuma liberação AWS efetuada. O proprietário solicitará à AWS. **Validação:** Kestra FAILED com fail_closed SUCCESS e nenhum publisher acionado. **Aprendizado:** autorização de acesso ao modelo não garante quota utilizável; timeout/retry ou recomendação simulada não resolvem esse bloqueio.

## Canary SQS e fronteira de confiança — correções apenas locais

O código local separa seletores stable/canary, limita concorrência, exige lease, drena mensagens em processamento e mede por versão. Os testes verificaram que não se escala a candidata para zero antes de comprovar drenagem e stable disponível. A simulação não foi aplicada ao EKS.

A inspeção também identificou o sync SSM executando validador/bootstrap da árvore GitOps mutável. A correção local exige validador confiável fora dessa árvore e assinatura GPG; teste Git/GPG temporário rejeitou pai não assinado. Enforcement operacional ainda não ativado. Nenhum desses dois resultados deve ser anunciado como correção em produção.

## Actions read não concedido à instalação — intervenção humana necessária

O App declara Actions read, mas a instalação conserva apenas Contents write, Pull requests write e Metadata read. Tokens por repositório com Actions read retornam422; runs sem essa permissão retornam403. É necessário o proprietário aceitar a atualização da instalação. Não usar claims do CI como evidência confiável nem token pessoal permanente para contornar o bloqueio.

</details>

</details>

</details>


</details>
