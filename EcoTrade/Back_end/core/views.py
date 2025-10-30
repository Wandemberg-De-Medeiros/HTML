# Arquivo: Back_end/core/views.py (VERSÃO CORRIGIDA E COMPLETA)

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
import uuid
import json

# ====================================================================
# SIMULAÇÃO DE BANCO DE DADOS EM MEMÓRIA (Atualizada para Auditoria)
# ====================================================================

# Usuários simulados: {email: {senha: '...', tipo: '...', nome: '...', ...}}
USUARIOS_DB = {
    "admin@ecotrade.com": {"senha": "123", "tipo": "Administrador", "nome": "Auditor Principal", "saldo_creditos": 0}, 
    "produtor@rural.com": {"senha": "123", "tipo": "Produtor Rural", "nome": "Produtor Verde", "saldo_creditos": 1200},
    "empresa@compra.com": {"senha": "123", "tipo": "Empresa Compradora", "nome": "Sustenta S.A.", "saldo_creditos": 0}
}

# Créditos de Carbono APROVADOS e DISPONÍVEIS no Marketplace
CREDITOS_APROVADOS = [
    {"id": "c1a2b3", "produtor": "Produtor Verde", "origem": "Reflorestamento - Lote A", "quantidade": 1000, "preco_un": 35.50},
    {"id": "d4e5f6", "produtor": "Produtor Amazônia", "origem": "Conservação de Matas - Projeto K", "quantidade": 500, "preco_un": 38.00},
]

# Requisições PENDENTES de Registro de Créditos (Produtor -> Auditor)
REQUISICOES_REGISTRO_PENDENTES = [
    {"req_id": "reg789", "produtor": "Produtor Verde", "origem": "Nova Área de Preservação", "quantidade": 200, "data_geracao": "2025-01-01", "status": "Pendente"}
]

# Requisições PENDENTES de Compra/Venda (Produtor/Empresa -> Auditor)
REQUISICOES_TRANSACAO_PENDENTES = [
    {"req_id": "ven101", "tipo_req": "Venda", "usuario": "Produtor Verde", "volume": 300, "preco_un": 40.00, "status": "Pendente"},
    {"req_id": "com202", "tipo_req": "Compra", "usuario": "Sustenta S.A.", "volume": 100, "oferta_id": "c1a2b3", "status": "Pendente"}
]

# ====================================================================
# FUNÇÃO DE APRESENTAÇÃO (Home Pública)
# ====================================================================
def apresentacao_view(request):
    # Esta página é pública e não requer autenticação
    return render(request, 'apresentacao.html')

# ====================================================================
# FUNÇÕES DE AUTENTICAÇÃO E DASHBOARD
# ====================================================================

def get_pendencias():
    return len(REQUISICOES_REGISTRO_PENDENTES) + len(REQUISICOES_TRANSACAO_PENDENTES)


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        user_info = USUARIOS_DB.get(email)
        
        if user_info and user_info['senha'] == senha:
            request.session['logged_in'] = True
            request.session['user_info'] = user_info
            # Armazena o tipo de usuário na sessão também
            request.session['user_tipo'] = user_info['tipo'] 
            return redirect(reverse('dashboard'))
        else:
            return render(request, 'login.html', {'mensagem_erro': "E-mail ou senha inválidos."})
            
    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()
    return redirect(reverse('login'))

