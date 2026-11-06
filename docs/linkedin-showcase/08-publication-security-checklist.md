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
