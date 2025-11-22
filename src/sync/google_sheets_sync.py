"""
Sincronização Automática com Google Sheets
Sistema de atualização em tempo real do banco de dados
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from src.database.database import ScoutingDatabase
from datetime import datetime
import os
import requests
import time

class GoogleSheetsSyncer:
    def __init__(self, sheet_url):
        """
        Inicializa sincronizador
        
        Args:
            sheet_url: URL completa do Google Sheets
        """
        self.sheet_url = sheet_url
        self.db = ScoutingDatabase()
        self.client = None
        
    def setup_credentials(self):
        """Configura autenticação com Google Sheets"""
        print("🔐 Configurando credenciais...")
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        try:
            # Tentar carregar credenciais
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "❌ Arquivo credentials.json não encontrado!\n"
                    "Siga as instruções no README para criar as credenciais."
                )
            
            self.creds = Credentials.from_service_account_file(
                'credentials.json',
                scopes=scopes
            )
            
            self.client = gspread.authorize(self.creds)
            print("✅ Credenciais configuradas com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar credenciais: {e}")
            return False
    
    def buscar_dados_sheets(self):
        """
        Busca dados atualizados da planilha
        
        Returns:
            DataFrame com dados da planilha
        """
        print("\n📥 Buscando dados do Google Sheets...")
        
        if not self.client:
            if not self.setup_credentials():
                return None
        
        try:
            # Abrir planilha
            sheet = self.client.open_by_url(self.sheet_url)
            worksheet = sheet.get_worksheet(0)  # Primeira aba
            
            # Pegar todos os dados
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            # Verificar se tem dados
            if len(df) == 0:
                print("⚠️  Planilha vazia!")
                return None
            
            # Mapear colunas da planilha para o formato esperado
            # Baseado na imagem da planilha
            df = df.rename(columns={
                'ID': 'ID',
                'Nome': 'Nome',
                'Posição': 'Posição',
                'Nacionalidade': 'Nacionalidade',
                'Idade': 'Idade',
                'Ano': 'Ano',
                'Clube': 'Clube',
                'Liga do Clube': 'Liga do Clube',
                'Fim de Contrato': 'Fim de contrato',
                'Altura': 'Altura',
                'Pé dominante': 'Pé',
                'TM': 'TM',
                'Última atualização': 'Última atualização'
            })
            
            print(f"✅ {len(df)} jogadores carregados do Google Sheets")
            print(f"📊 Colunas encontradas: {list(df.columns)}")
            
            return df
            
        except gspread.exceptions.SpreadsheetNotFound:
            print("❌ Planilha não encontrada! Verifique:")
            print("   1. A URL está correta")
            print("   2. A planilha foi compartilhada com o Service Account")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar dados: {e}")
            return None
    
    def baixar_fotos_transfermarkt(self, df):
        """
        Baixa fotos dos jogadores do Transfermarkt
        
        Args:
            df: DataFrame com dados dos jogadores (deve ter coluna 'TM' com IDs)
        """
        print("\n📸 Baixando fotos do Transfermarkt...")
        
        # Criar pasta de fotos
        os.makedirs('fotos', exist_ok=True)
        
        sucessos = 0
        erros = 0
        
        for _, row in df.iterrows():
            # Verificar se tem ID do Transfermarkt
            if pd.isna(row.get('TM')) or row.get('TM') == '':
                continue
            
            id_jogador = row['ID']
            tm_id = str(row['TM']).strip()
            
            # URL padrão das fotos do Transfermarkt
            foto_url = f'https://img.a.transfermarkt.technology/portrait/big/{tm_id}.jpg'
            
            try:
                response = requests.get(foto_url, timeout=10)
                
                if response.status_code == 200:
                    foto_path = f'fotos/{id_jogador}.jpg'
                    
                    with open(foto_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"  ✓ {row['Nome']}")
                    sucessos += 1
                else:
                    erros += 1
                
                # Pequeno delay para não sobrecarregar
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ✗ Erro em {row['Nome']}: {e}")
                erros += 1
        
        print(f"\n📊 Resultado: {sucessos} fotos baixadas, {erros} erros")
    
    def sincronizar_banco(self, baixar_fotos=True):
        """
        Atualiza banco de dados com dados da planilha
        
        Args:
            baixar_fotos: Se True, baixa fotos do Transfermarkt
        
        Returns:
            True se sincronização foi bem sucedida
        """
        print("\n" + "="*60)
        print("🔄 INICIANDO SINCRONIZAÇÃO")
        print("="*60)
        
        # Buscar dados atualizados
        df = self.buscar_dados_sheets()
        
        if df is None:
            print("\n❌ Sincronização cancelada - erro ao buscar dados")
            return False
        
        # Baixar fotos (se solicitado)
        if baixar_fotos:
            self.baixar_fotos_transfermarkt(df)
        
        # Importar para banco (usa função que já existe)
        print("\n💾 Atualizando banco de dados...")
        self.db.importar_dados_planilha(df)
        
        # Recriar alertas automáticos
        print("\n🚨 Gerando alertas...")
        self.db.criar_alertas_automaticos()
        
        # Estatísticas finais
        print("\n📈 Estatísticas do banco:")
        stats = self.db.get_estatisticas_gerais()
        print(f"   • Total de jogadores: {stats['total_jogadores']}")
        print(f"   • Vínculos ativos: {stats['total_vinculos_ativos']}")
        print(f"   • Contratos vencendo: {stats['contratos_vencendo']}")
        print(f"   • Alertas ativos: {stats['alertas_ativos']}")
        
        print("\n" + "="*60)
        print("✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        
        return True
    
    def sincronizar_automatico(self, intervalo_minutos=60):
        """
        Mantém sincronização automática em loop
        
        Args:
            intervalo_minutos: Intervalo entre sincronizações
        """
        import schedule
        
        schedule.every(intervalo_minutos).minutes.do(
            lambda: self.sincronizar_banco(baixar_fotos=False)  # Fotos só na primeira vez
        )
        
        print(f"\n⏰ Sincronização automática configurada:")
        print(f"   Intervalo: a cada {intervalo_minutos} minutos")
        print(f"   Próxima atualização: {datetime.now().strftime('%H:%M:%S')}")
        print("\n   Pressione Ctrl+C para interromper\n")
        
        # Primeira sincronização
        self.sincronizar_banco(baixar_fotos=True)
        
        # Loop de sincronização
        while True:
            schedule.run_pending()
            time.sleep(60)


def teste_conexao(sheet_url):
    """
    Testa conexão com Google Sheets
    
    Args:
        sheet_url: URL do Google Sheets
    """
    print("\n🧪 TESTE DE CONEXÃO")
    print("="*60)
    
    syncer = GoogleSheetsSyncer(sheet_url)
    
    # Teste 1: Credenciais
    print("\n1️⃣  Testando credenciais...")
    if not syncer.setup_credentials():
        return False
    
    # Teste 2: Acesso à planilha
    print("\n2️⃣  Testando acesso à planilha...")
    df = syncer.buscar_dados_sheets()
    
    if df is not None:
        print(f"\n✅ Conexão bem sucedida!")
        print(f"\n📊 Prévia dos dados (primeiras 3 linhas):")
        print(df.head(3))
        return True
    else:
        return False


if __name__ == "__main__":
    # CONFIGURAÇÃO
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1jNAxJIRoZxYH1jKwPCBrd4Na1ko04EDAYaUCVGsJdIA/edit?gid=0#gid=0"
    
    # Se a URL não foi configurada
    if "COLE_SUA_URL_AQUI" in SHEET_URL:
        print("\n⚠️  ATENÇÃO: Configure a URL da planilha!")
        print("   Edite este arquivo e substitua SHEET_URL pela sua URL")
        print("\n   Exemplo:")
        print('   SHEET_URL = "https://docs.google.com/spreadsheets/d/1ABC.../edit"')
        exit()
    
    # Menu de opções
    print("\n🎯 SISTEMA DE SINCRONIZAÇÃO")
    print("="*60)
    print("1 - Testar conexão")
    print("2 - Sincronizar agora (uma vez)")
    print("3 - Sincronização automática contínua")
    print("="*60)
    
    opcao = input("\nEscolha uma opção (1-3): ").strip()
    
    if opcao == "1":
        teste_conexao(SHEET_URL)
    
    elif opcao == "2":
        syncer = GoogleSheetsSyncer(SHEET_URL)
        syncer.sincronizar_banco(baixar_fotos=True)
    
    elif opcao == "3":
        intervalo = input("Intervalo em minutos (padrão 60): ").strip()
        intervalo = int(intervalo) if intervalo else 60
        
        syncer = GoogleSheetsSyncer(SHEET_URL)
        syncer.sincronizar_automatico(intervalo_minutos=intervalo)
    
    else:
        print("❌ Opção inválida!")
