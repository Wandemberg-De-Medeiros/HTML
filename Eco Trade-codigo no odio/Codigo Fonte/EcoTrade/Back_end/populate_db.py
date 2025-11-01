import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecotrade.settings')
django.setup()

from core.models import Usuario, CreditoCarbono, Requisicao
from decimal import Decimal

# Limpar dados existentes (opcional)
print("Limpando dados existentes...")
# Usuario.objects.all().delete()
# CreditoCarbono.objects.all().delete()
# Requisicao.objects.all().delete()

# Criar usuários
print("Criando usuários...")

# Administrador
admin, created = Usuario.objects.get_or_create(
    email='admin@ecotrade.com',
    defaults={
        'senha': 'admin123',
        'nome': 'Administrador Sistema',
        'tipo': 'Administrador',
        'documento': '00000000000',
        'cidade': 'Belém',
        'estado': 'Pará'
    }
)
if created:
    print(f"✓ Administrador criado: {admin.nome}")
else:
    print(f"✓ Administrador já existe: {admin.nome}")

# Produtor Rural 1
produtor1, created = Usuario.objects.get_or_create(
    email='joao@produtor.com',
    defaults={
        'senha': '123456',
        'nome': 'João Silva',
        'tipo': 'Produtor Rural',
        'saldo_creditos': Decimal('0.00'),
        'documento': '12345678901',
        'cidade': 'Santarém',
        'estado': 'Pará'
    }
)
if created:
    print(f"✓ Produtor Rural criado: {produtor1.nome}")
else:
    print(f"✓ Produtor Rural já existe: {produtor1.nome}")

# Produtor Rural 2
produtor2, created = Usuario.objects.get_or_create(
    email='maria@produtor.com',
    defaults={
        'senha': '123456',
        'nome': 'Maria Santos',
        'tipo': 'Produtor Rural',
        'saldo_creditos': Decimal('0.00'),
        'documento': '98765432109',
        'cidade': 'Altamira',
        'estado': 'Pará'
    }
)
if created:
    print(f"✓ Produtor Rural criado: {produtor2.nome}")
else:
    print(f"✓ Produtor Rural já existe: {produtor2.nome}")

# Empresa Compradora 1
empresa1, created = Usuario.objects.get_or_create(
    email='empresa@verde.com',
    defaults={
        'senha': '123456',
        'nome': 'Empresa Verde Ltda',
        'tipo': 'Empresa Compradora',
        'saldo_creditos': Decimal('0.00'),
        'documento': '12345678000190',
        'cidade': 'São Paulo',
        'estado': 'São Paulo'
    }
)
if created:
    print(f"✓ Empresa Compradora criada: {empresa1.nome}")
else:
    print(f"✓ Empresa Compradora já existe: {empresa1.nome}")

# Empresa Compradora 2
empresa2, created = Usuario.objects.get_or_create(
    email='sustentavel@corp.com',
    defaults={
        'senha': '123456',
        'nome': 'Sustentável Corp',
        'tipo': 'Empresa Compradora',
        'saldo_creditos': Decimal('0.00'),
        'documento': '98765432000180',
        'cidade': 'Rio de Janeiro',
        'estado': 'Rio de Janeiro'
    }
)
if created:
    print(f"✓ Empresa Compradora criada: {empresa2.nome}")
else:
    print(f"✓ Empresa Compradora já existe: {empresa2.nome}")

print("\n" + "="*60)
print("RESUMO DOS USUÁRIOS CRIADOS")
print("="*60)
print("\nPara fazer login, use:")
print("\n1. ADMINISTRADOR:")
print(f"   Email: admin@ecotrade.com")
print(f"   Senha: admin123")
print("\n2. PRODUTOR RURAL (João Silva):")
print(f"   Email: joao@produtor.com")
print(f"   Senha: 123456")
print("\n3. PRODUTOR RURAL (Maria Santos):")
print(f"   Email: maria@produtor.com")
print(f"   Senha: 123456")
print("\n4. EMPRESA COMPRADORA (Empresa Verde Ltda):")
print(f"   Email: empresa@verde.com")
print(f"   Senha: 123456")
print("\n5. EMPRESA COMPRADORA (Sustentável Corp):")
print(f"   Email: sustentavel@corp.com")
print(f"   Senha: 123456")
print("\n" + "="*60)
print("Banco de dados populado com sucesso!")
print("="*60)
