# CosmoTech — retenção de ReplicaSets por Deployment

Implementado em 06/11/2026, após confirmação do proprietário: **três ReplicaSets por Deployment em estado estável**, sendo o atual e dois históricos (`spec.revisionHistoryLimit: 2`). Não é uma mudança da quantidade de pods.

| Deployment | Antes | Depois | Pods desejados/prontos |
|---|---:|---:|---:|
| orders-api | 11 | 3 | 2/2 |
| orders-worker | 11 | 3 | 1/1 |
| orders-worker-canary | 7 | 3 | 0/0 |

O controlador Kubernetes removeu 20 ReplicaSets inativos, todos com zero pods. Não houve exclusão manual. As duas Applications Argo CD ficaram Synced/Healthy. A Application Worker pode mostrar seis ReplicaSets, pois contém dois Deployments. Durante rollout incompleto a contagem pode exceder três temporariamente.

## Persistência e segurança

O coletor protegido normaliza a retenção antes do hash/assinatura das evidências. O publisher exclusivo aplica a mesma política a todos os Deployments publicados pelo fluxo oficial, incluindo futuras aplicações e bundles de rollback. A política protegida não pode ser elevada pelo CI. Não foi implantada política de admissão abrangente para recursos criados fora desse fluxo.

O scheduler existente do Kestra reconciliou os três Deployments por commits GitOps assinados. O efeito idempotente `history-limit:2` permite alterar somente esse campo, confere o parent assinado e preserva a prova da release. Não houve nova aprovação ou release das aplicações.

Imagens, templates de pods, réplicas, HPA, Services, Secrets, estratégia Canary e os outros 17 Deployments permaneceram iguais. O rollback controlado utiliza bundles/digests persistidos em GitOps; não depende de conservar todos os ReplicaSets antigos. A retenção reduz as revisões disponíveis para `kubectl rollout undo`.

## Evidências

- Automação: `cdedf49` — 232 testes e quatro subtestes aprovados; Ruff aprovado.
- GitOps API: `49e063910042f7b6b64e3a9d24cee9346613416e`.
- GitOps Worker: `0efb05d2c14a8c1d561fc15fd74c772304bbba21`.
- [Comparação real e verificação das assinaturas](evidence/replicaset-retention-result-2026-11-06.json).
- [Inventário anterior](evidence/replicaset-retention-2026-11-06.json).

Nenhum recurso AWS ou imagem foi criado para esta alteração. Não foi isolado custo monetário das chamadas operacionais. O Worker 1.0.6 já havia sofrido rollback antes desta tarefa: o stable está em 1.0.5 e o candidato inativo; esta manutenção não valida um novo Canary. A API permanece em 2.0.4-lab. Não houve encerramento antecipado de observação.

O [diagnóstico anterior sobre escala de pods](replicas-phase1.md) é histórico e não deve ser executado para resolver retenção.

[Política de limpeza Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#clean-up-policy).
