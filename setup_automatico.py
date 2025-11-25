#!/usr/bin/env python3
"""
Script de Instalação e Setup - Scout Pro
Execute este script para configurar automaticamente o sistema
"""

import os
import sys
import subprocess

def print_header(texto):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"  {texto}")
    print("="*60 + "\n")

def executar_comando(comando, descricao):
    """Executa comando e mostra resultado"""
    print(f"🔄 {descricao}...")
    try:
        result = subprocess.run(comando, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {descricao} concluído!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        return False

def verificar_env():
    """Verifica se .env existe e está configurado"""
    if not os.path.exists('.env'):
        print("\n⚠️  Arquivo .env não encontrado!")
        print("\n📝 Crie um arquivo .env com:")
        print("="*60)
        print("DATABASE_URL=postgresql://user:password@host:port/database")
        print("GOOGLE_SHEETS_ID=your_spreadsheet_id")
        print("GOOGLE_CREDENTIALS_JSON=path/to/credentials.json")
        print("="*60)
        
        criar = input("\nDeseja criar um .env básico agora? (s/n): ")
        if criar.lower() == 's':
            with open('.env', 'w') as f:
                f.write("# Configurações do Scout Pro\n\n")
                f.write("# Banco de Dados PostgreSQL\n")
                f.write("DATABASE_URL=postgresql://user:password@host:port/database\n\n")
                f.write("# Google Sheets\n")
                f.write("GOOGLE_SHEETS_ID=your_spreadsheet_id\n")
                f.write("GOOGLE_CREDENTIALS_JSON=path/to/credentials.json\n")
            print("✅ Arquivo .env criado! Por favor, edite com suas credenciais.")
            return False
        return False
    return True

def main():
    """Função principal de instalação"""
    
    print_header("🚀 SCOUT PRO - INSTALAÇÃO AUTOMÁTICA")
    
    print("Este script irá:")
    print("  1. Instalar dependências necessárias")
    print("  2. Configurar banco de dados")
    print("  3. Criar primeiro usuário admin")
    print("  4. Preparar o sistema para uso\n")
    
    continuar = input("Deseja continuar? (s/n): ")
    if continuar.lower() != 's':
        print("❌ Instalação cancelada")
        return
    
    # Passo 1: Verificar .env
    print_header("1. Verificando Configurações")
    if not verificar_env():
        print("\n⚠️  Configure o .env e execute novamente")
        return
    
    print("✅ Arquivo .env encontrado")
    
    # Passo 2: Instalar dependências
    print_header("2. Instalando Dependências")
    
    dependencias = [
        "beautifulsoup4",
        "requests",
        "openpyxl",
        "lxml"
    ]
    
    for dep in dependencias:
        executar_comando(
            f"pip install {dep}",
            f"Instalando {dep}"
        )
    
    # Passo 3: Configurar banco de dados
    print_header("3. Configurando Banco de Dados")
    
    print("🔄 Criando tabelas necessárias...")
    try:
        from database_extended import ScoutingDatabaseExtended
        db = ScoutingDatabaseExtended()
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        print("\n💡 Verifique se DATABASE_URL está correto no .env")
        return
    
    # Passo 4: Criar primeiro usuário
    print_header("4. Criando Primeiro Usuário Admin")
    
    criar_usuario = input("Deseja criar o usuário admin agora? (s/n): ")
    if criar_usuario.lower() == 's':
        os.system("python criar_primeiro_usuario.py")
    else:
        print("⚠️  Você pode criar o usuário depois com:")
        print("   python criar_primeiro_usuario.py")
    
    # Passo 5: Criar diretório de backups
    print_header("5. Configurando Sistema de Backups")
    
    if not os.path.exists('backups'):
        os.makedirs('backups')
        print("✅ Diretório de backups criado")
    else:
        print("✅ Diretório de backups já existe")
    
    # Passo 6: Resumo final
    print_header("✅ INSTALAÇÃO CONCLUÍDA!")
    
    print("🎉 O Scout Pro está pronto para uso!\n")
    print("📋 Próximos passos:")
    print("   1. Configure suas credenciais no .env (se ainda não fez)")
    print("   2. Crie o primeiro usuário: python criar_primeiro_usuario.py")
    print("   3. Inicie o dashboard: streamlit run app/dashboard.py")
    print("   4. Faça login com suas credenciais")
    print("\n💡 Comandos úteis:")
    print("   - Backup: python backup_system.py")
    print("   - Scraping: python scraping_transfermarkt.py")
    print("\n📖 Leia o GUIA_IMPLEMENTACAO.md para mais informações")
    print("\n" + "="*60)
    print("⚽ Desenvolvido para o Sport Club do Recife")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Instalação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro durante instalação: {e}")
        sys.exit(1)
