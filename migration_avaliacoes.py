"""
Script de Migração: Criar tabela de avaliações
================================================

Este script cria a estrutura necessária no banco de dados PostgreSQL
para armazenar as avaliações massivas de atletas.

Executar: python migration_avaliacoes.py
"""

import os
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# SQL para criar tabela e índices (AJUSTADO PARA SCOUT PRO)
MIGRATION_SQL = """
-- Tabela de avaliações (compatível com estrutura existente)
CREATE TABLE IF NOT EXISTS avaliacoes (
    id SERIAL PRIMARY KEY,
    id_jogador INTEGER NOT NULL,
    nota_tecnico DECIMAL(2,1) NOT NULL CHECK (nota_tecnico >= 1 AND nota_tecnico <= 5),
    nota_tatico DECIMAL(2,1) NOT NULL CHECK (nota_tatico >= 1 AND nota_tatico <= 5),
    nota_fisico DECIMAL(2,1) NOT NULL CHECK (nota_fisico >= 1 AND nota_fisico <= 5),
    nota_mental DECIMAL(2,1) NOT NULL CHECK (nota_mental >= 1 AND nota_mental <= 5),
    observacoes TEXT,
    avaliador VARCHAR(100) NOT NULL,
    data_avaliacao DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador) ON DELETE CASCADE
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_avaliacoes_jogador ON avaliacoes(id_jogador);
CREATE INDEX IF NOT EXISTS idx_avaliacoes_data ON avaliacoes(data_avaliacao DESC);
CREATE INDEX IF NOT EXISTS idx_avaliacoes_avaliador ON avaliacoes(avaliador);
CREATE INDEX IF NOT EXISTS idx_avaliacoes_created ON avaliacoes(created_at DESC);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_avaliacoes_updated_at 
    BEFORE UPDATE ON avaliacoes 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- View para consultas agregadas (útil para análises)
CREATE OR REPLACE VIEW vw_avaliacoes_consolidadas AS
SELECT 
    j.id_jogador,
    j.nome,
    v.posicao,
    v.clube,
    COUNT(a.id) as total_avaliacoes,
    ROUND(AVG(a.nota_tecnico), 2) as media_tecnico,
    ROUND(AVG(a.nota_tatico), 2) as media_tatico,
    ROUND(AVG(a.nota_fisico), 2) as media_fisico,
    ROUND(AVG(a.nota_mental), 2) as media_mental,
    ROUND(AVG((a.nota_tecnico + a.nota_tatico + a.nota_fisico + a.nota_mental) / 4), 2) as media_geral,
    MAX(a.data_avaliacao) as ultima_avaliacao,
    MIN(a.data_avaliacao) as primeira_avaliacao
FROM 
    jogadores j
LEFT JOIN 
    avaliacoes a ON j.id_jogador = a.id_jogador
LEFT JOIN
    vinculos_clubes v ON j.id_jogador = v.id_jogador
GROUP BY 
    j.id_jogador, j.nome, v.posicao, v.clube;

-- View para últimas avaliações
CREATE OR REPLACE VIEW vw_ultimas_avaliacoes AS
SELECT 
    a.*,
    j.nome as jogador_nome,
    v.posicao,
    v.clube,
    ROUND((a.nota_tecnico + a.nota_tatico + a.nota_fisico + a.nota_mental) / 4, 2) as media_geral
FROM 
    avaliacoes a
INNER JOIN 
    jogadores j ON a.id_jogador = j.id_jogador
LEFT JOIN
    vinculos_clubes v ON j.id_jogador = v.id_jogador
ORDER BY 
    a.data_avaliacao DESC, a.created_at DESC;

-- Comentários nas tabelas
COMMENT ON TABLE avaliacoes IS 'Armazena avaliações multidimensionais de atletas';
COMMENT ON COLUMN avaliacoes.nota_tecnico IS 'Avaliação técnica do atleta (1-5)';
COMMENT ON COLUMN avaliacoes.nota_tatico IS 'Avaliação tática do atleta (1-5)';
COMMENT ON COLUMN avaliacoes.nota_fisico IS 'Avaliação física do atleta (1-5)';
COMMENT ON COLUMN avaliacoes.nota_mental IS 'Avaliação mental do atleta (1-5)';
COMMENT ON COLUMN avaliacoes.avaliador IS 'Nome do scout que realizou a avaliação';
COMMENT ON COLUMN avaliacoes.data_avaliacao IS 'Data em que a avaliação foi realizada';
"""

def executar_migracao():
    """Executa a migração do banco de dados"""
    try:
        # Conectar ao banco
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL não encontrada no .env")
        
        print("🔌 Conectando ao banco de dados...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("📦 Executando migração...")
        cursor.execute(MIGRATION_SQL)
        conn.commit()
        
        print("✅ Migração concluída com sucesso!")
        print("\n📊 Estruturas criadas:")
        print("   - Tabela: avaliacoes")
        print("   - Índices: 4 índices de performance")
        print("   - Trigger: auto-atualização de timestamps")
        print("   - Views: vw_avaliacoes_consolidadas, vw_ultimas_avaliacoes")
        
        # Verificar tabela
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = 'avaliacoes'
        """)
        
        if cursor.fetchone()[0] > 0:
            print("\n✅ Tabela 'avaliacoes' verificada com sucesso!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro na migração: {str(e)}")
        raise

def verificar_estrutura():
    """Verifica a estrutura da tabela de avaliações"""
    try:
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Listar colunas
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'avaliacoes'
            ORDER BY ordinal_position
        """)
        
        print("\n📋 Estrutura da tabela 'avaliacoes':")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"  {row[0]:<20} {row[1]:<15} NULL: {row[2]}")
        
        # Listar índices
        cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'avaliacoes'
        """)
        
        print("\n🔍 Índices:")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"  {row[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRAÇÃO: Tabela de Avaliações")
    print("=" * 60)
    
    executar_migracao()
    verificar_estrutura()
    
    print("\n" + "=" * 60)
    print("✅ Processo concluído!")
    print("=" * 60)
