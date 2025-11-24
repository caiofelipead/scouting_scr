"""
Google Sheets Sync - Compatível com Streamlit Cloud, Railway e Local
Sincronização com Google Sheets usando credenciais de múltiplas fontes
"""

import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd
from database import ScoutingDatabase
import re

class GoogleSheetsSync:
    def __init__(self):
        """Inicializa conexão com Google Sheets (multi-ambiente)"""
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        self.credentials = self._get_credentials()
        
        if self.credentials:
            self.client = gspread.authorize(self.credentials)
        
        # URL da planilha
        self.sheet_url = self._get_sheet_url()
        
        if not self.sheet_url:
            print("⚠️ GOOGLE_SHEET_URL não configurada.")
        
        self.db = ScoutingDatabase()
    
    def _get_credentials(self):
        """Obtém credenciais de diferentes fontes (prioridade: Streamlit → Env Var → Local)"""
        
        # 1. STREAMLIT CLOUD: Tenta usar st.secrets
        try:
            import streamlit as st
            if 'gcp_service_account' in st.secrets:
                print("🔵 Usando credenciais do Streamlit Secrets...")
                credentials_dict = dict(st.secrets["gcp_service_account"])
                return ServiceAccountCredentials.from_json_keyfile_dict(
                    credentials_dict,
                    self.scope
                )
        except Exception as e:
            print(f"⚠️ Streamlit secrets não disponível: {e}")
        
        # 2. RAILWAY/PRODUÇÃO: Tenta variável de ambiente
        credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
        if credentials_json:
            print("🟣 Usando credenciais da variável de ambiente...")
            try:
                credentials_dict = json.loads(credentials_json)
                return ServiceAccountCredentials.from_json_keyfile_dict(
                    credentials_dict,
                    self.scope
                )
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
        
        # 3. LOCAL: Tenta arquivo credentials.json
        if os.path.exists('credentials.json'):
            print("🟢 Usando credenciais do arquivo local...")
            return ServiceAccountCredentials.from_json_keyfile_name(
                'credentials.json',
                self.scope
            )
        
        print("❌ Nenhuma credencial encontrada!")
        return None
    
    def _get_sheet_url(self):
        """Obtém URL da planilha de diferentes fontes"""
        
        # 1. Streamlit secrets
        try:
            import streamlit as st
            if 'GOOGLE_SHEET_URL' in st.secrets:
                return st.secrets["GOOGLE_SHEET_URL"]
        except:
            pass
        
        # 2. Variável de ambiente
        sheet_url = os.getenv('GOOGLE_SHEET_URL')
        if sheet_url:
            return sheet_url
        
        return None
    
    def conectar_planilha(self, sheet_url=None):
        """Conecta a uma planilha específica"""
        url = sheet_url or self.sheet_url
        
        if not url:
            raise ValueError("URL da planilha não fornecida!")
        
        if not self.credentials:
            raise ValueError("Credenciais não configuradas!")

        try:
            print(f"📊 Conectando à planilha...")
            self.planilha = self.client.open_by_url(url)
            self.worksheet = self.planilha.sheet1  # Primeira aba
            print(f"✅ Conectado à planilha: {self.planilha.title}")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar à planilha: {e}")
            return False
    
    def ler_dados_planilha(self):
        """Lê todos os dados da planilha"""
        try:
            print("📖 Lendo dados da planilha...")
            
            # Pega todos os registros
            dados = self.worksheet.get_all_records()
            
            if not dados:
                print("⚠️ Planilha vazia!")
                return pd.DataFrame()
            
            df = pd.DataFrame(dados)
            print(f"✅ {len(df)} linhas lidas com sucesso!")
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao ler planilha: {e}")
            return pd.DataFrame()
    
    def sincronizar_para_banco(self, sheet_url=None, limpar_antes=False):
        """
        Sincroniza dados da planilha para o banco de dados
        """
        print("\n" + "="*60)
        print("🔄 SINCRONIZAÇÃO: Google Sheets → Banco de Dados")
        print("="*60 + "\n")
            try:
        
        # Conectar à planilha
        if not self.conectar_planilha(sheet_url):
            return False
        
        # Ler dados
        df = self.ler_dados_planilha()
        
        if df.empty:
            print("❌ Nenhum dado para sincronizar.")
            return False
        
        # Limpar banco se solicitado
        if limpar_antes:
            print("\n🧹 Limpando dados existentes...")
            self.db.limpar_dados()
        
        # Importar dados
        print(f"\n📥 Importando {len(df)} jogadores...")
        
        sucesso = 0
        erros = 0
        
        for idx, row in df.iterrows():
            try:
                # Extrai ID do Transfermarkt para usar como chave única
                tm_id = self._extrair_tm_id(row.get('TM', ''))

                # Preparar dados do jogador
                dados_jogador = {
                    'nome': str(row.get('Nome', '')).strip(),
                    'nacionalidade': str(row.get('Nacionalidade', '')).strip() or None,
                    'ano_nascimento': self._converter_int(row.get('Ano')),
                    'idade_atual': self._converter_int(row.get('Idade')),
                    'altura': self._converter_altura(row.get('Altura')),
                    'pe_dominante': str(row.get('Pé dominante', '')).strip() or None,
                    'transfermarkt_id': tm_id
                }
                
                # Inserir jogador (Agora usa o ID do TM para verificar duplicidade)
                id_jogador = self.db.inserir_jogador(dados_jogador)
                
                if id_jogador:
                    # Preparar dados do vínculo
                    dados_vinculo = {
                        'clube': str(row.get('Clube', '')).strip() or None,
                        'liga_clube': str(row.get('Liga do Clube', '')).strip() or None,
                        'posicao': str(row.get('Posição', '')).strip(),
                        'data_fim_contrato': self._converter_data(row.get('Fim de Contrato')),
                        'status_contrato': self._calcular_status_contrato(
                            row.get('Fim de Contrato')
                        )
                    }
                    
                    # Inserir vínculo
                    self.db.inserir_vinculo(id_jogador, dados_vinculo)
                    
                    sucesso += 1
                else:
                    erros += 1
                
                # Progresso
                if (idx + 1) % 50 == 0:
                    print(f"   Processados: {idx + 1}/{len(df)}")
                
            except Exception as e:
                print(f"⚠️ Erro na linha {idx + 1}: {e}")
                erros += 1
        
        print(f"\n✅ Importação concluída!")
        print(f"   Sucesso: {sucesso}")
        print(f"   Erros: {erros}")
        print("="*60)
        
        return True
            except Exception as e:
        print(f"❌ Erro geral na sincronização: {e}")
        return False
    
    def _converter_int(self, valor):
        """Converte valor para int, retorna None se inválido"""
        try:
            if pd.isna(valor) or valor == '':
                return None
            return int(float(valor))
        except:
            return None
    
    def _converter_altura(self, valor):
        """Converte altura para cm"""
        try:
            if pd.isna(valor) or valor == '':
                return None
            
            altura = float(valor)
            
            # Se está em metros (< 3), converte para cm
            if altura < 3:
                return int(altura * 100)
            
            return int(altura)
        except:
            return None
    
    def _extrair_tm_id(self, valor):
        """Extrai ID do Transfermarkt de URL ou retorna o próprio valor"""
        if pd.isna(valor) or valor == '':
            return None
        
        valor_str = str(valor).strip()
        
        # Se é uma URL do Transfermarkt
        # Padrão comum: .../nome-do-jogador/profil/spieler/123456
        match = re.search(r"spieler/(\d+)", valor_str)
        if match:
            return match.group(1)
        
        # Se é apenas dígitos, assume que é o ID
        if valor_str.isdigit():
            return valor_str
            
        return valor_str
    
    def _converter_data(self, valor):
        """Converte data para formato YYYY-MM-DD"""
        if pd.isna(valor) or valor == '':
            return None
        
        try:
            # Tenta vários formatos comuns
            formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
            
            for formato in formatos:
                try:
                    data = datetime.strptime(str(valor), formato)
                    return data.strftime('%Y-%m-%d')
                except:
                    continue
            
            return None
        except:
            return None
    
    def _calcular_status_contrato(self, data_fim):
        """Calcula status do contrato baseado na data de término"""
        if not data_fim:
            return 'Desconhecido'
        
        try:
            data_fim_dt = datetime.strptime(
                self._converter_data(data_fim) or '', 
                '%Y-%m-%d'
            )
            hoje = datetime.now()
            
            if data_fim_dt < hoje:
                return 'Vencido'
            
            dias_restantes = (data_fim_dt - hoje).days
            
            if dias_restantes <= 180:
                return 'Vencendo em breve'
            
            return 'Vigente'
            
        except:
            return 'Desconhecido'

