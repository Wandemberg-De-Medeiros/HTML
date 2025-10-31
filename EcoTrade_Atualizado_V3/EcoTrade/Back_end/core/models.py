from django.db import models

# Opções de Tipos de Usuário
TIPO_USUARIO_CHOICES = (
    ('Administrador', 'Administrador'),
    ('Produtor Rural', 'Produtor Rural'),
    ('Empresa Compradora', 'Empresa Compradora'),
)

# Opções de Status de Crédito/Requisição
STATUS_CHOICES = (
    ('Aprovado', 'Aprovado'),
    ('Pendente', 'Pendente'),
    ('Rejeitado', 'Rejeitado'),
    ('Vendido', 'Vendido'),
    ('Listado', 'Listado'),
)

# 1. MODELO DE USUÁRIO
class Usuario(models.Model):
    # O email será a chave principal (única)
    email = models.EmailField(unique=True) 
    senha = models.CharField(max_length=128) # Senha deve ser hashizada em produção
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=TIPO_USUARIO_CHOICES)
    saldo_creditos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Campos extras para cadastro (que estavam sendo ignorados no views.py)
    documento = models.CharField(max_length=50, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.tipo})"

# 2. MODELO DE CRÉDITO (Créditos registrados e aprovados, listados no Marketplace)
class CreditoCarbono(models.Model):
    # Chave estrangeira ligando o crédito ao Produtor que o gerou
    produtor = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo': 'Produtor Rural'})
    origem = models.CharField(max_length=255)
    quantidade = models.IntegerField()
    preco_un = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    data_registro = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Aprovado') # Só armazena créditos aprovados

    def __str__(self):
        return f"Crédito {self.id} - {self.origem} ({self.quantidade} tCO2e)"

# 3. MODELO DE REQUISIÇÃO (Para Registro e Transação)
class Requisicao(models.Model):
    TIPO_REQUISICAO_CHOICES = (
        ('Registro', 'Registro de Créditos'),
        ('Venda', 'Venda de Créditos'),
        ('Compra', 'Compra de Créditos'),
    )
    
    tipo_requisicao = models.CharField(max_length=50, choices=TIPO_REQUISICAO_CHOICES)
    
    # Quem enviou a requisição (Pode ser Produtor ou Empresa Compradora)
    usuario_origem = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='requisicoes_enviadas') 
    
    # NOVO: Crédito relacionado à requisição (para Venda/Compra)
    credito = models.ForeignKey(CreditoCarbono, on_delete=models.CASCADE, null=True, blank=True, related_name='requisicoes')
    
    # Dados variáveis dependendo do tipo (usamos campos opcionais)
    volume = models.IntegerField(null=True, blank=True)
    preco_un = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    origem_credito = models.CharField(max_length=255, null=True, blank=True) # Apenas para Requisição Tipo 'Registro'
    
    data_envio = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pendente')

    def __str__(self):
        return f"Req. {self.id} - {self.tipo_requisicao} ({self.status})"

# 4. MODELO DE TRANSAÇÃO (Histórico de Compra/Venda)
class Transacao(models.Model):
    TIPO_TRANSACAO_CHOICES = (
        ('Compra', 'Compra'),
        ('Venda', 'Venda'),
    )
    
    # Quem comprou
    comprador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='compras', limit_choices_to={'tipo': 'Empresa Compradora'})
    
    # Quem vendeu
    vendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='vendas', limit_choices_to={'tipo': 'Produtor Rural'})
    
    # Crédito transacionado
    credito = models.ForeignKey(CreditoCarbono, on_delete=models.CASCADE, related_name='transacoes')
    
    # Detalhes da transação
    volume = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    preco_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Data da transação
    data_transacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Transação {self.id} - {self.comprador.nome} comprou de {self.vendedor.nome}"
    
    def save(self, *args, **kwargs):
        # Calcula o preço total automaticamente
        self.preco_total = self.volume * self.preco_unitario
        super().save(*args, **kwargs)

# 5. MODELO DE AUDITORIA (Comentários e Histórico de Ações)
class Auditoria(models.Model):
    # Relaciona a ação a uma requisição (Registro ou Transação)
    requisicao = models.ForeignKey(Requisicao, on_delete=models.CASCADE, related_name='auditorias')
    
    # Quem realizou a ação (sempre o Administrador)
    auditor = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo': 'Administrador'})
    
    # Ação realizada (Aprovar, Rejeitar, Comentar)
    ACAO_CHOICES = (
        ('Aprovar', 'Aprovar'),
        ('Rejeitar', 'Rejeitar'),
        ('Comentar', 'Comentar'),
    )
    acao = models.CharField(max_length=50, choices=ACAO_CHOICES)
    
    comentario = models.TextField(blank=True, null=True)
    data_acao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Auditoria Req. {self.requisicao.id} - {self.acao} por {self.auditor.nome}"
