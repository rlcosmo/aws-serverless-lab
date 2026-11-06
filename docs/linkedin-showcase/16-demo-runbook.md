# Demonstração reproduzível

Estado atual em10/14. Não executar novamente o probe histórico: está desabilitado. A quota não é pré-requisito do gate determinístico.

## Histórico executado antes da decisão determinística, sem promoção de aplicação

1. Conferir STS, us-east-1, contexto EKS e Git.
2. Validar Terraform, revisar plano direcionado e aplicar somente policy Bedrock/SNS/KMS.
3. Preparar runtime Python isolado; confirmar Converse disponível.
4. Implantar portal decision-only, usuário Linux dedicado, dados privados e rota no HTTPS existente. Testar healthcheck200, anônimo401, autenticado200 e POST com origem inválida403.
5. Criar registro explicitamente de validação, com enforcementfalse/checks negativos, sem autoridade de promoção. Enviar um e-mail TESTE SEM DEPLOY via tópico confirmado. SNS aceitou; não repetir automaticamente.
6. Validar/instalar/executar `ops/promotion/bedrock-probe.yaml`. A execução real falhou por quota0; fail_closed concluiu sem invocar publisher. Esse probe é diagnóstico, não o gate principal.
7. Confirmar API e Worker atuais1/1. Nenhuma imagem/aplicação promovida.

Resultados e IDs sanitizados em14. Código de instalação do portal, unit e snippet nginx estão em `cosmotech-automation/ops/promotion/`. A chave CSRF e configuração operacional ficam fora do Git.

## Simulação local de Canary já executada

No checkout cosmotech-automation, com o ambiente Python existente:

```bash
PYTHONPATH=src /opt/aws-serverless-lab/.venv/bin/python scripts/demo_promotion_canary.py
```

Saída identificada ISOLATED_SIMULATION: Worker autoaprovado com mocks, CANARY_1, CANARY_2, falha, DRAIN_ROLLBACK, aguarda inflight1 e ROLLED_BACK após drenagem. Não acessa AWS, não invoca LLM e não executa deploy.

## Demonstração completa pendente

Após aceitação de Actions read na instalação do GitHub App, concluir as ligações operacionais do gate e validar assinatura/isolamento no destino. Só então iniciar:

1. Releases stable/candidata por digest e evidências verificadas diretamente.
2. Política determinística, Bedrock desabilitado; API aguardando humano; Worker elegível à liberação automática somente com provas completas.
3. Recibo consumido uma vez, staging assinado e Argo sincronizado na revisão esperada.
4. Canary1, observação com amostras mínimas e métricas frescas, Canary2 e nova observação.
5. Dados sintéticos identificados, sem alterar pedidos reais; medir participação efetiva por versão, sem percentuais prometidos.
6. Falha controlada, interrupção de novos polls, conclusão da mensagem em processamento, stable preservada/restaurada e candidata0 somente após prova de drenagem.
7. Registrar incidente/notificação, sync/health final e capturas reais sanitizadas.

Não usar credenciais humanas armazenadas para aprovar em nome do proprietário. Não registrar a demonstração completa como executada antes de haver provas. NLB e CloudTrail não fazem parte dessa sequência.
