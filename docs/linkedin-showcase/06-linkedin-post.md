# LinkedIn — texto revisado conforme as evidências — estado consolidado

> Estado vigente — 06/11/2026 UTC (05/11 em São Paulo). A integração real chegou à aprovação humana das GMUDs 3/API e 4/Worker. CI, coleta, política, GLPI, portal/SNS e controle de assinatura estão ativos. Nenhuma release de aplicação foi promovida nesta etapa; Canary, rollback EKS e a janela real de 12h continuam pendentes. Bedrock opcional/desabilitado, sem novas inferências. As seções históricas abaixo não descrevem necessariamente o ambiente atual.

## Texto LinkedIn — versão honesta para revisão

☁️ Minha experiência profissional recente tem sido principalmente em Microsoft Azure e AKS. No laboratório pessoal CosmoTech Solutions, estou aprofundando a prática em AWS com uma plataforma de pedidos assíncronos em EKS, SQS e DynamoDB.

🔐 Nesta etapa, conectei CI e Trivy ao Kestra e à criação de GMUDs nativas no GLPI. A autorização segue criticidade protegida: API exige humano; Worker pode seguir automaticamente quando os controles permitem; a política customizada exige cinco mudanças reais e bem-sucedidas da mesma aplicação e ambiente.

GitOps com assinatura exigida no Argo CD, identidade autenticada no portal e notificações SNS formam a trilha de controle. Uma tentativa com outro signatário foi recusada no destino. O Trivy também bloqueou uma imagem vulnerável antes da correção e de novas CIs aprovadas.

📊 O troubleshooting passou por métricas do plano de controle EKS: conectei os endpoints oficiais, preservei alertas e confirmei os targets ativos.

O laboratório ainda está em validação: as duas GMUDs aguardam revisão humana. Canary exclusivo do Worker, rollback com drenagem e observação de 12h têm componentes/testes isolados; a demonstração integrada depende das próximas aprovações. Bedrock permanece opcional e desabilitado.

Arquitetura, automação, segurança, observabilidade e práticas SRE — com evidências e limites documentados.

#AWS #AmazonEKS #Kubernetes #GitOps #ArgoCD #Kestra #GLPI #DevOps #SRE #CloudEngineering #Azure #AKS

Não publicar como projeto integralmente concluído. Para um post de conclusão, substituir esta versão somente após validação integrada e nova revisão das evidências.

## Histórico preservado — anterior à integração GMUD atual

<details>
<summary>Consultar registros anteriores (não representam o estado vigente)</summary>

# LinkedIn — texto revisado conforme as evidências

Rascunho publicável como relato de evolução. Não anunciar a integração completa de CD/Canary: ainda está pendente. Publicação não realizada.

---

Minha atuação recente como Senior SRE / Cloud Engineer esteve mais concentrada em Microsoft Azure e AKS. Para retomar e aprofundar a prática com AWS, construí o laboratório pessoal CosmoTech Solutions.

Com experiência em AWS e Azure e certificação AWS Solutions Architect – Associate, organizei uma aplicação de pedidos em torno de EKS, processamento assíncrono com SQS e persistência em DynamoDB. O fluxo de entrega combina testes, análise de vulnerabilidades, imagens no ECR e GitOps com Argo CD.

O foco da evolução foi a confiabilidade das decisões de entrega: políticas determinísticas por criticidade, IA opcional e um Canary adequado a consumidores SQS. Pesos HTTP não controlam a distribuição das mensagens entre Workers; por isso, a estratégia preparada usa capacidade de consumo controlada, métricas por versão e drenagem antes de retirar a candidata.

Nesta etapa, implantei o portal autenticado de decisão e validei o envio de uma notificação de teste pelo SNS. A integração de conectividade Kestra–Bedrock foi executada de verdade, mas a AWS rejeitou a inferência por quotas de conta iguais a zero. A decisão arquitetural atual usa aprovação determinística por criticidade e mantém Bedrock opcional e desabilitado. A quota não é mais requisito da promoção.

Os testes isolados cobrem falhas de IA, evidências incompletas, adulteração e reutilização de aprovação, duplicidade de entrega e rollback com mensagens em processamento. A ativação do gate completo e do Canary no EKS continua pendente; a instalação do GitHub App ainda precisa conceder leitura do Actions para verificar as evidências diretamente. Foram validados 101 testes locais de automação nesta retomada; não apresento a simulação como uma implantação real.

É um laboratório de aprendizado e demonstração, com limitações documentadas. O trabalho reforçou uma prática essencial de SRE: verificar o comportamento e tratar a falta de evidência como motivo para bloquear uma promoção.

#AWS #SRE #Kubernetes #GitOps #DevOps #PlatformEngineering

</details>
