"""
Extensão Database - Scout Pro
Adiciona funcionalidades financeiras e sincronização segura
IMPORTANTE: Mesclar este código no seu database.py existente
"""

import psycopg2
import pandas as pd
import streamlit as st
from datetime import datetime
import os


class ScoutingDatabaseExtended:
    """Extensão do banco de dados com funcionalidades adicionais"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self._criar_tabelas_estendidas()
    
    def get_connection(self):
        """Estabelece conexão com o banco PostgreSQL"""
        return psycopg2.connect(self.database_url)
    
    def _criar_tabelas_estendidas(self):
        """Cria/atualiza estrutura do banco com todas as funcionalidades"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Adiciona colunas financeiras e de agente
            colunas = [
                "ADD COLUMN IF NOT EXISTS salario_mensal_min DECIMAL(12,2)",
                "ADD COLUMN IF NOT EXISTS salario_mensal_max DECIMAL(12,2)",
                "ADD COLUMN IF NOT EXISTS moeda_salario VARCHAR(10) DEFAULT 'BRL'",
                "ADD COLUMN IF NOT EXISTS bonificacoes TEXT",
                "ADD COLUMN IF NOT EXISTS custo_transferencia DECIMAL(12,2)",
                "ADD COLUMN IF NOT EXISTS condicoes_negocio TEXT",
                "ADD COLUMN IF NOT EXISTS clausula_rescisoria DECIMAL(12,2)",
                "ADD COLUMN IF NOT EXISTS percentual_direitos INTEGER",
                "ADD COLUMN IF NOT EXISTS observacoes_financeiras TEXT",
                "ADD COLUMN IF NOT EXISTS agente_nome VARCHAR(100)",
                "ADD COLUMN IF NOT EXISTS agente_empresa VARCHAR(150)",
                "ADD COLUMN IF NOT EXISTS agente_telefone VARCHAR(20)",
                "ADD COLUMN IF NOT EXISTS agente_email VARCHAR(100)",
                "ADD COLUMN IF NOT EXISTS agente_comissao DECIMAL(5,2)",
                "ADD COLUMN IF NOT EXISTS url_agente TEXT",
                "ADD COLUMN IF NOT EXISTS agente_atualizado_em TIMESTAMP",
                "ADD COLUMN IF NOT EXISTS financeiro_atualizado_em TIMESTAMP"
            ]
            
            for coluna in colunas:
                try:
                    cursor.execute(f"ALTER TABLE jogadores {coluna}")
                except:
                    pass
            
            # TABELA DE AVALIAÇÕES
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS avaliacoes (
                    id SERIAL PRIMARY KEY,
                    jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                    usuario_id INTEGER,
                    potencial INTEGER CHECK (potencial BETWEEN 1 AND 5),
                    tatico INTEGER CHECK (tatico BETWEEN 1 AND 5),
                    tecnico INTEGER CHECK (tecnico BETWEEN 1 AND 5),
                    fisico INTEGER CHECK (fisico BETWEEN 1 AND 5),
                    mental INTEGER CHECK (mental BETWEEN 1 AND 5),
                    observacoes TEXT,
                    data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # TABELA DE TAGS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags_jogadores (
                    id SERIAL PRIMARY KEY,
                    jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                    tag VARCHAR(50),
                    adicionada_por INTEGER,
                    adicionada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(jogador_id, tag)
                )
            """)
            
            # TABELA DE WISHLIST
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wishlist (
                    id SERIAL PRIMARY KEY,
                    jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                    prioridade VARCHAR(20),
                    motivo TEXT,
                    adicionado_por INTEGER,
                    adicionado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(jogador_id)
                )
            """)
            
            # TABELA DE LOG DE AUDITORIA
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_auditoria (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER,
                    acao VARCHAR(100),
                    tabela VARCHAR(50),
                    registro_id INTEGER,
                    dados_anteriores JSONB,
                    dados_novos JSONB,
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
    
    def importar_dados_planilha_seguro(self, df):
        """
        Importa dados do Google Sheets SEM perder dados locais
        Faz MERGE ao invés de DELETE + INSERT
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            atualizados = 0
            inseridos = 0
            
            for _, row in df.iterrows():
                # Verifica se o jogador já existe
                cursor.execute("SELECT id FROM jogadores WHERE id = %s", (row['id'],))
                existe = cursor.fetchone()
                
                if existe:
                    # ATUALIZA apenas campos vindos do Sheets
                    # PRESERVA informações financeiras, agente e avaliações
                    cursor.execute("""
                        UPDATE jogadores SET
                            nome = %s,
                            posicao = %s,
                            idade = %s,
                            clube = %s,
                            liga = %s,
                            nacionalidade = %s,
                            valor_mercado = %s,
                            contrato_ate = %s,
                            transfermarkt_id = %s,
                            atualizado_em = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (
                        row['nome'], row['posicao'], row.get('idade'),
                        row['clube'], row['liga'], row['nacionalidade'],
                        row.get('valor_mercado'), row.get('contrato_ate'),
                        row.get('transfermarkt_id'), row['id']
                    ))
                    atualizados += 1
                else:
                    # INSERE novo jogador
                    cursor.execute("""
                        INSERT INTO jogadores (
                            id, nome, posicao, idade, clube, liga,
                            nacionalidade, valor_mercado, contrato_ate,
                            transfermarkt_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row['id'], row['nome'], row['posicao'], row.get('idade'),
                        row['clube'], row['liga'], row['nacionalidade'],
                        row.get('valor_mercado'), row.get('contrato_ate'),
                        row.get('transfermarkt_id')
                    ))
                    inseridos += 1
            
            conn.commit()
            return True, f"✅ {atualizados} atualizados, {inseridos} inseridos"
            
        except Exception as e:
            conn.rollback()
            return False, f"❌ Erro: {str(e)}"
        finally:
            cursor.close()
            conn.close()
    
    def atualizar_financeiro(self, jogador_id, dados_financeiros, usuario_id):
        """Atualiza informações financeiras de um jogador"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE jogadores SET
                    salario_mensal_min = %s,
                    salario_mensal_max = %s,
                    moeda_salario = %s,
                    bonificacoes = %s,
                    custo_transferencia = %s,
                    condicoes_negocio = %s,
                    clausula_rescisoria = %s,
                    percentual_direitos = %s,
                    observacoes_financeiras = %s,
                    financeiro_atualizado_em = CURRENT_TIMESTAMP
                WHERE id = %s
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
                jogador_id
            ))
            
            # Registra log
            cursor.execute("""
                INSERT INTO log_auditoria (usuario_id, acao, tabela, registro_id)
                VALUES (%s, 'atualizar_financeiro', 'jogadores', %s)
            """, (usuario_id, jogador_id))
            
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
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT j.*, 
                       a.potencial, a.tatico, a.tecnico, a.fisico, a.mental
                FROM jogadores j
                LEFT JOIN LATERAL (
                    SELECT potencial, tatico, tecnico, fisico, mental
                    FROM avaliacoes
                    WHERE jogador_id = j.id
                    ORDER BY data_avaliacao DESC
                    LIMIT 1
                ) a ON true
                WHERE moeda_salario = %s
            """
            params = [moeda]
            
            if salario_min is not None:
                query += " AND salario_mensal_max >= %s"
                params.append(salario_min)
            
            if salario_max is not None:
                query += " AND salario_mensal_min <= %s"
                params.append(salario_max)
            
            query += " ORDER BY salario_mensal_max DESC"
            
            cursor.execute(query, params)
            colunas = [desc[0] for desc in cursor.description]
            resultados = cursor.fetchall()
            
            df = pd.DataFrame(resultados, columns=colunas)
            return df
            
        finally:
            cursor.close()
            conn.close()
    
    def obter_dados_financeiros(self, jogador_id):
        """Obtém dados financeiros completos de um jogador"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT salario_mensal_min, salario_mensal_max, moeda_salario,
                       bonificacoes, custo_transferencia, condicoes_negocio,
                       clausula_rescisoria, percentual_direitos, 
                       observacoes_financeiras, financeiro_atualizado_em,
                       agente_nome, agente_empresa, agente_telefone,
                       agente_email, agente_comissao
                FROM jogadores
                WHERE id = %s
            """, (jogador_id,))
            
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
    
    def estatisticas_financeiras(self):
    """Retorna estatísticas gerais das propostas"""
    try:
        with self.engine.connect() as conn:
            result = conn.execute(text("""
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
            """))
            
            row = result.fetchone()
            
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
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {e}")
        # Retorna valores zerados em caso de erro
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
    
    tabelas = ['jogadores', 'avaliacoes', 'tags_jogadores', 'wishlist']
    
    for tabela in tabelas:
        try:
            df = db_extended.exportar_backup(tabela)
            df.to_csv(f"{backup_dir}/{tabela}.csv", index=False)
            print(f"✅ Backup de {tabela}: {len(df)} registros")
        except Exception as e:
            print(f"❌ Erro em {tabela}: {e}")
    
    return backup_dir
