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
