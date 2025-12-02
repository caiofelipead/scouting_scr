"""
Script para criar primeiro usuário - Scout Pro
Execute este script para criar o usuário administrador inicial
"""

from dotenv import load_dotenv  # ← ADICIONE ESTA LINHA
from pathlib import Path
import os

# ← ADICIONE ESTAS LINHAS
# Carrega variáveis do .env ANTES de qualquer verificação
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, override=True)

from auth import AuthManager  # ← Mova o import para depois do load_dotenv


def criar_primeiro_usuario():
    """Cria o primeiro usuário administrador do sistema"""
    
    print("="*50)
    print("🔐 CRIAÇÃO DO PRIMEIRO USUÁRIO ADMIN")
    print("="*50)
    print()
    
    auth = AuthManager()
    try:
        usuarios = auth.listar_usuarios()
        if any(u['nivel'] == 'admin' for u in usuarios):
            print("⚠️  Já existe um usuário admin no sistema!")
            print()
            sobrescrever = input("Deseja criar um novo admin mesmo assim? (s/n): ")
            if sobrescrever.lower() != 's':
                print("❌ Operação cancelada")
                return
    except:
        pass  # Tabela ainda não existe
    
    print("\n📝 Digite as informações do novo usuário:\n")
    
    # Coleta informações
    username = input("Username: ").strip()
    if not username:
        print("❌ Username não pode ser vazio")
        return
    
    nome_completo = input("Nome Completo: ").strip()
    if not nome_completo:
        print("❌ Nome não pode ser vazio")
        return
    
    email = input("Email (opcional): ").strip() or None
    
    # Senha
    import getpass
    while True:
        senha = getpass.getpass("Senha: ")
        if len(senha) < 6:
            print("❌ A senha deve ter pelo menos 6 caracteres")
            continue
        
        confirma = getpass.getpass("Confirme a senha: ")
        if senha != confirma:
            print("❌ As senhas não coincidem")
            continue
        
        break
    
    # Cria o usuário
    print("\n🔄 Criando usuário...")
    
    sucesso = auth.criar_usuario(
        username=username,
        senha=senha,
        nome_completo=nome_completo,
        email=email,
        nivel_acesso="admin"
    )
    
    if sucesso:
        print("\n" + "="*50)
        print("✅ USUÁRIO ADMIN CRIADO COM SUCESSO!")
        print("="*50)
        print(f"\n👤 Username: {username}")
        print(f"📧 Email: {email or 'Não informado'}")
        print(f"🎫 Nível: ADMIN")
        print("\n⚠️  IMPORTANTE:")
        print("   - Guarde essas credenciais em local seguro")
        print("   - Use o dashboard para criar outros usuários")
        print("   - Você pode alterar sua senha no sistema")
        print("\n🚀 Inicie o dashboard com: streamlit run app/dashboard.py")
        print("="*50)
    else:
        print("\n❌ ERRO ao criar usuário!")
        print("   - Username já existe OU")
        print("   - Erro de conexão com o banco")
        print("\n💡 Verifique:")
        print("   - Variável DATABASE_URL configurada no .env")
        print("   - Conexão com o banco PostgreSQL")


def criar_usuario_scout():
    """Cria um usuário scout adicional"""
    
    print("="*50)
    print("👤 CRIAÇÃO DE USUÁRIO SCOUT")
    print("="*50)
    print()
    
    auth = AuthManager()
    
    print("📝 Digite as informações do novo scout:\n")
    
    username = input("Username: ").strip()
    nome_completo = input("Nome Completo: ").strip()
    email = input("Email (opcional): ").strip() or None
    
    import getpass
    senha = getpass.getpass("Senha: ")
    
    if auth.criar_usuario(username, senha, nome_completo, email, "scout"):
        print("\n✅ Scout criado com sucesso!")
        print(f"Username: {username}")
    else:
        print("\n❌ Erro ao criar scout (username já existe)")


def menu_principal():
    """Menu principal do script"""
    
    print("\n" + "="*50)
    print("🔐 SCOUT PRO - GERENCIAMENTO DE USUÁRIOS")
    print("="*50)
    print("\n1. Criar primeiro usuário ADMIN")
    print("2. Criar usuário SCOUT")
    print("3. Listar usuários")
    print("4. Sair")
    print()
    
    opcao = input("Escolha uma opção (1-4): ").strip()
    
    if opcao == "1":
        criar_primeiro_usuario()
    elif opcao == "2":
        criar_usuario_scout()
    elif opcao == "3":
        auth = AuthManager()
        usuarios = auth.listar_usuarios()
        print("\n📋 USUÁRIOS CADASTRADOS:")
        print("="*50)
        for u in usuarios:
            status = "🟢" if u['ativo'] else "🔴"
            print(f"\n{status} {u['nome']}")
            print(f"   Username: {u['username']}")
            print(f"   Nível: {u['nivel']}")
            print(f"   Email: {u['email'] or 'N/A'}")
            if u['ultimo_acesso']:
                print(f"   Último acesso: {u['ultimo_acesso']}")
    elif opcao == "4":
        print("\n👋 Até logo!")
        return False
    else:
        print("\n❌ Opção inválida")
    
    return True


if __name__ == "__main__":
    # Verifica se DATABASE_URL está configurada
    if not os.getenv('DATABASE_URL'):
        print("\n❌ ERRO: Variável DATABASE_URL não configurada!")
        print("\n💡 Configure o .env com:")
        print("   DATABASE_URL=postgresql://user:password@host:port/database")
        exit(1)
    
    # Menu interativo
    continuar = True
    while continuar:
        continuar = menu_principal()
        if continuar:
            input("\n\nPressione ENTER para continuar...")
