#!/usr/bin/env python3
"""
Script de Migração: Criar Tabelas do Scout Pro v3.0
Cria as tabelas faltantes: wishlist, tags, jogador_tags, notas_rapidas, buscas_salvas

USO:
  python scripts/criar_tabelas_v3.py
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Adiciona o diretório raiz ao path para importar database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def criar_tabelas_v3():
    """Cria todas as tabelas do Scout Pro v3.0 no PostgreSQL"""
    
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ Erro: DATABASE_URL não encontrado no .env")
        print("💡 Este script precisa rodar conectado ao PostgreSQL do Railway")
        return False
    
    # Fix para Railway: postgres:// → postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print("🔵 Conectando ao PostgreSQL (Railway)...")
    
    try:
        engine = create_engine(
            database_url,
            poolclass=NullPool,
            connect_args={
                "connect_timeout": 10,
                "options": "-c timezone=utc"
            },
            pool_pre_ping=True
        )
        
        print("✅ Conectado ao PostgreSQL!\n")
        
        # SQL para criar todas as tabelas v3.0
        tabelas_sql = [
            # 1. TABELA TAGS
            (
                "tags",
                """
                CREATE TABLE IF NOT EXISTS tags (
                    id_tag SERIAL PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL UNIQUE,
                    cor VARCHAR(20) DEFAULT '#3b82f6',
                    descricao TEXT,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            ),
            
            # 2. TABELA JOGADOR_TAGS (relacionamento)
            (
                "jogador_tags",
                """
                CREATE TABLE IF NOT EXISTS jogador_tags (
                    id SERIAL PRIMARY KEY,
                    id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
                    id_tag INTEGER REFERENCES tags(id_tag) ON DELETE CASCADE,
                    adicionado_por VARCHAR(255),
                    adicionado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(id_jogador, id_tag)
                )
                """
            ),
            
            # 3. TABELA WISHLIST
            (
                "wishlist",
                """
                CREATE TABLE IF NOT EXISTS wishlist (
                    id SERIAL PRIMARY KEY,
                    id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE UNIQUE,
                    prioridade VARCHAR(20) DEFAULT 'media' CHECK (prioridade IN ('alta', 'media', 'baixa')),
                    observacao TEXT,
                    adicionado_por VARCHAR(255),
                    adicionado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            ),
            
            # 4. TABELA NOTAS_RAPIDAS
            (
                "notas_rapidas",
                """
                CREATE TABLE IF NOT EXISTS notas_rapidas (
                    id_nota SERIAL PRIMARY KEY,
                    id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
                    texto TEXT NOT NULL,
                    autor VARCHAR(255),
                    tipo VARCHAR(50) DEFAULT 'observacao',
                    data_nota TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            ),
            
            # 5. TABELA BUSCAS_SALVAS
            (
                "buscas_salvas",
                """
                CREATE TABLE IF NOT EXISTS buscas_salvas (
                    id_busca SERIAL PRIMARY KEY,
                    nome_busca VARCHAR(255) NOT NULL,
                    filtros JSONB NOT NULL,
                    criado_por VARCHAR(255),
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usado_em TIMESTAMP
                )
                """
            )
        ]
        
        # Criação das Views
        views_sql = [
            # VIEW: Benchmark por Posição
            (
                "vw_benchmark_posicoes",
                """
                CREATE OR REPLACE VIEW vw_benchmark_posicoes AS
                SELECT 
                    v.posicao,
                    COUNT(DISTINCT a.id_jogador) as total_jogadores,
                    ROUND(AVG(a.nota_tatico), 2) as media_tatico,
                    ROUND(AVG(a.nota_tecnico), 2) as media_tecnico,
                    ROUND(AVG(a.nota_fisico), 2) as media_fisico,
                    ROUND(AVG(a.nota_mental), 2) as media_mental,
                    ROUND(AVG(a.nota_potencial), 2) as media_potencial,
                    ROUND(AVG((a.nota_tatico + a.nota_tecnico + a.nota_fisico + a.nota_mental) / 4.0), 2) as media_geral
                FROM avaliacoes a
                INNER JOIN jogadores j ON a.id_jogador = j.id_jogador
                INNER JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
                WHERE a.data_avaliacao >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY v.posicao
                ORDER BY v.posicao
                """
            ),
            
            # VIEW: Alertas Inteligentes
            (
                "vw_alertas_inteligentes",
                """
                CREATE OR REPLACE VIEW vw_alertas_inteligentes AS
                SELECT 
                    'Contrato Vencendo' as tipo_alerta,
                    j.id_jogador,
                    j.nome,
                    v.clube,
                    v.posicao,
                    v.data_fim_contrato,
                    CASE 
                        WHEN v.data_fim_contrato <= CURRENT_DATE + INTERVAL '3 months' THEN 'alta'
                        WHEN v.data_fim_contrato <= CURRENT_DATE + INTERVAL '6 months' THEN 'media'
                        ELSE 'baixa'
                    END as prioridade,
                    'Contrato termina em ' || TO_CHAR(v.data_fim_contrato, 'DD/MM/YYYY') as descricao
                FROM vinculos_clubes v
                INNER JOIN jogadores j ON v.id_jogador = j.id_jogador
                WHERE v.data_fim_contrato BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '12 months'
                
                UNION ALL
                
                SELECT 
                    'Jovem Promessa' as tipo_alerta,
                    j.id_jogador,
                    j.nome,
                    v.clube,
                    v.posicao,
                    NULL as data_fim_contrato,
                    'media' as prioridade,
                    'Jogador com menos de 21 anos' as descricao
                FROM jogadores j
                INNER JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
                WHERE j.idade_atual <= 21
                
                ORDER BY prioridade, nome
                """
            )
        ]
        
        # Executar criação de tabelas
        print("📋 Criando tabelas do Scout Pro v3.0...\n")
        
        with engine.connect() as conn:
            for nome_tabela, sql in tabelas_sql:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"   ✅ Tabela '{nome_tabela}' criada/verificada")
                except Exception as e:
                    print(f"   ❌ Erro ao criar tabela '{nome_tabela}': {e}")
                    return False
            
            print("\n📊 Criando views...\n")
            
            # Executar criação de views
            for nome_view, sql in views_sql:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"   ✅ View '{nome_view}' criada/atualizada")
                except Exception as e:
                    print(f"   ⚠️  Aviso ao criar view '{nome_view}': {e}")
            
            # Inserir tags padrão
            print("\n🏷️  Inserindo tags padrão...\n")
            
            tags_padrao = [
                ('Prioridade', '#ef4444', 'Jogador de alta prioridade'),
                ('Monitorar', '#f59e0b', 'Jogador para monitoramento'),
                ('Promessa', '#10b981', 'Jovem promessa'),
                ('Veterano', '#6366f1', 'Jogador experiente'),
                ('Lesionado', '#ec4899', 'Jogador com histórico de lesões'),
                ('Indisponível', '#64748b', 'Jogador indisponível temporariamente')
            ]
            
            for nome, cor, descricao in tags_padrao:
                try:
                    query = """
                    INSERT INTO tags (nome, cor, descricao)
                    VALUES (:nome, :cor, :descricao)
                    ON CONFLICT (nome) DO NOTHING
                    """
                    conn.execute(text(query), {'nome': nome, 'cor': cor, 'descricao': descricao})
                    conn.commit()
                    print(f"   ✅ Tag '{nome}' inserida")
                except Exception as e:
                    print(f"   ⚠️  Tag '{nome}' já existe ou erro: {e}")
        
        engine.dispose()
        
        print("\n" + "="*60)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("\n📊 Tabelas criadas:")
        print("   • tags")
        print("   • jogador_tags")
        print("   • wishlist")
        print("   • notas_rapidas")
        print("   • buscas_salvas")
        print("\n📈 Views criadas:")
        print("   • vw_benchmark_posicoes")
        print("   • vw_alertas_inteligentes")
        print("\n🏷️  Tags padrão inseridas: 6")
        print("\n💡 Agora você pode usar todas as funcionalidades do Scout Pro v3.0!")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro na migração: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🚀 MIGRAÇÃO SCOUT PRO V3.0")
    print("="*60)
    print("\nEste script criará as seguintes tabelas no PostgreSQL:")
    print("  - tags")
    print("  - jogador_tags")
    print("  - wishlist")
    print("  - notas_rapidas")
    print("  - buscas_salvas")
    print("\nE as seguintes views:")
    print("  - vw_benchmark_posicoes")
    print("  - vw_alertas_inteligentes")
    print("\n" + "="*60 + "\n")
    
    resposta = input("Deseja continuar? (s/n): ")
    
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        sucesso = criar_tabelas_v3()
        sys.exit(0 if sucesso else 1)
    else:
        print("\n❌ Migração cancelada.")
        sys.exit(1)
