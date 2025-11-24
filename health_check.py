"""
Health Check - Verificação de Saúde da Aplicação
Verifica se todos os componentes do sistema estão funcionando
"""

import os
import sys
from datetime import datetime
import pandas as pd

def verificar_ambiente():
    """Verifica configuração do ambiente"""
    print("="*60)
    print("🔍 VERIFICAÇÃO DE AMBIENTE")
    print("="*60)
    
    checks = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'GOOGLE_SHEETS_CREDENTIALS_JSON': os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON'),
        'GOOGLE_SHEET_URL': os.getenv('GOOGLE_SHEET_URL'),
    }
    
    print("\n📋 Variáveis de Ambiente:")
    for key, value in checks.items():
        if value:
            if key == 'GOOGLE_SHEETS_CREDENTIALS_JSON':
                print(f"   ✅ {key}: Configurada (JSON {len(value)} chars)")
            else:
                # Oculta parte da URL por segurança
                display_value = value[:30] + "..." if len(value) > 30 else value
                print(f"   ✅ {key}: {display_value}")
        else:
            print(f"   ⚠️ {key}: NÃO configurada")
    
    # Detectar tipo de banco
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        if db_url.startswith('postgresql') or db_url.startswith('postgres'):
            db_type = "PostgreSQL (Railway)"
        else:
            db_type = "Outro"
    else:
        db_type = "SQLite (Local)"
    
    print(f"\n💾 Banco de Dados: {db_type}")
    
    return checks

def verificar_database():
    """Verifica conexão e dados do banco"""
    print("\n" + "="*60)
    print("💾 VERIFICAÇÃO DE BANCO DE DADOS")
    print("="*60)
    
    try:
        from database import ScoutingDatabase
        
        print("\n🔌 Testando conexão...")
        db = ScoutingDatabase()
        
        if not db.verificar_saude_conexao():
            print("❌ Falha na conexão com o banco!")
            return False
        
        print("\n📊 Verificando dados...")
        stats = db.obter_estatisticas()
        
        print(f"\n📈 Estatísticas:")
        print(f"   Jogadores cadastrados: {stats.get('total_jogadores', 0)}")
        print(f"   Alertas ativos: {stats.get('alertas_ativos', 0)}")
        print(f"   Contratos vencendo: {stats.get('contratos_vencendo', 0)}")
        
        if stats.get('total_jogadores', 0) == 0:
            print("\n⚠️ ATENÇÃO: Nenhum jogador cadastrado!")
            print("   Execute a migração de dados ou importação do Google Sheets")
        
        # Teste de leitura
        print("\n🧪 Testando leitura de dados...")
        df = db.buscar_todos_jogadores()
        
        if not df.empty:
            print(f"   ✅ Leitura OK - {len(df)} registros")
            print(f"\n   📋 Primeiros jogadores:")
            for i, row in df.head(3).iterrows():
                print(f"      • {row['nome']} - {row['posicao']} ({row['clube']})")
        else:
            print("   ⚠️ Nenhum dado retornado na consulta")
        
        db.fechar_conexao()
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulo database: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar banco de dados: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("\n" + "="*60)
    print("📦 VERIFICAÇÃO DE DEPENDÊNCIAS")
    print("="*60 + "\n")
    
    dependencias = {
        'streamlit': 'Interface web',
        'pandas': 'Manipulação de dados',
        'sqlalchemy': 'ORM banco de dados',
        'psycopg2': 'Driver PostgreSQL',
        'plotly': 'Visualizações',
        'gspread': 'Google Sheets',
        'beautifulsoup4': 'Web scraping'
    }
    
    falhas = []
    
    for modulo, descricao in dependencias.items():
        try:
            if modulo == 'psycopg2':
                __import__('psycopg2')
            else:
                __import__(modulo)
            print(f"   ✅ {modulo:<20} - {descricao}")
        except ImportError:
            print(f"   ❌ {modulo:<20} - {descricao} (NÃO INSTALADO)")
            falhas.append(modulo)
    
    if falhas:
        print(f"\n⚠️ Dependências faltando: {', '.join(falhas)}")
        print("   Execute: pip install -r requirements.txt")
        return False
    
    return True

