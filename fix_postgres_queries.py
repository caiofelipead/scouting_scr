#!/usr/bin/env python3
"""
Fix PostgreSQL Parameter Binding
Garante que todas as queries usem text() corretamente
"""

import re

print("🔧 Corrigindo queries PostgreSQL no database.py...")

# Ler arquivo
with open('database.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('database.py.bak3', 'w', encoding='utf-8') as f:
    f.write(content)

# Contar queries com parâmetros nomeados
queries_with_params = re.findall(r'query.*=.*"[^"]*:[a-z_]+', content, re.IGNORECASE | re.DOTALL)
print(f"\n📊 Encontradas {len(queries_with_params)} queries com parâmetros")

# Verificar se todas as execuções usam text()
issues = []

# Padrão: conn.execute(query, ...) sem text()
# Deveria ser: conn.execute(text(query), ...)
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    # Se tem execute( mas não tem text(
    if 'conn.execute(' in line and 'text(' not in line and 'query' in line:
        # Ignorar se for um comentário
        if not line.strip().startswith('#'):
            issues.append((i, line.strip()))

if issues:
    print(f"\n⚠️  {len(issues)} execuções podem estar sem text():")
    for line_num, line in issues[:5]:
        print(f"   Linha {line_num}: {line[:80]}...")
else:
    print("\n✅ Todas as execuções parecem usar text() corretamente")

# Aplicar correção automática: adicionar text() onde falta
corrections = 0
new_content = content

# Padrão: conn.execute(query_var, {params})
# Substituir por: conn.execute(text(query_var), {params})
patterns = [
    (r'conn\.execute\(([a-z_]+),', r'conn.execute(text(\1),'),
    (r'conn\.execute\(([a-z_]+)\)', r'conn.execute(text(\1))'),
]

for pattern, replacement in patterns:
    matches = re.findall(pattern, new_content)
    if matches:
        # Verificar se já não tem text(
        for match in matches:
            old = f'conn.execute({match},'
            if old in new_content and f'text({match}' not in new_content:
                new_content = re.sub(pattern, replacement, new_content)
                corrections += 1

if corrections > 0:
    print(f"\n🔄 Aplicadas {corrections} correções automáticas")

    # Salvar
    with open('database.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✅ Arquivo atualizado!")
else:
    print("\n✅ Nenhuma correção necessária - queries já estão corretas")

print("\n📝 Próximo passo: Teste o dashboard novamente")
