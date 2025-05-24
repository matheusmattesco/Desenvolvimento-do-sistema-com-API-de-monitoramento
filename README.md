# API de Análise Postural por Vídeo

## Descrição do Sistema

Este sistema é uma **API REST** que gerencia usuários e realiza análise de posturas a partir de vídeos enviados pelos usuários, utilizando modelos treinados para reconhecimento postural.

---

## Funcionalidades

### 1. Gestão de Usuários
- **Listar usuários:** Usuários autenticados podem listar todos os usuários cadastrados.
- **Registrar usuário:** Qualquer pessoa pode registrar uma nova conta.
- **Gerenciar usuário (GET, PUT, DELETE):** Usuários autenticados podem obter dados de um usuário específico pelo username, atualizar seus dados ou deletar um usuário.

### 2. Upload e Gerenciamento de Modelo de Classificação
- Usuários autenticados podem fazer upload de um modelo treinado (arquivo `.pkl` ou `.pt`) que será salvo como o modelo ativo utilizado para análises futuras dos vídeos.

### 3. Upload e Análise de Vídeos para Reconhecimento Postural
- Usuários autenticados podem enviar vídeos para o sistema.
- O sistema salva o vídeo e realiza análise para identificar o tempo que a pessoa permaneceu em posturas como sentado, levantado e deitado.
- Os resultados da análise são armazenados e retornados na resposta junto com os dados do vídeo.

### 4. Listagem dos Resultados da Análise
- Usuários autenticados podem listar todos os vídeos analisados com os respectivos tempos em cada postura e links para os vídeos.

---

## Tecnologias Utilizadas

- Django REST Framework
- drf-yasg para documentação Swagger
- Python para processamento de vídeo e análise postural
- Modelos treinados (.pkl, .pt) para classificação postural

---

## Como executar

- git clone https://github.com/matheusmattesco/Desenvolvimento-do-sistema-com-API-de-monitoramento
- cd Desenvolvimento-do-sistema-com-API-de-monitoramento
- docker compose build
- docker compose up -d
- docker exec -it <nome_do_container_django> python manage.py migrate
---

