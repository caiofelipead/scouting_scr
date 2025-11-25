"""
Extensão Database - Scout Pro
Suporte híbrido corrigido: nomes de tabela conforme banco
"""

import os
import pandas as pd
from datetime import datetime

USE_POSTGRESQL = bool(os.getenv('DATABASE_URL'))

if USE_POSTGRESQL:
    import psycopg2
    from sqlalchemy import create_engine, text
else:
    import sqlite3

class ScoutingDatabaseExtended:
    def __init__(self):
        self.use_postgresql = USE_POSTGRESQL
        if self.use_postgresql:
            self.database_url = os.getenv('DATABASE_URL')
            if self.database_url.startswith("postgres://"):
                self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        else:
            if os.getenv("RAILWAY_VOLUME_MOUNT_PATH"):
                self.db_path = os.path.join(os.getenv("RAILWAY_VOLUME_MOUNT_PATH"), "scouting.db")
            else:
                self.db_path = "scouting.db"
        self._criar_tabelas_estendidas()

    def get_connection(self):
        if self.use_postgresql:
            return psycopg2.connect(self.database_url)
        else:
            return sqlite3.connect(self.db_path)

    def _criar_tabelas_estendidas(self):
        if self.use_postgresql:
            self._criar_tabelas_postgresql()
        else:
            self._criar_tabelas_sqlite()

    def _tabela_vinculos(self):
        return "vinculos_clubes" if self.use_postgresql else "vinculos"

    def _criar_tabelas_postgresql(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            colunas = [
                "ADD COLUMN IF NOT EXISTS salario_mensal_min DECIMAL(12,2)",
                "ADD COLUMN IF NOT EXISTS salario_mensal_max DECIMAL(12,2)"
            ]
            for coluna in colunas:
                try:
                    cursor.execute(f"ALTER TABLE jogadores {coluna}")
                except Exception:
                    pass
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS propostas (
                    id_proposta SERIAL PRIMARY KEY,
                    id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
                    clube_interessado VARCHAR(100),
                    valor_proposta DECIMAL(12,2),
                    moeda VARCHAR(10) DEFAULT 'BRL',
                    status VARCHAR(20) CHECK (status IN ('Em análise', 'Aceita', 'Recusada')),
                    data_proposta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observacoes TEXT,
                    responsavel VARCHAR(255)
                )
            """)
            conn.commit()
        except Exception as e:
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def _criar_tabelas_sqlite(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            colunas = [
                "ADD COLUMN salario_mensal_min REAL",
                "ADD COLUMN salario_mensal_max REAL"
            ]
            for coluna in colunas:
                try:
                    cursor.execute(f"ALTER TABLE jogadores {coluna}")
                except Exception:
                    pass
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
            conn.commit()
        except Exception as e:
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def buscar_por_faixa_salarial(self, salario_min=None, salario_max=None, moeda='BRL'):
        conn = self.get_connection()
        try:
            vinculos = self._tabela_vinculos()
            query = f"""
                SELECT 
                    j.*, 
                    v.clube, 
                    v.liga_clube as liga, 
                    v.posicao
                FROM jogadores j
                LEFT JOIN {vinculos} v ON j.id_jogador = v.id_jogador
                WHERE j.moeda_salario = %s
            """ if self.use_postgresql else f"""
                SELECT 
                    j.*, 
                    v.clube, 
                    v.liga_clube as liga, 
                    v.posicao 
                FROM jogadores j
                LEFT JOIN {vinculos} v ON j.id_jogador = v.id_jogador
                WHERE j.moeda_salario = ?
            """
            params = [moeda]
            if salario_min is not None:
                query += " AND j.salario_mensal_max >= %s" if self.use_postgresql else " AND j.salario_mensal_max >= ?"
                params.append(salario_min)
            if salario_max is not None:
                query += " AND j.salario_mensal_min <= %s" if self.use_postgresql else " AND j.salario_mensal_min <= ?"
                params.append(salario_max)
            query += " ORDER BY j.salario_mensal_max DESC"
            df = pd.read_sql_query(query, conn, params=params)
            return df
        finally:
            conn.close()

