#!/usr/bin/env python3
"""
Organiza o diretório do projeto, removendo arquivos temporários
"""

from pathlib import Path
import shutil

print("="*60)
print("🧹 ORGANIZANDO DIRETÓRIO DO PROJETO")
print("="*60)

# Lista de arquivos temporários/debug para remover
arquivos_remover = [
    # Scripts de diagnóstico e correção
    "diagnostico_fotos.py",
    "fix_fotos_dashboard.py",
    "fix_fotos_forcado.py",
    "diagnostico_ids_fotos.py",
    "criar_mapeamento_ids.py",
    "criar_mapeamento_ids_v2.py",
    "mapeamento_final.py",
    "verificar_fotos_final.py",
    "verificar_correcao.py",
    "diagnostico_fotos_erradas.py",
    "corrigir_mapeamento_tm.py",
    "correcao_definitiva_fotos.py",

    # Backups de Python
    "app/dashboard.py.backup",
    "database.py.bak2",
    "database.py.bak3",
    "database.py.bak4",
    "database.py.bak5",

    # CSVs temporários
    "mapeamento_ids_template.csv",
    "mapeamento_ids.csv",
    "mapeamento_final.csv",
    "mapeamento_correto_tm.csv",
    "mapeamento_definitivo.csv",

    # Logs
    "log_renomeacao.txt",
    "log_renomeacao_definitivo.txt",
]

# Pastas para limpar
pastas_limpar = [
    "fotos/temp_renomeacao",
    "__pycache__",
]

print("\n📁 Arquivos a remover:")
removidos = 0
mantidos = []

for arquivo in arquivos_remover:
    path = Path(arquivo)
    if path.exists():
        path.unlink()
        print(f"   ✓ {arquivo}")
        removidos += 1
    else:
        mantidos.append(arquivo)

print(f"\n✅ {removidos} arquivos removidos")

if mantidos:
    print(f"\n📝 {len(mantidos)} arquivos já não existiam (OK)")

# Limpar pastas
print("\n📂 Limpando pastas...")
for pasta in pastas_limpar:
    path = Path(pasta)
    if path.exists():
        shutil.rmtree(path)
        print(f"   ✓ {pasta}")

# Manter apenas arquivos importantes
print("\n" + "="*60)
print("📋 ARQUIVOS MANTIDOS (IMPORTANTES)")
print("="*60)

arquivos_importantes = {
    "Configuração": [
        ".env",
        ".gitignore",
        "requirements.txt",
        "docker-compose.yml",
        "Dockerfile"
    ],
    "Código Principal": [
        "database.py",
        "app/dashboard.py",
        "google_sheets_sync_railway.py"
    ],
    "Dados": [
        "fotos/",
        "fotos/backup_ids_antigos/"
    ],
    "Documentação": [
        "README.md",
        "CHANGELOG.md"
    ]
}

for categoria, arquivos in arquivos_importantes.items():
    print(f"\n{categoria}:")
    for arquivo in arquivos:
        path = Path(arquivo)
        if path.exists():
            if path.is_dir():
                n_arquivos = len(list(path.glob("**/*")))
                print(f"   ✅ {arquivo} ({n_arquivos} arquivos)")
            else:
                print(f"   ✅ {arquivo}")
        else:
            print(f"   ⚠️  {arquivo} (não encontrado)")

print("\n" + "="*60)
print("💡 ESTRUTURA RECOMENDADA DO PROJETO")
print("="*60)

estrutura = """
scouting_scr/
├── .env                          # Variáveis de ambiente
├── .gitignore                    # Arquivos ignorados
├── requirements.txt              # Dependências Python
├── README.md                     # Documentação
├── database.py                   # Conexão com banco
├── google_sheets_sync_railway.py # Sincronização Sheets
│
├── app/
│   └── dashboard.py              # Dashboard Streamlit
│
├── fotos/                        # Fotos dos jogadores
│   ├── 1417.jpg
│   ├── 1418.jpg
│   └── backup_ids_antigos/       # Backup (pode remover após confirmar)
│
├── scripts/                      # Scripts úteis (opcional)
│   └── atualizar_fotos.py
│
└── docs/                         # Documentação (opcional)
    └── manual_usuario.md
"""

print(estrutura)

print("="*60)
print("✅ ORGANIZAÇÃO CONCLUÍDA!")
print("="*60)

# Verificar se backup pode ser removido
backup_dir = Path("fotos/backup_ids_antigos")
if backup_dir.exists():
    n_backups = len(list(backup_dir.glob("*.jpg")))
    print(f"\n⚠️  ATENÇÃO:")
    print(f"   Pasta de backup contém {n_backups} fotos")
    print(f"   Local: {backup_dir}")
    print(f"\n   Se as fotos estão OK no dashboard, você pode remover:")
    print(f"   rm -rf {backup_dir}")
    print(f"\n   Isso vai liberar espaço em disco.")

print("\n" + "="*60)
