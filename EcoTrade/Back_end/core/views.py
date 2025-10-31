# Arquivo: Back_end/core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from django.http import HttpResponse
from decimal import Decimal
import json

# IMPORTAÇÃO DOS MODELOS DO BANCO DE DADOS
from .models import Usuario, CreditoCarbono, Requisicao, Transacao, Auditoria, TIPO_USUARIO_CHOICES


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
# A view de cadastro foi removida a pedido do cliente.
# A rota foi comentada em core/urls.py.
# def cadastro_view(request):
#     ... (código removido)

# ====================================================================
# VIEWS PROTEGIDAS (DASHBOARD E OPERAÇÕES)
# ====================================================================

# Rota /dashboard/
def dashboard_view(request):
    user, user_info = get_user_logged(request)
    if not user:
        return redirect(reverse('login'))
    
    pendencias = get_pendencias() if user_info['tipo'] == 'Administrador' else 0
    
    # Busca transações reais do banco de dados
    if user.tipo == 'Produtor Rural':
        # Transações onde o usuário vendeu
        transacoes_db = Transacao.objects.filter(vendedor=user).order_by('-data_transacao')[:5]
        transacoes = []
        for t in transacoes_db:
            transacoes.append({
                "id": f"#{t.id:06d}",
                "data": t.data_transacao.strftime("%d/%m/%Y"),
                "tipo": "Venda",
                "quantidade": t.volume,
                "parte": t.comprador.nome,
                "status": "Concluída"
            })
    elif user.tipo == 'Empresa Compradora':
        # Transações onde o usuário comprou
        transacoes_db = Transacao.objects.filter(comprador=user).order_by('-data_transacao')[:5]
        transacoes = []
        for t in transacoes_db:
            transacoes.append({
                "id": f"#{t.id:06d}",
                "data": t.data_transacao.strftime("%d/%m/%Y"),
                "tipo": "Compra",
                "quantidade": t.volume,
                "parte": t.vendedor.nome,
                "status": "Concluída"
            })
    else:
        # Administrador vê todas as transações
        transacoes_db = Transacao.objects.all().order_by('-data_transacao')[:5]
        transacoes = []
        for t in transacoes_db:
            transacoes.append({
                "id": f"#{t.id:06d}",
                "data": t.data_transacao.strftime("%d/%m/%Y"),
                "tipo": "Transação",
                "quantidade": t.volume,
                "parte": f"{t.vendedor.nome} → {t.comprador.nome}",
                "status": "Concluída"
            })
    
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
    
    # 1. BUSCA DE OFERTAS APROVADAS (Marketplace para COMPRA)
    # Lista todos os créditos com status 'Listado' no marketplace, exceto os do próprio usuário logado.
    ofertas_db = CreditoCarbono.objects.filter(status='Listado').exclude(produtor=user).select_related('produtor')

    ofertas = []
    for credito in ofertas_db:
        ofertas.append({
            "id": credito.id,
            "produtor": credito.produtor.nome, 
            "origem": credito.origem,
            "quantidade": credito.quantidade,
            "preco_un": credito.preco_un
        })
        
    # 2. CRÉDITOS APROVADOS DO USUÁRIO (para listar para VENDA)
    meus_creditos_db = CreditoCarbono.objects.filter(
        produtor=user, 
        status='Aprovado'  # Apenas créditos aprovados e não listados
    )
    meus_creditos = []
    for credito in meus_creditos_db:
         meus_creditos.append({
            "id": credito.id,
            "origem": credito.origem,
            "quantidade": credito.quantidade,
            "preco_un": credito.preco_un
        })

    if request.method == 'POST':
        # 3. PROCESSAMENTO DE VENDA/LISTAGEM (POST do Produtor Rural)
        if user.tipo == 'Produtor Rural' and request.POST.get('acao') == 'vender':
            credito_id = request.POST.get('credito_id_para_venda')
            volume = request.POST.get('volume_venda')
            preco_unitario = request.POST.get('preco_unitario_venda')
            
            if credito_id and volume and preco_unitario:
                try:
                    credito_a_vender = get_object_or_404(CreditoCarbono, id=credito_id, produtor=user, status='Aprovado')
                    
                    volume_int = int(volume)
                    preco_float = float(preco_unitario)
                    
                    # Valida se o volume não excede a quantidade disponível
                    if volume_int > credito_a_vender.quantidade:
                        mensagem_erro = f"Erro: Você só possui {credito_a_vender.quantidade} tCO2e disponíveis neste crédito."
                    else:
                        credito_a_vender.quantidade = volume_int
                        credito_a_vender.preco_un = Decimal(str(preco_float))
                        credito_a_vender.status = 'Listado'
                        credito_a_vender.save()
                        
                        mensagem_sucesso = "Crédito listado com sucesso! Agora está visível no Marketplace."
                        return redirect(reverse('transacoes'))
                        
                except CreditoCarbono.DoesNotExist:
                     mensagem_erro = "Erro: Crédito não encontrado ou você não é o proprietário."
                except ValueError:
                    mensagem_erro = "Volume e preço devem ser números válidos."
            else:
                mensagem_erro = "Preencha todos os campos para listar a venda."
                
        # 4. PROCESSAMENTO DE COMPRA (POST da Empresa Compradora)
        elif user.tipo == 'Empresa Compradora' and request.POST.get('acao') == 'comprar':
             credito_id = request.POST.get('credito_id_compra')
             
             try:
                 credito_a_comprar = get_object_or_404(CreditoCarbono, id=credito_id, status='Listado')
                 
                 # Cria uma requisição de transação (compra)
                 Requisicao.objects.create(
                     tipo_requisicao='Compra', 
                     usuario_origem=user,
                     credito=credito_a_comprar,
                     volume=credito_a_comprar.quantidade, 
                     preco_un=credito_a_comprar.preco_un
                 )
                 
                 # Altera o status do crédito para 'Pendente' (aguardando aprovação)
                 credito_a_comprar.status = 'Pendente'
                 credito_a_comprar.save()
                 
                 mensagem_sucesso = f"Intenção de compra do crédito #{credito_id} enviada! Aguardando aprovação do Auditor."
                 return redirect(reverse('transacoes'))
             except CreditoCarbono.DoesNotExist:
                  mensagem_erro = "Erro: O crédito selecionado não está mais disponível no Marketplace."
             except Exception as e:
                 mensagem_erro = f"Ocorreu um erro ao processar a compra: {e}"

    context = {
        'ofertas': ofertas,
        'meus_creditos': meus_creditos,
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
    ).select_related('usuario_origem').prefetch_related('auditorias')

    if request.method == 'POST':
        req_id = request.POST.get('req_id')
        acao = request.POST.get('acao') 
        comentario = request.POST.get('comentario', '')
        
        req_encontrada = get_object_or_404(Requisicao, id=req_id)
        
        if acao == 'aprovar':
            # 1. Muda o status da Requisição
            req_encontrada.status = 'Aprovado'
            req_encontrada.save()
            
            # 2. Cria o Crédito no banco (status='Aprovado', ainda não listado)
            novo_credito = CreditoCarbono.objects.create(
                produtor=req_encontrada.usuario_origem,
                origem=req_encontrada.origem_credito,
                quantidade=req_encontrada.volume,
                preco_un=Decimal('0.00'),  # Preço será definido pelo produtor ao listar
                status='Aprovado'
            )
            
            # 3. Atualiza o saldo de créditos do produtor
            produtor = req_encontrada.usuario_origem
            produtor.saldo_creditos += req_encontrada.volume
            produtor.save()
            
            # 4. Registra a Auditoria
            Auditoria.objects.create(
                requisicao=req_encontrada,
                auditor=user,
                acao='Aprovar',
                comentario=comentario
            )
            
            mensagem_sucesso = f"Requisição #{req_id} APROVADA! {req_encontrada.volume} tCO2e adicionados ao saldo do produtor {produtor.nome}."
            
        elif acao == 'rejeitar':
            req_encontrada.status = 'Rejeitado'
            req_encontrada.save()
            
            # Registra a Auditoria
            Auditoria.objects.create(
                requisicao=req_encontrada,
                auditor=user,
                acao='Rejeitar',
                comentario=comentario
            )
            mensagem_sucesso = f"Requisição #{req_id} REJEITADA."

        elif acao == 'comentar':
            # Apenas registra o comentário sem mudar o status
            Auditoria.objects.create(
                requisicao=req_encontrada,
                auditor=user,
                acao='Comentar',
                comentario=comentario
            )
            mensagem_sucesso = f"Comentário adicionado à Requisição #{req_id}."
        
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