def cadastro_view(request):
    # O cadastro deve ser acessível publicamente, então não checa 'logged_in' aqui.
    
    if request.method == 'POST':
        # Lógica de cadastro (mantida)
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        # CORREÇÃO: Usar 'tipo-usuario' do template
        tipo = request.POST.get('tipo-usuario') 
        nome = request.POST.get('nome-completo')
        documento = request.POST.get('documento')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        
        if email in USUARIOS_DB:
            return render(request, 'cadastro.html', {'mensagem_erro': "E-mail já cadastrado."})
        
        USUARIOS_DB[email] = {
            "senha": senha, 
            "tipo": tipo, 
            "nome": nome,
            "documento": documento,
            "cidade": cidade,
            "estado": estado,
            "saldo_creditos": 0
        }
        
        # Redireciona para o login após cadastro bem-sucedido
        return redirect(reverse('login'))
        
    
    # Se a requisição não for POST, renderiza o formulário
    # Adicionando contexto básico para a sidebar, caso o usuário acesse logado (ex: Admin)
    context = {}
    if request.session.get('logged_in'):
        user_info = request.session['user_info']
        context = {
            'user_nome': user_info['nome'],
            'user_tipo': user_info['tipo'],
            'active_page': 'cadastro',
            'pendencias': get_pendencias() if user_info['tipo'] == 'Administrador' else 0
        }
    
    return render(request, 'cadastro.html', context)


def dashboard_view(request):
    if not request.session.get('logged_in'):
        return redirect(reverse('login'))
        
    user_info = request.session['user_info']
    
    pendencias = get_pendencias() if user_info['tipo'] == 'Administrador' else 0

    context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'saldo': user_info.get('saldo_creditos', 0), 
        'transacoes': [
            {'id': 't001', 'data': '2025-05-10', 'tipo': 'Venda', 'quantidade': 150, 'parte': 'Sustenta S.A.', 'status': 'Concluído'},
            {'id': 't002', 'data': '2025-05-15', 'tipo': 'Compra', 'quantidade': 50, 'parte': 'Produtor Delta', 'status': 'Pendente'}
        ],
        'pendencias': pendencias,
        'active_page': 'dashboard'
    }
    
    return render(request, 'index.html', context)


# ====================================================================
# VIEWS: PRODUTOR/EMPRESA (Submissão de Requisição)
# ====================================================================

def registro_creditos_view(request):
    if not request.session.get('logged_in'):
        return redirect(reverse('login'))
        
    user_info = request.session['user_info']
    
    # Se for Administrador, redireciona para a nova página de Auditoria
    if user_info['tipo'] == 'Administrador':
        return redirect(reverse('requisicoes_registro'))
    
    context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'active_page': 'registro_creditos'
    }
    
    if request.method == 'POST':
        # Se não for Produtor Rural, não permite a submissão e redireciona
        if user_info['tipo'] != 'Produtor Rural':
             # Redireciona para o dashboard com uma mensagem de erro
            return redirect(reverse('dashboard'))

        origem = request.POST.get('origem')
        quantidade = request.POST.get('quantidade')
        data_geracao = request.POST.get('data-geracao')
        
        if not quantidade or not origem or not data_geracao:
            context['mensagem_erro'] = "Preencha todos os campos obrigatórios."
            return render(request, 'registro_creditos.html', context)

        # Lógica de registro para Produtor Rural
        novo_credito_req = {
            "req_id": str(uuid.uuid4())[:6], 
            "produtor": user_info['nome'],
            "origem": origem,
            "quantidade": int(quantidade),
            "data_geracao": data_geracao,
            "status": "Pendente"
        }
        
        REQUISICOES_REGISTRO_PENDENTES.append(novo_credito_req)
        
        # CORREÇÃO: Renderiza a mesma página com mensagem de sucesso
        context['mensagem_sucesso'] = "Requisição de registro enviada com sucesso! Aguardando aprovação do Auditor."
        return render(request, 'registro_creditos.html', context)
        
    return render(request, 'registro_creditos.html', context)


