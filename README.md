# ⚽ Scout Pro - Sistema Profissional de Monitoramento de Jogadores

Sistema completo de scouting com dashboard interativo, sincronização automática com Google Sheets e download inteligente de fotos do Transfermarkt.

---

## 🎯 **Características Principais**

✅ **Sincronização automática** com Google Sheets  
✅ **Dashboard interativo** com Streamlit  
✅ **Download automático** de fotos do Transfermarkt via scraping  
✅ **Sistema de alertas** para contratos vencendo  
✅ **Filtros avançados** e busca inteligente  
✅ **Análises estatísticas** e visualizações  
✅ **Exportação de dados** em CSV  
✅ **Banco de dados normalizado** (SQLite)

---

## 📋 **Requisitos**

- Python 3.8 ou superior
- Conta Google (para acesso ao Google Sheets)
- Conexão com internet
- Planilha Google Sheets com dados dos jogadores

---

## 🚀 **Instalação Rápida**

### **1. Preparar Ambiente**

```bash
# Clone ou baixe o projeto
cd /caminho/para/scout_pro

# Instale as dependências
pip install -r requirements.txt
```

**Dependências principais:**
- `streamlit` - Interface do dashboard
- `pandas` - Manipulação de dados
- `gspread` - Integração com Google Sheets
- `plotly` - Gráficos interativos
- `beautifulsoup4` - Scraping de fotos
- `requests` - Requisições HTTP

---

## 🔐 **Configuração do Google Sheets API**

### **Passo 1: Criar Projeto no Google Cloud**

1. Acesse: https://console.cloud.google.com
2. Clique em **"Select a project"** → **"New Project"**
3. Nome: `Scout Pro`
4. Clique em **"Create"**

### **Passo 2: Ativar APIs**

1. Menu lateral: **APIs & Services** → **Library**
2. Busque e ative:
   - ✅ **Google Sheets API**
   - ✅ **Google Drive API**

### **Passo 3: Criar Service Account**

1. **APIs & Services** → **Credentials**
2. **"+ CREATE CREDENTIALS"** → **"Service account"**
3. Preencha:
   - **Nome:** `scout-sync`
   - **Role:** Project → Viewer
4. Clique em **"CREATE AND CONTINUE"** → **"DONE"**

### **Passo 4: Baixar Credenciais**

1. Clique no Service Account criado
2. Aba **"KEYS"** → **"ADD KEY"** → **"Create new key"**
3. Formato: **JSON**
4. **Renomeie** o arquivo baixado para `credentials.json`
5. **Mova** para a pasta raiz do projeto

### **Passo 5: Compartilhar Planilha**

1. Abra o arquivo `credentials.json`
2. Copie o email do campo `"client_email"`
   - Exemplo: `scout-sync@scout-pro-123456.iam.gserviceaccount.com`
3. Abra sua planilha do Google Sheets
4. Clique em **"Compartilhar"**
5. Cole o email do Service Account
6. Permissão: **Viewer** (Leitor)
7. Clique em **"Enviar"**

✅ **Configuração concluída!**

---

## 📁 **Estrutura do Projeto**

```
scout_pro/
├── credentials.json          ← Arquivo de credenciais (NÃO commitar!)
├── requirements.txt          ← Dependências Python
├── README.md                 ← Este arquivo
│
├── database.py               ← Gerenciamento do banco SQLite
├── google_sheets_sync.py     ← Sincronização com Google Sheets
├── dashboard.py              ← Dashboard Streamlit
├── import_data.py            ← Script de importação inicial
├── baixar_fotos_scraping.py  ← Download de fotos do Transfermarkt
├── limpar_duplicatas.py      ← Utilitário para limpar duplicatas
│
├── scouting.db              ← Banco de dados (criado automaticamente)
└── fotos/                   ← Fotos dos jogadores (criado automaticamente)
```

---

## 📊 **Formato da Planilha Google Sheets**

