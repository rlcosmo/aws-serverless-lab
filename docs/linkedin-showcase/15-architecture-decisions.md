# Decisões arquiteturais — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

RCL reservado na autoridade persistente existente, sem serviço AWS novo. SQLite AUTOINCREMENT/UNIQUE/BEGIN IMMEDIATE, intent antes do POST, retry ambíguo bloqueado, nenhuma renumeração histórica. IDs internos preservados; versão lida do código por AST. Portal é só apresentação/decisão autenticada, sem chave de publisher. Labels e metadados RCL propagam contexto, nunca concedem autorização. Rollback/cancelamento não libera números nem conta como sucesso. Mudança externa do GLPI sem intent correspondente bloqueia, sem bypass bidirecional.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

# Decisões arquiteturais — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Decisões vigentes

- Kestra determina autorização; Bedrock opcional/desabilitado, sem novas chamadas com quotas zero.
- Criticidade protegida, GLPI Change nativo, identidade imutável e journal antes dos efeitos. Retry ambíguo exige reconciliação.
- Histórico real GLPI, cinco sucessos auditáveis distintos por app/ambiente; dados sintéticos excluídos.
- Publisher exclusivo e assinatura no destino; CI solicita e publica imagem, sem chave GitOps. Administradores permanecem fronteira privilegiada.
- Canary somente Worker e sem alegação de pesos de tráfego SQS; bootstrap humano explícito e ligação Canary normal pendente.
- Deploy validado não encerra GMUD: Review8 durante12h, Closed6 apenas após janela limpa; rollback nunca é sucesso.
- Sem NLB/CloudTrail, novas inferências ou aprovação API pelo agente.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# Decisões arquiteturais

| Decisão | Justificativa | Estado |
|---|---|---|
| Kestra determinístico por criticidade | API humana; Worker elegível automático com evidências completas | Defaults sem IA testados; gate integrado pendente |
| Bedrock opcional e desabilitado | Preservar adaptador regional sem dependência obrigatória nem chamadas com quota zero | Probe remoto disabled=true, revisão2 |
| Portal humano separado da autoridade | HTTPS, identidade Kestra allowlisted, CSRF e decisão vinculada; portal não publica GitOps | Implantado e fronteira HTTP validada; release real pendente |
| SNS/KMS existentes | Reutilizar assinatura confirmada e criptografia; mínimo acesso à chave/tópico | Teste aceito, mailbox não confirmado |
| Publisher GPG exclusivo e recibo Ed25519 | Vincular release e consumo único; destino deve recusar assinaturas alheias; bootstrap fora do GitOps | Testado em Git temporário; enforcement não ativado |
| CI envia referências | Não aceitar claims de aprovação, testes ou enforcement vindos do solicitante | Workflows/SSM locais preparados; coletor local testado |
| Mesma fila, concorrência limitada | Evitar fila/roteador novos; não prometer pesos exatos SQS | Canary local preparado; EKS pendente |
| Lease e drenagem antes de retirar candidata | Perda do controlador interrompe novos polls; mensagem iniciada pode concluir | Testado isoladamente |
| Sem Argo Rollouts nesta etapa | Pesos HTTP não resolvem consumo SQS; controlador novo não demonstrou benefício necessário | Nenhuma instalação |
| Exigir fontes de evidência autenticadas | Não substituir testes/Trivy por claims do CI | Actions read pendente na instalação do App; cutover bloqueado |
| Preservar NLB/CloudTrail adiados | Não são dependências indispensáveis demonstradas deste escopo | Nenhuma alteração |

Administradores do host/Kestra/cluster continuam fronteira privilegiada; não prometer resistência a comprometimento administrativo. Os riscos históricos de MFA/telemetria pública permanecem documentados, sem remediação nesta execução.

</details>

</details>
