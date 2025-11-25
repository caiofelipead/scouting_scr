"""
Scraping Transfermarkt - Scout Pro
Busca informações de agentes dos jogadores
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from typing import Optional, Dict
import psycopg2
import os


class TransfermarktScraper:
    """Scraper para buscar dados do Transfermarkt"""
    
    def __init__(self):
        self.base_url = "https://www.transfermarkt.com.br"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.database_url = os.getenv('DATABASE_URL')
    
    def get_connection(self):
        """Estabelece conexão com o banco PostgreSQL"""
        return psycopg2.connect(self.database_url)
    
    def buscar_agente(self, transfermarkt_id: int) -> Optional[Dict]:
        """
        Busca informações do agente do jogador no Transfermarkt
        
        Args:
            transfermarkt_id: ID do jogador no Transfermarkt
        
        Returns:
            Dict com informações do agente ou None
        """
        try:
            # URL do perfil do jogador
            url = f"{self.base_url}/profil/spieler/{transfermarkt_id}"
            
            # Faz a requisição
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse do HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Busca informações do agente
            agente_info = {
                'agente_nome': None,
                'agente_empresa': None,
                'url_agente': None
            }
            
            # Procura pela seção de informações do jogador
            info_table = soup.find('table', {'class': 'auflistung'})
            
            if info_table:
                rows = info_table.find_all('tr')
                
                for row in rows:
                    header = row.find('th')
                    if header and 'Empresário:' in header.get_text():
                        data = row.find('td')
                        if data:
                            # Busca o nome do agente
                            agente_link = data.find('a')
                            if agente_link:
                                agente_info['agente_nome'] = agente_link.get_text(strip=True)
                                agente_info['url_agente'] = self.base_url + agente_link.get('href', '')
                            
                            # Busca a empresa/agência
                            empresa_span = data.find('span', {'class': 'hide-for-small'})
                            if empresa_span:
                                agente_info['agente_empresa'] = empresa_span.get_text(strip=True)
            
            # Busca também na área de detalhes do perfil
            if not agente_info['agente_nome']:
                # Alternativa: busca em outras estruturas HTML
                info_elements = soup.find_all('span', {'class': 'info-table__content'})
                for i, elem in enumerate(info_elements):
                    if 'Empresário' in elem.get_text():
                        # Próximo elemento pode conter o nome
                        if i + 1 < len(info_elements):
                            agente_info['agente_nome'] = info_elements[i + 1].get_text(strip=True)
            
            # Se encontrou informações, retorna
            if agente_info['agente_nome']:
                return agente_info
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados do Transfermarkt ID {transfermarkt_id}: {e}")
            return None
        except Exception as e:
            print(f"Erro ao processar dados: {e}")
            return None
    
    def atualizar_agente_banco(self, jogador_id: int, agente_info: Dict) -> bool:
        """
        Atualiza informações do agente no banco de dados
        
        Args:
            jogador_id: ID do jogador no banco
            agente_info: Dicionário com informações do agente
        
        Returns:
            True se atualizado com sucesso
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE jogadores 
                SET agente_nome = %s,
                    agente_empresa = %s,
                    url_agente = %s,
                    agente_atualizado_em = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                agente_info['agente_nome'],
                agente_info['agente_empresa'],
                agente_info['url_agente'],
                jogador_id
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar banco: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def atualizar_todos_agentes(self, limite: Optional[int] = None):
        """
        Atualiza informações de agentes para todos os jogadores
        
        Args:
            limite: Número máximo de jogadores a atualizar (None = todos)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Busca jogadores que têm Transfermarkt ID mas não têm agente
            query = """
                SELECT id, nome, transfermarkt_id 
                FROM jogadores 
                WHERE transfermarkt_id IS NOT NULL 
                AND (agente_nome IS NULL OR agente_nome = '')
                ORDER BY id
            """
            
            if limite:
                query += f" LIMIT {limite}"
            
            cursor.execute(query)
            jogadores = cursor.fetchall()
            
            print(f"\n🔍 Iniciando scraping de {len(jogadores)} jogadores...")
            
            sucessos = 0
            erros = 0
            
            for idx, (jogador_id, nome, transfermarkt_id) in enumerate(jogadores, 1):
                print(f"\n[{idx}/{len(jogadores)}] Buscando agente de {nome}...")
                
                # Busca informações do agente
                agente_info = self.buscar_agente(transfermarkt_id)
                
                if agente_info and agente_info['agente_nome']:
                    # Atualiza no banco
                    if self.atualizar_agente_banco(jogador_id, agente_info):
                        print(f"✅ Agente encontrado: {agente_info['agente_nome']}")
                        if agente_info['agente_empresa']:
                            print(f"   Empresa: {agente_info['agente_empresa']}")
                        sucessos += 1
                    else:
                        print(f"❌ Erro ao salvar no banco")
                        erros += 1
                else:
                    print(f"⚠️ Agente não encontrado")
                    erros += 1
                
                # Delay para não sobrecarregar o servidor
                time.sleep(random.uniform(2, 4))
            
            print(f"\n" + "="*50)
            print(f"✅ Concluído!")
            print(f"Sucessos: {sucessos}")
            print(f"Sem informação: {erros}")
            print("="*50)
            
        except Exception as e:
            print(f"Erro durante atualização em massa: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def buscar_agente_especifico(self, nome_jogador: str) -> Optional[Dict]:
        """
        Busca informações do agente de um jogador específico
        
        Args:
            nome_jogador: Nome do jogador
        
        Returns:
            Dict com informações do agente
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, nome, transfermarkt_id, agente_nome
                FROM jogadores 
                WHERE LOWER(nome) LIKE LOWER(%s)
                LIMIT 1
            """, (f"%{nome_jogador}%",))
            
            resultado = cursor.fetchone()
            
            if not resultado:
                print(f"❌ Jogador '{nome_jogador}' não encontrado")
                return None
            
            jogador_id, nome, transfermarkt_id, agente_atual = resultado
            
            if not transfermarkt_id:
                print(f"❌ Jogador '{nome}' não possui Transfermarkt ID")
                return None
            
            print(f"\n🔍 Buscando agente de {nome}...")
            
            agente_info = self.buscar_agente(transfermarkt_id)
            
            if agente_info and agente_info['agente_nome']:
                self.atualizar_agente_banco(jogador_id, agente_info)
                print(f"✅ Agente: {agente_info['agente_nome']}")
                if agente_info['agente_empresa']:
                    print(f"   Empresa: {agente_info['agente_empresa']}")
                return agente_info
            else:
                print(f"⚠️ Agente não encontrado para {nome}")
                return None
                
        except Exception as e:
            print(f"Erro: {e}")
            return None
        finally:
            cursor.close()
            conn.close()


def criar_colunas_agente():
    """Adiciona colunas de agente na tabela jogadores se não existirem"""
    
    database_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        # Adiciona colunas se não existirem
        cursor.execute("""
            ALTER TABLE jogadores 
            ADD COLUMN IF NOT EXISTS agente_nome VARCHAR(100),
            ADD COLUMN IF NOT EXISTS agente_empresa VARCHAR(150),
            ADD COLUMN IF NOT EXISTS url_agente TEXT,
            ADD COLUMN IF NOT EXISTS agente_atualizado_em TIMESTAMP
        """)
        
        conn.commit()
        print("✅ Colunas de agente criadas/verificadas com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao criar colunas: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    """Script de linha de comando"""
    
    import sys
    
    # Cria colunas se necessário
    criar_colunas_agente()
    
    scraper = TransfermarktScraper()
    
    if len(sys.argv) > 1:
        # Busca jogador específico
        nome = " ".join(sys.argv[1:])
        scraper.buscar_agente_especifico(nome)
    else:
        # Menu interativo
        print("\n🔍 Scraping de Agentes - Transfermarkt")
        print("="*50)
        print("1. Atualizar todos os jogadores")
        print("2. Atualizar primeiros N jogadores")
        print("3. Buscar jogador específico")
        print("="*50)
        
        opcao = input("\nEscolha uma opção (1-3): ")
        
        if opcao == "1":
            confirma = input("⚠️ Isso pode levar muito tempo. Confirma? (s/n): ")
            if confirma.lower() == 's':
                scraper.atualizar_todos_agentes()
        
        elif opcao == "2":
            limite = int(input("Quantos jogadores? "))
            scraper.atualizar_todos_agentes(limite=limite)
        
        elif opcao == "3":
            nome = input("Nome do jogador: ")
            scraper.buscar_agente_especifico(nome)
