"""
Sistema de Banco de Dados para Scout Pro
Suporta SQLite (desenvolvimento) e PostgreSQL (produção/Railway)
"""

import os
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

class ScoutingDatabase:
    def __init__(self):
        """Inicializa conexão com o banco de dados (SQLite ou PostgreSQL)"""
        
        # Detectar ambiente: Railway usa DATABASE_URL
        self.database_url = os.getenv('DATABASE_URL')
        
        if self.database_url:
            # PRODUÇÃO: PostgreSQL no Railway
            print("🔵 Conectando ao PostgreSQL (Railway)...")
            
            # Fix para Railway: postgres:// → postgresql://
            if self.database_url.startswith("postgres://"):
                self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
            
            self.engine = create_engine(
                self.database_url,
                poolclass=NullPool,  # Evita problemas de conexão
                connect_args={
                    "connect_timeout": 10,
                    "options": "-c timezone=utc"
                },
                pool_pre_ping=True  # Verifica conexão antes de usar
            )
            self.db_type = 'postgresql'
            print("✅ Conectado ao PostgreSQL com sucesso!")
        else:
            # DESENVOLVIMENTO: SQLite local
            print("🟢 Usando SQLite local...")
            self.engine = create_engine('sqlite:///scouting.db')
            self.db_type = 'sqlite'
            print("✅ Conectado ao SQLite com sucesso!")
        
        self.criar_tabelas()
    
    def criar_tabelas(self):
        """Cria as tabelas no banco (compatível com SQLite e PostgreSQL)"""
        
        if self.db_type == 'postgresql':
            # PostgreSQL usa SERIAL em vez de AUTOINCREMENT
            sql_jogadores = """
            CREATE TABLE IF NOT EXISTS jogadores (
                id_jogador SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                nacionalidade VARCHAR(100),
                ano_nascimento INTEGER,
                idade_atual INTEGER,
                altura INTEGER,
                pe_dominante VARCHAR(50),
                transfermarkt_id VARCHAR(100),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            sql_vinculos = """
            CREATE TABLE IF NOT EXISTS vinculos_clubes (
                id_vinculo SERIAL PRIMARY KEY,
                id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
                clube VARCHAR(255),
                liga_clube VARCHAR(255),
                posicao VARCHAR(100) NOT NULL,
                data_fim_contrato DATE,
                status_contrato VARCHAR(50),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            sql_alertas = """
            CREATE TABLE IF NOT EXISTS alertas (
                id_alerta SERIAL PRIMARY KEY,
                id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
                tipo_alerta VARCHAR(100) NOT NULL,
                descricao TEXT,
                prioridade VARCHAR(50),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT TRUE
            )
            """
            
            sql_avaliacoes = """
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id_avaliacao SERIAL PRIMARY KEY,
                id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
                data_avaliacao DATE NOT NULL,
                nota_potencial DECIMAL(3,1),
                nota_tatico DECIMAL(3,1),
                nota_tecnico DECIMAL(3,1),
                nota_fisico DECIMAL(3,1),
                nota_mental DECIMAL(3,1),
                observacoes TEXT,
                avaliador VARCHAR(255),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:
            # SQLite (código original)
            sql_jogadores = """
            CREATE TABLE IF NOT EXISTS jogadores (
                id_jogador INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                nacionalidade TEXT,
                ano_nascimento INTEGER,
                idade_atual INTEGER,
                altura INTEGER,
                pe_dominante TEXT,
                transfermarkt_id TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            sql_vinculos = """
            CREATE TABLE IF NOT EXISTS vinculos_clubes (
                id_vinculo INTEGER PRIMARY KEY AUTOINCREMENT,
                id_jogador INTEGER,
                clube TEXT,
                liga_clube TEXT,
                posicao TEXT NOT NULL,
                data_fim_contrato DATE,
                status_contrato TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador) ON DELETE CASCADE
            )
            """
            
            sql_alertas = """
            CREATE TABLE IF NOT EXISTS alertas (
                id_alerta INTEGER PRIMARY KEY AUTOINCREMENT,
                id_jogador INTEGER,
                tipo_alerta TEXT NOT NULL,
                descricao TEXT,
                prioridade TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1,
                FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador) ON DELETE CASCADE
            )
            """
            
            sql_avaliacoes = """
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id_avaliacao INTEGER PRIMARY KEY AUTOINCREMENT,
                id_jogador INTEGER,
                data_avaliacao DATE NOT NULL,
                nota_potencial REAL,
                nota_tatico REAL,
                nota_tecnico REAL,
                nota_fisico REAL,
                nota_mental REAL,
                observacoes TEXT,
                avaliador TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador) ON DELETE CASCADE
            )
            """
        
        # Executar criação das tabelas
        try:
            with self.engine.connect() as conn:
                conn.execute(text(sql_jogadores))
                conn.execute(text(sql_vinculos))
                conn.execute(text(sql_alertas))
                conn.execute(text(sql_avaliacoes))
                conn.commit()
                print("✅ Tabelas criadas/verificadas com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
            raise
    
    def inserir_jogador(self, dados_jogador: dict) -> Optional[int]:
        """
        Insere ou atualiza um jogador no banco
        Retorna o ID do jogador
        """
        try:
            # Verifica se jogador já existe
            query_check = "SELECT id_jogador FROM jogadores WHERE nome = :nome"
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query_check), {"nome": dados_jogador['nome']})
                jogador_existente = result.fetchone()
                
                if jogador_existente:
                    # Atualiza jogador existente
                    id_jogador = jogador_existente[0]
                    query_update = """
                    UPDATE jogadores SET
                        nacionalidade = :nacionalidade,
                        ano_nascimento = :ano_nascimento,
                        idade_atual = :idade_atual,
                        altura = :altura,
                        pe_dominante = :pe_dominante,
                        transfermarkt_id = :transfermarkt_id,
                        data_atualizacao = CURRENT_TIMESTAMP
                    WHERE id_jogador = :id_jogador
                    """
                    dados_jogador['id_jogador'] = id_jogador
                    conn.execute(text(query_update), dados_jogador)
                    conn.commit()
                else:
                    # Insere novo jogador
                    query_insert = """
                    INSERT INTO jogadores 
                    (nome, nacionalidade, ano_nascimento, idade_atual, altura, pe_dominante, transfermarkt_id)
                    VALUES 
                    (:nome, :nacionalidade, :ano_nascimento, :idade_atual, :altura, :pe_dominante, :transfermarkt_id)
                    """
                    
                    if self.db_type == 'postgresql':
                        query_insert += " RETURNING id_jogador"
                        result = conn.execute(text(query_insert), dados_jogador)
                        id_jogador = result.fetchone()[0]
                        conn.commit()
                    else:
                        conn.execute(text(query_insert), dados_jogador)
                        conn.commit()
                        result = conn.execute(text("SELECT last_insert_rowid()"))
                        id_jogador = result.fetchone()[0]
                
                return id_jogador
                
        except Exception as e:
            print(f"❌ Erro ao inserir jogador {dados_jogador.get('nome', 'Desconhecido')}: {e}")
            return None
    
    def inserir_vinculo(self, id_jogador: int, dados_vinculo: dict) -> bool:
        """Insere ou atualiza vínculo de clube do jogador"""
        try:
            # Verifica se já existe vínculo ativo para este jogador
            query_check = """
            SELECT id_vinculo FROM vinculos_clubes 
            WHERE id_jogador = :id_jogador
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query_check), {"id_jogador": id_jogador})
                vinculo_existente = result.fetchone()
                
                if vinculo_existente:
                    # Atualiza vínculo existente
                    query_update = """
                    UPDATE vinculos_clubes SET
                        clube = :clube,
                        liga_clube = :liga_clube,
                        posicao = :posicao,
                        data_fim_contrato = :data_fim_contrato,
                        status_contrato = :status_contrato,
                        data_atualizacao = CURRENT_TIMESTAMP
                    WHERE id_jogador = :id_jogador
                    """
                    dados_vinculo['id_jogador'] = id_jogador
                    conn.execute(text(query_update), dados_vinculo)
                else:
                    # Insere novo vínculo
                    query_insert = """
                    INSERT INTO vinculos_clubes 
                    (id_jogador, clube, liga_clube, posicao, data_fim_contrato, status_contrato)
                    VALUES 
                    (:id_jogador, :clube, :liga_clube, :posicao, :data_fim_contrato, :status_contrato)
                    """
                    dados_vinculo['id_jogador'] = id_jogador
                    conn.execute(text(query_insert), dados_vinculo)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ Erro ao inserir vínculo: {e}")
            return False
    
    def inserir_alerta(self, id_jogador: int, tipo_alerta: str, descricao: str, prioridade: str = 'média') -> bool:
        """Insere um alerta para um jogador"""
        try:
            query = """
            INSERT INTO alertas (id_jogador, tipo_alerta, descricao, prioridade)
            VALUES (:id_jogador, :tipo_alerta, :descricao, :prioridade)
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(query), {
                    'id_jogador': id_jogador,
                    'tipo_alerta': tipo_alerta,
                    'descricao': descricao,
                    'prioridade': prioridade
                })
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ Erro ao inserir alerta: {e}")
            return False
    
    def buscar_todos_jogadores(self) -> pd.DataFrame:
        """Retorna todos os jogadores com seus vínculos"""
        query = """
        SELECT 
            j.id_jogador,
            j.nome,
            j.nacionalidade,
            j.ano_nascimento,
            j.idade_atual,
            j.altura,
            j.pe_dominante,
            j.transfermarkt_id,
            v.clube,
            v.liga_clube,
            v.posicao,
            v.data_fim_contrato,
            v.status_contrato
        FROM jogadores j
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        ORDER BY j.nome
        """
        
        try:
            df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            print(f"❌ Erro ao buscar jogadores: {e}")
            return pd.DataFrame()
    
    def buscar_jogador_por_nome(self, nome: str) -> pd.DataFrame:
        """Busca jogadores por nome (parcial)"""
        query = """
        SELECT 
            j.id_jogador,
            j.nome,
            j.nacionalidade,
            j.ano_nascimento,
            j.idade_atual,
            j.altura,
            j.pe_dominante,
            j.transfermarkt_id,
            v.clube,
            v.liga_clube,
            v.posicao,
            v.data_fim_contrato,
            v.status_contrato
        FROM jogadores j
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        WHERE LOWER(j.nome) LIKE LOWER(:nome)
        ORDER BY j.nome
        """
        
        try:
            df = pd.read_sql(query, self.engine, params={'nome': f'%{nome}%'})
            return df
        except Exception as e:
            print(f"❌ Erro ao buscar jogador: {e}")
            return pd.DataFrame()
    
    def buscar_alertas_ativos(self) -> pd.DataFrame:
        """Retorna todos os alertas ativos"""
        
        if self.db_type == 'postgresql':
            query = """
            SELECT 
                a.id_alerta,
                a.tipo_alerta,
                a.descricao,
                a.prioridade,
                a.data_criacao,
                j.nome as jogador_nome,
                v.clube,
                v.posicao
            FROM alertas a
            INNER JOIN jogadores j ON a.id_jogador = j.id_jogador
            LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
            WHERE a.ativo = TRUE
            ORDER BY 
                CASE a.prioridade 
                    WHEN 'alta' THEN 1 
                    WHEN 'média' THEN 2 
                    WHEN 'baixa' THEN 3 
                END,
                a.data_criacao DESC
            """
        else:
            query = """
            SELECT 
                a.id_alerta,
                a.tipo_alerta,
                a.descricao,
                a.prioridade,
                a.data_criacao,
                j.nome as jogador_nome,
                v.clube,
                v.posicao
            FROM alertas a
            INNER JOIN jogadores j ON a.id_jogador = j.id_jogador
            LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
            WHERE a.ativo = 1
            ORDER BY 
                CASE a.prioridade 
                    WHEN 'alta' THEN 1 
                    WHEN 'média' THEN 2 
                    WHEN 'baixa' THEN 3 
                END,
                a.data_criacao DESC
            """
        
        try:
            df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            print(f"❌ Erro ao buscar alertas: {e}")
            return pd.DataFrame()
    
    def marcar_alerta_resolvido(self, id_alerta: int) -> bool:
        """Marca um alerta como resolvido (ativo = False)"""
        try:
            if self.db_type == 'postgresql':
                query = "UPDATE alertas SET ativo = FALSE WHERE id_alerta = :id_alerta"
            else:
                query = "UPDATE alertas SET ativo = 0 WHERE id_alerta = :id_alerta"
            
            with self.engine.connect() as conn:
                conn.execute(text(query), {'id_alerta': id_alerta})
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Erro ao marcar alerta como resolvido: {e}")
            return False
    
    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas gerais do banco"""
        stats = {}
        
        try:
            with self.engine.connect() as conn:
                # Total de jogadores
                result = conn.execute(text("SELECT COUNT(*) FROM jogadores"))
                stats['total_jogadores'] = result.fetchone()[0]
                
                # Alertas ativos
                if self.db_type == 'postgresql':
                    result = conn.execute(text("SELECT COUNT(*) FROM alertas WHERE ativo = TRUE"))
                else:
                    result = conn.execute(text("SELECT COUNT(*) FROM alertas WHERE ativo = 1"))
                stats['alertas_ativos'] = result.fetchone()[0]
                
                # Contratos vencendo (próximos 6 meses)
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM vinculos_clubes 
                    WHERE data_fim_contrato <= DATE('now', '+6 months')
                    AND data_fim_contrato >= DATE('now')
                """))
                stats['contratos_vencendo'] = result.fetchone()[0]
                
                return stats
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {
                'total_jogadores': 0,
                'alertas_ativos': 0,
                'contratos_vencendo': 0
            }
    
    def limpar_dados(self) -> bool:
        """
        CUIDADO: Remove todos os dados do banco
        Mantém a estrutura das tabelas
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM avaliacoes"))
                conn.execute(text("DELETE FROM alertas"))
                conn.execute(text("DELETE FROM vinculos_clubes"))
                conn.execute(text("DELETE FROM jogadores"))
                conn.commit()
                print("✅ Todos os dados foram removidos do banco!")
                return True
        except Exception as e:
            print(f"❌ Erro ao limpar dados: {e}")
            return False
    
    def verificar_saude_conexao(self) -> bool:
        """Verifica se a conexão com o banco está funcionando"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                print(f"✅ Conexão com {self.db_type.upper()} está saudável!")
                return True
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def fechar_conexao(self):
        """Fecha a conexão com o banco"""
        try:
            self.engine.dispose()
            print("✅ Conexão fechada com sucesso!")
        except Exception as e:
            print(f"⚠️ Aviso ao fechar conexão: {e}")


# Função auxiliar para uso rápido
def get_database():
    """Retorna uma instância do banco de dados"""
    return ScoutingDatabase()


if __name__ == "__main__":
    # Teste rápido
    print("🧪 Testando conexão com o banco de dados...\n")
    
    db = ScoutingDatabase()
    db.verificar_saude_conexao()
    
    stats = db.obter_estatisticas()
    print(f"\n📊 Estatísticas:")
    print(f"   Total de jogadores: {stats['total_jogadores']}")
    print(f"   Alertas ativos: {stats['alertas_ativos']}")
    print(f"   Contratos vencendo: {stats['contratos_vencendo']}")
    
    db.fechar_conexao()