def transacoes_view(request):
    if not request.session.get('logged_in'):
        return redirect(reverse('login'))
        
    user_info = request.session['user_info']

    # Se for Administrador, redireciona para a nova página de Auditoria
    if user_info['tipo'] == 'Administrador':
        return redirect(reverse('requisicoes_transacao'))
    
    mensagem_sucesso = None
    
    if request.method == 'POST':
        if user_info['tipo'] == 'Produtor Rural':
            volume = request.POST.get('volume')
            preco_unitario = request.POST.get('preco_unitario')
            
            nova_req_venda = {
                "req_id": str(uuid.uuid4())[:6], 
                "tipo_req": "Venda",
                "usuario": user_info['nome'],
                "volume": int(volume),
                "preco_un": float(preco_unitario),
                "status": "Pendente"
            }
            REQUISICOES_TRANSACAO_PENDENTES.append(nova_req_venda)
            mensagem_sucesso = "Requisição de venda enviada! Aguardando aprovação do Auditor."

            

    context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'ofertas': CREDITOS_APROVADOS, 
        'mensagem_sucesso': mensagem_sucesso,
        'saldo': user_info.get('saldo_creditos', 0),
        'active_page': 'transacoes',
        'pendencias': get_pendencias() if user_info['tipo'] == 'Administrador' else 0
    }
    
    return render(request, 'transacoes.html', context)


# ====================================================================
# NOVAS VIEWS EXCLUSIVAS PARA O ADMINISTRADOR (AUDITORIA)
# ====================================================================

def requisicoes_registro_view(request):
    if not request.session.get('logged_in') or request.session['user_info']['tipo'] != 'Administrador':
        return redirect(reverse('dashboard'))

    user_info = request.session['user_info']
    pendencias = get_pendencias()
    msg = None
    
    if request.method == 'POST':
        req_id = request.POST.get('req_id')
        acao = request.POST.get('acao') 
        
        req_encontrada = next((req for req in REQUISICOES_REGISTRO_PENDENTES if req['req_id'] == req_id), None)
        
        if req_encontrada:
            if acao == 'aprovar':
                novo_credito_aprovado = {
                    "id": req_encontrada['req_id'], 
                    "produtor": req_encontrada['produtor'], 
                    "origem": req_encontrada['origem'], 
                    "quantidade": req_encontrada['quantidade'], 
                    "preco_un": 35.00
                }
                CREDITOS_APROVADOS.append(novo_credito_aprovado)
                REQUISICOES_REGISTRO_PENDENTES.remove(req_encontrada)
                msg = f"Requisição de Registro {req_id} APROVADA e listada no Marketplace."
            
            elif acao == 'rejeitar':
                REQUISICOES_REGISTRO_PENDENTES.remove(req_encontrada)
                msg = f"Requisição de Registro {req_id} REJEITADA."
            
        else:
            msg = "Requisição não encontrada."
            
        # Recalcula pendencias após a ação
        pendencias = get_pendencias()

    context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'requisicoes': REQUISICOES_REGISTRO_PENDENTES,
        'mensagem_sucesso': msg,
        'USUARIOS_DB': USUARIOS_DB, 
        'active_page': 'requisicoes_registro',
        'pendencias': pendencias
    }
    
    return render(request, 'requisicoes_registro.html', context)


def requisicoes_transacao_view(request):
    if not request.session.get('logged_in') or request.session['user_info']['tipo'] != 'Administrador':
        return redirect(reverse('dashboard'))

    user_info = request.session['user_info']
    pendencias = get_pendencias()
    msg = None
    
    if request.method == 'POST':
        req_id = request.POST.get('req_id')
        acao = request.POST.get('acao') 
        req_encontrada = next((req for req in REQUISICOES_TRANSACAO_PENDENTES if req['req_id'] == req_id), None)
        
        if req_encontrada:
            # Lógica simples de remoção após aprovação/rejeição (o processamento financeiro real é omitido)
            REQUISICOES_TRANSACAO_PENDENTES.remove(req_encontrada)
            msg = f"Requisição de Transação {req_id} {acao.upper()} com sucesso."
        else:
            msg = "Requisição não encontrada."
            
        # Recalcula pendencias após a ação
        pendencias = get_pendencias()

    context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'requisicoes': REQUISICOES_TRANSACAO_PENDENTES,
        'mensagem_sucesso': msg,
        'USUARIOS_DB': USUARIOS_DB,
        'active_page': 'requisicoes_transacao',
        'pendencias': pendencias
    }
    
    return render(request, 'requisicoes_transacao.html', context)