# Arquivo: Back_end/core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q # Usado para consultas ORM complexas
from django.http import HttpResponse

# IMPORTAÇÃO DOS MODELOS DO BANCO DE DADOS (Assumindo que foram criados em core/models.py)
from .models import Usuario, CreditoCarbono, Requisicao, TIPO_USUARIO_CHOICES


# ====================================================================
# FUNÇÕES AUXILIARES COM ORM
# ====================================================================

# Obtém o objeto Usuario logado, ou None
def get_user_logged(request):
    """
    Verifica se o usuário está logado e retorna o objeto Usuario do banco de dados.
    Em caso de falha, limpa a sessão.
    """
    if not request.session.get('logged_in'):
        return None, None
        
    user_id = request.session.get('user_id')
    if not user_id:
        request.session.clear()
        return None, None
        
    try:
        user = Usuario.objects.get(id=user_id)
        # Retorna o objeto Usuario e um dicionário de informações essenciais para o contexto
        user_info = {'nome': user.nome, 'tipo': user.tipo, 'id': user.id}
        return user, user_info
    except Usuario.DoesNotExist:
        request.session.clear() 
        return None, None

# Calcula o número total de requisições pendentes
def get_pendencias():
    """Retorna a contagem total de requisições de Registro e Transação Pendentes."""
    return Requisicao.objects.filter(status='Pendente').count()

# ====================================================================
# VIEWS PÚBLICAS E DE AUTENTICAÇÃO
# ====================================================================

# Rota /
def apresentacao_view(request):
    return render(request, 'apresentacao.html')

# Rota /login/
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        try:
            # 1. Busca o usuário pelo e-mail
            user_db = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return render(request, 'login.html', {'erro': "Credenciais inválidas. Tente novamente."})
        
        # 2. Checa a senha (ATENÇÃO: Senha em texto puro para fins didáticos)
        if user_db.senha == senha:
            # Autenticação bem-sucedida
            request.session['logged_in'] = True
            request.session['user_id'] = user_db.id # Armazena apenas o ID
            
            return redirect(reverse('dashboard'))
        else:
            return render(request, 'login.html', {'erro': "Credenciais inválidas. Tente novamente."})
            
    return render(request, 'login.html')

# Rota /sair/
def sair_view(request):
    request.session.clear() 
    return redirect(reverse('apresentacao'))

# Rota /cadastro/
def cadastro_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        tipo = request.POST.get('tipo-usuario')
        nome = request.POST.get('nome-completo')
        documento = request.POST.get('documento')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        
        if Usuario.objects.filter(email=email).exists():
            return render(request, 'cadastro.html', {'mensagem_erro': "E-mail já cadastrado."})
        
        # Cria novo usuário no banco de dados
        Usuario.objects.create(
            email=email, 
            senha=senha, 
            tipo=tipo, 
            nome=nome,
            documento=documento,
            cidade=cidade,
            estado=estado
        )
        
        return redirect(reverse('login'))
        
    # Passa as opções de tipo de usuário para o template, se necessário
    return render(request, 'cadastro.html', {'tipos_usuario': TIPO_USUARIO_CHOICES})

# ====================================================================
# VIEWS PROTEGIDAS (DASHBOARD E OPERAÇÕES)
# ====================================================================

# Rota /dashboard/
def dashboard_view(request):
    user, user_info = get_user_logged(request)
    if not user:
        return redirect(reverse('login'))
    
    pendencias = get_pendencias() if user_info['tipo'] == 'Administrador' else 0
    
    # Simula dados de transações (Você deve criar um modelo 'Transacao' para ter dados reais)
    transacoes = [
        {"id": "#001023", "data": "28/10/2025", "tipo": "Compra", "quantidade": 500, "parte": "Empresa Alfa Ltda", "status": "Concluída"},
        {"id": "#001022", "data": "27/10/2025", "tipo": "Venda", "quantidade": 150, "parte": "Produtor Rural Beto", "status": "Concluída"},
    ]
    
    context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'saldo': user.saldo_creditos,
        'transacoes': transacoes,
        'pendencias': pendencias,
        'active_page': 'dashboard'
    }
    
    return render(request, 'index.html', context)