Sua planilha deve ter as seguintes colunas:

| Coluna | Tipo | Obrigatório | Exemplo | Observações |
|--------|------|-------------|---------|-------------|
| ID | Numérico | ✅ Sim | 1, 2, 3... | Identificador único |
| Nome | Texto | ✅ Sim | João Silva | Nome completo |
| Posição | Texto | ✅ Sim | Atacante | GOL, ZAG, ATA, etc |
| Nacionalidade | Texto | ❌ Não | Brasil | País de origem |
| Idade | Numérico | ❌ Não | 25 | Idade atual |
| Ano | Numérico | ❌ Não | 1998 | Ano de nascimento |
| Altura | Numérico | ❌ Não | 1.80 ou 180 | Em metros (1.80) ou cm (180) |
| Pé | Texto | ❌ Não | Direito | Pé dominante |
| Clube | Texto | ❌ Não | Flamengo | Clube atual |
| Liga do Clube | Texto | ❌ Não | Brasileirão Série A | Liga do clube |
| Fim de contrato | Data | ❌ Não | 31/12/2025 | Data fim contrato |
| Potencial | Texto | ❌ Não | Alto | Alto/Médio/Baixo |
| Nível atual | Texto | ❌ Não | Experiente | |
| TM | Texto | ❌ Não | 123456 ou URL completa | ID do Transfermarkt |

**⚠️ Importante sobre a coluna TM (Transfermarkt):**
- Aceita apenas o ID: `123456`
- Aceita URL completa: `https://www.transfermarkt.com.br/jogador/profil/spieler/123456`
- O sistema extrai automaticamente o ID da URL

**⚠️ Importante sobre a Altura:**
- Se usar metros (1.80, 1.75): será convertido automaticamente para cm
- Se usar centímetros (180, 175): será mantido como está

---

## 🎬 **Primeiros Passos**

### **1. Importação Inicial**

```bash
# Execute a importação dos dados
python import_data.py
```

**O que acontece:**
- Conecta ao Google Sheets
- Carrega todos os jogadores
- Cria/atualiza o banco de dados
- Gera alertas automáticos

**Opções durante a importação:**
```
⚠️  ATENÇÃO: Esta operação pode limpar dados existentes
Deseja LIMPAR os dados antes de importar? (sim/não): sim
```

Digite **sim** se quiser começar do zero (recomendado na primeira vez).

### **2. Baixar Fotos dos Jogadores**

```bash
# Execute o script de download
python baixar_fotos_scraping.py
```

**Menu interativo:**
```
1 - Testar com Neymar (TM ID: 68290)
2 - Testar com outro jogador (digite o TM ID ou URL)
3 - Baixar primeiras 5 fotos (teste rápido)
4 - Baixar primeiras 20 fotos (teste médio)
5 - Baixar TODAS as fotos (modo lento - 2s delay)
6 - Baixar TODAS as fotos (modo normal - 1.5s delay)
```

**Recomendação:**
- Comece testando com a opção **1** (Neymar)
- Depois teste com **3** (5 primeiras fotos)
- Se funcionar bem, use **5** para baixar todas

**⏱️ Tempo estimado:**
- Para 100 jogadores: ~3-4 minutos
- Para 500 jogadores: ~17-20 minutos
- Para 800 jogadores: ~27-30 minutos

### **3. Abrir o Dashboard**

```bash
# Iniciar o dashboard Streamlit
streamlit run dashboard.py
```

O navegador abrirá automaticamente em: `http://localhost:8501`

---

## 🎨 **Recursos do Dashboard**

### **📍 Aba 1: Visão Geral**
- 📊 KPIs principais (total de jogadores, contratos vencendo, alertas)
- 📈 Distribuição por posição (gráfico de barras)
- 🎂 Pirâmide etária
- 🌍 Top 10 nacionalidades
- 📅 Status dos contratos

