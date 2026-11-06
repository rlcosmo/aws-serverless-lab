# Carrossel de seis páginas — estado consolidado

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

Carrossel de seis páginas1080×1350 em carousel/, SVG/PNG e PDF cosmotech-carousel-review.pdf. Slide4 destaca portal operacional/identidades; slide5 distingue rollback histórico e Canary atual. Revisar PDFs e imagens antes da publicação externa.

### Commits desta rodada

Automation bb6b9c4; infraestrutura774efd0; Workerdf58807; API8e74c1c. GitOpsAPI ebc0e17; Worker final6a7be69, com etapas intermediárias assinadas registradas na evidência.

<details><summary>Histórico técnico preservado — não representa o estado vigente</summary>

# Carrossel de seis páginas — estado consolidado

## Revisão de execução —06/11/2026

Consulta real: 2026-11-06T11:30:15.400580+00:00. API 2.0.2-lab / RCL000004 / GLPI8: OBSERVING, aprovação humana autenticada pelo responsável. Worker 1.0.4 / RCL000006 / GLPI10: OBSERVING, Canary COMPLETE, aprovação automática condicionada. Nenhuma aprovação da API pelo agente.

O carrossel tem seis páginas1080×1350 e PDF vetorial. Inclui GMUDs atuais, aprovação humana/automática, links CD e selo Canary. Ilustrações editoriais são identificadas e não imitam prints reais.

Carga real com dados sintéticos: 800 respostas202 e 0 erros HTTP; três pedidos consultados como COMPLETED. API/SQS/DynamoDB reais; pagamento e expedição são simulações explícitas do laboratório. Startup Istio15021 com5s, sem a falha de conexão anterior nos testes desta rodada. Readiness503 pode ocorrer durante drain deliberado; reinícios e eventos estão registrados por teste.

As janelas de12h continuam abertas, sem encerramento antecipado. Rollback solicitado pelo responsável após promoção ainda não foi executado. Capturas reais de UI e suas anotações seguem pendentes; placeholders não são prints. Bedrock permanece opcional/desabilitado, sem inferências. Nenhuma operação NLB/CloudTrail ou recurso AWS novo; custo variável de chamadas/carga/telemetria não isolado.

## Histórico preservado desta atualização

<details><summary>Snapshot anterior (não é o estado vigente)</summary>

# Carrossel de seis páginas — estado consolidado

## Estado RCL —06/11/2026

RCL000001/GLPI5: Worker1.0.1 abortado por evidência inicial insuficiente; candidata drenada e stable preservada. RCL000002/GLPI6: API2.0.1-lab aguarda aprovação humana. RCL000003/GLPI7: Worker1.0.2 concluiu Canary1→2, promoção e drenagem, em observação até22:04:27Z de06/11 (19:04:27 em São Paulo). Nenhum encerramento12h antecipado; nenhuma aprovação API pelo agente. As GMUDs anteriores não foram renumeradas.

Carrossel reexportado: seis páginas1080×1350 SVG/PNG e [PDF6 páginas](carousel/cosmotech-carousel-review.pdf), com identidade CosmoTech e RCLs reais. Fonte: scripts/build_rcl_review_kit.py, reutilizando o renderizador existente. [Contato visual](carousel/contact-sheet.png). Revisão parcial; não anunciar fechamento12h nem aprovação API. Capturas reais de UI continuam pendentes e os placeholders explícitos não são prova operacional.

## Snapshots anteriores preservados

<details><summary>Histórico técnico anterior (não é o estado vigente)</summary>

# Carrossel de seis páginas — estado consolidado

> Atualização pós-aprovação —06/11/2026: GMUD3/API e4/Worker aprovadas pelo responsável, deploys concluídos e GLPI em OBSERVING/Review8. API e Worker usaram RollingUpdate; Worker foi bootstrap de telemetria, sem Canary. Kestra agora tem labels aplicação/versão/GMUD, inclusive nas duas execuções existentes. Correção da primeira probe Istio aplicada ao injector para novos pods Orders e validada em dois pods reais isolados, sem Warning/restart. Os diagramas/carrossel existentes são snapshots anteriores às aprovações e precisam de revisão antes de publicação definitiva.

> Snapshot anterior às aprovações — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Carrossel entregue para revisão

Seis páginas 1080 × 1350 em SVG/PNG e [PDF de seis páginas](carousel/cosmotech-carousel-review.pdf). [Contato visual](carousel/contact-sheet.png). Roteiro: experiência Azure/AKS e AWS; arquitetura; três políticas; fluxo GMUD; Canary ainda pendente; resultados reais e limites.

Ver [README do kit](README.md). Exportações são diagramas e conteúdo editorial, não screenshots. Não inserir números de desempenho inventados ou apresentar testes sintéticos como deploy real.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# Carrossel de seis páginas

| Página | Conteúdo | Captura real necessária |
|---|---|---|
| 1. CosmoTech AWS Lab | Objetivo profissional, AWS/Azure e limites de laboratório | Capa/diagrama sanitizado, sem selo de produção ou alta disponibilidade |
| 2. Arquitetura AWS | EKS, entrada, aplicação assíncrona e persistência | Nós e deployments atuais; diagrama com preparado versus implantado |
| 3. Kestra determinístico | Política por criticidade; IA opcional e desabilitada | 101 testes locais; probe remoto desabilitado. Gate integrado depende de Actions read no App |
| 4. Criticidade | API humana; Worker condicional no desenho | Portal autenticado e e-mail TESTE SEM DEPLOY; não apresentar como aprovação real de release |
| 5. Canary Worker | Concorrência controlada, lease e drenagem | Por enquanto, execução local legendada SIMULAÇÃO. Captura EKS/Grafana/rollback depende de implantação futura |
| 6. Observabilidade e aprendizado | Evidência, métricas por versão e limites | Dashboards existentes somente com fontes/queries validadas; novo dashboard continua preparado |

Nunca reproduzir credenciais, IDs de conta, IPs, cabeçalhos, e-mail pessoal, rotas administrativas ou chave privada. Cortar ou mascarar antes de exportar. Não gerar capturas falsas. Não anunciar o carrossel como demonstração completa de Canary operacional enquanto13 estiver pendente.

</details>

</details>

</details>


</details>
