"""
Script de Migração: SQLite → PostgreSQL (Versão Robusta)
Migra todos os dados do scouting.db local para o PostgreSQL do Railway
Lida com a ausência de colunas opcionais como 'data_criacao'.
"""

import os
import sys
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

def conectar_sqlite():
    """Conecta ao banco SQLite local"""
    if not os.path.exists('scouting.db'):
        print("❌ Arquivo scouting.db não encontrado!")
        print("   Certifique-se de estar no diretório correto.")
        sys.exit(1)
    
    print("📂 Conectando ao SQLite local...")
    engine = create_engine('sqlite:///scouting.db')
    return engine

def conectar_postgresql():
    """Conecta ao PostgreSQL do Railway"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ Variável DATABASE_URL não encontrada!")
        print("   Configure a variável de ambiente com a URL do PostgreSQL.")
        print("   Exemplo:")
        print("   export DATABASE_URL='postgresql://user:pass@host:port/db'")
        sys.exit(1)
    
    # Fix para Railway (se a URL vier como postgres://)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print("🔵 Conectando ao PostgreSQL...")
    try:
        engine = create_engine(
            database_url,
            poolclass=NullPool,
            connect_args={
                "connect_timeout": 10,
                "options": "-c timezone=utc"
            }
        )
        return engine
    except Exception as e:
        print(f"❌ Erro ao configurar conexão PostgreSQL: {e}")
        sys.exit(1)

def criar_tabelas_postgresql(pg_engine):
    """Cria as tabelas no PostgreSQL"""
    print("\n📋 Criando estrutura de tabelas no PostgreSQL...")
    
    sqls = [
        """
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
        """,
        """
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
        """,
        """
        CREATE TABLE IF NOT EXISTS alertas (
            id_alerta SERIAL PRIMARY KEY,
            id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
            tipo_alerta VARCHAR(100) NOT NULL,
            descricao TEXT,
            prioridade VARCHAR(50),
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo BOOLEAN DEFAULT TRUE
        )
        """,
        """
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
    ]
    
    try:
        with pg_engine.connect() as conn:
            for sql in sqls:
                conn.execute(text(sql))
            conn.commit()
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        sys.exit(1)

def limpar_postgresql(pg_engine):
    """Limpa dados existentes no PostgreSQL (se houver)"""
    print("\n🧹 Limpando dados existentes no PostgreSQL...")
    
    try:
        with pg_engine.connect() as conn:
            # Ordem inversa para respeitar Foreign Keys
            conn.execute(text("DELETE FROM avaliacoes"))
            conn.execute(text("DELETE FROM alertas"))
            conn.execute(text("DELETE FROM vinculos_clubes"))
            conn.execute(text("DELETE FROM jogadores"))
            conn.commit()
        print("✅ PostgreSQL limpo!")
    except Exception as e:
        print(f"⚠️ Aviso ao limpar (pode ser normal se tabelas estiverem vazias): {e}")

def migrar_jogadores(sqlite_engine, pg_engine):
    """Migra tabela de jogadores com tratamento de erro para colunas faltantes"""
    print("\n👥 Migrando jogadores...")
    
    try:
        # Ler do SQLite
        df = pd.read_sql("SELECT * FROM jogadores", sqlite_engine)
        print(f"   📊 {len(df)} jogadores encontrados")
        
        if len(df) == 0:
            print("   ⚠️ Nenhum jogador para migrar")
            return {}
        
        # Mapear IDs antigos -> novos
        id_map = {}
        
        with pg_engine.connect() as conn:
            for _, row in df.iterrows():
                # Prepara valores com fallback se a coluna não existir no SQLite
                # Isso resolve o erro 'data_criacao'
                valores = {
                    'nome': row['nome'],
                    'nacionalidade': row.get('nacionalidade'),
                    'ano_nascimento': row.get('ano_nascimento'),
                    'idade_atual': row.get('idade_atual'),
                    'altura': row.get('altura'),
                    'pe_dominante': row.get('pe_dominante'),
                    'transfermarkt_id': row.get('transfermarkt_id'),
                    'data_criacao': row.get('data_criacao', datetime.now()),
                    'data_atualizacao': row.get('data_atualizacao', datetime.now())
                }

                query = """
                INSERT INTO jogadores 
                (nome, nacionalidade, ano_nascimento, idade_atual, altura, pe_dominante, transfermarkt_id, data_criacao, data_atualizacao)
                VALUES 
                (:nome, :nacionalidade, :ano_nascimento, :idade_atual, :altura, :pe_dominante, :transfermarkt_id, :data_criacao, :data_atualizacao)
                RETURNING id_jogador
                """
                
                result = conn.execute(text(query), valores)
                novo_id = result.fetchone()[0]
                
                # Salva o mapeamento: ID antigo -> Novo ID
                # Isso é crucial para manter os vínculos corretos
                id_antigo = row.get('id_jogador')
                if id_antigo:
                    id_map[id_antigo] = novo_id
            
            conn.commit()
        
        print(f"   ✅ {len(id_map)} jogadores migrados com sucesso!")
        return id_map
        
    except Exception as e:
        print(f"   ❌ Erro ao migrar jogadores: {e}")
        # Não sai do script, tenta continuar
        return {}