### **👥 Aba 2: Lista de Jogadores**
- 🔍 Busca por nome
- 🎯 Filtros avançados:
  - Posição
  - Liga
  - Faixa etária
  - Status do contrato
- 📊 Visualização em Cards ou Tabela
- ⬇️ Exportação para CSV
- 📸 Fotos dos jogadores

### **🚨 Aba 3: Central de Alertas**
- ⚠️ Contratos vencendo
- 🎯 Jogadores de alto potencial
- 📌 Filtro por prioridade (alta/média/baixa)
- ✅ Marcar alertas como resolvidos

### **📊 Aba 4: Análises Avançadas**
- 📈 Distribuição por liga
- 📊 Idade média por posição
- 🗺️ Heatmap: Nacionalidade × Posição
- 📉 Gráficos comparativos

---

## 🔧 **Manutenção e Utilitários**

### **Limpar Duplicatas**

Se você importou dados duplicados:

```bash
# Verificar e limpar duplicatas
python limpar_duplicatas.py
```

Ou via linha de comando:

```bash
# Limpar todo o banco
python -c "from database import ScoutingDatabase; db = ScoutingDatabase(); db.limpar_dados(); print('✅ Banco limpo!')"

# Reimportar dados
python import_data.py
```

### **Sincronização Manual**

Para atualizar os dados do Google Sheets:

```bash
python google_sheets_sync.py
# Escolha opção 2: Sincronizar agora
```

Ou use o botão **"🔄 Atualizar dados"** na barra lateral do dashboard.

### **Corrigir Alturas**

Se as alturas estão erradas (mostrando "1" para todos):

1. Verifique o formato na planilha (deve ser 1.80 ou 180)
2. Reimporte os dados:

```bash
python import_data.py
# Responda "sim" para limpar antes
```

---

## ❌ **Solução de Problemas**

### **Problema: "ModuleNotFoundError"**

**Solução:**
```bash
pip install -r requirements.txt
```

### **Problema: "Arquivo credentials.json não encontrado"**

**Verificar:**
1. O arquivo está na pasta raiz do projeto?
2. O nome está correto? (não pode ser credentials.json.txt)
3. Baixou o arquivo JSON correto do Google Cloud?

**Solução:**
```bash
# Verificar se o arquivo existe
ls -la credentials.json

# Se não existir, baixe novamente do Google Cloud Console
```

### **Problema: "Permission denied" no Google Sheets**

**Solução:**
1. Abra o arquivo `credentials.json`
2. Copie o email do campo `"client_email"`
3. Vá na planilha → Compartilhar → Cole o email → Enviar
4. Certifique-se de dar permissão de **Viewer**

### **Problema: Dados duplicados no dashboard**

**Solução:**
```bash
# Limpar e reimportar
python limpar_duplicatas.py
# Responda "sim" quando perguntado

python import_data.py
```

### **Problema: Fotos não aparecem**

**Verificar:**
1. A pasta `fotos/` foi criada?
   ```bash
   ls -la fotos/
   ```

2. Existem arquivos .jpg dentro?
   ```bash
   ls -la fotos/ | head -20
   ```

3. A coluna "TM" tem os IDs do Transfermarkt?

**Solução:**
```bash
# Baixar fotos novamente
python baixar_fotos_scraping.py
# Escolha opção 3 (teste com 5 fotos)
```

### **Problema: Altura aparece como "1" para todos**

**Causa:** Altura está em metros (1.80) na planilha e o código não estava tratando.

**Solução:** O código já foi corrigido. Reimporte:
```bash
python import_data.py
```

### **Problema: Erros ao baixar fotos**

**Possíveis causas:**
- Rate limiting do Transfermarkt
- IDs inválidos na planilha
- Problemas de conexão

**Solução:**
1. Teste com um jogador específico:
   ```bash
   python baixar_fotos_scraping.py
   # Escolha opção 1 (testar Neymar)
   ```

2. Aumente o delay entre requisições:
   ```bash
   # Escolha opção 5 (delay de 2 segundos)
   ```

