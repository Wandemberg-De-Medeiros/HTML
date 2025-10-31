# Guia de Testes - EcoTrade (Versão 2.0 - Módulo Auditoria e API)

Este guia contém os passos para testar as novas funcionalidades implementadas: Módulo de Auditoria e API Pública.

## 🔑 Credenciais de Teste

| Usuário | Tipo | E-mail | Senha |
| :--- | :--- | :--- | :--- |
| **Admin** | Administrador | `admin@ecotrade.com` | `admin123` |
| **João Silva** | Produtor Rural | `joao@produtor.com` | `123456` |
| **Empresa Verde** | Empresa Compradora | `empresa@verde.com` | `123456` |

---

## 🧪 Teste 1: Módulo de Auditoria (Registro de Créditos)

**Objetivo:** Verificar se o Administrador pode aprovar/rejeitar requisições de registro e adicionar comentários, e se o histórico de auditoria é registrado.

| Passo | Usuário | Ação | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| 1 | João Silva | Logar e ir para **"Registro de Créditos"**. | Acesso ao formulário. |
| 2 | João Silva | Registrar 100 tCO2e (Origem: Agrofloresta). | Mensagem de sucesso. |
| 3 | Admin | Logar e ir para **"Requisições de Registro"**. | Requisição de João pendente na tabela. |
| 4 | Admin | Na requisição de João, preencher **"Comentário"** com "Análise inicial OK" e clicar em **"Comentar"**. | Mensagem de sucesso. A requisição continua pendente. Histórico de auditoria aparece na coluna. |
| 5 | Admin | Na requisição de João, preencher **"Comentário"** com "Aprovado após análise de documentos" e clicar em **"Aprovar"**. | Mensagem de sucesso. Requisição desaparece da lista. |
| 6 | João Silva | Logar e ir para **"Home"**. | Saldo atualizado para **100 tCO2e**. |

---

## 🧪 Teste 2: Módulo de Auditoria (Transação de Créditos)

**Objetivo:** Verificar se o Administrador pode aprovar/rejeitar requisições de compra e adicionar comentários, e se o histórico de auditoria é registrado.

| Passo | Usuário | Ação | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| 1 | João Silva | Logar e ir para **"Comprar/Vender Créditos"**. | Acesso à seção de venda. |
| 2 | João Silva | Listar os 100 tCO2e (Agrofloresta) para venda no Marketplace (Volume: 100, Preço: 50.00). | Mensagem de sucesso. |
| 3 | Empresa Verde | Logar e ir para **"Comprar/Vender Créditos"**. | Oferta de 100 tCO2e de João visível no Marketplace. |
| 4 | Empresa Verde | Clicar em **"Comprar"** na oferta de João. | Mensagem de sucesso. Oferta desaparece do Marketplace. |
| 5 | Admin | Logar e ir para **"Requisições Compra/Venda"**. | Requisição de Compra da Empresa Verde pendente. |
| 6 | Admin | Na requisição, preencher **"Comentário"** com "Verificado saldo do vendedor" e clicar em **"Comentar"**. | Mensagem de sucesso. Requisição continua pendente. Histórico de auditoria aparece na coluna. |
| 7 | Admin | Na requisição, clicar em **"Aprovar"** (sem comentário). | Mensagem de sucesso. Requisição desaparece da lista. |
| 8 | João Silva | Logar e ir para **"Home"**. | Saldo atualizado para **0 tCO2e**. |
| 9 | Empresa Verde | Logar e ir para **"Home"**. | Saldo atualizado para **100 tCO2e**. |

---

## 🧪 Teste 3: API Pública (`/api/creditos/`)

**Objetivo:** Verificar se o endpoint da API retorna os dados dos créditos registrados e aprovados em formato JSON.

| Passo | Ação | Resultado Esperado |
| :--- | :--- | :--- |
| 1 | Acessar a URL: `http://127.0.0.1:8000/api/creditos/` (ou a URL exposta) | Deve retornar um JSON contendo os créditos de carbono **aprovados** (e não vendidos) no sistema. |
| 2 | Verificar o conteúdo do JSON. | O JSON deve conter a lista de créditos com campos como `id`, `produtor`, `origem`, `quantidade`, `preco_unitario`, `status` (`Aprovado`) e `data_registro`. |
| 3 | **Observação:** Como o crédito do Teste 2 foi vendido, ele **não** deve aparecer na API. Se você registrar um novo crédito e aprová-lo, ele deve aparecer. | Apenas créditos com status 'Aprovado' devem ser listados. |
