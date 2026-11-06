# Carrossel de seis páginas — estado consolidado

> Estado vigente — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

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
