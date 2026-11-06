# Artefatos e evidências CosmoTech

- `aws-architecture.{svg,png}`: arquitetura existente, com legenda de estado.
- `cicd-gmud-gitops.{svg,png}`: fluxo CI→GLPI/RCL→Kestra→aprovação→publisher→Argo→observação.
- `worker-canary.{svg,png}`: consumidores SQS, métricas, promoção, drenagem e rollback.
- `rcl-live-evidence.json`: consulta GLPI/Kestra e janela Canary real; não é screenshot.
- `operational-release-evidence.json`: duas execuções release_pipeline, labels, etapas/horários, autoria, retries idempotentes e eventos Canary.
- `operator-auth-evidence.json`: GETs reais autenticados, acesso anônimo/credencial inválida negado, histórico e logs; zero aprovação pelo teste.
- `glpi-outage-recovery-evidence.json`: indisponibilidade real breve, cache visível, ações bloqueadas e recuperação sem duplicação.
- `versioned-pod-images-evidence.json`: imagens tag@digest, labels, versão pública da API, saúde final, saldo e amostras de pedidos.
- `rcl000008-traffic-evidence.json`:800 pedidos sintéticos aceitos em serviços reais; não representa carga de produção.
- `rcl000007-000008-probe-evidence.json`: eventos/reinícios dos pods finais, startup15021 com5s.
- `live-legacy-gate-rejection.json`: execução histórica não autoriza a nova promoção, sem acionar publisher.
- `artifact-manifest.json`: SHA256/tamanho dos artefatos visuais e evidências.

Arquivos anteriores preservam evidências históricas. Sem tokens, senhas, conta AWS ou endereços internos. Não tratar testes isolados ou placeholders como validação integrada. PDFs e PNGs não contêm prints inventados.

- `tag-only-deployment-evidence.json`: migração real para tags ECR imutáveis sem `@sha256`, commits assinados, digests executados conferidos e janelas preservadas. Atualiza somente o formato das referências; registros tag@digest anteriores permanecem históricos.

- `operational-email-cd-links-evidence.json`: login por e-mail, dez acompanhamentos CD autenticados200, acesso anônimo401 e compatibilidade308 de links antigos; zero decisões no teste.

- `kestra-native-view-evidence.json`: login operacional real pelo formulário/API nativo, catálogo idêntico de17 fluxos, logs/execuções/dashboard, negação de alterações e preservação do admin inclusive com adaptador temporariamente indisponível. São resultados HTTP reais; não existe print de browser automatizado nesta rodada.

- `two-replica-release-requests.json`: CIs reais, aliases ECR, propostas HPA2/2, GMUDs9/10 e pausa autenticada; não é prova de implantação ou de novo Canary.

## Retenção por Deployment — 06/11/2026

`replicaset-retention-evidence.json` contém comparação real antes/depois, saúde Argo CD e commits assinados. Não contém capturas de tela nem validação de novo Canary. Consulte `../../replicaset-retention-plan.md` para escopo e limites.