def migrar_vinculos(sqlite_engine, pg_engine, id_map):
    """Migra tabela de vínculos"""
    print("\n🔗 Migrando vínculos de clubes...")
    
    if not id_map:
        print("   ⚠️ Pular vínculos (sem mapeamento de jogadores)")
        return

    try:
        df = pd.read_sql("SELECT * FROM vinculos_clubes", sqlite_engine)
        print(f"   📊 {len(df)} vínculos encontrados")
        
        if len(df) == 0:
            print("   ⚠️ Nenhum vínculo para migrar")
            return
        
        count = 0
        with pg_engine.connect() as conn:
            for _, row in df.iterrows():
                # Usar novo ID do jogador
                id_antigo = row.get('id_jogador')
                novo_id_jogador = id_map.get(id_antigo)
                
                if not novo_id_jogador:
                    # Pode acontecer se o jogador foi deletado ou não migrado
                    continue
                
                valores = {
                    'id_jogador': novo_id_jogador,
                    'clube': row.get('clube'),
                    'liga_clube': row.get('liga_clube'),
                    'posicao': row.get('posicao', 'Desconhecido'),
                    'data_fim_contrato': row.get('data_fim_contrato'),
                    'status_contrato': row.get('status_contrato'),
                    'data_criacao': row.get('data_criacao', datetime.now()),
                    'data_atualizacao': row.get('data_atualizacao', datetime.now())
                }

                query = """
                INSERT INTO vinculos_clubes 
                (id_jogador, clube, liga_clube, posicao, data_fim_contrato, status_contrato, data_criacao, data_atualizacao)
                VALUES 
                (:id_jogador, :clube, :liga_clube, :posicao, :data_fim_contrato, :status_contrato, :data_criacao, :data_atualizacao)
                """
                
                conn.execute(text(query), valores)
                count += 1
            
            conn.commit()
        
        print(f"   ✅ {count} vínculos migrados!")
        
    except Exception as e:
        print(f"   ❌ Erro ao migrar vínculos: {e}")

def migrar_alertas(sqlite_engine, pg_engine, id_map):
    """Migra tabela de alertas"""
    print("\n🚨 Migrando alertas...")
    
    if not id_map:
        return

    try:
        # Verifica se a tabela existe no SQLite antes de ler
        # SQLite não lança erro fácil, então try/except é bom
        df = pd.read_sql("SELECT * FROM alertas", sqlite_engine)
        print(f"   📊 {len(df)} alertas encontrados")
        
        if len(df) == 0:
            return
        
        count = 0
        with pg_engine.connect() as conn:
            for _, row in df.iterrows():
                novo_id_jogador = id_map.get(row.get('id_jogador'))
                
                if not novo_id_jogador:
                    continue
                
                valores = {
                    'id_jogador': novo_id_jogador,
                    'tipo_alerta': row.get('tipo_alerta', 'Geral'),
                    'descricao': row.get('descricao'),
                    'prioridade': row.get('prioridade', 'média'),
                    'data_criacao': row.get('data_criacao', datetime.now()),
                    'ativo': bool(row.get('ativo', 1))
                }

                query = """
                INSERT INTO alertas 
                (id_jogador, tipo_alerta, descricao, prioridade, data_criacao, ativo)
                VALUES 
                (:id_jogador, :tipo_alerta, :descricao, :prioridade, :data_criacao, :ativo)
                """
                
                conn.execute(text(query), valores)
                count += 1
            
            conn.commit()
        
        print(f"   ✅ {count} alertas migrados!")
        
    except Exception as e:
        # Tabela pode não existir no SQLite antigo, não é crítico
        print(f"   ⚠️ Pular alertas (tabela não encontrada ou erro): {e}")

