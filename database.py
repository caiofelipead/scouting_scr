"""
Sistema de Banco de Dados para Scouting
Gerencia conexões e operações com SQLite
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

class ScoutingDatabase:
    def __init__(self, db_path='scouting.db'):
        """Inicializa conexão com banco de dados"""
        self.db_path = db_path
        self.criar_tabelas()
    
    def connect(self):
        """Cria conexão com o banco"""
        return sqlite3.connect(self.db_path)
    
    def verificar_e_criar_colunas(self):
        """Verifica e adiciona colunas faltantes em tabelas existentes"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Verificar se a coluna 'ativo' existe na tabela alertas
            cursor.execute("PRAGMA table_info(alertas)")
            colunas = [col[1] for col in cursor.fetchall()]
            
            if 'ativo' not in colunas:
                cursor.execute("ALTER TABLE alertas ADD COLUMN ativo BOOLEAN DEFAULT 1")
                conn.commit()
        except sqlite3.OperationalError:
            # Tabela não existe, será criada
            pass

        try:
            cursor.execute("PRAGMA table_info(avaliacoes)")
            colunas_aval = [col[1] for col in cursor.fetchall()]
    
            if 'nota_potencial' not in colunas_aval:
                cursor.execute("ALTER TABLE avaliacoes ADD COLUMN nota_potencial REAL CHECK(nota_potencial >= 1 AND nota_potencial <= 5)")
                conn.commit()
        except sqlite3.OperationalError:
            pass
        
        conn.close()
    
    def criar_tabelas(self):
        """Cria todas as tabelas necessárias"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Tabela de jogadores
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jogadores (
            id_jogador INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            nacionalidade TEXT,
            ano_nascimento INTEGER,
            idade_atual INTEGER,
            altura INTEGER,
            pe_dominante TEXT,
            transfermarkt_id TEXT
        )
        """)
        
        # Tabela de vínculos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vinculos (
            id_vinculo INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER,
            clube TEXT,
            liga_clube TEXT,
            posicao TEXT,
            data_fim_contrato DATE,
            status_contrato TEXT,
            FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador)
        )
        """)
        
        # Tabela de alertas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas (
            id_alerta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER,
            tipo_alerta TEXT,
            descricao TEXT,
            prioridade TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo BOOLEAN DEFAULT 1,
            FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador)
        )
        """)
        
        # Tabela de avaliações
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id_avaliacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER NOT NULL,
            data_avaliacao DATE NOT NULL,
            nota_potencial REAL CHECK(nota_potencial >= 1 AND nota_potencial <= 5),
            nota_tatico REAL CHECK(nota_tatico >= 1 AND nota_tatico <= 5),
            nota_tecnico REAL CHECK(nota_tecnico >= 1 AND nota_tecnico <= 5),
            nota_fisico REAL CHECK(nota_fisico >= 1 AND nota_fisico <= 5),
            nota_mental REAL CHECK(nota_mental >= 1 AND nota_mental <= 5),
            observacoes TEXT,
            avaliador TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador)
        )
        """)
        
        conn.commit()
        conn.close()
        
        # Verificar e adicionar colunas faltantes em tabelas existentes
        self.verificar_e_criar_colunas()
    
    def criar_tabela_avaliacoes(self):
        """Cria tabela de avaliações se não existir (método adicional para compatibilidade)"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id_avaliacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER NOT NULL,
            data_avaliacao DATE NOT NULL,
            nota_potencial REAL CHECK(nota_potencial >= 1 AND nota_potencial <= 5),
            nota_tatico REAL CHECK(nota_tatico >= 1 AND nota_tatico <= 5),
            nota_tecnico REAL CHECK(nota_tecnico >= 1 AND nota_tecnico <= 5),
            nota_fisico REAL CHECK(nota_fisico >= 1 AND nota_fisico <= 5),
            nota_mental REAL CHECK(nota_mental >= 1 AND nota_mental <= 5),
            observacoes TEXT,
            avaliador TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador)
        )
        """)
        
        conn.commit()
        conn.close()
    
    def salvar_avaliacao(self, id_jogador, data_avaliacao, nota_potencial, nota_tatico, nota_tecnico, 
                     nota_fisico, nota_mental, observacoes="", avaliador=""):
        """Salva uma nova avaliação"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO avaliacoes 
        (id_jogador, data_avaliacao, nota_potencial, nota_tatico, nota_tecnico, nota_fisico, nota_mental, observacoes, avaliador)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_jogador, data_avaliacao, nota_potencial, nota_tatico, nota_tecnico, nota_fisico, nota_mental, observacoes, avaliador))
        
        conn.commit()
        conn.close()
    
    def get_avaliacoes_jogador(self, id_jogador):
        """Retorna todas as avaliações de um jogador"""
        conn = self.connect()
        try:
            df = pd.read_sql_query("""
            SELECT * FROM avaliacoes 
            WHERE id_jogador = ?
            ORDER BY data_avaliacao DESC
            """, conn, params=(id_jogador,))
        except:
            df = pd.DataFrame()
        conn.close()
        return df
    
    def get_ultima_avaliacao(self, id_jogador):
        """Retorna a última avaliação de um jogador"""
        conn = self.connect()
        try:
            df = pd.read_sql_query("""
            SELECT * FROM avaliacoes 
            WHERE id_jogador = ?
            ORDER BY data_avaliacao DESC
            LIMIT 1
            """, conn, params=(id_jogador,))
        except:
            df = pd.DataFrame()
        conn.close()
        return df
    
    def deletar_avaliacao(self, id_avaliacao):
        """Deleta uma avaliação específica"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM avaliacoes WHERE id_avaliacao = ?", (id_avaliacao,))
        conn.commit()
        conn.close()
    
    def limpar_dados(self):
        """Remove todos os dados das tabelas"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM alertas")
        except:
            pass
        
        try:
            cursor.execute("DELETE FROM vinculos")
        except:
            pass
        
        try:
            cursor.execute("DELETE FROM jogadores")
        except:
            pass
        
        try:
            cursor.execute("DELETE FROM avaliacoes")
        except:
            pass
        
        conn.commit()
        conn.close()
    
    def inserir_jogador(self, id_jogador, nome, nacionalidade, ano_nascimento, 
                       idade_atual, altura, pe_dominante, transfermarkt_id=None):
        """Insere ou atualiza um jogador"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT OR REPLACE INTO jogadores 
        (id_jogador, nome, nacionalidade, ano_nascimento, idade_atual, altura, pe_dominante, transfermarkt_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_jogador, nome, nacionalidade, ano_nascimento, idade_atual, altura, pe_dominante, transfermarkt_id))
        
        conn.commit()
        conn.close()
    
    def inserir_vinculo(self, id_jogador, clube, liga_clube, posicao, 
                       data_fim_contrato, status_contrato):
        """Insere vínculo de um jogador"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Primeiro remove vínculos antigos do jogador
        cursor.execute("DELETE FROM vinculos WHERE id_jogador = ?", (id_jogador,))
        
        # Insere novo vínculo
        cursor.execute("""
        INSERT INTO vinculos 
        (id_jogador, clube, liga_clube, posicao, data_fim_contrato, status_contrato)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (id_jogador, clube, liga_clube, posicao, data_fim_contrato, status_contrato))
        
        conn.commit()
        conn.close()
    
    def get_jogadores_com_vinculos(self):
        """Retorna todos os jogadores com seus vínculos"""
        conn = self.connect()
        
        query = """
        SELECT 
            j.id_jogador,
            j.nome,
            j.nacionalidade,
            j.idade_atual,
            j.altura,
            j.pe_dominante,
            v.clube,
            v.liga_clube,
            v.posicao,
            v.data_fim_contrato,
            v.status_contrato
        FROM jogadores j
        LEFT JOIN vinculos v ON j.id_jogador = v.id_jogador
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_estatisticas_gerais(self):
        """Retorna estatísticas gerais do banco de dados"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Total de jogadores
        try:
            cursor.execute("SELECT COUNT(*) FROM jogadores")
            total_jogadores = cursor.fetchone()[0]
        except:
            total_jogadores = 0
        
        # Vínculos ativos
        try:
            cursor.execute("SELECT COUNT(*) FROM vinculos WHERE status_contrato = 'ativo'")
            total_vinculos_ativos = cursor.fetchone()[0]
        except:
            total_vinculos_ativos = 0
        
        # Contratos vencendo em 12 meses
        try:
            cursor.execute("""
            SELECT COUNT(*) FROM vinculos 
            WHERE status_contrato IN ('ultimo_ano', 'ultimos_6_meses')
            """)
            contratos_vencendo = cursor.fetchone()[0]
        except:
            contratos_vencendo = 0
        
        # Alertas ativos
        try:
            cursor.execute("SELECT COUNT(*) FROM alertas WHERE ativo = 1")
            alertas_ativos = cursor.fetchone()[0]
        except:
            # Se a coluna ativo não existir, tenta sem ela
            try:
                cursor.execute("SELECT COUNT(*) FROM alertas")
                alertas_ativos = cursor.fetchone()[0]
            except:
                alertas_ativos = 0
        
        conn.close()
        
        return {
            'total_jogadores': total_jogadores,
            'total_vinculos_ativos': total_vinculos_ativos,
            'contratos_vencendo': contratos_vencendo,
            'alertas_ativos': alertas_ativos
        }
    
    def criar_alerta(self, id_jogador, tipo_alerta, descricao, prioridade='media'):
        """Cria um novo alerta"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO alertas (id_jogador, tipo_alerta, descricao, prioridade, ativo)
            VALUES (?, ?, ?, ?, 1)
            """, (id_jogador, tipo_alerta, descricao, prioridade))
        except:
            # Se a coluna ativo não existir, insere sem ela
            cursor.execute("""
            INSERT INTO alertas (id_jogador, tipo_alerta, descricao, prioridade)
            VALUES (?, ?, ?, ?)
            """, (id_jogador, tipo_alerta, descricao, prioridade))
        
        conn.commit()
        conn.close()
    
    def get_alertas_ativos(self):
        """Retorna todos os alertas ativos"""
        conn = self.connect()
        
        try:
            query = """
            SELECT 
                a.id_alerta,
                a.id_jogador,
                j.nome as jogador,
                a.tipo_alerta,
                a.descricao,
                a.prioridade,
                a.data_criacao
            FROM alertas a
            JOIN jogadores j ON a.id_jogador = j.id_jogador
            WHERE a.ativo = 1
            ORDER BY 
                CASE a.prioridade
                    WHEN 'alta' THEN 1
                    WHEN 'media' THEN 2
                    WHEN 'baixa' THEN 3
                END,
                a.data_criacao DESC
            """
            df = pd.read_sql_query(query, conn)
        except:
            # Se a coluna ativo não existir, busca todos
            try:
                query = """
                SELECT 
                    a.id_alerta,
                    a.id_jogador,
                    j.nome as jogador,
                    a.tipo_alerta,
                    a.descricao,
                    a.prioridade,
                    a.data_criacao
                FROM alertas a
                JOIN jogadores j ON a.id_jogador = j.id_jogador
                ORDER BY 
                    CASE a.prioridade
                        WHEN 'alta' THEN 1
                        WHEN 'media' THEN 2
                        WHEN 'baixa' THEN 3
                    END,
                    a.data_criacao DESC
                """
                df = pd.read_sql_query(query, conn)
            except:
                df = pd.DataFrame()
        
        conn.close()
        return df
    
    def desativar_alerta(self, id_alerta):
        """Desativa um alerta"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE alertas SET ativo = 0 WHERE id_alerta = ?", (id_alerta,))
        except:
            # Se não conseguir desativar, deleta
            cursor.execute("DELETE FROM alertas WHERE id_alerta = ?", (id_alerta,))
        
        conn.commit()
        conn.close()
