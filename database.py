"""
Sistema de Banco de Dados para Scout Pro v3.0 - OTIMIZADO
Suporta SQLite (desenvolvimento) e PostgreSQL (produção/Railway)
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import pandas as pd
import numpy as np
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

# --- FUNÇÕES DE CACHE (Fora da Classe para evitar erros de Hash) ---

@st.cache_data(ttl=3600, show_spinner=False)
def _cached_buscar_todos_jogadores(_engine):
    query = """
    SELECT 
        j.id_jogador, j.nome, j.nacionalidade, j.ano_nascimento, j.idade_atual, 
        j.altura, j.pe_dominante, j.transfermarkt_id,
        v.clube, v.liga_clube, v.posicao, v.data_fim_contrato, v.status_contrato
    FROM jogadores j
    LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
    ORDER BY j.nome
    """
    try:
        return pd.read_sql(text(query), _engine)
    except Exception as e:
        print(f"❌ Erro ao buscar jogadores: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def _cached_buscar_avaliacoes(_engine, id_jogador: int):
    query = """
    SELECT 
        id_avaliacao, data_avaliacao, nota_potencial, nota_tatico, nota_tecnico,
        nota_fisico, nota_mental, observacoes, avaliador
    FROM avaliacoes 
    WHERE id_jogador = :id_jogador
    ORDER BY data_avaliacao DESC
    """
    try:
        return pd.read_sql(text(query), _engine, params={'id_jogador': id_jogador})
    except Exception as e:
        print(f"❌ Erro ao buscar avaliações: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def _cached_buscar_alertas(_engine):
    query = """
    SELECT 
        a.id_alerta, a.tipo_alerta, a.descricao, a.prioridade, a.data_criacao,
        j.nome as jogador, v.clube
    FROM alertas a
    INNER JOIN jogadores j ON a.id_jogador = j.id_jogador
    LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
    WHERE a.ativo = 1 OR a.ativo = TRUE
    ORDER BY a.data_criacao DESC
    """
    try:
        return pd.read_sql(text(query), _engine)
    except Exception as e:
        print(f"❌ Erro ao buscar alertas: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def _cached_get_all_tags(_engine):
    query = "SELECT * FROM tags ORDER BY nome"
    try:
        return pd.read_sql(text(query), _engine)
    except Exception as e:
        print(f"❌ Erro ao buscar tags: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def _cached_get_wishlist(_engine, prioridade=None):
    if prioridade:
        query = """
        SELECT j.*, v.clube, v.posicao, v.liga_clube, v.data_fim_contrato,
               w.prioridade, w.observacao, w.adicionado_em as wishlist_adicionado_em
        FROM wishlist w
        INNER JOIN jogadores j ON w.id_jogador = j.id_jogador
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        WHERE w.prioridade = :prioridade
        ORDER BY w.adicionado_em DESC
        """
        params = {'prioridade': prioridade}
    else:
        query = """
        SELECT j.*, v.clube, v.posicao, v.liga_clube, v.data_fim_contrato,
               w.prioridade, w.observacao, w.adicionado_em as wishlist_adicionado_em
        FROM wishlist w
        INNER JOIN jogadores j ON w.id_jogador = j.id_jogador
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        ORDER BY 
            CASE w.prioridade 
                WHEN 'alta' THEN 1 
                WHEN 'media' THEN 2 
                WHEN 'baixa' THEN 3 
            END,
            w.adicionado_em DESC
        """
        params = {}
    
    try:
        return pd.read_sql(text(query), _engine, params=params)
    except Exception as e:
        print(f"❌ Erro ao buscar wishlist: {e}")
        return pd.DataFrame()

# --- CLASSE PRINCIPAL ---

class ScoutingDatabase:
    def __init__(self):
        """Inicializa conexão com o banco de dados (SQLite ou PostgreSQL)"""
        self.database_url = os.getenv('DATABASE_URL')
        
        if self.database_url:
            print("🔵 Conectando ao PostgreSQL (Railway)...")
            if self.database_url.startswith("postgres://"):
                self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
            
            self.engine = create_engine(
                self.database_url,
                poolclass=NullPool,
                connect_args={
                    "connect_timeout": 10,
                    "options": "-c timezone=utc"
                },
                pool_pre_ping=True,
                echo=False
            )
            self.db_type = 'postgresql'
        else:
            print("🟢 Usando SQLite local...")
            self.engine = create_engine('sqlite:///scouting.db')
            self.db_type = 'sqlite'
        
        self.criar_tabelas()

    def _safe_int(self, value):
        if isinstance(value, (np.int64, np.int32, np.int16)):
            return int(value)
        return value

    def criar_tabelas(self):
        """Cria todas as tabelas e views (v3.0)"""
        if self.db_type == 'postgresql':
            id_type = "SERIAL PRIMARY KEY"
            bool_true = "TRUE"
        else:
            id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
            bool_true = "1"

        commands = [
            f"""CREATE TABLE IF NOT EXISTS jogadores (
                id_jogador {id_type},
                nome VARCHAR(255) NOT NULL,
                nacionalidade VARCHAR(100),
                ano_nascimento INTEGER,
                idade_atual INTEGER,
                altura INTEGER,
                pe_dominante VARCHAR(50),
                transfermarkt_id VARCHAR(100),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            f"""CREATE TABLE IF NOT EXISTS vinculos_clubes (
                id_vinculo {id_type},
                id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
                clube VARCHAR(255),
                liga_clube VARCHAR(255),
                posicao VARCHAR(100) NOT NULL,
                data_fim_contrato DATE,
                status_contrato VARCHAR(50),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            f"""CREATE TABLE IF NOT EXISTS alertas (
                id_alerta {id_type},
                id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
                tipo_alerta VARCHAR(100) NOT NULL,
                descricao TEXT,
                prioridade VARCHAR(50),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT {bool_true}
            )""",
            f"""CREATE TABLE IF NOT EXISTS avaliacoes (
                id_avaliacao {id_type},
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
            )""",
            f"""CREATE TABLE IF NOT EXISTS tags (
                id_tag {id_type},
                nome VARCHAR(50) NOT NULL UNIQUE,
                cor VARCHAR(20) DEFAULT '#808080',
                descricao TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS jogador_tags (
                id_jogador INTEGER,
                id_tag INTEGER,
                adicionado_por VARCHAR(100),
                adicionado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id_jogador, id_tag),
                FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
                FOREIGN KEY (id_tag) REFERENCES tags(id_tag) ON DELETE CASCADE
            )""",
            f"""CREATE TABLE IF NOT EXISTS wishlist (
                id {id_type},
                id_jogador INTEGER UNIQUE,
                prioridade VARCHAR(20),
                observacao TEXT,
                adicionado_por VARCHAR(100),
                adicionado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador) ON DELETE CASCADE
            )""",
            f"""CREATE TABLE IF NOT EXISTS notas_rapidas (
                id_nota {id_type},
                id_jogador INTEGER,
                texto TEXT NOT NULL,
                autor VARCHAR(100),
                tipo VARCHAR(50) DEFAULT 'observacao',
                data_nota TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador) ON DELETE CASCADE
            )""",
            f"""CREATE TABLE IF NOT EXISTS buscas_salvas (
                id_busca {id_type},
                nome_busca VARCHAR(100) NOT NULL,
                filtros TEXT NOT NULL,
                criado_por VARCHAR(100),
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            # Nova Tabela Propostas
            f"""CREATE TABLE IF NOT EXISTS propostas (
                id_proposta {id_type},
                id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
                valor_proposta NUMERIC(12, 2),
                moeda VARCHAR(10) DEFAULT 'BRL',
                tipo_transferencia VARCHAR(50) DEFAULT 'Definitiva',
                clube_interessado VARCHAR(255),
                data_proposta DATE DEFAULT CURRENT_DATE,
                status VARCHAR(50) DEFAULT 'Em análise',
                observacoes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        ]

        # Views
        view_benchmark = """
        CREATE VIEW IF NOT EXISTS vw_benchmark_posicoes AS
        SELECT 
            v.posicao,
            COUNT(j.id_jogador) as total_analisados,
            AVG(a.nota_potencial) as med_potencial,
            AVG(a.nota_tatico) as med_tatico,
            AVG(a.nota_tecnico) as med_tecnico,
            AVG(a.nota_fisico) as med_fisico,
            AVG(a.nota_mental) as med_mental
        FROM jogadores j
        JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        JOIN avaliacoes a ON j.id_jogador = a.id_jogador
        GROUP BY v.posicao
        """

        if self.db_type == 'postgresql':
            condicao_data = "v.data_fim_contrato <= (CURRENT_DATE + INTERVAL '6 months')"
        else:
            condicao_data = "v.data_fim_contrato <= DATE('now', '+6 months')"

        view_alertas_inteligentes = f"""
        CREATE VIEW IF NOT EXISTS vw_alertas_inteligentes AS
        SELECT 
            a.id_jogador, j.nome, v.clube, a.tipo_alerta, a.descricao,
            a.prioridade, a.data_criacao
        FROM alertas a
        JOIN jogadores j ON a.id_jogador = j.id_jogador
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        WHERE a.ativo = 1 OR a.ativo = TRUE
        UNION ALL
        SELECT 
            j.id_jogador, j.nome, v.clube, 'Contrato' as tipo_alerta,
            'Contrato expira em menos de 6 meses' as descricao,
            'alta' as prioridade, v.data_atualizacao as data_criacao
        FROM vinculos_clubes v
        JOIN jogadores j ON v.id_jogador = j.id_jogador
        WHERE {condicao_data}
        """

        try:
            with self.engine.connect() as conn:
                for sql in commands:
                    conn.execute(text(sql))
                
                # Dropar e recriar views para garantir atualização
                conn.execute(text("DROP VIEW IF EXISTS vw_benchmark_posicoes"))
                conn.execute(text(view_benchmark))
                conn.execute(text("DROP VIEW IF EXISTS vw_alertas_inteligentes"))
                conn.execute(text(view_alertas_inteligentes))
                
                conn.commit()
                print(f"✅ Estrutura do banco de dados ({self.db_type}) atualizada com sucesso!")
        except Exception as e:
            print(f"❌ Erro crítico ao criar tabelas: {e}")

    # --- INSERÇÕES E UPDATES ---

    def inserir_vinculo(self, id_jogador: int, dados_vinculo: dict) -> bool:
        id_jogador = self._safe_int(id_jogador)
        try:
            query_check = "SELECT id_vinculo FROM vinculos_clubes WHERE id_jogador = :id_jogador"
            with self.engine.connect() as conn:
                result = conn.execute(text(query_check), {"id_jogador": id_jogador})
                vinculo_existente = result.fetchone()
                
                if vinculo_existente:
                    query_update = """
                    UPDATE vinculos_clubes SET
                        clube = :clube, liga_clube = :liga_clube, posicao = :posicao,
                        data_fim_contrato = :data_fim_contrato, status_contrato = :status_contrato,
                        data_atualizacao = CURRENT_TIMESTAMP
                    WHERE id_jogador = :id_jogador
                    """
                    dados_vinculo['id_jogador'] = id_jogador
                    conn.execute(text(query_update), dados_vinculo)
                else:
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

    def inserir_jogador(self, dados_jogador: dict) -> Optional[int]:
        try:
            id_jogador = None
            tm_id = dados_jogador.get('transfermarkt_id')
            nome = dados_jogador.get('nome')
            
            if tm_id:
                id_jogador = self.buscar_jogador_por_tm_id(tm_id)
            
            if not id_jogador and nome:
                with self.engine.connect() as conn:
                    result = conn.execute(text("SELECT id_jogador FROM jogadores WHERE nome = :nome"), {"nome": nome})
                    row = result.fetchone()
                    if row: id_jogador = row[0]
            
            with self.engine.connect() as conn:
                if id_jogador:
                    query_update = """
                    UPDATE jogadores SET
                        nome = :nome, nacionalidade = :nacionalidade, ano_nascimento = :ano_nascimento,
                        idade_atual = :idade_atual, altura = :altura, pe_dominante = :pe_dominante,
                        transfermarkt_id = :transfermarkt_id, data_atualizacao = CURRENT_TIMESTAMP
                    WHERE id_jogador = :id_jogador
                    """
                    dados_jogador['id_jogador'] = id_jogador
                    conn.execute(text(query_update), dados_jogador)
                    conn.commit()
                else:
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
                    else:
                        conn.execute(text(query_insert), dados_jogador)
                        result = conn.execute(text("SELECT last_insert_rowid()"))
                        id_jogador = result.fetchone()[0]
                    conn.commit()
                return id_jogador
        except Exception as e:
            print(f"❌ Erro ao inserir jogador: {e}")
            return None

    def inserir_avaliacao(self, id_jogador: int, dados_avaliacao: dict) -> bool:
        id_jogador = self._safe_int(id_jogador)
        try:
            query = """
            INSERT INTO avaliacoes (
                id_jogador, data_avaliacao, nota_potencial, nota_tatico,
                nota_tecnico, nota_fisico, nota_mental, observacoes, avaliador
            ) VALUES (
                :id_jogador, :data_avaliacao, :nota_potencial, :nota_tatico,
                :nota_tecnico, :nota_fisico, :nota_mental, :observacoes, :avaliador
            )
            """
            with self.engine.connect() as conn:
                conn.execute(text(query), {**dados_avaliacao, 'id_jogador': id_jogador})
                conn.commit()
                # Limpa cache de avaliações
                st.cache_data.clear()
                return True
        except Exception as e:
            print(f"❌ Erro ao inserir avaliação: {e}")
            return False

    def inserir_alerta(self, id_jogador: int, tipo_alerta: str, descricao: str, prioridade: str = 'média') -> bool:
        id_jogador = self._safe_int(id_jogador)
        try:
            with self.engine.connect() as conn:
                conn.execute(text("INSERT INTO alertas (id_jogador, tipo_alerta, descricao, prioridade) VALUES (:id_jogador, :tipo_alerta, :descricao, :prioridade)"),
                             {'id_jogador': id_jogador, 'tipo_alerta': tipo_alerta, 'descricao': descricao, 'prioridade': prioridade})
                conn.commit()
            st.cache_data.clear()
            return True
        except Exception as e:
            print(f"❌ Erro alerta: {e}")
            return False

    # --- GETTERS (USANDO O CACHE EXTERNO) ---

    def buscar_todos_jogadores(self):
        return _cached_buscar_todos_jogadores(self.engine)

    def buscar_avaliacoes_jogador(self, id_jogador):
        return _cached_buscar_avaliacoes(self.engine, self._safe_int(id_jogador))

    def buscar_alertas_ativos(self):
        return _cached_buscar_alertas(self.engine)

    def get_all_tags(self):
        return _cached_get_all_tags(self.engine)
    
    def get_wishlist(self, prioridade=None):
        return _cached_get_wishlist(self.engine, prioridade)

    # --- UTILITÁRIOS E BUSCAS ESPECÍFICAS ---

    def buscar_jogador_por_tm_id(self, tm_id: str) -> Optional[int]:
        if not tm_id: return None
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT id_jogador FROM jogadores WHERE transfermarkt_id = :tm_id"), {"tm_id": tm_id})
                row = result.fetchone()
                return row[0] if row else None
        except Exception: return None

    def obter_estatisticas(self) -> dict:
        try:
            with self.engine.connect() as conn:
                total = conn.execute(text("SELECT COUNT(*) FROM jogadores")).fetchone()[0]
                alertas_q = "SELECT COUNT(*) FROM alertas WHERE ativo = TRUE" if self.db_type == 'postgresql' else "SELECT COUNT(*) FROM alertas WHERE ativo = 1"
                alertas = conn.execute(text(alertas_q)).fetchone()[0]
                
                date_q = "CURRENT_DATE + INTERVAL '6 months'" if self.db_type == 'postgresql' else "DATE('now', '+6 months')"
                now_q = "CURRENT_DATE" if self.db_type == 'postgresql' else "DATE('now')"
                
                contratos = conn.execute(text(f"SELECT COUNT(*) FROM vinculos_clubes WHERE data_fim_contrato <= {date_q} AND data_fim_contrato >= {now_q}")).fetchone()[0]
                vinculos = conn.execute(text("SELECT COUNT(*) FROM vinculos_clubes")).fetchone()[0]
                
                return {
                    'total_jogadores': total, 'alertas_ativos': alertas,
                    'contratos_vencendo': contratos, 'total_vinculos_ativos': vinculos
                }
        except Exception:
            return {'total_jogadores': 0, 'alertas_ativos': 0, 'contratos_vencendo': 0, 'total_vinculos_ativos': 0}

    def busca_avancada(self, filtros):
        query = """
        SELECT DISTINCT j.*, v.clube, v.posicao, v.liga_clube, v.data_fim_contrato, v.status_contrato
        FROM jogadores j
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        LEFT JOIN jogador_tags jt ON j.id_jogador = jt.id_jogador
        WHERE 1=1
        """
        params = {}
        
        # Filtros Dinâmicos
        if filtros.get('posicoes'):
            placeholders = ', '.join([f':pos{i}' for i in range(len(filtros['posicoes']))])
            query += f" AND v.posicao IN ({placeholders})"
            for i, val in enumerate(filtros['posicoes']): params[f'pos{i}'] = val
            
        if filtros.get('nacionalidades'):
            placeholders = ', '.join([f':nac{i}' for i in range(len(filtros['nacionalidades']))])
            query += f" AND j.nacionalidade IN ({placeholders})"
            for i, val in enumerate(filtros['nacionalidades']): params[f'nac{i}'] = val

        if filtros.get('idade_min'):
            query += " AND j.idade_atual >= :idade_min"
            params['idade_min'] = filtros['idade_min']

        if filtros.get('idade_max'):
            query += " AND j.idade_atual <= :idade_max"
            params['idade_max'] = filtros['idade_max']
            
        if filtros.get('tags'):
            placeholders = ', '.join([f':tag{i}' for i in range(len(filtros['tags']))])
            query += f" AND jt.id_tag IN ({placeholders})"
            for i, val in enumerate(filtros['tags']): params[f'tag{i}'] = val

        query += " ORDER BY j.nome"
        
        try:
            df = pd.read_sql(text(query), self.engine, params=params)
            return df
        except Exception as e:
            print(f"❌ Erro na busca avançada: {e}")
            return pd.DataFrame()

    def adicionar_tag_jogador(self, id_jogador, id_tag, adicionado_por=None):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("INSERT INTO jogador_tags (id_jogador, id_tag, adicionado_por) VALUES (:id_jogador, :id_tag, :adicionado_por)"),
                             {'id_jogador': id_jogador, 'id_tag': id_tag, 'adicionado_por': adicionado_por})
                conn.commit()
            st.cache_data.clear()
            return True
        except Exception: return False

    def remover_tag_jogador(self, id_jogador, id_tag):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM jogador_tags WHERE id_jogador = :id_jogador AND id_tag = :id_tag"),
                             {'id_jogador': id_jogador, 'id_tag': id_tag})
                conn.commit()
            st.cache_data.clear()
            return True
        except Exception: return False

    def get_jogador_tags(self, id_jogador):
        query = """
        SELECT t.id_tag, t.nome, t.cor, t.descricao, jt.adicionado_em
        FROM jogador_tags jt
        INNER JOIN tags t ON jt.id_tag = t.id_tag
        WHERE jt.id_jogador = :id_jogador
        ORDER BY jt.adicionado_em DESC
        """
        try:
            return pd.read_sql(text(query), self.engine, params={'id_jogador': self._safe_int(id_jogador)})
        except Exception: return pd.DataFrame()

    def adicionar_wishlist(self, id_jogador, prioridade='media', observacao=None, adicionado_por=None):
        id_jogador = self._safe_int(id_jogador)
        try:
            with self.engine.connect() as conn:
                # Upsert simplificado
                check = conn.execute(text("SELECT id FROM wishlist WHERE id_jogador = :id"), {'id': id_jogador}).fetchone()
                if check:
                    conn.execute(text("UPDATE wishlist SET prioridade=:p, observacao=:o WHERE id_jogador=:id"),
                                 {'p': prioridade, 'o': observacao, 'id': id_jogador})
                else:
                    conn.execute(text("INSERT INTO wishlist (id_jogador, prioridade, observacao, adicionado_por) VALUES (:id, :p, :o, :user)"),
                                 {'id': id_jogador, 'p': prioridade, 'o': observacao, 'user': adicionado_por})
                conn.commit()
            st.cache_data.clear()
            return True
        except Exception as e:
            print(f"Erro wishlist: {e}")
            return False

    def remover_wishlist(self, id_jogador):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM wishlist WHERE id_jogador = :id"), {'id': self._safe_int(id_jogador)})
                conn.commit()
            st.cache_data.clear()
            return True
        except Exception: return False

    def esta_na_wishlist(self, id_jogador):
        try:
            with self.engine.connect() as conn:
                count = conn.execute(text("SELECT COUNT(*) FROM wishlist WHERE id_jogador = :id"), 
                                   {'id': self._safe_int(id_jogador)}).fetchone()[0]
                return count > 0
        except Exception: return False

    def get_notas_rapidas(self, id_jogador):
        return pd.read_sql(text("SELECT * FROM notas_rapidas WHERE id_jogador = :id ORDER BY data_nota DESC"),
                           self.engine, params={'id': self._safe_int(id_jogador)})

    def adicionar_nota_rapida(self, id_jogador, texto, autor=None, tipo='observacao'):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("INSERT INTO notas_rapidas (id_jogador, texto, autor, tipo) VALUES (:id, :t, :a, :tp)"),
                             {'id': self._safe_int(id_jogador), 't': texto, 'a': autor, 'tp': tipo})
                conn.commit()
            return True
        except Exception: return False
    
    def deletar_nota_rapida(self, id_nota):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM notas_rapidas WHERE id_nota = :id"), {'id': id_nota})
                conn.commit()
            return True
        except Exception: return False

    def fechar_conexao(self):
        self.engine.dispose()

def get_database():
    return ScoutingDatabase()

if __name__ == "__main__":
    db = ScoutingDatabase()
    stats = db.obter_estatisticas()
    print(f"Stats: {stats}")
