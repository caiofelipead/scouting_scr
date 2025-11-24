#!/usr/bin/env python3
import re

print("🔧 Corrigindo sintaxe DATE() para PostgreSQL...")

# Ler arquivo
with open('database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Backup
with open('database.py.bak5', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Encontrar e substituir a query problemática
new_lines = []
i = 0
corrected = False

while i < len(lines):
    line = lines[i]

    # Procurar pela linha que inicia a query problemática
    if 'contratos = conn.execute(text(' in line and i + 4 < len(lines):
        # Verificar se é a query com DATE('now')
        if "DATE('now', '+6 months')" in lines[i+2]:
            # Substituir pelas versões compatíveis
            indent = ' ' * 16
            new_lines.append(indent + "# Compatível com SQLite e PostgreSQL\n")
            new_lines.append(indent + "if self.db_type == 'postgresql':\n")
            new_lines.append(indent + "    contratos = conn.execute(text(\"\"\"\n")
            new_lines.append(indent + "        SELECT COUNT(*) FROM vinculos_clubes \n")
            new_lines.append(indent + "        WHERE data_fim_contrato <= CURRENT_DATE + INTERVAL '6 months'\n")
            new_lines.append(indent + "        AND data_fim_contrato >= CURRENT_DATE\n")
            new_lines.append(indent + "    \"\"\")).fetchone()[0]\n")
            new_lines.append(indent + "else:\n")
            new_lines.append(indent + "    contratos = conn.execute(text(\"\"\"\n")
            new_lines.append(indent + "        SELECT COUNT(*) FROM vinculos_clubes \n")
            new_lines.append(indent + "        WHERE data_fim_contrato <= DATE('now', '+6 months')\n")
            new_lines.append(indent + "        AND data_fim_contrato >= DATE('now')\n")
            new_lines.append(indent + "    \"\"\")).fetchone()[0]\n")

            # Pular as 5 linhas antigas (a query completa)
            i += 5
            corrected = True
            print("✅ Query de contratos vencendo corrigida!")
            continue

    new_lines.append(line)
    i += 1

if corrected:
    # Salvar
    with open('database.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("\n🎉 Correção aplicada com sucesso!")
    print("\n📝 Verificando a correção:")

    # Mostrar as linhas corrigidas
    with open('database.py', 'r') as f:
        content = f.read()
        if "CURRENT_DATE + INTERVAL '6 months'" in content:
            print("   ✅ Sintaxe PostgreSQL encontrada")
        if "DATE('now', '+6 months')" in content:
            print("   ✅ Sintaxe SQLite preservada (fallback)")
else:
    print("\n⚠️  Query não encontrada ou já corrigida")

print("\n✅ Pronto! Reinicie o dashboard.")
