#!/usr/bin/env python3
# Patch para adicionar load_dotenv ao database.py

print("🔧 Adicionando load_dotenv ao database.py...")

# Ler o arquivo
with open('database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Verificar se já tem load_dotenv
if any('load_dotenv' in line for line in lines):
    print("⚠️  load_dotenv já existe no arquivo!")
    exit(0)

# Encontrar a linha "import os" e adicionar depois
new_lines = []
dotenv_added = False

for i, line in enumerate(lines):
    new_lines.append(line)

    # Adicionar após "import os"
    if line.strip() == 'import os' and not dotenv_added:
        new_lines.append('from dotenv import load_dotenv\n')
        dotenv_added = True

# Se não adicionou ainda, adicionar antes da classe
if not dotenv_added:
    for i, line in enumerate(new_lines):
        if 'class ScoutingDatabase' in line:
            new_lines.insert(i, '\nfrom dotenv import load_dotenv\n')
            new_lines.insert(i+1, 'load_dotenv()\n\n')
            break

# Adicionar load_dotenv() após os imports, antes da classe
for i, line in enumerate(new_lines):
    if 'class ScoutingDatabase' in line:
        # Verificar se já não tem load_dotenv() antes
        has_call = any('load_dotenv()' in new_lines[j] for j in range(max(0, i-5), i))
        if not has_call:
            new_lines.insert(i, '\n# Carregar variáveis de ambiente do .env\n')
            new_lines.insert(i+1, 'load_dotenv()\n\n')
        break

# Escrever de volta
with open('database.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ load_dotenv adicionado com sucesso!")
print("\n📝 Verificando as primeiras linhas:")

with open('database.py', 'r') as f:
    for i, line in enumerate(f):
        if i < 20:
            print(line, end='')
        else:
            break
