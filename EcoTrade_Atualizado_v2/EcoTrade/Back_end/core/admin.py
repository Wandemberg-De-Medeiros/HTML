from django.contrib import admin
from .models import Usuario, CreditoCarbono, Requisicao, Transacao

# Registra os modelos no painel administrativo do Django
admin.site.register(Usuario)
admin.site.register(CreditoCarbono)
admin.site.register(Requisicao)
admin.site.register(Transacao)
