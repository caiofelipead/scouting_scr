"""
Google Sheets Sync - Compatível com Streamlit Cloud, Railway e Local
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
        
        self.db = ScoutingDatabase()
    
    def _get_credentials(self):
        """Obtém credenciais de diferentes fontes (prioridade)"""
        
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
        except:
            pass
        
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
                return None
        
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
        
        # 3. URL padrão (fallback)
        return "https://docs.google.com/spreadsheets/d/1jNAxJIRoZxYH1jKwPCBrd4Na1ko04EDAYaUCVGsJdIA"
    
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
            self.worksheet = self.planilha.sheet1
            print(f"✅ Conectado à planilha: {self.planilha.title}")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar à planilha: {e}")
            return False
    
    # ... resto dos métodos igual ao google_sheets_sync_railway.py
    
    def ler_dados_planilha(self):
        """Lê todos os dados da planilha"""
        try:
            print("📖 Lendo dados da planilha...")
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
    
    # Copie todos os outros métodos do google_sheets_sync_railway.py aqui
    # (_converter_int, _converter_altura, _extrair_tm_id, etc.)