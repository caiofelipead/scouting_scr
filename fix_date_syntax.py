#!/usr/bin/env python3
"""
Corrige sintaxe DATE() SQLite para PostgreSQL
"""

print("🔧 Corrigindo sintaxe DATE() para PostgreSQL...")

# Ler arquivo
with open('database.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('database.py.bak5', 'w', encoding='utf-8') as f:
    f.write(content)

# Query antiga (SQLite)
old_query = """contratos = conn.execute(text("""
                    SELECT COUNT(*) FROM vinculos_clubes 
                    WHERE data_fim_contrato <= DATE('now', '+6 months')
                    AND data_fim_contrato >= DATE('now')
                """)).fetchone()[0]"""

# Query nova (compatível com SQLite E PostgreSQL)
new_query = """# Compatível com SQLite e PostgreSQL
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
                    """)).fetchone()[0]"""

# Substituir
if "DATE('now', '+6 months')" in content:
    # Encontrar a query completa
    import re
    pattern = r"contratos = conn\.execute\(text\(.*?\)\)\.fetchone\(\)\[0\]"

    # Substituição manual por ser complexa
    lines = content.split('\n')
    new_lines = []
    skip_lines = 0

    for i, line in enumerate(lines):
        if skip_lines > 0:
            skip_lines -= 1
            continue

        if "contratos = conn.execute(text("""" in line and i < len(lines) - 4:
            # Verificar se é a query problemática
            if "DATE('now', '+6 months')" in lines[i+2]:
                # Adicionar nova versão
                new_lines.append("                # Compatível com SQLite e PostgreSQL")
                new_lines.append("                if self.db_type == 'postgresql':")
                new_lines.append("                    contratos = conn.execute(text("""")
                new_lines.append("                        SELECT COUNT(*) FROM vinculos_clubes ")
                new_lines.append("                        WHERE data_fim_contrato <= CURRENT_DATE + INTERVAL '6 months'")
                new_lines.append("                        AND data_fim_contrato >= CURRENT_DATE")
                new_lines.append("                    """)).fetchone()[0]")
                new_lines.append("                else:")
                new_lines.append("                    contratos = conn.execute(text("""")
                new_lines.append("                        SELECT COUNT(*) FROM vinculos_clubes ")
                new_lines.append("                        WHERE data_fim_contrato <= DATE('now', '+6 months')")
                new_lines.append("                        AND data_fim_contrato >= DATE('now')")
                new_lines.append("                    """)).fetchone()[0]")
                skip_lines = 4  # Pular as 4 linhas antigas
                print("✅ Query de contratos corrigida para PostgreSQL!")
                continue

        new_lines.append(line)

    content = '\n'.join(new_lines)

    # Salvar
    with open('database.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n🎉 Correção aplicada com sucesso!")
else:
    print("\n⚠️  Query já foi corrigida ou não encontrada")

print("\n✅ Arquivo atualizado! Reinicie o dashboard.")
