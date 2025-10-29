from django.shortcuts import render

# Create your views here.
# Arquivo: Back_end/core/views.py

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
import uuid
import json # Usaremos json para simular dados do DB

# ====================================================================
# SIMULAÇÃO DE BANCO DE DADOS EM MEMÓRIA (MELHORIA DE DADOS)
# (Em Django real, usaríamos models.py e o ORM)
# ====================================================================

# Usuários simulados: {email: {senha: '...', tipo: '...', nome: '...'}}
USUARIOS_DB = {
    "admin@ecotrade.com": {"senha": "123", "tipo": "Administrador", "nome": "Admin UNAMA"},
    "produtor@rural.com": {"senha": "123", "tipo": "Produtor Rural", "nome": "Produtor Verde"},
    "empresa@compra.com": {"senha": "123", "tipo": "Empresa Compradora", "nome": "Sustenta S.A."}
}

# Créditos de Carbono simulados
CREDITOS_DISPONIVEIS = [
    {"id": "c1a2b3", "produtor": "Produtor Verde", "origem": "Reflorestamento - Lote A", "quantidade": 1500, "preco_un": 35.00, "status": "Aprovado"},
    {"id": "d4e5f6", "produtor": "Produtor Teste", "origem": "Manejo Sustentável - Lote B", "quantidade": 800, "preco_un": 38.50, "status": "Aprovado"}
]

# ====================================================================
# VIEWS (FUNÇÕES QUE LIDAM COM AS ROTAS)
# ====================================================================

# Rota /
def apresentacao_view(request):
    return render(request, 'apresentacao.html')

# Rota /login/
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        if email in USUARIOS_DB and USUARIOS_DB[email]['senha'] == senha:
            # Autenticação simulada bem-sucedida
            # No Django real, você usaria 'auth.login(request, user)'
            request.session['logged_in'] = True
            request.session['user_email'] = email
            request.session['user_info'] = USUARIOS_DB[email]
            
            return redirect(reverse('dashboard'))
        else:
            return render(request, 'login.html', {'erro': "Credenciais inválidas. Tente novamente."})
            
    return render(request, 'login.html')

# Rota /sair/
def sair_view(request):
    request.session.clear() # Limpa a sessão
    return redirect(reverse('apresentacao'))

# Rota /dashboard/ (REQUISITO 4)
def dashboard_view(request):
    if not request.session.get('logged_in'):
        return redirect(reverse('login'))
    
    user_info = request.session['user_info']
    
    # Simula dados do dashboard
    saldo_creditos = 12500 if user_info['tipo'] == 'Produtor Rural' else 8000
    transacoes = [
        {"id": "#001023", "data": "28/10/2025", "tipo": "Compra", "quantidade": 500, "parte": "Empresa Alfa Ltda", "status": "Concluída"},
        {"id": "#001022", "data": "27/10/2025", "tipo": "Venda", "quantidade": 150, "parte": "Produtor Rural Beto", "status": "Concluída"},
    ]
    
    context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'saldo': saldo_creditos,
        'transacoes': transacoes
    }
    
    return render(request, 'index.html', context)


# Rota /cadastro/ (REQUISITO 1)
def cadastro_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        tipo = request.POST.get('tipo-usuario')
        nome = request.POST.get('nome-completo')
        documento = request.POST.get('documento')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        
        if email in USUARIOS_DB:
            return render(request, 'cadastro.html', {'mensagem_erro': "E-mail já cadastrado."})
        
        # Adiciona novo usuário à simulação de BD
        USUARIOS_DB[email] = {
            "senha": senha, 
            "tipo": tipo, 
            "nome": nome,
            "documento": documento,
            "cidade": cidade,
            "estado": estado
        }
        
        return redirect(reverse('login'))
        
    return render(request, 'cadastro.html')

# Rota /registro_creditos/ (REQUISITO 2)
def registro_creditos_view(request):
    if not request.session.get('logged_in'):
        return redirect(reverse('login'))
        
    user_info = request.session['user_info']

    if user_info['tipo'] != 'Produtor Rural':
        context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
    }

    if request.method == 'POST':
        quantidade = request.POST.get('quantidade')
        origem = request.POST.get('origem')
        data_geracao = request.POST.get('data-geracao')
        
        novo_credito = {
            "id": str(uuid.uuid4())[:6], 
            "produtor": request.session['user_info']['nome'],
            "origem": origem,
            "quantidade": int(quantidade),
            "data": data_geracao,
            "status": "Pendente"
        }
        
        print("Novo Crédito Registrado:", novo_credito)
        return render(request, 'registro_creditos.html', {'mensagem_sucesso': "Crédito registrado com sucesso! Aguardando aprovação."})
        
    return render(request, 'registro_creditos.html')

# Rota /transacoes/ (REQUISITO 3)
def transacoes_view(request):
    if not request.session.get('logged_in'):
        return redirect(reverse('login'))
    user_info = request.session['user_info']

    if request.method == 'POST' and user_info['tipo'] == 'Produtor Rural':

        volume = request.POST.get('volume')
        preco_unitario = request.POST.get('preco_unitario')
        
        nova_oferta = {
            "id": str(uuid.uuid4())[:6], 
            "produtor": user_info['nome'],
            "origem": f"Venda Rápida - {user_info['nome']}",
            "quantidade": int(volume),
            "preco_un": float(preco_unitario),
        }
        CREDITOS_DISPONIVEIS.append(nova_oferta)
        print("Nova Oferta de Venda Criada:", nova_oferta)
        mensagem_sucesso = "Seus créditos foram listados com sucesso no Marketplace!"

    context = {
       'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'ofertas': CREDITOS_DISPONIVEIS,
        'mensagem_sucesso': mensagem_sucesso if 'mensagem_sucesso' in locals() else None,
    }
    
    return render(request, 'transacoes.html', context)