def migrar_avaliacoes(sqlite_engine, pg_engine, id_map):
    """Migra tabela de avaliações"""
    print("\n⭐ Migrando avaliações...")
    
    if not id_map:
        return

    try:
        df = pd.read_sql("SELECT * FROM avaliacoes", sqlite_engine)
        print(f"   📊 {len(df)} avaliações encontradas")
        
        if len(df) == 0:
            return
        
        count = 0
        with pg_engine.connect() as conn:
            for _, row in df.iterrows():
                novo_id_jogador = id_map.get(row.get('id_jogador'))
                
                if not novo_id_jogador:
                    continue
                
                valores = {
                    'id_jogador': novo_id_jogador,
                    'data_avaliacao': row.get('data_avaliacao'),
                    'nota_potencial': row.get('nota_potencial'),
                    'nota_tatico': row.get('nota_tatico'),
                    'nota_tecnico': row.get('nota_tecnico'),
                    'nota_fisico': row.get('nota_fisico'),
                    'nota_mental': row.get('nota_mental'),
                    'observacoes': row.get('observacoes'),
                    'avaliador': row.get('avaliador'),
                    'data_criacao': row.get('data_criacao', datetime.now())
                }

                query = """
                INSERT INTO avaliacoes 
                (id_jogador, data_avaliacao, nota_potencial, nota_tatico, nota_tecnico, 
                 nota_fisico, nota_mental, observacoes, avaliador, data_criacao)
                VALUES 
                (:id_jogador, :data_avaliacao, :nota_potencial, :nota_tatico, :nota_tecnico,
                 :nota_fisico, :nota_mental, :observacoes, :avaliador, :data_criacao)
                """
                
                conn.execute(text(query), valores)
                count += 1
            
            conn.commit()
        
        print(f"   ✅ {count} avaliações migradas!")
        
    except Exception as e:
        print(f"   ⚠️ Pular avaliações (erro ou tabela vazia): {e}")

def verificar_migracao(pg_engine):
    """Verifica se a migração foi bem-sucedida"""
    print("\n🔍 Verificando migração...")
    
    try:
        with pg_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM jogadores"))
            total_jogadores = result.fetchone()[0]
            
            result = conn.execute(text("SELECT COUNT(*) FROM vinculos_clubes"))
            total_vinculos = result.fetchone()[0]
        
        print(f"\n📊 Resumo final no PostgreSQL:")
        print(f"   👥 Jogadores: {total_jogadores}")
        print(f"   🔗 Vínculos: {total_vinculos}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")

def main():
    print("="*60)
    print("🚀 MIGRAÇÃO: SQLite → PostgreSQL")
    print("="*60)
    print()
    
    # Conectar aos bancos
    sqlite_engine = conectar_sqlite()
    pg_engine = conectar_postgresql()
    
    # Confirmar migração
    print("\n⚠️  ATENÇÃO!")
    print("Esta operação irá:")
    print("1. Limpar todos os dados existentes no PostgreSQL")
    print("2. Copiar todos os dados do SQLite local para o PostgreSQL")
    print()
    
    resposta = input("Deseja continuar? (sim/não): ").strip().lower()
    
    if resposta not in ['sim', 's', 'yes', 'y']:
        print("\n❌ Migração cancelada pelo usuário.")
        sys.exit(0)
    
    # Executar migração
    criar_tabelas_postgresql(pg_engine)
    limpar_postgresql(pg_engine)
    
    id_map = migrar_jogadores(sqlite_engine, pg_engine)
    
    # Só continua se houver jogadores migrados
    if id_map:
        migrar_vinculos(sqlite_engine, pg_engine, id_map)
        migrar_alertas(sqlite_engine, pg_engine, id_map)
        migrar_avaliacoes(sqlite_engine, pg_engine, id_map)
    
    verificar_migracao(pg_engine)
    
    print("\n" + "="*60)
    print("✅ MIGRAÇÃO CONCLUÍDA!")
    print("="*60)

if __name__ == "__main__":
    main()