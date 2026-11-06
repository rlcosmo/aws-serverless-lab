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
