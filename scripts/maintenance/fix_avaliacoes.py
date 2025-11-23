"""
Script para recriar a tabela de avaliações corretamente
"""

import os
import sqlite3


def fix_avaliacoes_table():
    db_path = "scouting.db"

    if not os.path.exists(db_path):
        print(f"❌ Banco de dados {db_path} não encontrado.")
        return

    print("🔧 Corrigindo tabela de avaliações...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Fazer backup dos dados existentes (se houver)
    try:
        cursor.execute("SELECT * FROM avaliacoes")
        backup_data = cursor.fetchall()
        print(f"  📦 Backup de {len(backup_data)} avaliações encontradas")
    except:
        backup_data = []
        print("  ℹ️ Nenhuma avaliação existente para backup")

    # 2. Dropar tabela antiga
    try:
        cursor.execute("DROP TABLE IF EXISTS avaliacoes")
        print("  🗑️ Tabela antiga removida")
    except Exception as e:
        print(f"  ⚠️ Erro ao remover tabela: {e}")

    # 3. Criar nova tabela com estrutura correta
    cursor.execute(
        """
    CREATE TABLE avaliacoes (
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
    """
    )

    conn.commit()
    print("  ✅ Tabela de avaliações recriada com sucesso!")

    # 4. Verificar estrutura
    cursor.execute("PRAGMA table_info(avaliacoes)")
    colunas = cursor.fetchall()
    print("\n  📊 Estrutura da tabela avaliacoes:")
    for col in colunas:
        print(f"    ✓ {col[1]} ({col[2]})")

    conn.close()
    print("\n✅ Correção concluída! Execute o dashboard novamente.")


if __name__ == "__main__":
    fix_avaliacoes_table()
