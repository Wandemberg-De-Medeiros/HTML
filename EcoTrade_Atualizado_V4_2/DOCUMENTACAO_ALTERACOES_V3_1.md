# Documentação de Alterações - EcoTrade (Versão 3.1)

Esta documentação detalha as alterações implementadas para atender às novas solicitações do cliente, focando na navegação do Administrador e na melhoria da página de Apresentação.

## 1. Alterações na Navegação do Administrador

O link "Cadastro de Usuários" foi removido do sidebar do Administrador e substituído pelo "Histórico de Cadastro de Crédito".

### 1.1. Alterações no Backend (`core/views.py` e `core/urls.py`)

- **Remoção da View `cadastro_view`:** A função `cadastro_view` foi removida/comentada do `core/views.py`.
- **Remoção da Rota `/cadastro/`:** A rota `path('cadastro/', ...)` foi removida/comentada do `core/urls.py`.
- **Nova View `historico_creditos_view`:**
    - Implementada em `core/views.py`.
    - Busca todos os objetos `CreditoCarbono` (exceto os rejeitados) e os envia para o template.
- **Nova Rota `/historico_creditos/`:**
    - Adicionada em `core/urls.py` com o nome `historico_creditos`.

### 1.2. Alterações no Frontend (Templates)

- **Sidebar de Navegação:** Nos templates `index.html`, `requisicoes_registro.html` e `requisicoes_transacao.html`, o item de menu:
    - `<li class="{% if active_page == 'cadastro' %}active{% endif %}"><a href="{% url 'cadastro' %}"><i class="fas fa-user-plus"></i> Cadastro de Usuários</a></li>`
    - Foi substituído por:
    - `<li class="{% if active_page == 'historico_creditos' %}active{% endif %}"><a href="{% url 'historico_creditos' %}"><i class="fas fa-history"></i> Histórico de Créditos</a></li>`
- **Novo Template `historico_creditos.html`:**
    - Criado para exibir a lista de créditos de carbono, com colunas para ID, Produtor, Origem, Volume, Preço e Status.
    - Inclui um link em destaque para a **API Pública** (`{% url 'api_creditos' %}`), atendendo ao requisito de acesso à API por esta tela.

## 2. Melhoria na Estilização e Conteúdo da Página de Apresentação

A página `apresentacao.html` foi totalmente reestruturada e estilizada para incluir mais informações sobre o projeto, mantendo o esquema de cores (Verde/Azul).

### 2.1. Alterações no Frontend (`apresentacao.html`)

- **Estrutura de Conteúdo:** Adicionadas novas seções:
    - **Como Trabalhamos:** Explica o fluxo de registro, marketplace e rastreabilidade.
    - **Idealização e Equipe:** Informações sobre a origem do projeto (Semana Ubíqua UNAMA) e a equipe de desenvolvimento.
    - **Comentários de Usuários:** Depoimentos fictícios para dar credibilidade ao projeto.
    - **Entre em Contato:** Informações de contato (e-mail, telefone, endereço).
- **Estilização:** Utilização de ícones Font Awesome e classes CSS para aplicar um design mais moderno e informativo.

### 2.2. Alterações no CSS (`apresentacao.css`)

- Adicionados estilos para as novas seções (`.info-section`, `.team-members`, `.testimonials-grid`, `.contact-section`) e elementos internos (`.card`, `.member-card`, `.testimonial-card`), garantindo a consistência visual com o tema Verde/Azul.