# Rota /registro_creditos/ (Produtor Rural)
def registro_creditos_view(request):
    user, user_info = get_user_logged(request)
    if not user:
        return redirect(reverse('login'))
        
    # Nível de Autorização: Redireciona se não for Produtor Rural
    if user.tipo == 'Administrador':
        return redirect(reverse('requisicoes_registro'))
    if user.tipo != 'Produtor Rural':
        return redirect(reverse('dashboard'))

    mensagem_sucesso = None
    mensagem_erro = None

    if request.method == 'POST':
        quantidade = request.POST.get('quantidade')
        origem = request.POST.get('origem')
        data_geracao = request.POST.get('data-geracao')
        
        try:
            # Cria a requisição de registro no DB
            Requisicao.objects.create(
                tipo_requisicao='Registro', 
                usuario_origem=user,
                volume=int(quantidade),
                origem_credito=origem
                # Status será 'Pendente' por padrão
            )
            mensagem_sucesso = "Requisição de registro enviada com sucesso! Aguardando aprovação do Auditor."
        except ValueError:
            mensagem_erro = "Erro: A quantidade deve ser um número inteiro."
        
    context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'mensagem_sucesso': mensagem_sucesso,
        'mensagem_erro': mensagem_erro,
        'active_page': 'registro_creditos'
    }
    return render(request, 'registro_creditos.html', context)


# Rota /transacoes/ (Produtor Rural e Empresa Compradora)
def transacoes_view(request):
    user, user_info = get_user_logged(request)
    if not user:
        return redirect(reverse('login'))

    # Nível de Autorização: Redireciona se for Administrador
    if user.tipo == 'Administrador':
        return redirect(reverse('requisicoes_transacao'))
        
    mensagem_sucesso = None
    mensagem_erro = None
    
    # 1. BUSCA DE OFERTAS APROVADAS (Marketplace)
    # Busca ofertas aprovadas no DB e otimiza a busca pelo nome do produtor
    ofertas_db = CreditoCarbono.objects.filter(status='Aprovado').select_related('produtor')

    ofertas = []
    for credito in ofertas_db:
        ofertas.append({
            "id": credito.id,
            "produtor": credito.produtor.nome, 
            "origem": credito.origem,
            "quantidade": credito.quantidade,
            "preco_un": credito.preco_un
        })

    if request.method == 'POST':
        # 2. PROCESSAMENTO DE VENDA (POST do Produtor Rural)
        if user.tipo == 'Produtor Rural':
            volume = request.POST.get('volume')
            preco_unitario = request.POST.get('preco_unitario')
            
            if volume and preco_unitario:
                try:
                    # Cria a requisição de Venda no DB
                    Requisicao.objects.create(
                        tipo_requisicao='Venda',
                        usuario_origem=user,
                        volume=int(volume),
                        preco_un=float(preco_unitario)
                    )
                    mensagem_sucesso = "Requisição de venda enviada! Aguardando aprovação do Auditor."
                except ValueError:
                    mensagem_erro = "Volume e preço devem ser números válidos."
            else:
                mensagem_erro = "Preencha o volume e o preço unitário para listar a venda."
                
        # 3. PROCESSAMENTO DE COMPRA (POST da Empresa Compradora - Lógica futura)
        elif user.tipo == 'Empresa Compradora':
             # Aqui o POST do botão "Comprar" do Marketplace seria processado.
             # Por simplicidade, assume-se que é uma intenção de compra
             mensagem_sucesso = "Sua intenção de compra foi registrada e será auditada."


    context = {
        'ofertas': ofertas,
        'user_tipo': user_info['tipo'],
        'user_nome': user_info['nome'],
        'saldo': user.saldo_creditos,
        'mensagem_sucesso': mensagem_sucesso,
        'mensagem_erro': mensagem_erro,
        'active_page': 'transacoes'
    }
    
    return render(request, 'transacoes.html', context)


