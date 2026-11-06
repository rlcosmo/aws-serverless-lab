# Estado da implantação e retomada

Atualização: 2026-11-06T00:44Z (05/11 no fuso do proprietário).

## Decisão vigente

Kestra deve autorizar por política determinística de criticidade. Esta decisão do
proprietário substitui a exigência anterior de inferência para o Worker.
Bedrock é opcional e desabilitado; quotas zeradas não bloqueiam o desenho
atual. Não fazer novas chamadas enquanto persistirem zeradas.
API HIGH sempre exige humano autorizado; Worker MEDIUM pode ser automático
somente com todas as evidências técnicas verificadas, sem mudança sensível e
com dependências revisadas. Falhas graves não podem ser sobrepostas por humano.
NLB e CloudTrail continuam fora do escopo.

## Resultado desta retomada

| Entrega | Resultado real | Limite |
|---|---|---|
| Política determinística | Default `ai_enabled=false`; CLI, coordinator, verificação Kestra, portal e SNS aceitam ausência de IA | Código dos componentes; não é gate integrado ativo |
| Testes automation | 101 passed; Ruff passou em src/tests | Testes locais; usam mocks, Git/GPG temporários; não são prova integrada |
| Host existente | Seis módulos atualizados, backup local preservado; portal reiniciado, active e healthcheck HTTP200 | Serviço de decisão; sem autoridade de publicação |
| Probe Bedrock | YAML validado sem warnings; revisão2 com `disabled=true` e guarda de execução | Nenhuma execução/inferência nesta retomada |
| Evidências GitHub | App declara Actions read; instalação não concedeu | Token Actions read HTTP422; runs com token contents read HTTP403 nos dois apps |
| Gate/publisher/enforcement | Não ativados | Não foi publicado workflow parcial nem removida credencial do CI antes do cutover |
| Canary/rollback | Não implantados no EKS | Nenhum dado sintético enviado; nenhuma promoção de aplicação |
| SNS | Teste anterior aceito, mailbox continua não verificada | Nenhum novo Publish nesta retomada |

A sequência de atualização do host retornou código7 na primeira leitura imediata
do healthcheck após reinício. A verificação seguinte confirmou active, HTTP200 e
os dois defaults de IA falsos. A atualização do probe já havia sido confirmada;
não foi repetida nem executada inferência.

## Dependência humana confirmada: permissão do GitHub App

App `rlcosmo-cosmotech-gitops`, instalação `178643233`. Os três repositórios
`cosmotech-gitops`, `cosmotech-orders-api` e `cosmotech-orders-worker` já estão
selecionados. O App declara `actions:read`, mas as permissões concedidas à
instalação são apenas `contents:write`, `pull_requests:write`, `metadata:read`.

O proprietário precisa aceitar a atualização **Actions: Read-only** em
[configurações da instalação](https://github.com/settings/installations/178643233).
Não é necessário fornecer chave privada ou token. O cliente runtime pede tokens
por repositório, com Actions read e Contents read para coleta; não usar token
pessoal do proprietário como substituto permanente.

Sem essa aceitação, o coletor não pode verificar diretamente testes/Trivy nos
runs. Não aceitar check enviado pelo CI nem marcar `enforcement_verified=true`
para contornar essa ausência. Nenhuma aprovação de release API foi feita.

## Continuação após a intervenção

1. Revalidar concessão Actions read e consulta autenticada dos runs de ambos os apps.
2. Conectar os adaptadores existentes de GitHub/ECR/diff/Argo/incidentes/observabilidade
   ao fluxo principal `promotion_gate`, sem tarefa Bedrock obrigatória.
3. Integrar portal/SNS, staging/publisher e reconciliação; revisar planos Terraform,
   findings e ativação conjunta. Os documentos SSM/access entry/permissões adicionais
   preparados anteriormente continuam não aplicados nesta retomada.
4. Ativar assinatura verificada no destino, publisher exclusivo, validador/bootstrap
   confiáveis e CI apenas solicitante. Demonstrar tentativa real de bypass bloqueada
   sem interromper as aplicações. Administradores continuam fronteira privilegiada.
5. Instrumentar baseline e ativar Canary somente Worker, sem aumentar nós; verificar
   capacidade, séries reais por digest, amostras/janelas e lease. API aguarda humano real.
6. Demonstrar progressão e rollback com dados sintéticos identificados e drenagem
   comprovada. Atualizar evidências e capturas; não chamar simulação de integração.

## Custos, commits e preservação

Cost Explorer consultado em 06/11 UTC: `UnblendedCost` de 01/11 a 06/11
(exclusivo), excluindo Credit/Refund: **US$33,4835982918**, `Estimated=true`.
É acumulado da conta, com atraso de faturamento; não representa custo incremental
da retomada. Sem inferência, novo SNS Publish, nova instância, controlador, tópico,
chave ou volume. Leituras AWS/Secrets Manager/Cost Explorer e operações SSM podem
ter cobrança; custo incremental exato não apurado.

Commit local automation `e93bef3`; detalhes e validações no índice14. Não houve push, publicação
LinkedIn, alteração dos workflows remotos, apply Terraform ou deploy de aplicação.
O portal conserva ledger/CSRF e o backup de código no host. Nenhuma fila, tabela,
volume, estado Terraform ou histórico Git foi removido. A autorização de execução
anterior e a nova decisão permanecem válidas para a continuação do mesmo escopo.