def verificar_google_sheets():
    """Verifica conexão com Google Sheets"""
    print("\n" + "="*60)
    print("📊 VERIFICAÇÃO DO GOOGLE SHEETS")
    print("="*60)
    
    credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
    sheet_url = os.getenv('GOOGLE_SHEET_URL')
    
    if not credentials_json:
        print("\n⚠️ GOOGLE_SHEETS_CREDENTIALS_JSON não configurada")
        print("   Google Sheets sync não funcionará")
        return False
    
    if not sheet_url:
        print("\n⚠️ GOOGLE_SHEET_URL não configurada")
        print("   Configure a URL da planilha")
        return False
    
    try:
        import json
        from oauth2client.service_account import ServiceAccountCredentials
        import gspread
        
        print("\n🔐 Validando credenciais...")
        credentials_dict = json.loads(credentials_json)
        
        required_keys = ['client_email', 'private_key', 'project_id']
        for key in required_keys:
            if key not in credentials_dict:
                print(f"   ❌ Chave '{key}' não encontrada nas credenciais")
                return False
        
        print("   ✅ Credenciais válidas")
        print(f"   📧 Service Account: {credentials_dict['client_email']}")
        
        print("\n🔌 Testando conexão com Google Sheets...")
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            credentials_dict, 
            scope
        )
        client = gspread.authorize(credentials)
        
        print("   ✅ Autenticação OK")
        
        print(f"\n📄 Acessando planilha...")
        planilha = client.open_by_url(sheet_url)
        
        print(f"   ✅ Planilha acessada: {planilha.title}")
        print(f"   📊 Abas disponíveis: {[ws.title for ws in planilha.worksheets()]}")
        
        # Ler primeira linha para testar
        worksheet = planilha.sheet1
        primeira_linha = worksheet.row_values(1)
        print(f"   📋 Colunas: {', '.join(primeira_linha)}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Erro ao decodificar JSON: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erro ao conectar: {e}")
        return False

def verificar_arquivos():
    """Verifica se arquivos essenciais existem"""
    print("\n" + "="*60)
    print("📁 VERIFICAÇÃO DE ARQUIVOS")
    print("="*60 + "\n")
    
    arquivos = {
        'database.py': 'Módulo de banco de dados',
        'dashboard.py': 'Dashboard Streamlit',
        'requirements.txt': 'Dependências Python',
        'google_sheets_sync.py': 'Sincronização Google Sheets (opcional)',
    }
    
    todos_ok = True
    
    for arquivo, descricao in arquivos.items():
        if os.path.exists(arquivo):
            size = os.path.getsize(arquivo)
            print(f"   ✅ {arquivo:<30} - {descricao} ({size} bytes)")
        else:
            print(f"   ⚠️ {arquivo:<30} - {descricao} (NÃO ENCONTRADO)")
            if arquivo in ['database.py', 'dashboard.py', 'requirements.txt']:
                todos_ok = False
    
    return todos_ok

def gerar_relatorio():
    """Gera relatório completo de health check"""
    print("\n" + "="*60)
    print(f"🏥 HEALTH CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    resultados = {
        'Ambiente': verificar_ambiente(),
        'Arquivos': verificar_arquivos(),
        'Dependências': verificar_dependencias(),
        'Banco de Dados': verificar_database(),
        'Google Sheets': verificar_google_sheets()
    }
    
    print("\n" + "="*60)
    print("📊 RESUMO DO HEALTH CHECK")
    print("="*60 + "\n")
    
    for componente, status in resultados.items():
        if isinstance(status, bool):
            emoji = "✅" if status else "❌"
            print(f"   {emoji} {componente}")
        else:
            print(f"   ℹ️ {componente}")
    
    # Contabilizar sucessos
    checks_bool = [v for v in resultados.values() if isinstance(v, bool)]
    total = len(checks_bool)
    sucessos = sum(checks_bool)
    
    print(f"\n📈 Score: {sucessos}/{total} componentes OK")
    
    if sucessos == total:
        print("\n🎉 Sistema totalmente operacional!")
        return 0
    elif sucessos >= total * 0.7:
        print("\n⚠️ Sistema parcialmente operacional")
        print("   Alguns componentes precisam de atenção")
        return 1
    else:
        print("\n❌ Sistema com problemas críticos")
        print("   Verifique os erros acima antes de usar")
        return 2

def main():
    """Função principal"""
    try:
        exit_code = gerar_relatorio()
        
        print("\n" + "="*60)
        print("🔧 PRÓXIMOS PASSOS")
        print("="*60)
        
        if exit_code == 0:
            print("\nSistema pronto para uso!")
            print("Execute: streamlit run dashboard.py")
        elif exit_code == 1:
            print("\nCorreções necessárias:")
            print("1. Configure variáveis de ambiente faltantes")
            print("2. Execute migração de dados se necessário")
            print("3. Verifique configurações do Google Sheets")
        else:
            print("\nCorreções URGENTES necessárias:")
            print("1. Instale dependências: pip install -r requirements.txt")
            print("2. Configure DATABASE_URL")
            print("3. Verifique erros de conexão com banco")
        
        print("\n" + "="*60)
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n❌ Health check interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Erro fatal no health check: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
