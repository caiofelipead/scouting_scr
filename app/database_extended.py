"""
Extensão Database - Scout Pro
Adiciona funcionalidades financeiras mantendo compatibilidade com SQLite
"""

import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import os


class ScoutingDatabaseExtended:
    """Extensão do banco de dados SQLite com funcionalidades adicionais"""
    
    def __init__(self):
        # Usa o mesmo caminho do ScoutingDatabase principal
        if os.getenv("RAILWAY_VOLUME_MOUNT_PATH"):
            self.db_path = os.path.join(
                os.getenv("RAILWAY_VOLUME_MOUNT_PATH"), "scouting.db"
            )
        else:
            self.db_path = "scouting.db"
        
        self._criar_tabelas_estendidas()
    
    def get_connection(self):
        """Estabelece conexão com o banco SQLite"""
        return sqlite3.connect(self.db_path)
    
    def _criar_tabelas_estendidas(self):
        """Cria/atualiza estrutura do banco com funcionalidades financeiras"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Adiciona colunas financeiras à tabela jogadores existente
            colunas = [
                "ADD COLUMN salario_mensal_min REAL",
                "ADD COLUMN salario_mensal_max REAL",
                "ADD COLUMN moeda_salario TEXT DEFAULT 'BRL'",
                "ADD COLUMN bonificacoes TEXT",
                "ADD COLUMN custo_transferencia REAL",
                "ADD COLUMN condicoes_negocio TEXT",
                "ADD COLUMN clausula_rescisoria REAL",
                "ADD COLUMN percentual_direitos INTEGER DEFAULT 100",
                "ADD COLUMN observacoes_financeiras TEXT",
                "ADD COLUMN agente_nome TEXT",
                "ADD COLUMN agente_empresa TEXT",
                "ADD COLUMN agente_telefone TEXT",
                "ADD COLUMN agente_email TEXT",
                "ADD COLUMN agente_comissao REAL",
                "ADD COLUMN url_agente TEXT",
                "ADD COLUMN agente_atualizado_em TIMESTAMP",
                "ADD COLUMN financeiro_atualizado_em TIMESTAMP"
            ]
            
            for coluna in colunas:
                try:
                    cursor.execute(f"ALTER TABLE jogadores {coluna}")
                except sqlite3.OperationalError:
                    # Coluna já existe
                    pass
            
            # TABELA DE PROPOSTAS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS propostas (
                    id_proposta INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_jogador INTEGER,
                    clube_interessado TEXT,
                    valor_proposta REAL,
                    moeda TEXT DEFAULT 'BRL',
                    status TEXT CHECK (status IN ('Em análise', 'Aceita', 'Recusada')),
                    data_proposta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observacoes TEXT,
                    responsavel TEXT,
                    FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador)
                )
            """)
            
            # TABELA DE LOG DE AUDITORIA
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_auditoria (
                    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    acao TEXT,
                    tabela TEXT,
                    registro_id INTEGER,
                    dados_anteriores TEXT,
                    dados_novos TEXT,
                    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Erro ao criar tabelas: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def atualizar_financeiro(self, id_jogador, dados_financeiros, usuario_id):
        """Atualiza informações financeiras de um jogador"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE jogadores SET
                    salario_mensal_min = ?,
                    salario_mensal_max = ?,
                    moeda_salario = ?,
                    bonificacoes = ?,
                    custo_transferencia = ?,
                    condicoes_negocio = ?,
                    clausula_rescisoria = ?,
                    percentual_direitos = ?,
                    observacoes_financeiras = ?,
                    financeiro_atualizado_em = CURRENT_TIMESTAMP
                WHERE id_jogador = ?
            """, (
                dados_financeiros.get('salario_min'),
                dados_financeiros.get('salario_max'),
                dados_financeiros.get('moeda', 'BRL'),
                dados_financeiros.get('bonificacoes'),
                dados_financeiros.get('custo_transferencia'),
                dados_financeiros.get('condicoes'),
                dados_financeiros.get('clausula'),
                dados_financeiros.get('percentual_direitos'),
                dados_financeiros.get('observacoes'),
                id_jogador
            ))
            
            # Registra log
            cursor.execute("""
                INSERT INTO log_auditoria (usuario_id, acao, tabela, registro_id)
                VALUES (?, 'atualizar_financeiro', 'jogadores', ?)
            """, (usuario_id, id_jogador))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar financeiro: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def buscar_por_faixa_salarial(self, salario_min=None, salario_max=None, moeda='BRL'):
        """Busca jogadores por faixa salarial"""
        conn = self.get_connection()
        
        try:
            query = """
                SELECT 
                    j.*,
                    v.clube,
                    v.liga_clube as liga,
                    v.posicao,
                    a.nota_potencial as potencial,
                    a.nota_tatico as tatico,
                    a.nota_tecnico as tecnico,
                    a.nota_fisico as fisico,
                    a.nota_mental as mental
                FROM jogadores j
                LEFT JOIN vinculos v ON j.id_jogador = v.id_jogador
                LEFT JOIN (
                    SELECT 
                        id_jogador,
                        nota_potencial,
                        nota_tatico,
                        nota_tecnico,
                        nota_fisico,
                        nota_mental,
                        ROW_NUMBER() OVER (PARTITION BY id_jogador ORDER BY data_avaliacao DESC) as rn
                    FROM avaliacoes
                ) a ON j.id_jogador = a.id_jogador AND a.rn = 1
                WHERE j.moeda_salario = ?
            """
            params = [moeda]
            
            if salario_min is not None:
                query += " AND j.salario_mensal_max >= ?"
                params.append(salario_min)
            
            if salario_max is not None:
                query += " AND j.salario_mensal_min <= ?"
                params.append(salario_max)
            
            query += " ORDER BY j.salario_mensal_max DESC"
            
            df = pd.read_sql_query(query, conn, params=params)
            return df
            
        finally:
            conn.close()
    
    def obter_dados_financeiros(self, id_jogador):
        """Obtém dados financeiros completos de um jogador"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    salario_mensal_min,
                    salario_mensal_max,
                    moeda_salario,
                    bonificacoes,
                    custo_transferencia,
                    condicoes_negocio,
                    clausula_rescisoria,
                    percentual_direitos,
                    observacoes_financeiras,
                    financeiro_atualizado_em,
                    agente_nome,
                    agente_empresa,
                    agente_telefone,
                    agente_email,
                    agente_comissao
                FROM jogadores
                WHERE id_jogador = ?
            """, (id_jogador,))
            
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    'salario_min': resultado[0],
                    'salario_max': resultado[1],
                    'moeda': resultado[2],
                    'bonificacoes': resultado[3],
                    'custo_transferencia': resultado[4],
                    'condicoes': resultado[5],
                    'clausula': resultado[6],
                    'percentual_direitos': resultado[7],
                    'observacoes': resultado[8],
                    'atualizado_em': resultado[9],
                    'agente_nome': resultado[10],
                    'agente_empresa': resultado[11],
                    'agente_telefone': resultado[12],
                    'agente_email': resultado[13],
                    'agente_comissao': resultado[14]
                }
            return None
            
        finally:
            cursor.close()
            conn.close()
    
    def exportar_backup(self, tabela):
        """Exporta tabela para backup em CSV"""
        conn = self.get_connection()
        
        try:
            df = pd.read_sql(f"SELECT * FROM {tabela}", conn)
            return df
        finally:
            conn.close()
    
    def estatisticas_jogadores(self):
        """Retorna estatísticas gerais dos jogadores"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN salario_mensal_min IS NOT NULL THEN 1 END) as com_info_financeira,
                    COUNT(CASE WHEN agente_nome IS NOT NULL THEN 1 END) as com_agente,
                    COUNT(DISTINCT v.liga_clube) as ligas_diferentes,
                    COUNT(DISTINCT v.clube) as clubes_diferentes,
                    COUNT(DISTINCT v.posicao) as posicoes_diferentes,
                    ROUND(AVG(CASE WHEN idade_atual IS NOT NULL THEN idade_atual END), 1) as idade_media,
                    COUNT(CASE WHEN v.data_fim_contrato < date('now') THEN 1 END) as contratos_vencidos
                FROM jogadores j
                LEFT JOIN vinculos v ON j.id_jogador = v.id_jogador
            """)
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'total': int(row[0]),
                    'com_info_financeira': int(row[1]),
                    'com_agente': int(row[2]),
                    'ligas_diferentes': int(row[3]),
                    'clubes_diferentes': int(row[4]),
                    'posicoes_diferentes': int(row[5]),
                    'idade_media': float(row[6]) if row[6] else 0.0,
                    'contratos_vencidos': int(row[7])
                }
            else:
                return self._estatisticas_vazias()
                
        except Exception as e:
            print(f"Erro ao buscar estatísticas de jogadores: {e}")
            return self._estatisticas_vazias()
        finally:
            cursor.close()
            conn.close()
    
    def estatisticas_financeiras(self):
        """Retorna estatísticas gerais das propostas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_propostas,
                    COALESCE(SUM(CASE WHEN status = 'Aceita' THEN 1 ELSE 0 END), 0) as aceitas,
                    COALESCE(SUM(CASE WHEN status = 'Recusada' THEN 1 ELSE 0 END), 0) as recusadas,
                    COALESCE(SUM(CASE WHEN status = 'Em análise' THEN 1 ELSE 0 END), 0) as em_analise,
                    COALESCE(SUM(valor_proposta), 0) as valor_total,
                    COALESCE(AVG(valor_proposta), 0) as valor_medio,
                    COALESCE(MAX(valor_proposta), 0) as maior_proposta,
                    COALESCE(MIN(valor_proposta), 0) as menor_proposta
                FROM propostas
            """)
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'total_propostas': int(row[0]),
                    'aceitas': int(row[1]),
                    'recusadas': int(row[2]),
                    'em_analise': int(row[3]),
                    'valor_total': float(row[4]),
                    'valor_medio': float(row[5]),
                    'maior_proposta': float(row[6]),
                    'menor_proposta': float(row[7])
                }
            else:
                return self._propostas_vazias()
                
        except Exception as e:
            print(f"Erro ao buscar estatísticas: {e}")
            return self._propostas_vazias()
        finally:
            cursor.close()
            conn.close()
    
    def _estatisticas_vazias(self):
        """Retorna estatísticas zeradas"""
        return {
            'total': 0,
            'com_info_financeira': 0,
            'com_agente': 0,
            'ligas_diferentes': 0,
            'clubes_diferentes': 0,
            'posicoes_diferentes': 0,
            'idade_media': 0.0,
            'contratos_vencidos': 0
        }
    
    def _propostas_vazias(self):
        """Retorna propostas zeradas"""
        return {
            'total_propostas': 0,
            'aceitas': 0,
            'recusadas': 0,
            'em_analise': 0,
            'valor_total': 0.0,
            'valor_medio': 0.0,
            'maior_proposta': 0.0,
            'menor_proposta': 0.0
        }


# FUNÇÕES AUXILIARES

def criar_backup_automatico(db_extended):
    """Cria backup de todas as tabelas importantes"""
    import os
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    tabelas = ['jogadores', 'avaliacoes', 'alertas', 'vinculos', 'propostas']
    
    for tabela in tabelas:
        try:
            df = db_extended.exportar_backup(tabela)
            df.to_csv(f"{backup_dir}/{tabela}.csv", index=False)
            print(f"✅ Backup de {tabela}: {len(df)} registros")
        except Exception as e:
            print(f"❌ Erro em {tabela}: {e}")
    
    return backup_dir
