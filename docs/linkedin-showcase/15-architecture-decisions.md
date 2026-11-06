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
