# Segurança da publicação — estado consolidado

## Revisão de execução —06/11/2026

Consulta real: 2026-11-06T11:30:15.400580+00:00. API 2.0.2-lab / RCL000004 / GLPI8: OBSERVING, aprovação humana autenticada pelo responsável. Worker 1.0.4 / RCL000006 / GLPI10: OBSERVING, Canary COMPLETE, aprovação automática condicionada. Nenhuma aprovação da API pelo agente.

Artefatos públicos omitem tokens, cookies, conta/ARNs, IPs internos e principal pessoal. Evidências textuais/JSON são consultas reais sanitizadas. Não publicar screenshot-placeholder como captura nem declarar12h concluídas.

Carga real com dados sintéticos: 800 respostas202 e 0 erros HTTP; três pedidos consultados como COMPLETED. API/SQS/DynamoDB reais; pagamento e expedição são simulações explícitas do laboratório. Startup Istio15021 com5s, sem a falha de conexão anterior nos testes desta rodada. Readiness503 pode ocorrer durante drain deliberado; reinícios e eventos estão registrados por teste.

As janelas de12h continuam abertas, sem encerramento antecipado. Rollback solicitado pelo responsável após promoção ainda não foi executado. Capturas reais de UI e suas anotações seguem pendentes; placeholders não são prints. Bedrock permanece opcional/desabilitado, sem inferências. Nenhuma operação NLB/CloudTrail ou recurso AWS novo; custo variável de chamadas/carga/telemetria não isolado.

## Histórico preservado desta atualização

<details><summary>Snapshot anterior (não é o estado vigente)</summary>

# Segurança da publicação — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

Portal preserva autenticação/autorizações/CSRF/Origin/auditoria; CSS e clipboard JS são autorizados por hashes CSP, sem unsafe-inline ou dependências externas. GET autenticado200 e anônimo401 confirmados nas três RCLs; nenhum POST de aprovação em produção pelo agente. Ativos visuais/evidência pública foram revisados sem tokens, conta AWS, IPs privados ou identidade pessoal. Capturas continuam placeholders claramente identificados.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

# Segurança da publicação — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Revisão de publicação atual

O material visual omite conta AWS, ARNs, IPs, tokens e destinatários. Ícones oficiais AWS preservados com proveniência em assets/aws. Acesso aos links de aprovação requer identidade do responsável; nenhum token deve ser incluído em URL/imagem.

Capturas reais ainda não disponíveis. Os quatro placeholders estão rotulados, sem interface simulada, e não devem ser usados como evidência. Antes de substituir, redigir identidade/e-mail, conta, endereços privados, cabeçalhos/cookies/CSRF, secrets e logs sensíveis. Só então adicionar setas/legendas e registrar origem/data/hash.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# Segurança da publicação

## Estado vigente — 2026-11-06T00:44Z

Kestra determinístico por criticidade; Bedrock opcional e desabilitado. Probe remoto
disabled=true revisão2, portal atualizado e healthcheck200. 101 testes locais e
Ruff passaram. Gate integrado/publisher/enforcement/Canary e rollback reais
continuam pendentes; instalação do GitHub App requer aceitação de Actions read.
Nenhuma aplicação promovida, nova inferência ou SNS Publish nesta retomada.
Plano em [10](10-action-plan.md), provas em [14](14-evidence-index.md).

Os trechos anteriores de preparação são históricos e não anulam esse estado. NLB e CloudTrail permanecem fora do escopo.


Checklist editorial; nenhuma caixa implica remediação executada.

- [ ] Revisar capturas e documentos para conta AWS, ARNs, IPs, tokens, cookies, chaves, campos de autenticação e URLs administrativas.
- [ ] Não publicar snapshots de Secrets Manager, kubeconfigs, Terraform state/plan, ledgers de aprovação, dumps ou arquivos temporários de evidência bruta.
- [ ] Manter destinatário de aprovação e identidade humana real somente na configuração privada necessária; anonimizar e-mail e nome nas capturas públicas.
- [ ] Não exibir chave privada do gate/CSRF nem credenciais do GitHub App. Uma chave pública de verificação não é credencial de assinatura.
- [ ] Validar metadados, OCR, abas, histórico do terminal e painéis de rede das imagens.
- [ ] Não mostrar métricas financeiras, créditos ou quotas pessoais de telemetria.
- [ ] Revisar histórico Git e artifacts antes de tornar qualquer repositório público. Nenhum scan integral do histórico foi realizado aqui.
- [ ] Distinguir saída de teste/moto/ISOLATED_SIMULATION de execução AWS, LLM ou e-mail real.
- [ ] Não declarar gate obrigatório ou prevenção de bypass do ambiente sem fechar as permissões de GitOps/SSM/Argo/Kestra.
- [ ] Não usar link público ou resposta de e-mail para autorizar promoção; validar identidade, challenge e vínculo a digest/execução.
- [ ] Não divulgar observabilidade como segura: acesso anônimo e MFA ausente continuam riscos internos abertos, fora desta correção.
- [ ] Não afirmar reparo NLB, CloudTrail persistente, alta disponibilidade ou prontidão de produção.
- [ ] Revisar licença de imagens/materiais e exceções do scan; testes passados não equivalem a ausência de vulnerabilidades.
- [ ] Obter revisão editorial e autorização do proprietário antes de publicar, mudar visibilidade, fazer commit ou push.

O post06 está escrito para o estado atual de implementação local e teste isolado. Se a intenção for anunciar funcionalidades ativas, aguardar13.


## Atualização desta revisão — 2026-11-05T21:04:49.426224+00:00

- [ ] Não publicar chaves GPG/Ed25519 privadas, GNUPGHOME, ledger com identidade, cabeçalhos Basic, challenges CSRF ou credenciais SNS/Kestra.
- [ ] Revisar diff e fixtures: IDs fictícios dos testes não autorizam publicar IDs reais presentes nos arquivos de configuração.
- [ ] Manter MFA ausente e endpoints anônimos como riscos internos não resolvidos.

</details>

</details>

</details>
