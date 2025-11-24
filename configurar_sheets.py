#!/usr/bin/env python3
"""
Script de Configuração e Teste - Google Sheets Sync
Configura variáveis de ambiente e testa a conexão
"""

import os
import sys
import json

def configurar_ambiente():
    """Configura variáveis de ambiente para o Google Sheets"""
    print("=" * 70)
    print("🔧 CONFIGURADOR DE AMBIENTE - GOOGLE SHEETS")
    print("=" * 70)
    print()

    # URL da planilha
    sheet_url = "https://docs.google.com/spreadsheets/d/1jNAxJIRoZxYH1jKwPCBrd4Na1ko04EDAYaUCVGsJdIA"

    # Verificar se credentials.json existe
    if not os.path.exists('credentials.json'):
        print("❌ Arquivo credentials.json não encontrado!")
        print()
        print("📝 Para criar o arquivo credentials.json:")
        print("   1. Acesse https://console.cloud.google.com/iam-admin/serviceaccounts")
        print("   2. Selecione o projeto: scout-database-477916")
        print("   3. Clique na service account: scr-scouting@scout-database-477916.iam.gserviceaccount.com")
        print("   4. Vá para a aba KEYS")
        print("   5. Clique em ADD KEY → Create new key → JSON")
        print("   6. Salve o arquivo como credentials.json neste diretório")
        print()
        print("⚠️  IMPORTANTE: Revogue as chaves antigas antes de criar uma nova!")
        print()
        return False

    print("✅ Arquivo credentials.json encontrado!")

    # Definir variável de ambiente GOOGLE_SHEET_URL
    print("\n🔗 Configurando GOOGLE_SHEET_URL...")
    os.environ['GOOGLE_SHEET_URL'] = sheet_url
    print(f"✅ URL configurada: {sheet_url}")

    print("\n" + "=" * 70)
    print("✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 70)
    print("\n📋 Próximos passos:")
    print("   1. Execute: python configurar_sheets.py (para testar)")
    print("   2. Ou execute: GOOGLE_SHEET_URL='...' python corrigir_tudo.py")
    print()
    return True

def testar_conexao():
    """Testa a conexão com Google Sheets"""
    print("\n🧪 Testando conexão com Google Sheets...")

    try:
        from google_sheets_sync_streamlit import GoogleSheetsSync

        sync = GoogleSheetsSync()

        # Tentar conectar
        sheet_url = os.getenv('GOOGLE_SHEET_URL')
        if not sheet_url:
            print("❌ GOOGLE_SHEET_URL não definida!")
            return False

        if sync.conectar_planilha(sheet_url):
            print("✅ Conexão bem-sucedida!")

            # Tentar ler dados
            df = sync.ler_dados_planilha()
            if not df.empty:
                print(f"✅ Planilha possui {len(df)} linhas de dados")
                print(f"\n📊 Colunas encontradas: {', '.join(df.columns)}")
                return True
            else:
                print("⚠️ Planilha está vazia!")
                return False
        else:
            print("❌ Falha na conexão!")
            return False

    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        print("   Instale as dependências: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
        return False

if __name__ == "__main__":
    if configurar_ambiente():
        # Perguntar se quer testar
        resposta = input("\n🔍 Deseja testar a conexão agora? (s/n): ").strip().lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            testar_conexao()
