# Arquivo: Back_end/core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # 1. Rota de Apresentação (Pública)
    path('', views.apresentacao_view, name='apresentacao'), # A rota raiz agora aponta para a página pública
    
    # 2. Rotas de Autenticação
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('sair/', views.logout_view, name='sair'),

    # 3. Rotas Protegidas (Dashboard/Operações)
    # A rota do Dashboard não deve ser mais a raiz.
    path('dashboard/', views.dashboard_view, name='dashboard'), 
    path('registro_creditos/', views.registro_creditos_view, name='registro_creditos'),
    path('transacoes/', views.transacoes_view, name='transacoes'),
    
    # 4. Rotas do Auditor (Novas)
    path('requisicoes_registro/', views.requisicoes_registro_view, name='requisicoes_registro'),
    path('requisicoes_transacao/', views.requisicoes_transacao_view, name='requisicoes_transacao'),
]