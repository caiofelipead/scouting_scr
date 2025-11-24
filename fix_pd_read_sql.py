#!/usr/bin/env python3
"""
Corrige pd.read_sql para usar text() em PostgreSQL
"""

print("🔧 Corrigindo pd.read_sql no database.py...")

# Ler arquivo
with open('database.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('database.py.bak4', 'w', encoding='utf-8') as f:
    f.write(content)

# Substituições
replacements = [
    # Linha 358
    ('return pd.read_sql(query, self.engine)', 
     'return pd.read_sql(text(query), self.engine)'),

    # Linha 373 (a que causa erro)
    ("return pd.read_sql(query, self.engine, params={'id_jogador': id_jogador})",
     "return pd.read_sql(text(query), self.engine, params={'id_jogador': id_jogador})"),

    # Linha 390
    ('return pd.read_sql(query, self.engine)',
     'return pd.read_sql(text(query), self.engine)'),
]

corrections = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        corrections += 1
        print(f"✅ Corrigido: {old[:50]}...")

# Salvar
with open('database.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n🎉 {corrections} correções aplicadas!")
print("\n📝 Verificando:")

# Verificar
with open('database.py', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        if 'pd.read_sql' in line and i in [358, 373, 390]:
            print(f"   Linha {i}: {line.strip()}")

print("\n✅ Arquivo corrigido! Reinicie o dashboard.")
