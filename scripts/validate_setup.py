#!/usr/bin/env python3
"""Script de validação do setup completo"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config

def check_structure():
    """Verifica estrutura de diretórios"""
    print("📁 Verificando estrutura de diretórios...")
    
    required_dirs = [
        Config.DATA_DIR,
        Config.LOGS_DIR,
        Config.BACKUPS_DIR,
        Config.PHOTOS_DIR,
        Config.BASE_DIR / 'src',
        Config.BASE_DIR / 'app',
        Config.BASE_DIR / 'scripts',
        Config.BASE_DIR / 'tests',
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"  ✅ {dir_path.name}")
        else:
            print(f"  ❌ {dir_path.name} não encontrado")
            all_exist = False
    
    return all_exist

def check_files():
    """Verifica arquivos essenciais"""
    print("\n📄 Verificando arquivos essenciais...")
    
    required_files = [
        (Config.BASE_DIR / 'requirements.txt', True),
        (Config.BASE_DIR / 'Makefile', True),
        (Config.BASE_DIR / '.gitignore', True),
        (Config.BASE_DIR / 'src' / 'config.py', True),
        (Config.BASE_DIR / '.env', False),  # Opcional localmente
    ]
    
    all_exist = True
    for file_path, required in required_files:
        if file_path.exists():
            print(f"  ✅ {file_path.name}")
        elif required:
            print(f"  ❌ {file_path.name} não encontrado")
            all_exist = False
        else:
            print(f"  ⚠️  {file_path.name} não encontrado (opcional)")
    
    return all_exist

def check_credentials():
    """Verifica credenciais (com aviso se não existir)"""
    print("\n🔐 Verificando credenciais...")
    
    if Config.GOOGLE_CREDENTIALS_PATH.exists():
        print(f"  ✅ credentials.json encontrado")
        return True
    else:
        print(f"  ⚠️  credentials.json não encontrado")
        print(f"     (Normal em desenvolvimento - necessário para produção)")
        return True  # Não falha a validação

def main():
    """Executa todas as validações"""
    print("="*60)
    print("�� Validação Completa do Scout Pro")
    print("="*60)
    print()
    
    checks = [
        ("Estrutura", check_structure()),
        ("Arquivos", check_files()),
        ("Credenciais", check_credentials()),
    ]
    
    print("\n" + "="*60)
    print("📊 RESUMO DA VALIDAÇÃO")
    print("="*60)
    
    for name, result in checks:
        status = "✅ OK" if result else "❌ FALHOU"
        print(f"{name}: {status}")
    
    all_ok = all(result for _, result in checks)
    
    if all_ok:
        print("\n✅ Todas as verificações passaram!")
        print("💡 Para usar em produção, adicione credentials.json")
        return 0
    else:
        print("\n⚠️  Algumas verificações falharam.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
