"""Sistema de Banco de Dados para Scout Pro v3.0 - OTIMIZADO
Suporta SQLite (desenvolvimento) e PostgreSQL (produção/Railway)"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import pandas as pd
import numpy as np
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

# --- FUNÇÕES DE CACHE (Fora da Classe para evitar erros de Hash) ---

@st.cache_data(ttl=3600, show_spinner=False)
def _cached_buscar_todos_jogadores(_engine):
    """Cache de 1 hora para todos os jogadores"""
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
    """Cache de 10 minutos para avaliações"""
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

@st.cache_data(ttl=300, show_spinner=False)
def _cached_get_ids_wishlist(_engine):
    """Cache de 5 minutos - retorna SET com IDs da wishlist para lookup rápido"""
    try:
        with _engine.connect() as conn:
            result = conn.execute(text("SELECT id_jogador FROM wishlist"))
            return {row[0] for row in result.fetchall()}
    except Exception as e:
        print(f"❌ Erro ao buscar IDs wishlist: {e}")
        return set()

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
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def _cached_get_all_tags(_engine):
    try:
        return pd.read_sql(text("SELECT * FROM tags ORDER BY nome"), _engine)
    except Exception:
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
    except Exception:
        return pd.DataFrame()

# --- CLASSE PRINCIPAL ---

class ScoutingDatabase:
    def __init__(self):
        """Inicializa conexão com o banco de dados (SQLite ou PostgreSQL)"""
        self.database_url = os.getenv('DATABASE_URL')
        
        if self.database_url:
            print("🚀 Conectando ao PostgreSQL Railway...")
            
            # Garantir formato correto
            if self.database_url.startswith("postgres://"):
                self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
            
            try:
                # ✅ CONFIGURAÇÃO OTIMIZADA PARA RAILWAY + PGBOUNCER
                self.engine = create_engine(
                    self.database_url,
                    
                    # Connection Pooling (trabalha COM o pooling do Railway)
                    poolclass=QueuePool,         # Pool inteligente
                    pool_size=15,                 # Máximo 15 conexões simultâneas
                    max_overflow=30,             # Até 30 conexões em picos
                    pool_timeout=30,             # Timeout de 30 segundos
                    pool_recycle=3600,           # Reciclar conexões a cada 1h
                    pool_pre_ping=True,          # Testar conexão antes de usar
                    
                    # Argumentos de conexão
                    connect_args={
                        "sslmode": "require",           # SSL obrigatório
                        "connect_timeout": 10,          # Timeout de conexão
                        "options": "-c timezone=utc"    # Timezone UTC
                    },
                    
                    # Performance
                    echo=False,                  # Desabilitar logs SQL
                    future=True                  # SQLAlchemy 2.0 style
                )
                
                # ✅ TESTAR CONEXÃO
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                self.db_type = 'postgresql'
                print("✅ Conectado ao PostgreSQL Railway com sucesso!")
                
            except Exception as e:
                print(f"⚠️  Erro ao conectar PostgreSQL: {e}")
                print("⚠️  Usando SQLite local como fallback...")
                self.engine = create_engine('sqlite:///scouting.db', echo=False)
                self.db_type = 'sqlite'
        
        else:
            print("ℹ️  DATABASE_URL não encontrada. Usando SQLite local...")
            self.engine = create_engine('sqlite:///scouting.db', echo=False)
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

        try:
            with self.engine.connect() as conn:
                for sql in commands:
                    conn.execute(text(sql))
                
                conn.commit()
                print(f"✅ Estrutura do banco ({self.db_type}) atualizada!")

        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")

    # --- MÉTODOS QUE USAM CACHE ---

    def buscar_todos_jogadores(self):
        """Interface pública - usa cache externo"""
        return _cached_buscar_todos_jogadores(self.engine)

    def buscar_avaliacoes_jogador(self, id_jogador):
        """Interface pública - usa cache externo"""
        return _cached_buscar_avaliacoes(self.engine, self._safe_int(id_jogador))

    def buscar_alertas_ativos(self):
        return _cached_buscar_alertas(self.engine)

    def get_all_tags(self):
        return _cached_get_all_tags(self.engine)
    
    def get_wishlist(self, prioridade=None):
        return _cached_get_wishlist(self.engine, prioridade)

    def get_ids_wishlist(self):
        return _cached_get_ids_wishlist(self.engine)

    # --- MÉTODOS DE BUSCAS SALVAS ---

    def get_buscas_salvas(self, criado_por=None):
        """Recupera buscas salvas do banco de dados"""
        try:
            if criado_por:
                query = """
                SELECT id_busca, nome_busca, filtros, criado_por, criado_em
                FROM buscas_salvas
                WHERE criado_por = :usuario
                ORDER BY criado_em DESC
                """
                params = {'usuario': criado_por}
            else:
                query = """
                SELECT id_busca, nome_busca, filtros, criado_por, criado_em
                FROM buscas_salvas
                ORDER BY criado_em DESC
                """
                params = {}
            
            return pd.read_sql(text(query), self.engine, params=params)
        except Exception as e:
            print(f"❌ Erro ao buscar buscas salvas: {e}")
            return pd.DataFrame()

    def salvar_busca(self, nome_busca: str, filtros: dict, criado_por: str = None) -> bool:
        """Salva uma busca personalizada"""
        try:
            filtros_json = json.dumps(filtros)
            
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO buscas_salvas (nome_busca, filtros, criado_por)
                    VALUES (:nome, :filtros, :usuario)
                """), {
                    'nome': nome_busca,
                    'filtros': filtros_json,
                    'usuario': criado_por
                })
                conn.commit()
            
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar busca: {e}")
            return False

    def deletar_busca_salva(self, id_busca: int) -> bool:
        """Remove uma busca salva"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM buscas_salvas WHERE id_busca = :id"), 
                            {'id': self._safe_int(id_busca)})
                conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erro ao deletar busca: {e}")
            return False

    def carregar_filtros_busca(self, id_busca: int) -> Optional[dict]:
        """Carrega os filtros de uma busca salva"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT filtros FROM buscas_salvas WHERE id_busca = :id
                """), {'id': self._safe_int(id_busca)}).fetchone()
                
                if result:
                    return json.loads(result[0])
                return None
        except Exception as e:
            print(f"❌ Erro ao carregar filtros: {e}")
            return None

    # --- MÉTODOS DE ESCRITA (sem cache) ---

    def inserir_vinculo(self, id_jogador: int, dados_vinculo: dict) -> bool:
        id_jogador = self._safe_int(id_jogador)
        try:
            with self.engine.connect() as conn:
                check = conn.execute(text("SELECT id_vinculo FROM vinculos_clubes WHERE id_jogador = :id"), {"id": id_jogador}).fetchone()
                
                if check:
                    conn.execute(text("""
                        UPDATE vinculos_clubes SET clube=:clube, liga_clube=:liga_clube, posicao=:posicao,
                        data_fim_contrato=:data_fim_contrato, status_contrato=:status_contrato, data_atualizacao=CURRENT_TIMESTAMP
                        WHERE id_jogador=:id
                    """), {**dados_vinculo, 'id': id_jogador})
                else:
                    conn.execute(text("""
                        INSERT INTO vinculos_clubes (id_jogador, clube, liga_clube, posicao, data_fim_contrato, status_contrato)
                        VALUES (:id, :clube, :liga_clube, :posicao, :data_fim_contrato, :status_contrato)
                    """), {**dados_vinculo, 'id': id_jogador})
                conn.commit()
            return True
        except Exception:
            return False

    def inserir_jogador(self, dados_jogador: dict) -> Optional[int]:
        try:
            tm_id = dados_jogador.get('transfermarkt_id')
            nome = dados_jogador.get('nome')
            id_jogador = None
            
            if tm_id:
                id_jogador = self.buscar_jogador_por_tm_id(tm_id)
            
            if not id_jogador and nome:
                with self.engine.connect() as conn:
                    row = conn.execute(text("SELECT id_jogador FROM jogadores WHERE nome = :n"), {"n": nome}).fetchone()
                    if row: id_jogador = row[0]
            
            with self.engine.connect() as conn:
                if id_jogador:
                    conn.execute(text("""
                        UPDATE jogadores SET nome=:nome, nacionalidade=:nacionalidade, ano_nascimento=:ano_nascimento,
                        idade_atual=:idade_atual, altura=:altura, pe_dominante=:pe_dominante,
                        transfermarkt_id=:transfermarkt_id, data_atualizacao=CURRENT_TIMESTAMP
                        WHERE id_jogador=:id
                    """), {**dados_jogador, 'id': id_jogador})
                    conn.commit()
                else:
                    if self.db_type == 'postgresql':
                        result = conn.execute(text("""
                            INSERT INTO jogadores (nome, nacionalidade, ano_nascimento, idade_atual, altura, pe_dominante, transfermarkt_id)
                            VALUES (:nome, :nacionalidade, :ano_nascimento, :idade_atual, :altura, :pe_dominante, :transfermarkt_id) RETURNING id_jogador
                        """), dados_jogador)
                        id_jogador = result.fetchone()[0]
                    else:
                        conn.execute(text("""
                            INSERT INTO jogadores (nome, nacionalidade, ano_nascimento, idade_atual, altura, pe_dominante, transfermarkt_id)
                            VALUES (:nome, :nacionalidade, :ano_nascimento, :idade_atual, :altura, :pe_dominante, :transfermarkt_id)
                        """), dados_jogador)
                        id_jogador = conn.execute(text("SELECT last_insert_rowid()")).fetchone()[0]
                    conn.commit()
                return id_jogador
        except Exception:
            return None

    def inserir_avaliacao(self, id_jogador: int, dados_avaliacao: dict) -> bool:
        try:
            # Mapeia os nomes dos parâmetros corretamente
            params = {
                'id': self._safe_int(id_jogador),
                'data': dados_avaliacao.get('data_avaliacao'),
                'pot': dados_avaliacao.get('nota_potencial'),
                'tac': dados_avaliacao.get('nota_tatico'),
                'tec': dados_avaliacao.get('nota_tecnico'),
                'fis': dados_avaliacao.get('nota_fisico'),
                'men': dados_avaliacao.get('nota_mental'),
                'obs': dados_avaliacao.get('observacoes', ''),
                'ava': dados_avaliacao.get('avaliador', '')
            }

            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO avaliacoes (id_jogador, data_avaliacao, nota_potencial, nota_tatico,
                    nota_tecnico, nota_fisico, nota_mental, observacoes, avaliador)
                    VALUES (:id, :data, :pot, :tac, :tec, :fis, :men, :obs, :ava)
                """), params)
                conn.commit()
            st.cache_data.clear()
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir avaliação: {e}")
            return False

    def adicionar_wishlist(self, id_jogador, prioridade='media', observacao=None, adicionado_por=None):
        id_jogador = self._safe_int(id_jogador)
        try:
            with self.engine.connect() as conn:
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
        except Exception:
            return False

    def remover_wishlist(self, id_jogador):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM wishlist WHERE id_jogador = :id"), {'id': self._safe_int(id_jogador)})
                conn.commit()
            st.cache_data.clear()
            return True
        except Exception:
            return False

    def esta_na_wishlist(self, id_jogador):
        """Verifica se jogador está na wishlist (usa cache)"""
        ids_wishlist = self.get_ids_wishlist()
        return self._safe_int(id_jogador) in ids_wishlist

    # --- OUTROS MÉTODOS ÚTEIS ---

    def buscar_jogador_por_tm_id(self, tm_id: str) -> Optional[int]:
        if not tm_id: return None
        try:
            with self.engine.connect() as conn:
                row = conn.execute(text("SELECT id_jogador FROM jogadores WHERE transfermarkt_id = :tm"), {"tm": tm_id}).fetchone()
                return row[0] if row else None
        except Exception:
            return None

    def obter_estatisticas(self) -> dict:
        try:
            with self.engine.connect() as conn:
                total = conn.execute(text("SELECT COUNT(*) FROM jogadores")).fetchone()[0]
                alertas = conn.execute(text(f"SELECT COUNT(*) FROM alertas WHERE ativo = {'TRUE' if self.db_type == 'postgresql' else '1'}")).fetchone()[0]
                
                date_expr = "CURRENT_DATE + INTERVAL '6 months'" if self.db_type == 'postgresql' else "DATE('now', '+6 months')"
                now_expr = "CURRENT_DATE" if self.db_type == 'postgresql' else "DATE('now')"
                
                contratos = conn.execute(text(f"SELECT COUNT(*) FROM vinculos_clubes WHERE data_fim_contrato <= {date_expr} AND data_fim_contrato >= {now_expr}")).fetchone()[0]
                vinculos = conn.execute(text("SELECT COUNT(*) FROM vinculos_clubes")).fetchone()[0]
                
                return {'total_jogadores': total, 'alertas_ativos': alertas, 'contratos_vencendo': contratos, 'total_vinculos_ativos': vinculos}
        except Exception:
            return {'total_jogadores': 0, 'alertas_ativos': 0, 'contratos_vencendo': 0, 'total_vinculos_ativos': 0}

    def get_jogadores_com_vinculos(self):
        """Alias para buscar_todos_jogadores"""
        return self.buscar_todos_jogadores()

    def get_avaliacoes_jogador(self, id_jogador):
        """Alias para buscar_avaliacoes_jogador"""
        return self.buscar_avaliacoes_jogador(id_jogador)

    def get_ultima_avaliacao(self, id_jogador):
        df = self.buscar_avaliacoes_jogador(id_jogador)
        return df.head(1) if not df.empty else pd.DataFrame()

    def salvar_avaliacao(self, **kwargs):
        id_jogador = kwargs.pop('id_jogador', None)
        return self.inserir_avaliacao(id_jogador, kwargs) if id_jogador else False

    def limpar_dados(self):
        """Remove todos os dados das tabelas para sincronização completa"""
        try:
            with self.engine.connect() as conn:
                if self.db_type == 'postgresql':
                    conn.execute(text("TRUNCATE TABLE alertas, avaliacoes, vinculos_clubes, wishlist, notas_rapidas, jogador_tags, propostas, buscas_salvas CASCADE"))
                    conn.execute(text("TRUNCATE TABLE jogadores CASCADE"))
                else:
                    tabelas = ['alertas', 'avaliacoes', 'vinculos_clubes', 'wishlist', 'notas_rapidas', 'jogador_tags', 'propostas', 'buscas_salvas', 'jogadores']
                    for t in tabelas:
                        conn.execute(text(f"DELETE FROM {t}"))
                
                conn.commit()
                print("🧹 Banco de dados limpo com sucesso!")
                return True
        except Exception as e:
            print(f"❌ Erro ao limpar dados: {e}")
            return False

    def fechar_conexao(self):
        self.engine.dispose()

def get_database():
    return ScoutingDatabase()

if __name__ == "__main__":
    db = ScoutingDatabase()
    stats = db.obter_estatisticas()
    print(f"📊 Stats: {stats}")
