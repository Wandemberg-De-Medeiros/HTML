# Guia de Testes - Sistema EcoTrade

## URL de Acesso
**URL do Sistema:** https://8000-i82i7q3o2id90luwm7em2-f88f56bb.manusvm.computer

## Credenciais de Teste

### 1. Administrador
- **Email:** admin@ecotrade.com
- **Senha:** admin123
- **Função:** Aprovar requisições de registro e transações

### 2. Produtor Rural - João Silva
- **Email:** joao@produtor.com
- **Senha:** 123456
- **Função:** Registrar créditos e vender no marketplace

### 3. Produtor Rural - Maria Santos
- **Email:** maria@produtor.com
- **Senha:** 123456
- **Função:** Registrar créditos e vender no marketplace

### 4. Empresa Compradora - Empresa Verde Ltda
- **Email:** empresa@verde.com
- **Senha:** 123456
- **Função:** Comprar créditos do marketplace

### 5. Empresa Compradora - Sustentável Corp
- **Email:** sustentavel@corp.com
- **Senha:** 123456
- **Função:** Comprar créditos do marketplace

---

## Fluxo de Teste Completo

### ETAPA 1: Registro de Créditos (Produtor Rural)

1. **Login como João Silva** (joao@produtor.com)
2. Acesse **"Registro de Créditos"** no menu lateral
3. Preencha o formulário:
   - **Quantidade:** 500
   - **Origem:** Reflorestamento Amazônia
   - **Data de Geração:** (qualquer data)
4. Clique em **"Enviar Requisição"**
5. **Resultado esperado:** Mensagem de sucesso "Requisição de registro enviada com sucesso!"
6. Verifique que o **saldo ainda é 0** (aguardando aprovação)

---

### ETAPA 2: Aprovação de Registro (Administrador)

1. **Faça logout** e **login como Administrador** (admin@ecotrade.com)
2. Acesse **"Requisições de Registro"** no menu lateral
3. Você verá a requisição de João Silva pendente
4. Clique em **"Aprovar"**
5. **Resultado esperado:** 
   - Mensagem "Requisição #X APROVADA! 500 tCO2e adicionados ao saldo do produtor João Silva"
   - A requisição desaparece da lista de pendentes

---

### ETAPA 3: Verificar Saldo Atualizado (Produtor Rural)

1. **Faça logout** e **login novamente como João Silva**
2. No **Dashboard** (tela principal), verifique:
   - **Saldo de Créditos:** deve mostrar **500 tCO2e**
3. **Resultado esperado:** O saldo foi atualizado automaticamente após aprovação

---

### ETAPA 4: Listar Créditos para Venda (Produtor Rural)

1. Ainda logado como **João Silva**
2. Acesse **"Comprar/Vender Créditos"** no menu lateral
3. Role até a seção **"Listar Créditos para Venda"**
4. Preencha o formulário:
   - **Selecione o Crédito:** Reflorestamento Amazônia - 500 tCO2e
   - **Volume a Vender:** 500
   - **Preço Unitário:** 45.00
5. Clique em **"Listar para Venda"**
6. **Resultado esperado:** 
   - Mensagem "Crédito listado com sucesso! Agora está visível no Marketplace"
   - O crédito aparece na tabela "Créditos Disponíveis para Compra" (para outros usuários)

---

### ETAPA 5: Comprar Créditos (Empresa Compradora)

1. **Faça logout** e **login como Empresa Verde Ltda** (empresa@verde.com)
2. Acesse **"Comprar/Vender Créditos"**
3. Na tabela **"Créditos Disponíveis para Compra"**, você verá:
   - Origem: Reflorestamento Amazônia
   - Produtor: João Silva
   - Volume: 500 tCO2e
   - Preço: R$ 45,00
4. Clique em **"Comprar"**
5. **Resultado esperado:** 
   - Mensagem "Intenção de compra do crédito #X enviada! Aguardando aprovação do Auditor"
   - O crédito desaparece da lista (status mudou para Pendente)

