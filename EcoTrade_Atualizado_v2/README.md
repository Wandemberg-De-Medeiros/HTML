# EcoTrade - Sistema de Créditos de Carbono

## 📋 Descrição

Sistema completo de compra e venda de créditos de carbono com atualização automática de saldos em tempo real. O sistema permite que produtores rurais registrem créditos, listem para venda no marketplace, e empresas compradoras possam adquiri-los, tudo com aprovação de um administrador/auditor.

## ✨ Funcionalidades Implementadas

### ✅ Registro de Créditos
- Produtor rural registra créditos de carbono
- Administrador aprova/rejeita requisições
- **Saldo atualizado automaticamente** após aprovação

### ✅ Venda de Créditos
- Produtor seleciona créditos aprovados
- Define volume e preço unitário
- Lista no marketplace para compradores

### ✅ Compra de Créditos
- Empresa compradora visualiza ofertas no marketplace
- Solicita compra de créditos
- Administrador aprova transação
- **Saldos atualizados automaticamente:**
  - Vendedor: saldo decrementado
  - Comprador: saldo incrementado

### ✅ Histórico de Transações
- Registro completo de todas as transações
- Exibição no dashboard de vendedores e compradores
- Rastreabilidade total

### ✅ Painel Administrativo
- Aprovação de requisições de registro
- Aprovação de transações de compra/venda
- Validação de saldos antes de aprovar

---

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.11+
- pip3

### Passo 1: Instalar Dependências
```bash
pip3 install django
```

### Passo 2: Navegar até o diretório do projeto
```bash
cd EcoTrade/Back_end
```

### Passo 3: Aplicar Migrações (se necessário)
```bash
python3.11 manage.py migrate
```

### Passo 4: Popular Banco de Dados com Usuários de Teste
```bash
python3.11 populate_db.py
```

### Passo 5: Iniciar Servidor
```bash
python3.11 manage.py runserver 0.0.0.0:8000
```

### Passo 6: Acessar o Sistema
Abra o navegador e acesse: **http://localhost:8000**

---

## 👥 Usuários de Teste

### Administrador
- **Email:** admin@ecotrade.com
- **Senha:** admin123

### Produtor Rural - João Silva
- **Email:** joao@produtor.com
- **Senha:** 123456

### Produtor Rural - Maria Santos
- **Email:** maria@produtor.com
- **Senha:** 123456

### Empresa Compradora - Empresa Verde Ltda
- **Email:** empresa@verde.com
- **Senha:** 123456

### Empresa Compradora - Sustentável Corp
- **Email:** sustentavel@corp.com
- **Senha:** 123456

---

## 📖 Como Testar o Sistema Completo

Consulte o arquivo **GUIA_DE_TESTES.md** para um passo a passo detalhado de como testar todas as funcionalidades.

---

## 📂 Estrutura do Projeto

```
EcoTrade/
├── Back_end/
│   ├── core/                    # Aplicação principal
│   │   ├── migrations/          # Migrações do banco de dados
│   │   ├── models.py            # Modelos (Usuario, CreditoCarbono, Requisicao, Transacao)
│   │   ├── views.py             # Lógica de negócio
│   │   ├── urls.py              # Rotas da aplicação
│   │   └── admin.py             # Configuração do admin Django
│   ├── ecotrade/                # Configurações do projeto
│   │   ├── settings.py          # Configurações gerais
│   │   └── urls.py              # Rotas principais
│   ├── db.sqlite3               # Banco de dados SQLite
│   ├── manage.py                # Script de gerenciamento Django
│   └── populate_db.py           # Script para popular banco de dados
├── Index/                       # Templates HTML
│   ├── index.html               # Dashboard
│   ├── transacoes.html          # Marketplace de compra/venda
│   ├── registro_creditos.html   # Registro de créditos
│   ├── requisicoes_registro.html    # Aprovação de registros (admin)
│   ├── requisicoes_transacao.html   # Aprovação de transações (admin)
│   ├── login.html               # Tela de login
│   └── cadastro.html            # Cadastro de usuários
└── Style/                       # Arquivos CSS
    ├── style.css                # Estilos gerais
    ├── transacoes.css           # Estilos do marketplace
    └── ...
```

---

## 🔧 Tecnologias Utilizadas

- **Backend:** Django 5.2.7
- **Banco de Dados:** SQLite3
- **Frontend:** HTML5, CSS3, JavaScript
- **Linguagem:** Python 3.11

---

## 📝 Documentação Adicional

- **DOCUMENTACAO_ALTERACOES.md** - Detalhamento técnico de todas as alterações realizadas
- **GUIA_DE_TESTES.md** - Passo a passo para testar o sistema completo

---

## 🎯 Fluxo de Uso

### 1️⃣ Registro de Créditos
```
Produtor Rural → Registra créditos → Administrador aprova → Saldo atualizado
```

### 2️⃣ Venda de Créditos
```
Produtor Rural → Seleciona crédito → Define preço → Lista no marketplace
```

### 3️⃣ Compra de Créditos
```
Empresa Compradora → Vê ofertas → Solicita compra → Administrador aprova → Saldos atualizados
```

---

## ✅ Validações Implementadas

- ✅ Validação de saldo antes de aprovar transação
- ✅ Validação de volume disponível ao listar para venda
- ✅ Controle de status dos créditos (Aprovado → Listado → Pendente → Vendido)
- ✅ Rastreabilidade completa de transações

---

## 🔒 Segurança

⚠️ **ATENÇÃO:** Este sistema foi desenvolvido para fins educacionais/demonstração.

Para uso em produção, implemente:
- Hash de senhas (bcrypt/argon2)
- HTTPS
- Autenticação robusta
- Proteção contra injeção SQL
- Rate limiting

---

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação técnica em **DOCUMENTACAO_ALTERACOES.md**.

---

## 📄 Licença

Este projeto é de código aberto para fins educacionais.

---

**Desenvolvido para o sistema EcoTrade - Marketplace de Créditos de Carbono**