3. Verifique se os IDs do Transfermarkt estão corretos na planilha

---

## 🗃️ **Estrutura do Banco de Dados**

O sistema cria 4 tabelas principais:

### **1. jogadores**
```sql
- id_jogador (PRIMARY KEY)
- nome
- nacionalidade
- ano_nascimento
- idade_atual
- altura
- pe_dominante
- transfermarkt_id
```

### **2. vinculos**
```sql
- id_vinculo (PRIMARY KEY)
- id_jogador (FOREIGN KEY)
- clube
- liga_clube
- posicao
- data_fim_contrato
- status_contrato
```

### **3. alertas**
```sql
- id_alerta (PRIMARY KEY)
- id_jogador (FOREIGN KEY)
- tipo_alerta
- descricao
- prioridade
- data_criacao
- ativo
```

### **4. avaliacoes**
```sql
- id_avaliacao (PRIMARY KEY)
- id_jogador (FOREIGN KEY)
- data_avaliacao
- nota_potencial
- nota_tatico
- nota_tecnico
- nota_fisico
- nota_mental
- observacoes
- avaliador
```

---

## 📈 **Comandos Úteis**

```bash
# Instalar dependências
pip install -r requirements.txt

# Importar dados do Google Sheets
python import_data.py

# Baixar fotos do Transfermarkt
python baixar_fotos_scraping.py

# Limpar duplicatas
python limpar_duplicatas.py

# Abrir dashboard
streamlit run dashboard.py

# Verificar estrutura do banco
sqlite3 scouting.db "SELECT COUNT(*) FROM jogadores;"

# Ver alertas ativos
sqlite3 scouting.db "SELECT * FROM alertas WHERE ativo = 1;"

# Exportar dados para CSV
sqlite3 -header -csv scouting.db "SELECT * FROM jogadores;" > jogadores.csv
```

---

## 🔒 **Segurança**

### **NUNCA COMMITAR `credentials.json`**

Adicione ao `.gitignore`:

```
# Credenciais
credentials.json

# Banco de dados
scouting.db
*.db

# Fotos
fotos/
*.jpg
*.jpeg
*.png

# Python
*.pyc
__pycache__/
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp
```

---

## 🚀 **Próximas Funcionalidades**

- [ ] Sistema de avaliações técnicas completo
- [ ] Radar charts de habilidades
- [ ] Comparação entre jogadores
- [ ] Relatórios PDF automáticos
- [ ] Histórico de transferências
- [ ] Integração com APIs de estatísticas
- [ ] Sistema de notas e observações
- [ ] Dashboard mobile-friendly

---

## 📝 **Changelog**

### **v1.2.0** (2025-11-21)
- ✅ Correção de duplicatas no banco
- ✅ Tratamento de altura em metros/centímetros
- ✅ Download inteligente de fotos com scraping
- ✅ Extração automática de IDs do Transfermarkt
- ✅ Melhorias na interface do dashboard

### **v1.1.0** (2025-11)
- ✅ Sincronização com Google Sheets
- ✅ Sistema de alertas automáticos
- ✅ Dashboard interativo com Streamlit
- ✅ Filtros avançados

### **v1.0.0** (2025-11)
- ✅ Versão inicial do sistema

---

## 📞 **Suporte**

Problemas? Siga esta ordem:

1. ✅ Leia a seção "Solução de Problemas"
2. ✅ Verifique se seguiu todos os passos de instalação
3. ✅ Teste a conexão com Google Sheets
4. ✅ Verifique os logs de erro

---

## 👤 **Autor**

**Caio Felipe**  
Scout Profissional - Sport Club do Recife  
Estudante de Data Science - UFMS

**Certificações:**
- CBF Academy - Análise de Desempenho PRO

---

## 📄 **Licença**

Este projeto é de uso privado para fins de scouting profissional.

---

**⚽ Bom scouting!**
