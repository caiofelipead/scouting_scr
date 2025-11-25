"""
Sistema de Banco de Dados para Scout Pro v3.0 - OTIMIZADO
Suporta SQLite (desenvolvimento) e PostgreSQL (produção/Railway)
"""

import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import numpy as np
import streamlit as st

load_dotenv()

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
                pool_pre_ping=True
            )
            self.db_type = 'postgresql'
            print("✅ Conectado ao PostgreSQL com sucesso!")
        else:
            print("🟢 Usando SQLite local...")
            self.engine = create_engine('sqlite:///scouting.db')
            self.db_type = 'sqlite'
            print("✅ Conectado ao SQLite com sucesso!")
        
        self.criar_tabelas()
    
    def _safe_int(self, value):
        """Converte numpy int64/int32 para int nativo Python"""
        if isinstance(value, (np.int64, np.int32, np.int16)):
            return int(value)
        return value

    def criar_tabela_propostas(self):
        """Cria ou atualiza a tabela propostas com todas as colunas necessárias"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS propostas (
                        id_proposta SERIAL PRIMARY KEY,
                        id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
                        valor_proposta NUMERIC(12, 2),
                        moeda VARCHAR(10) DEFAULT 'BRL',
                        tipo_transferencia VARCHAR(50) DEFAULT 'Definitiva',
                        clube_interessado VARCHAR(255),
                        data_proposta DATE DEFAULT CURRENT_DATE,
                        status VARCHAR(50) DEFAULT 'Em análise',
                        observacoes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao criar tabela propostas: {e}")
            return False
        
    def criar_tabelas(self):
        """Cria todas as tabelas e views (v3.0) - Compatível com SQLite e PostgreSQL"""
        
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
            )"""
        ]

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
            a.id_jogador,
            j.nome,
            v.clube,
            a.tipo_alerta,
            a.descricao,
            a.prioridade,
            a.data_criacao
        FROM alertas a
        JOIN jogadores j ON a.id_jogador = j.id_jogador
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        WHERE a.ativo = 1 OR a.ativo = TRUE
        
        UNION ALL
        
        SELECT 
            j.id_jogador,
            j.nome,
            v.clube,
            'Contrato' as tipo_alerta,
            'Contrato expira em menos de 6 meses' as descricao,
            'alta' as prioridade,
            v.data_atualizacao as data_criacao
        FROM vinculos_clubes v
        JOIN jogadores j ON v.id_jogador = j.id_jogador
        WHERE {condicao_data}
        """

        try:
            with self.engine.connect() as conn:
                for sql in commands:
                    conn.execute(text(sql))
                
                try:
                    conn.execute(text("DROP VIEW IF EXISTS vw_benchmark_posicoes"))
                    conn.execute(text(view_benchmark))
                except Exception as ev:
                    print(f"⚠️ Aviso View Benchmark: {ev}")

                try:
                    conn.execute(text("DROP VIEW IF EXISTS vw_alertas_inteligentes"))
                    conn.execute(text(view_alertas_inteligentes))
                except Exception as ev:
                    print(f"⚠️ Aviso View Alertas: {ev}")

                conn.commit()
                print(f"✅ Estrutura do banco de dados ({self.db_type}) atualizada com sucesso (V3.0)!")
        except Exception as e:
            print(f"❌ Erro crítico ao criar tabelas: {e}")

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
        """Insere ou atualiza um jogador no banco."""
        try:
            id_jogador = None
            tm_id = dados_jogador.get('transfermarkt_id')
            nome = dados_jogador.get('nome')
            
            if tm_id:
                id_jogador = self.buscar_jogador_por_tm_id(tm_id)
            
            if not id_jogador and nome:
                query_check_nome = "SELECT id_jogador FROM jogadores WHERE nome = :nome"
                with self.engine.connect() as conn:
                    result = conn.execute(text(query_check_nome), {"nome": nome})
                    row = result.fetchone()
                    if row:
                        id_jogador = row[0]
            
            with self.engine.connect() as conn:
                if id_jogador:
                    query_update = """
                    UPDATE jogadores SET
                        nome = :nome,
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

    def buscar_jogador_por_tm_id(self, tm_id: str) -> Optional[int]:
        if not tm_id:
            return None
            
        query = "SELECT id_jogador FROM jogadores WHERE transfermarkt_id = :tm_id"
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"tm_id": tm_id})
                row = result.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"❌ Erro ao buscar jogador por TM ID: {e}")
            return None

    def inserir_alerta(self, id_jogador: int, tipo_alerta: str, descricao: str, prioridade: str = 'média') -> bool:
        id_jogador = self._safe_int(id_jogador)
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
                conn.execute(text(query), {
                    'id_jogador': id_jogador,
                    'data_avaliacao': dados_avaliacao['data_avaliacao'],
                    'nota_potencial': dados_avaliacao.get('nota_potencial'),
                    'nota_tatico': dados_avaliacao.get('nota_tatico'),
                    'nota_tecnico': dados_avaliacao.get('nota_tecnico'),
                    'nota_fisico': dados_avaliacao.get('nota_fisico'),
                    'nota_mental': dados_avaliacao.get('nota_mental'),
                    'observacoes': dados_avaliacao.get('observacoes'),
                    'avaliador': dados_avaliacao.get('avaliador')
                })
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Erro ao inserir avaliação: {e}")
            return False

    def buscar_todos_jogadores(self) -> pd.DataFrame:
        query = """
        SELECT 
            j.id_jogador, j.nome, j.nacionalidade, j.ano_nascimento, j.idade_atual, j.altura, j.pe_dominante, j.transfermarkt_id,
            v.clube, v.liga_clube, v.posicao, v.data_fim_contrato, v.status_contrato
        FROM jogadores j
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        ORDER BY j.nome
        """
        try:
            return pd.read_sql(text(query), self.engine)
        except Exception as e:
            print(f"❌ Erro ao buscar jogadores: {e}")
            return pd.DataFrame()

    def buscar_avaliacoes_jogador(self, id_jogador: int) -> pd.DataFrame:
        id_jogador = self._safe_int(id_jogador)
        query = """
        SELECT 
            id_avaliacao, data_avaliacao, nota_potencial, nota_tatico, nota_tecnico,
            nota_fisico, nota_mental, observacoes, avaliador
        FROM avaliacoes 
        WHERE id_jogador = :id_jogador
        ORDER BY data_avaliacao DESC
        """
        try:
            return pd.read_sql(text(query), self.engine, params={'id_jogador': id_jogador})
        except Exception as e:
            print(f"❌ Erro ao buscar avaliações: {e}")
            return pd.DataFrame()

    def buscar_alertas_ativos(self) -> pd.DataFrame:
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
            return pd.read_sql(text(query), self.engine)
        except Exception as e:
            print(f"❌ Erro ao buscar alertas: {e}")
            return pd.DataFrame()

    def obter_estatisticas(self) -> dict:
        try:
            with self.engine.connect() as conn:
                total_jogadores = conn.execute(text("SELECT COUNT(*) FROM jogadores")).fetchone()[0]
                
                if self.db_type == 'postgresql':
                    alertas = conn.execute(text("SELECT COUNT(*) FROM alertas WHERE ativo = TRUE")).fetchone()[0]
                else:
                    alertas = conn.execute(text("SELECT COUNT(*) FROM alertas WHERE ativo = 1")).fetchone()[0]
                
                if self.db_type == 'postgresql':
                    contratos = conn.execute(text("""
                        SELECT COUNT(*) FROM vinculos_clubes 
                        WHERE data_fim_contrato <= CURRENT_DATE + INTERVAL '6 months'
                        AND data_fim_contrato >= CURRENT_DATE
                    """)).fetchone()[0]
                else:
                    contratos = conn.execute(text("""
                        SELECT COUNT(*) FROM vinculos_clubes 
                        WHERE data_fim_contrato <= DATE('now', '+6 months')
                        AND data_fim_contrato >= DATE('now')
                    """)).fetchone()[0]
                
                vinculos = conn.execute(text("SELECT COUNT(*) FROM vinculos_clubes")).fetchone()[0]
                
                return {
                    'total_jogadores': total_jogadores,
                    'alertas_ativos': alertas,
                    'contratos_vencendo': contratos,
                    'total_vinculos_ativos': vinculos
                }
        except Exception:
            return {'total_jogadores': 0, 'alertas_ativos': 0, 'contratos_vencendo': 0, 'total_vinculos_ativos': 0}

    def connect(self):
        return self.engine.connect()
        
    def fechar_conexao(self):
        try:
            self.engine.dispose()
            print("✅ Conexão fechada.")
        except:
            pass
            
    def verificar_saude_conexao(self):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except:
            return False
            
    def limpar_dados(self):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM avaliacoes"))
                conn.execute(text("DELETE FROM alertas"))
                conn.execute(text("DELETE FROM vinculos_clubes"))
                conn.execute(text("DELETE FROM jogadores"))
                conn.commit()
            return True
        except:
            return False

    def get_estatisticas_gerais(self):
        return self.obter_estatisticas()

    def get_jogadores_com_vinculos(self):
        return self.buscar_todos_jogadores()

    def get_avaliacoes_jogador(self, id_jogador):
        id_jogador = self._safe_int(id_jogador)
        return self.buscar_avaliacoes_jogador(id_jogador)

    def get_alertas_ativos(self):
        return self.buscar_alertas_ativos()

    def get_ultima_avaliacao(self, id_jogador):
        id_jogador = self._safe_int(id_jogador)
        df = self.buscar_avaliacoes_jogador(id_jogador)
        if not df.empty:
            return df.head(1)
        return pd.DataFrame()

    def salvar_avaliacao(self, **kwargs):
        id_jogador = kwargs.pop('id_jogador', None)
        if id_jogador:
            return self.inserir_avaliacao(id_jogador, kwargs)
        return False

    def criar_tabela_avaliacoes(self):
        pass

    def get_dados_google_sheets(self):
        try:
            from google_sheets_sync_streamlit import GoogleSheetsSync
            sync = GoogleSheetsSync()
            sync.conectar_planilha()
            return sync.ler_dados_planilha()
        except ImportError:
            print("⚠️ Módulo google_sheets_sync_streamlit não encontrado.")
            return None
        except Exception as e:
            print(f"❌ Erro no sync: {e}")
            return None

    def importar_dados_planilha(self, df):
        if df is None or df.empty:
            return False
        
        try:
            from google_sheets_sync_streamlit import GoogleSheetsSync
            sync = GoogleSheetsSync()
            
            sucesso = 0
            for _, row in df.iterrows():
                tm_id = sync._extrair_tm_id(row.get('TM', ''))
                
                dados_jogador = {
                    'nome': str(row.get('Nome', '')).strip(),
                    'nacionalidade': str(row.get('Nacionalidade', '')).strip() or None,
                    'ano_nascimento': sync._converter_int(row.get('Ano')),
                    'idade_atual': sync._converter_int(row.get('Idade')),
                    'altura': sync._converter_altura(row.get('Altura')),
                    'pe_dominante': str(row.get('Pé dominante', '')).strip() or None,
                    'transfermarkt_id': tm_id
                }
                
                id_jogador = self.inserir_jogador(dados_jogador)
                
                if id_jogador:
                    dados_vinculo = {
                        'clube': str(row.get('Clube', '')).strip() or None,
                        'liga_clube': str(row.get('Liga do Clube', '')).strip() or None,
                        'posicao': str(row.get('Posição', '')).strip(),
                        'data_fim_contrato': sync._converter_data(row.get('Fim de Contrato')),
                        'status_contrato': sync._calcular_status_contrato(row.get('Fim de Contrato'))
                    }
                    self.inserir_vinculo(id_jogador, dados_vinculo)
                    sucesso += 1
            
            print(f"✅ Importação concluída: {sucesso} registros processados.")
            return True
            
        except Exception as e:
            print(f"❌ Erro na importação manual: {e}")
            return False

    @st.cache_data(ttl=300, show_spinner=False)
    def get_all_tags(_self):
        """Busca todas as tags COM CACHE"""
        query = "SELECT * FROM tags ORDER BY nome"
        try:
            return pd.read_sql(text(query), _self.engine)
        except Exception as e:
            print(f"❌ Erro ao buscar tags: {e}")
            return pd.DataFrame()

    def get_jogador_tags(self, id_jogador):
        id_jogador = self._safe_int(id_jogador)
        query = """
        SELECT t.id_tag, t.nome, t.cor, t.descricao, jt.adicionado_em
        FROM jogador_tags jt
        INNER JOIN tags t ON jt.id_tag = t.id_tag
        WHERE jt.id_jogador = :id_jogador
        ORDER BY jt.adicionado_em DESC
        """
        try:
            return pd.read_sql(text(query), self.engine, params={'id_jogador': id_jogador})
        except Exception as e:
            print(f"❌ Erro ao buscar tags do jogador: {e}")
            return pd.DataFrame()

    def adicionar_tag_jogador(self, id_jogador, id_tag, adicionado_por=None):
        id_jogador = self._safe_int(id_jogador)
        id_tag = self._safe_int(id_tag)
        try:
            with self.engine.connect() as conn:
                query = """
                INSERT INTO jogador_tags (id_jogador, id_tag, adicionado_por)
                VALUES (:id_jogador, :id_tag, :adicionado_por)
                """
                conn.execute(text(query), {
                    'id_jogador': id_jogador,
                    'id_tag': id_tag,
                    'adicionado_por': adicionado_por
                })
                conn.commit()
                st.cache_data.clear()
                return True
        except Exception as e:
            print(f"❌ Erro ao adicionar tag: {e}")
            return False

    def remover_tag_jogador(self, id_jogador, id_tag):
        id_jogador = self._safe_int(id_jogador)
        id_tag = self._safe_int(id_tag)
        try:
            with self.engine.connect() as conn:
                query = "DELETE FROM jogador_tags WHERE id_jogador = :id_jogador AND id_tag = :id_tag"
                conn.execute(text(query), {'id_jogador': id_jogador, 'id_tag': id_tag})
                conn.commit()
                st.cache_data.clear()
                return True
        except Exception as e:
            print(f"❌ Erro ao remover tag: {e}")
            return False

    def get_jogadores_por_tag(self, id_tag):
        id_tag = self._safe_int(id_tag)
        query = """
        SELECT 
            j.*,
            v.clube,
            v.posicao,
            v.liga_clube,
            jt.adicionado_em as tag_adicionado_em
        FROM jogador_tags jt
        INNER JOIN jogadores j ON jt.id_jogador = j.id_jogador
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        WHERE jt.id_tag = :id_tag
        ORDER BY jt.adicionado_em DESC
        """
        try:
            return pd.read_sql(text(query), self.engine, params={'id_tag': id_tag})
        except Exception as e:
            print(f"❌ Erro ao buscar jogadores por tag: {e}")
            return pd.DataFrame()

    def adicionar_wishlist(self, id_jogador, prioridade='media', observacao=None, adicionado_por=None):
        id_jogador = self._safe_int(id_jogador)
        try:
            with self.engine.connect() as conn:
                check_query = "SELECT id FROM wishlist WHERE id_jogador = :id_jogador"
                result = conn.execute(text(check_query), {'id_jogador': id_jogador})
                existe = result.fetchone()
                
                if existe:
                    query = """
                    UPDATE wishlist SET 
                        prioridade = :prioridade,
                        observacao = :observacao
                    WHERE id_jogador = :id_jogador
                    """
                else:
                    query = """
                    INSERT INTO wishlist (id_jogador, prioridade, observacao, adicionado_por)
                    VALUES (:id_jogador, :prioridade, :observacao, :adicionado_por)
                    """
                
                conn.execute(text(query), {
                    'id_jogador': id_jogador,
                    'prioridade': prioridade,
                    'observacao': observacao,
                    'adicionado_por': adicionado_por
                })
                conn.commit()
                st.cache_data.clear()
                return True
        except Exception as e:
            print(f"❌ Erro ao adicionar à wishlist: {e}")
            return False

    def remover_wishlist(self, id_jogador):
        id_jogador = self._safe_int(id_jogador)
        try:
            with self.engine.connect() as conn:
                query = "DELETE FROM wishlist WHERE id_jogador = :id_jogador"
                conn.execute(text(query), {'id_jogador': id_jogador})
                conn.commit()
                st.cache_data.clear()
                return True
        except Exception as e:
            print(f"❌ Erro ao remover da wishlist: {e}")
            return False

    @st.cache_data(ttl=300, show_spinner=False)
    def get_wishlist(_self, prioridade=None):
        """Busca wishlist COM CACHE"""
        if prioridade:
            query = """
            SELECT 
                j.*,
                v.clube,
                v.posicao,
                v.liga_clube,
                v.data_fim_contrato,
                w.prioridade,
                w.observacao,
                w.adicionado_em as wishlist_adicionado_em
            FROM wishlist w
            INNER JOIN jogadores j ON w.id_jogador = j.id_jogador
            LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
            WHERE w.prioridade = :prioridade
            ORDER BY w.adicionado_em DESC
            """
            try:
                return pd.read_sql(text(query), _self.engine, params={'prioridade': prioridade})
            except Exception as e:
                print(f"❌ Erro ao buscar wishlist: {e}")
                return pd.DataFrame()
        else:
            query = """
            SELECT 
                j.*,
                v.clube,
                v.posicao,
                v.liga_clube,
                v.data_fim_contrato,
                w.prioridade,
                w.observacao,
                w.adicionado_em as wishlist_adicionado_em
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
            try:
                return pd.read_sql(text(query), _self.engine)
            except Exception as e:
                print(f"❌ Erro ao buscar wishlist: {e}")
                return pd.DataFrame()

    def get_ids_wishlist(self):
        """Retorna SET com todos os IDs da wishlist (para lookup rápido)"""
        try:
            with self.engine.connect() as conn:
                query = "SELECT id_jogador FROM wishlist"
                result = conn.execute(text(query))
                ids = {row[0] for row in result.fetchall()}
                return ids
        except Exception as e:
            print(f"❌ Erro ao buscar IDs wishlist: {e}")
            return set()

    def esta_na_wishlist(self, id_jogador):
        id_jogador = self._safe_int(id_jogador)
        try:
            with self.engine.connect() as conn:
                query = "SELECT COUNT(*) FROM wishlist WHERE id_jogador = :id_jogador"
                result = conn.execute(text(query), {'id_jogador': id_jogador})
                count = result.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"❌ Erro ao verificar wishlist: {e}")
            return False

    def adicionar_nota_rapida(self, id_jogador, texto, autor=None, tipo='observacao'):
        id_jogador = self._safe_int(id_jogador)
        try:
            with self.engine.connect() as conn:
                query = """
                INSERT INTO notas_rapidas (id_jogador, texto, autor, tipo)
                VALUES (:id_jogador, :texto, :autor, :tipo)
                """
                conn.execute(text(query), {
                    'id_jogador': id_jogador,
                    'texto': texto,
                    'autor': autor,
                    'tipo': tipo
                })
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Erro ao adicionar nota: {e}")
            return False

    def get_notas_rapidas(self, id_jogador):
        id_jogador = self._safe_int(id_jogador)
        query = """
        SELECT *
        FROM notas_rapidas
        WHERE id_jogador = :id_jogador
        ORDER BY data_nota DESC
        """
        try:
            return pd.read_sql(text(query), self.engine, params={'id_jogador': id_jogador})
        except Exception as e:
            print(f"❌ Erro ao buscar notas: {e}")
            return pd.DataFrame()

    def deletar_nota_rapida(self, id_nota):
        id_nota = self._safe_int(id_nota)
        try:
            with self.engine.connect() as conn:
                query = "DELETE FROM notas_rapidas WHERE id_nota = :id_nota"
                conn.execute(text(query), {'id_nota': id_nota})
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Erro ao deletar nota: {e}")
            return False

    def get_benchmark_posicao(self, posicao):
        query = """
        SELECT * FROM vw_benchmark_posicoes
        WHERE posicao = :posicao
        """
        try:
            return pd.read_sql(text(query), self.engine, params={'posicao': posicao})
        except Exception as e:
            print(f"❌ Erro ao buscar benchmark: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=300, show_spinner=False)
    def get_all_benchmarks(_self):
        """Busca benchmarks COM CACHE"""
        query = "SELECT * FROM vw_benchmark_posicoes ORDER BY posicao"
        try:
            return pd.read_sql(text(query), _self.engine)
        except Exception as e:
            print(f"❌ Erro ao buscar benchmarks: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=300, show_spinner=False)
    def get_alertas_inteligentes(_self, tipo_alerta=None, prioridade=None):
        """Busca alertas inteligentes COM CACHE"""
        query = "SELECT * FROM vw_alertas_inteligentes WHERE 1=1"
        params = {}
        
        if tipo_alerta:
            query += " AND tipo_alerta = :tipo_alerta"
            params['tipo_alerta'] = tipo_alerta
        
        if prioridade:
            query += " AND prioridade = :prioridade"
            params['prioridade'] = prioridade
        
        query += " ORDER BY CASE prioridade WHEN 'alta' THEN 1 WHEN 'media' THEN 2 ELSE 3 END, nome"
        
        try:
            if params:
                return pd.read_sql(text(query), _self.engine, params=params)
            else:
                return pd.read_sql(text(query), _self.engine)
        except Exception as e:
            print(f"❌ Erro ao buscar alertas inteligentes: {e}")
            return pd.DataFrame()

    def busca_avancada(self, filtros):
        query = """
        SELECT DISTINCT
            j.*,
            v.clube,
            v.posicao,
            v.liga_clube,
            v.data_fim_contrato,
            v.status_contrato
        FROM jogadores j
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        LEFT JOIN jogador_tags jt ON j.id_jogador = jt.id_jogador
        WHERE 1=1
        """
        
        params = {}
        
        if filtros.get('posicoes'):
            placeholders = ', '.join([f':pos{i}' for i in range(len(filtros['posicoes']))])
            query += f" AND v.posicao IN ({placeholders})"
            for i, pos in enumerate(filtros['posicoes']):
                params[f'pos{i}'] = pos
        
        if filtros.get('nacionalidades'):
            placeholders = ', '.join([f':nac{i}' for i in range(len(filtros['nacionalidades']))])
            query += f" AND j.nacionalidade IN ({placeholders})"
            for i, nac in enumerate(filtros['nacionalidades']):
                params[f'nac{i}'] = nac
        
        if filtros.get('idade_min'):
            query += " AND j.idade_atual >= :idade_min"
            params['idade_min'] = filtros['idade_min']
        
        if filtros.get('idade_max'):
            query += " AND j.idade_atual <= :idade_max"
            params['idade_max'] = filtros['idade_max']
        
        if filtros.get('clubes'):
            placeholders = ', '.join([f':clube{i}' for i in range(len(filtros['clubes']))])
            query += f" AND v.clube IN ({placeholders})"
            for i, clube in enumerate(filtros['clubes']):
                params[f'clube{i}'] = clube
        
        if filtros.get('contrato_vencendo'):
            if self.db_type == 'postgresql':
                query += " AND v.data_fim_contrato <= CURRENT_DATE + INTERVAL '12 months'"
            else:
                query += " AND v.data_fim_contrato <= DATE('now', '+12 months')"
        
        if filtros.get('tags'):
            placeholders = ', '.join([f':tag{i}' for i in range(len(filtros['tags']))])
            query += f" AND jt.id_tag IN ({placeholders})"
            for i, tag in enumerate(filtros['tags']):
                params[f'tag{i}'] = tag
        
        query += " ORDER BY j.nome"
        
        try:
            df = pd.read_sql(text(query), self.engine, params=params if params else None)
            
            if filtros.get('media_min') and not df.empty:
                medias = []
                for _, jogador in df.iterrows():
                    media = self.calcular_media_jogador(jogador['id_jogador'])
                    medias.append(media)
                df['media_geral'] = medias
                df = df[df['media_geral'] >= filtros['media_min']]
            
            return df
        except Exception as e:
            print(f"❌ Erro na busca avançada: {e}")
            return pd.DataFrame()

    def calcular_media_jogador(self, id_jogador):
        id_jogador = self._safe_int(id_jogador)
        avals = self.get_ultima_avaliacao(id_jogador)
        if not avals.empty:
            return (
                avals['nota_tatico'].iloc[0] +
                avals['nota_tecnico'].iloc[0] +
                avals['nota_fisico'].iloc[0] +
                avals['nota_mental'].iloc[0]
            ) / 4
        return 0.0

    def salvar_busca(self, nome_busca, filtros, criado_por=None):
        import json
        try:
            with self.engine.connect() as conn:
                query = """
                INSERT INTO buscas_salvas (nome_busca, filtros, criado_por)
                VALUES (:nome_busca, :filtros, :criado_por)
                """
                conn.execute(text(query), {
                    'nome_busca': nome_busca,
                    'filtros': json.dumps(filtros),
                    'criado_por': criado_por
                })
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Erro ao salvar busca: {e}")
            return False

    def get_buscas_salvas(self):
        query = "SELECT * FROM buscas_salvas ORDER BY criado_em DESC"
        try:
            return pd.read_sql(text(query), self.engine)
        except Exception as e:
            print(f"❌ Erro ao buscar buscas salvas: {e}")
            return pd.DataFrame()

    def executar_busca_salva(self, id_busca):
        id_busca = self._safe_int(id_busca)
        import json
        try:
            with self.engine.connect() as conn:
                query = "SELECT filtros FROM buscas_salvas WHERE id_busca = :id_busca"
                result = conn.execute(text(query), {'id_busca': id_busca})
                row = result.fetchone()
                
                if row:
                    filtros = json.loads(row[0])
                    return self.busca_avancada(filtros)
                return pd.DataFrame()
        except Exception as e:
            print(f"❌ Erro ao executar busca salva: {e}")
            return pd.DataFrame()

    def execute_query(self, query_str):
        """Executa uma query SQL direta e retorna lista de dicionários"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query_str))
                rows = result.fetchall()
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"❌ Erro ao executar query: {e}")
            return []

def get_database():
    return ScoutingDatabase()

if __name__ == "__main__":
    print("🧪 Testando conexão com o banco de dados...\n")
    db = ScoutingDatabase()
    stats = db.obter_estatisticas()
    print(f"\n📊 Estatísticas:")
    print(f"   Total de jogadores: {stats['total_jogadores']}")
    
    print(f"\n🆕 Testando novas funcionalidades:")
    try:
        tags = db.get_all_tags()
        print(f"   ✅ Tags: {len(tags)} disponíveis")
    except:
        print(f"   ⚠️ Tags: Tabela ainda não criada")
    
    db.fechar_conexao()