---

### ETAPA 6: Aprovar Transação (Administrador)

1. **Faça logout** e **login como Administrador**
2. Acesse **"Requisições Compra/Venda"**
3. Você verá a requisição de compra:
   - Comprador: Empresa Verde Ltda
   - Vendedor: João Silva
   - Volume: 500 tCO2e
   - Preço Unit.: R$ 45,00
   - Total: R$ 22.500,00
4. Clique em **"Aprovar"**
5. **Resultado esperado:** 
   - Mensagem "Transação #X APROVADA! 500 tCO2e transferidos de João Silva para Empresa Verde Ltda"

---

### ETAPA 7: Verificar Saldos Atualizados

#### 7.1 Verificar Saldo do Vendedor (João Silva)
1. **Faça logout** e **login como João Silva**
2. No **Dashboard**, verifique:
   - **Saldo de Créditos:** deve mostrar **0 tCO2e** (vendeu os 500)
3. No **Histórico de Transações**, deve aparecer:
   - Tipo: Venda
   - Quantidade: 500
   - Parte Envolvida: Empresa Verde Ltda
   - Status: Concluída

#### 7.2 Verificar Saldo do Comprador (Empresa Verde Ltda)
1. **Faça logout** e **login como Empresa Verde Ltda**
2. No **Dashboard**, verifique:
   - **Saldo de Créditos:** deve mostrar **500 tCO2e** (comprou os 500)
3. No **Histórico de Transações**, deve aparecer:
   - Tipo: Compra
   - Quantidade: 500
   - Parte Envolvida: João Silva
   - Status: Concluída

---

## Teste Adicional: Múltiplos Produtores e Compradores

### Cenário: Maria Santos vende para Sustentável Corp

1. **Login como Maria Santos** → Registrar 300 tCO2e (Origem: Conservação Florestal)
2. **Login como Administrador** → Aprovar registro de Maria
3. **Login como Maria Santos** → Listar 300 tCO2e por R$ 50,00
4. **Login como Sustentável Corp** → Comprar crédito de Maria
5. **Login como Administrador** → Aprovar transação
6. **Verificar saldos:**
   - Maria Santos: 0 tCO2e (vendeu tudo)
   - Sustentável Corp: 300 tCO2e (comprou)

---

## Validações Implementadas

### ✅ Atualização de Saldo no Registro
- Quando administrador aprova registro, o saldo do produtor é incrementado

### ✅ Atualização de Saldo na Venda
- Quando administrador aprova compra:
  - Saldo do vendedor é **decrementado**
  - Saldo do comprador é **incrementado**

### ✅ Histórico de Transações
- Todas as transações aprovadas são registradas
- Aparecem no dashboard de vendedor e comprador

### ✅ Controle de Status
- Créditos aprovados → podem ser listados
- Créditos listados → aparecem no marketplace
- Créditos em transação → não aparecem no marketplace
- Créditos vendidos → marcados como vendidos

---

## Observações Importantes

1. **Saldo em tempo real:** O saldo é atualizado no banco de dados imediatamente após aprovação
2. **Para ver saldo atualizado:** Recarregue a página ou navegue para o Dashboard
3. **Múltiplas transações:** O sistema suporta múltiplas transações simultâneas
4. **Validação de saldo:** O sistema valida se o vendedor tem saldo suficiente antes de aprovar

---

## Problemas Conhecidos Resolvidos

- ✅ Campo `credito_alvo` ausente → Corrigido para `credito`
- ✅ Saldo não atualizado → Implementado atualização em `requisicoes_registro_view` e `requisicoes_transacao_view`
- ✅ Formulário de venda sem seleção de crédito → Implementado dropdown com créditos disponíveis
- ✅ Histórico de transações vazio → Implementado modelo `Transacao` e integração com dashboard
