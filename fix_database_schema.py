#!/usr/bin/env python3
"""
Script para corrigir o esquema do banco de dados SQLite
Remove o banco antigo e cria um novo com o esquema correto
"""

import os
import sqlite3
from datetime import datetime

def backup_database():
    """Faz backup do banco existente"""
    if os.path.exists('scouting.db'):
        backup_name = f'scouting_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        os.rename('scouting.db', backup_name)
        print(f"✅ Backup criado: {backup_name}")
        return True
    return False

def create_new_database():
    """Cria novo banco com esquema correto"""
    print("🔨 Criando novo banco de dados...")

    conn = sqlite3.connect('scouting.db')
    cursor = conn.cursor()

    # Criar tabela jogadores
    cursor.execute("""
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
    """)

    # Criar tabela vinculos_clubes
    cursor.execute("""
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
    """)

    # Criar tabela alertas
    cursor.execute("""
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
    """)

    # Criar tabela avaliacoes
    cursor.execute("""
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
    """)

    conn.commit()
    conn.close()

    print("✅ Banco de dados criado com sucesso!")

def main():
    print("=" * 70)
    print("🔧 CORREÇÃO DO ESQUEMA DO BANCO DE DADOS")
    print("=" * 70)
    print()

    # Fazer backup
    print("📦 Fazendo backup do banco atual...")
    backup_database()

    # Criar novo banco
    create_new_database()

    print()
    print("=" * 70)
    print("✅ CORREÇÃO CONCLUÍDA!")
    print("=" * 70)
    print()
    print("🔄 Próximos passos:")
    print("   1. Execute: GOOGLE_SHEET_URL='https://docs.google.com/spreadsheets/d/1jNAxJIRoZxYH1jKwPCBrd4Na1ko04EDAYaUCVGsJdIA' python corrigir_tudo.py")
    print("   2. Verifique se a importação foi bem-sucedida")
    print()

if __name__ == "__main__":
    main()
