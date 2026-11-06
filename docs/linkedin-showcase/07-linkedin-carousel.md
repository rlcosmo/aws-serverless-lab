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
