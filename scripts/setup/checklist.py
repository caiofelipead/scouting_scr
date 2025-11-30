"""
Checklist de Configuração do Sistema
Verifica se tudo está pronto para usar
"""

import os
import sys


def check_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    if version >= (3, 8):
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"Python {version.major}.{version.minor} (requer 3.8+)"


def check_dependencies():
    """Verifica se as bibliotecas estão instaladas"""
    required = [
        "streamlit",
        "pandas",
        "plotly",
        "gspread",
        "google.auth",
        "requests",
        "schedule",
    ]

    missing = []
    installed = []

    for package in required:
        try:
            __import__(package)
            installed.append(package)
        except ImportError:
            missing.append(package)

    if missing:
        return False, f"Faltam: {', '.join(missing)}"
    else:
        return True, f"Todas instaladas ({len(installed)}/{len(required)})"


def check_credentials():
    """Verifica se credentials.json existe"""
    if os.path.exists("credentials.json"):
        return True, "credentials.json encontrado"
    else:
        return False, "credentials.json NÃO encontrado"


def check_project_structure():
    """Verifica se os arquivos necessários existem"""
    required_files = [
        "database.py",
        "google_sheets_sync.py",
        "dashboard.py",
        "import_data.py",
        "requirements.txt",
    ]

    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)

    if missing:
        return False, f"Faltam: {', '.join(missing)}"
    else:
        return (
            True,
            f"Todos os arquivos presentes ({len(required_files)}/{len(required_files)})",
        )


def check_folders():
    """Verifica pastas necessárias"""
    if not os.path.exists("fotos"):
        try:
            os.makedirs("fotos")
            return True, "Pasta 'fotos/' criada"
        except Exception:
            return False, "Erro ao criar pasta 'fotos/'"
    else:
        return True, "Pasta 'fotos/' já existe"


def check_database_connection():
    """Testa conexão com banco de dados"""
    try:
        from src.database.database_antigo_sqlite import ScoutingDatabase

        db = ScoutingDatabase()
        return True, "Banco de dados OK"
    except Exception as e:
        return False, f"Erro: {str(e)}"


def check_google_sheets():
    """Testa conexão com Google Sheets (se credenciais existem)"""
    if not os.path.exists("credentials.json"):
        return None, "Pule - configure credentials.json primeiro"

    try:
        from src.sync.google_sheets_sync import GoogleSheetsSyncer

        SHEET_URL = "https://docs.google.com/spreadsheets/d/1jNAxJIRoZxYH1jKwPCBrd4Na1ko04EDAYaUCVGsJdIA/edit?gid=0#gid=0"

        syncer = GoogleSheetsSyncer(SHEET_URL)
        if syncer.setup_credentials():
            df = syncer.buscar_dados_sheets()
            if df is not None:
                return True, f"Conectado - {len(df)} jogadores encontrados"
            else:
                return False, "Falha ao buscar dados - verifique compartilhamento"
        else:
            return False, "Falha na autenticação"
    except Exception as e:
        return False, f"Erro: {str(e)}"


def run_checklist():
    """Executa todos os checks"""
    print("\n" + "=" * 60)
    print("🔍 CHECKLIST DE CONFIGURAÇÃO - SCOUT PRO")
    print("=" * 60 + "\n")

    checks = [
        ("1. Versão do Python", check_python_version),
        ("2. Dependências instaladas", check_dependencies),
        ("3. Arquivo de credenciais", check_credentials),
        ("4. Estrutura do projeto", check_project_structure),
        ("5. Pastas necessárias", check_folders),
        ("6. Conexão com banco de dados", check_database_connection),
        ("7. Conexão com Google Sheets", check_google_sheets),
    ]

    results = []

    for name, check_func in checks:
        try:
            status, message = check_func()

            if status is True:
                icon = "✅"
                color = ""
            elif status is False:
                icon = "❌"
                color = ""
            else:  # None = skip
                icon = "⏭️ "
                color = ""

            print(f"{icon} {name}")
            print(f"   {message}\n")

            results.append(status)

        except Exception as e:
            print(f"❌ {name}")
            print(f"   Erro inesperado: {e}\n")
            results.append(False)

    # Resumo final
    print("=" * 60)
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)

    if failed == 0 and skipped == 0:
        print("🎉 TUDO PRONTO! Sistema configurado corretamente.")
        print("\n📋 Próximos passos:")
        print("   1. python import_data.py       # Importar dados")
        print("   2. streamlit run dashboard.py  # Abrir dashboard")
    elif failed > 0:
        print(f"⚠️  {failed} problema(s) encontrado(s)")
        print("\n📖 Consulte o README.md para resolver os problemas")

        if not os.path.exists("credentials.json"):
            print("\n🔑 AÇÃO NECESSÁRIA:")
            print("   Configure o Google Sheets API (veja Passo 2 do README)")
    else:
        print(f"⏭️  {skipped} item(s) pendente(s)")
        print("\n📖 Complete a configuração seguindo o README.md")

    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    run_checklist()