# Rota /historico_creditos/
def historico_creditos_view(request):
    user, user_info = get_user_logged(request)
    if not user or user.tipo != 'Administrador':
        return redirect(reverse('dashboard'))

    # Busca todos os créditos de carbono registrados (aprovados, listados, pendentes, vendidos)
    # Exclui créditos com status 'Rejeitado'
    creditos = CreditoCarbono.objects.exclude(status='Rejeitado').select_related('produtor').order_by('-data_registro')

    context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'creditos': creditos,
        'active_page': 'historico_creditos',
        'pendencias': get_pendencias()
    }
    
    return render(request, 'historico_creditos.html', context)

# Rota /requisicoes_transacao/
def requisicoes_transacao_view(request):


    user, user_info = get_user_logged(request)
    if not user or user.tipo != 'Administrador':
        return redirect(reverse('dashboard'))

    mensagem_sucesso = None
    mensagem_erro = None
    
    # Busca todas as requisições de COMPRA PENDENTES
    requisicoes_pendentes = Requisicao.objects.filter(
        tipo_requisicao='Compra', 
        status='Pendente'
    ).select_related('usuario_origem', 'credito', 'credito__produtor').prefetch_related('auditorias')

    if request.method == 'POST':
        req_id = request.POST.get('req_id')
        acao = request.POST.get('acao') 
        comentario = request.POST.get('comentario', '')
        
        req_encontrada = get_object_or_404(Requisicao, id=req_id)
        
        if acao == 'aprovar':
            try:
                # 1. Obtém os dados da requisição
                comprador = req_encontrada.usuario_origem
                credito = req_encontrada.credito
                vendedor = credito.produtor
                volume = req_encontrada.volume
                preco_un = req_encontrada.preco_un
                preco_total = volume * preco_un
                
                # 2. Valida se o vendedor tem saldo suficiente
                if vendedor.saldo_creditos < volume:
                    mensagem_erro = f"Erro: O vendedor {vendedor.nome} não possui saldo suficiente."
                    return render(request, 'requisicoes_transacao.html', {
                        'user_nome': user_info['nome'],
                        'user_tipo': user_info['tipo'],
                        'requisicoes': requisicoes_pendentes,
                        'mensagem_erro': mensagem_erro,
                        'active_page': 'requisicoes_transacao',
                        'pendencias': get_pendencias()
                    })
                
                # 3. Atualiza saldos
                vendedor.saldo_creditos -= volume
                vendedor.save()
                
                comprador.saldo_creditos += volume
                comprador.save()
                
                # 4. Marca o crédito como vendido
                credito.status = 'Vendido'
                credito.save()
                
                # 5. Cria registro de transação
                Transacao.objects.create(
                    comprador=comprador,
                    vendedor=vendedor,
                    credito=credito,
                    volume=volume,
                    preco_unitario=preco_un
                )
                
                # 6. Atualiza status da requisição
                req_encontrada.status = 'Aprovado'
                req_encontrada.save()

                # 7. Registra a Auditoria
                Auditoria.objects.create(
                    requisicao=req_encontrada,
                    auditor=user,
                    acao='Aprovar',
                    comentario=comentario
                )
                
                mensagem_sucesso = f"Transação #{req_id} APROVADA! {volume} tCO2e transferidos de {vendedor.nome} para {comprador.nome}."
                
            except Exception as e:
                mensagem_erro = f"Erro ao processar transação: {e}"
            
        elif acao == 'rejeitar':
            # Rejeita a requisição e retorna o crédito para o marketplace
            req_encontrada.status = 'Rejeitado'
            req_encontrada.save()
            
            if req_encontrada.credito:
                req_encontrada.credito.status = 'Listado'
                req_encontrada.credito.save()
            
            # Registra a Auditoria
            Auditoria.objects.create(
                requisicao=req_encontrada,
                auditor=user,
                acao='Rejeitar',
                comentario=comentario
            )
            
            mensagem_sucesso = f"Requisição #{req_id} REJEITADA. Crédito retornado ao marketplace."

        elif acao == 'comentar':
            # Apenas registra o comentário sem mudar o status
            Auditoria.objects.create(
                requisicao=req_encontrada,
                auditor=user,
                acao='Comentar',
                comentario=comentario
            )
            mensagem_sucesso = f"Comentário adicionado à Requisição #{req_id}."
        
        return redirect(reverse('requisicoes_transacao'))

    context = {
        'user_nome': user_info['nome'],
        'user_tipo': user_info['tipo'],
        'requisicoes': requisicoes_pendentes,
        'mensagem_sucesso': mensagem_sucesso,
        'mensagem_erro': mensagem_erro,
        'active_page': 'requisicoes_transacao',
        'pendencias': get_pendencias()
    }
    
    return render(request, 'requisicoes_transacao.html', context)


# ====================================================================
# API PÚBLICA
# ====================================================================

# Rota /api/creditos/
def api_creditos_view(request):
    """
    Endpoint simples que retorna todos os créditos de carbono registrados e aprovados
    no formato JSON, promovendo a transparência.
    """
    
    # Busca apenas créditos que foram aprovados (e não vendidos)
    creditos_aprovados = CreditoCarbono.objects.filter(status='Aprovado').select_related('produtor')
    
    data = []
    for credito in creditos_aprovados:
        data.append({
            'id': credito.id,
            'produtor': credito.produtor.nome,
            'origem': credito.origem,
            'quantidade': credito.quantidade,
            'preco_unitario': str(credito.preco_un), # Converte Decimal para string para JSON
            'status': credito.status,
            'data_registro': credito.data_registro.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    return HttpResponse(json.dumps(data, indent=4), content_type='application/json')
