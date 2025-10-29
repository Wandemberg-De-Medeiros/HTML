# Arquivo: Back_end/core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Rota de Saída/Apresentação (Landing Page)
    path('', views.apresentacao_view, name='apresentacao'),
    
    # Rota de Autenticação
    path('login/', views.login_view, name='login'),
    path('sair/', views.sair_view, name='sair'),

    # Rotas do Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('registro_creditos/', views.registro_creditos_view, name='registro_creditos'),
    path('transacoes/', views.transacoes_view, name='transacoes'),
]