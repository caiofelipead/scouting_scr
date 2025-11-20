# ⚡ COMANDOS RÁPIDOS - REFERÊNCIA

## 🔧 Instalação e Setup

```bash
# Instalar dependências
pip install -r requirements.txt

# Verificar configuração
python checklist.py

# Primeira importação
python import_data.py
```

---

## 🚀 Executar Sistema

```bash
# Abrir dashboard
streamlit run dashboard.py

# Sincronizar dados (manual)
python google_sheets_sync.py  # Opção 2

# Sincronização automática (60 min)
python google_sheets_sync.py  # Opção 3
```

---

## 📊 Operações do Dashboard

**Acessar:**
- URL: http://localhost:8501

**Filtros disponíveis (sidebar):**
- Posição
- Liga
- Faixa etária
- Status do contrato

**Exportar dados:**
- Aba "Lista de Jogadores"
- Botão "📥 Exportar dados filtrados (CSV)"

---

## 🔄 Sincronização

### Menu do google_sheets_sync.py:

```
1 - Testar conexão             # Verifica se está tudo OK
2 - Sincronizar agora          # Atualiza dados uma vez
3 - Sincronização automática   # Loop contínuo
```

### Comandos diretos no Python:

```python
from google_sheets_sync import GoogleSheetsSyncer

SHEET_URL = "https://docs.google.com/spreadsheets/d/1jNAxJIRo..."

# Sincronizar
syncer = GoogleSheetsSyncer(SHEET_URL)
syncer.sincronizar_banco(baixar_fotos=True)

# Sync automático (60 min)
syncer.sincronizar_automatico(intervalo_minutos=60)
```

---

## 🗄️ Banco de Dados

### Consultas SQL diretas:

```python
from database import ScoutingDatabase

db = ScoutingDatabase()
conn = db.connect()

# Ver todos os jogadores
import pandas as pd
df = pd.read_sql_query("SELECT * FROM jogadores", conn)

# Jogadores com contrato vencendo
df = pd.read_sql_query("""
    SELECT j.nome, v.clube, v.data_fim_contrato
    FROM jogadores j
    JOIN vinculos v ON j.id_jogador = v.id_jogador
    WHERE v.status_contrato = 'ultimos_6_meses'
""", conn)

conn.close()
```

---

## 📸 Gerenciar Fotos

### Baixar fotos manualmente:

```python
from google_sheets_sync import GoogleSheetsSyncer
import pandas as pd

SHEET_URL = "sua_url"
syncer = GoogleSheetsSyncer(SHEET_URL)

# Buscar dados
df = syncer.buscar_dados_sheets()

# Baixar apenas fotos
syncer.baixar_fotos_transfermarkt(df)
```

### Verificar fotos baixadas:

```bash
# Linux/Mac
ls fotos/ | wc -l

# Windows
dir fotos /b | find /c /v ""
```

---

## 🔍 Diagnóstico

### Checklist completo:

```bash
python checklist.py
```

### Verificações individuais:

```python
# Testar conexão Google Sheets
from google_sheets_sync import teste_conexao
teste_conexao("SUA_URL")

# Testar banco de dados
from database import ScoutingDatabase
db = ScoutingDatabase()
stats = db.get_estatisticas_gerais()
print(stats)

# Ver alertas ativos
alertas = db.get_alertas_ativos()
print(alertas)
```

---

## 🛠️ Manutenção

### Limpar e resetar:

```bash
# Deletar banco e recomeçar
rm scouting.db
python import_data.py

# Deletar fotos e rebaixar
rm -rf fotos/
python google_sheets_sync.py  # Opção 2
```

### Backup:

```bash
# Backup do banco
cp scouting.db scouting_backup_$(date +%Y%m%d).db

# Backup das fotos
tar -czf fotos_backup_$(date +%Y%m%d).tar.gz fotos/
```

---

## 📦 Estrutura de Arquivos

```
scout-pro/
├── credentials.json          # Credenciais Google (NÃO COMMITAR!)
├── scouting.db              # Banco de dados SQLite
├── fotos/                   # Fotos dos jogadores
│   ├── 1.jpg
│   ├── 2.jpg
│   └── ...
├── database.py              # Gerenciamento do banco
├── google_sheets_sync.py    # Sincronização
├── dashboard.py             # Interface Streamlit
├── import_data.py           # Importação inicial
├── checklist.py             # Verificação de setup
├── requirements.txt         # Dependências
├── README.md                # Guia completo
├── GUIA_RAPIDO.md          # Guia simplificado
├── PASSO_A_PASSO.md        # Tutorial passo a passo
└── .gitignore              # Arquivos a ignorar no Git
```

---

## 🔒 Segurança

### Arquivos sensíveis (NUNCA COMMITAR):

- `credentials.json` ← Credenciais do Google
- `scouting.db` ← Dados dos jogadores
- `fotos/` ← Imagens dos jogadores

### Verificar .gitignore:

```bash
cat .gitignore

# Deve conter:
credentials.json
*.db
fotos/
```

---

## 🆘 Solução Rápida de Problemas

```bash
# Erro: ModuleNotFoundError
pip install -r requirements.txt

# Erro: credentials.json não encontrado
# → Verifique se está na pasta correta

# Erro: Planilha não encontrada
# → Compartilhe a planilha com Service Account

# Dashboard não abre
streamlit run dashboard.py --server.port 8502  # Tentar outra porta

# Dados desatualizados
python import_data.py  # Re-importar

# Resetar tudo
rm scouting.db
rm -rf fotos/
python import_data.py
```

---

## 📚 Documentação Completa

- **README.md** - Guia detalhado com explicações
- **GUIA_RAPIDO.md** - Versão 15 minutos
- **PASSO_A_PASSO.md** - Tutorial visual completo
- **Este arquivo** - Comandos de referência rápida

---

## 🎯 Workflows Comuns

### Workflow 1: Uso diário

```bash
# 1. Abrir dashboard
streamlit run dashboard.py

# 2. Quando precisar atualizar dados (no terminal)
python google_sheets_sync.py  # Opção 2
```

### Workflow 2: Primeira vez

```bash
# 1. Instalar
pip install -r requirements.txt

# 2. Configurar Google (manual - 10 min)
# ... (siga PASSO_A_PASSO.md)

# 3. Verificar
python checklist.py

# 4. Importar
python import_data.py

# 5. Usar
streamlit run dashboard.py
```

### Workflow 3: Sincronização contínua

```bash
# Terminal 1: Dashboard
streamlit run dashboard.py

# Terminal 2: Auto-sync (60 min)
python google_sheets_sync.py  # Opção 3
```

---

**Última atualização:** 20/11/2025  
**Versão:** 1.0  
**Desenvolvido para:** Caio Felipe - Scout @ Sport Club do Recife