# ====================================================================
# VIEWS EXCLUSIVAS PARA O ADMINISTRADOR (AUDITORIA)
# ====================================================================

# Rota /requisicoes_registro/
def requisicoes_registro_view(request):
    user, user_info = get_user_logged(request)
    if not user or user.tipo != 'Administrador':
        return redirect(reverse('dashboard'))
    
    mensagem_sucesso = None
    
    # Busca todas as requisições de REGISTRO PENDENTES
    requisicoes_pendentes = Requisicao.objects.filter(
        tipo_requisicao='Registro', 
        status='Pendente'
    ).select_related('usuario_origem') # Otimiza busca do usuário de origem

    if request.method == 'POST':
        req_id = request.POST.get('req_id')
        acao = request.POST.get('acao') 
        
        req_encontrada = get_object_or_404(Requisicao, id=req_id)
        
        if acao == 'aprovar':
            # 1. Muda o status da Requisição
            req_encontrada.status = 'Aprovado'
            req_encontrada.save()
            
            # 2. Cria o Crédito no Marketplace (CreditoCarbono)
            # Preço unitário simulado para o Marketplace
            preco_simulado = 35.00
            
            CreditoCarbono.objects.create(
                produtor=req_encontrada.usuario_origem,
                origem=req_encontrada.origem_credito,
                quantidade=req_encontrada.volume,
                preco_un=preco_simulado,
                status='Aprovado'
            )
            mensagem_sucesso = f"Requisição {req_id} APROVADA e créditos listados no Marketplace."
            
        elif acao == 'rejeitar':
            req_encontrada.status = 'Rejeitado'
            req_encontrada.save()
            mensagem_sucesso = f"Requisição {req_id} REJEITADA."
        
        # Redireciona para atualizar a lista após a ação (boa prática)
        return redirect(reverse('requisicoes_registro'))

    context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'requisicoes': requisicoes_pendentes,
        'mensagem_sucesso': mensagem_sucesso,
        'active_page': 'requisicoes_registro',
        'pendencias': get_pendencias()
    }
    
    return render(request, 'requisicoes_registro.html', context)


# Rota /requisicoes_transacao/
def requisicoes_transacao_view(request):
    user, user_info = get_user_logged(request)
    if not user or user.tipo != 'Administrador':
        return redirect(reverse('dashboard'))

    mensagem_sucesso = None
    
    # Busca todas as requisições de VENDA ou COMPRA PENDENTES
    requisicoes_pendentes = Requisicao.objects.filter(
        Q(tipo_requisicao='Venda') | Q(tipo_requisicao='Compra'), 
        status='Pendente'
    ).select_related('usuario_origem')

    if request.method == 'POST':
        req_id = request.POST.get('req_id')
        acao = request.POST.get('acao') 
        
        req_encontrada = get_object_or_404(Requisicao, id=req_id)
        
        # A lógica de aprovação de transação envolveria manipulação de saldo e CreditoCarbono.
        if acao == 'aprovar':
            req_encontrada.status = 'Aprovado'
            req_encontrada.save()
            mensagem_sucesso = f"Requisição de Transação {req_id} APROVADA (Ajuste de saldo necessário)."
        
        elif acao == 'rejeitar':
            req_encontrada.status = 'Rejeitado'
            req_encontrada.save()
            mensagem_sucesso = f"Requisição de Transação {req_id} REJEITADA."
            
        return redirect(reverse('requisicoes_transacao'))

    context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'requisicoes': requisicoes_pendentes,
        'mensagem_sucesso': mensagem_sucesso,
        'active_page': 'requisicoes_transacao',
        'pendencias': get_pendencias()
    }
    
    return render(request, 'requisicoes_transacao.html', context)