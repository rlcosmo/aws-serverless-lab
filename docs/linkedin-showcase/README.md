# CosmoTech Solutions — kit LinkedIn e evidências

Revisão06/11/2026: API2.0.3-lab/RCL000007 e Worker1.0.5/RCL000008 implantados, em observação12h. Canary exclusivo Worker concluído. Os16 documentos preservam os snapshots anteriores em histórico expansível.

- `assets/`: três diagramas de arquitetura/CI-CD/Canary em SVG e PNG; JSONs de execução real com escopo e timestamp; manifesto de integridade.
- `carousel/`: seis páginas1080×1350 em SVG/PNG, folha de contato e PDF para revisão/publicação.
- `screenshots/`: plano e placeholders identificados; capturas reais de UI ainda pendentes. Não usar diagramas como prints de ferramentas.
- `06-linkedin-post.md`: texto pt-BR com contexto Azure/AKS→prática AWS; publicar somente após revisão dos limites.
- `14-evidence-index.md`: fontes, IDs, resultados, pendências e distinção entre testes reais e isolados.

Portal operacional: https://kestra.cosmotechsolutions.com.br/releases/ . Login do operador: /releases/login. Segredos e credenciais não fazem parte do kit. Não afirmar encerramento12h ou rollback humano validado antes da prova real.

Atualização de imagem: Deployments agora usam ECR + tag de versão, sem sufixo de digest. A validação independente do digest e a imutabilidade ECR permanecem obrigatórias. Fonte/evidência: `assets/tag-only-deployment-evidence.json`; implementação automation696d8a8.
