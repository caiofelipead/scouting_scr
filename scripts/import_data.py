"""
Script de Importação - Google Sheets para Banco de Dados
Converte dados da planilha para estrutura normalizada
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sync.google_sheets_sync import GoogleSheetsSyncer


def processar_importacao():
    """Processa a importação completa dos dados do Google Sheets"""

    # URL da sua planilha
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1jNAxJIRoZxYH1jKwPCBrd4Na1ko04EDAYaUCVGsJdIA/edit?gid=0#gid=0"

    print("\n" + "=" * 60)
    print("🚀 IMPORTAÇÃO INICIAL DE DADOS")
    print("=" * 60)

    # Perguntar se deve limpar dados existentes
    print("\n⚠️  ATENÇÃO: Esta operação pode limpar dados existentes")
    resposta = input("Deseja LIMPAR os dados antes de importar? (sim/não): ")

    limpar_antes = resposta.lower() in ["sim", "s", "yes", "y"]

    # Criar sincronizador
    syncer = GoogleSheetsSyncer(SHEET_URL)

    # Limpar dados se solicitado
    if limpar_antes:
        print("\n🗑️  Limpando dados existentes...")
        syncer.db.limpar_dados()
        print("✅ Dados limpos!")

    # Executar sincronização completa
    sucesso = syncer.sincronizar_banco(baixar_fotos=False)

    if sucesso:
        print("\n" + "=" * 60)
        print("🎯 PRÓXIMOS PASSOS:")
        print("=" * 60)
        print("1. Execute: streamlit run dashboard.py")
        print("2. Acesse o dashboard interativo no navegador")
        print("3. Explore filtros, KPIs e visualizações")
        print("=" * 60)
    else:
        print("\n❌ Importação falhou. Verifique:")
        print("   1. Arquivo credentials.json existe?")
        print("   2. Planilha foi compartilhada com Service Account?")
        print("   3. APIs do Google estão ativadas?")

    return sucesso


if __name__ == "__main__":
    processar_importacao()