def main():
    """Função principal para teste/execução manual"""
    print("🔄 Sincronizador Google Sheets\n")
    
    # Verificar se credenciais estão configuradas
    if not os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON') and not os.path.exists('credentials.json'):
        try:
            import streamlit as st
            if 'gcp_service_account' not in st.secrets:
                print("❌ Credenciais não encontradas!")
                return
        except:
            print("❌ Credenciais não encontradas!")
            return
    
    # Obter URL da planilha
    sheet_url = os.getenv('GOOGLE_SHEET_URL')
    
    if not sheet_url:
        try:
            import streamlit as st
            sheet_url = st.secrets.get("GOOGLE_SHEET_URL")
        except:
            pass
    
    if not sheet_url:
        print("⚠️ GOOGLE_SHEET_URL não definida no ambiente.")
        sheet_url = input("Digite a URL da planilha Google Sheets: ").strip()
    
    # Inicializar sincronizador
    sync = GoogleSheetsSync()
    
    # Menu
    print("\nOpções:")
    print("1 - Sincronizar (manter dados existentes)")
    print("2 - Sincronizar (limpar banco antes)")
    print("3 - Apenas ler planilha (sem importar)")
    
    opcao = input("\nEscolha uma opção: ").strip()
    
    if opcao == '1':
        sync.sincronizar_para_banco(sheet_url, limpar_antes=False)
    elif opcao == '2':
        confirma = input("⚠️ Isso vai limpar todos os dados! Confirma? (sim/não): ")
        if confirma.lower() in ['sim', 's']:
            sync.sincronizar_para_banco(sheet_url, limpar_antes=True)
    elif opcao == '3':
        sync.conectar_planilha(sheet_url)
        df = sync.ler_dados_planilha()
        print(f"\n📊 Preview dos dados:")
        print(df.head())
    else:
        print("❌ Opção inválida!")


if __name__ == "__main__":
    main()
