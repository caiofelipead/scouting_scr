# ⚽ Scout Pro - Sistema de Monitoramento de Jogadores

Sistema profissional de scouting com dashboard interativo e sincronização automática com Google Sheets.

---

## 📋 **Requisitos**

- Python 3.8 ou superior
- Conta Google (para acesso ao Google Sheets)
- Conexão com internet

---

## 🚀 **Instalação - Passo a Passo**

### **Passo 1: Preparar Ambiente**

```bash
# 1. Abra o terminal na pasta do projeto
cd /caminho/para/projeto

# 2. Instale as dependências
pip install -r requirements.txt
```

---

### **Passo 2: Configurar Google Sheets API**

#### **2.1 - Criar Projeto no Google Cloud**

1. Acesse: https://console.cloud.google.com
2. Clique em **"Select a project"** → **"New Project"**
3. Nome do projeto: `Scout Pro`
4. Clique em **"Create"**

#### **2.2 - Ativar APIs Necessárias**

1. No menu lateral, vá em: **APIs & Services** → **Library**
2. Busque e ative estas 2 APIs:
   - ✅ **Google Sheets API** → Clique em "Enable"
   - ✅ **Google Drive API** → Clique em "Enable"

#### **2.3 - Criar Service Account**

1. No menu lateral: **APIs & Services** → **Credentials**
2. Clique em **"+ CREATE CREDENTIALS"** → **"Service account"**
3. Preencha:
   - **Service account name:** `scout-sync`
   - **Service account ID:** (será gerado automaticamente)
4. Clique em **"CREATE AND CONTINUE"**
5. Em **"Role"**, selecione: **Project** → **Viewer**
6. Clique em **"CONTINUE"** e depois **"DONE"**

#### **2.4 - Baixar Credenciais**

1. Na lista de Service Accounts, clique no email que você acabou de criar
2. Vá na aba **"KEYS"**
3. Clique em **"ADD KEY"** → **"Create new key"**
4. Selecione **JSON** e clique em **"CREATE"**
5. Um arquivo JSON será baixado automaticamente
6. **RENOMEIE** este arquivo para `credentials.json`
7. **MOVA** o arquivo para a pasta do projeto (mesma pasta onde estão os arquivos .py)

#### **2.5 - Compartilhar Planilha com Service Account**

1. **COPIE** o email do Service Account (está no arquivo credentials.json, campo "client_email")
   - Exemplo: `scout-sync@scout-pro-123456.iam.gserviceaccount.com`

2. Abra sua planilha do Google Sheets:
   https://docs.google.com/spreadsheets/d/1jNAxJIRoZxYH1jKwPCBrd4Na1ko04EDAYaUCVGsJdIA/edit

3. Clique em **"Compartilhar"** (botão verde no canto superior direito)

4. **COLE** o email do Service Account

5. Permissão: **Viewer** (Leitor)

6. Clique em **"Enviar"**

✅ **Pronto! A configuração do Google está completa.**

---

### **Passo 3: Estrutura do Projeto**

Verifique se sua pasta tem esta estrutura:

```
scout-pro/
├── credentials.json          ← ARQUIVO BAIXADO (NÃO COMMITAR!)
├── requirements.txt
├── README.md
├── database.py
├── google_sheets_sync.py
├── dashboard.py
├── import_data.py
├── scouting.db              ← Será criado automaticamente
└── fotos/                   ← Será criada automaticamente
```

---

## 🧪 **Testando a Configuração**

### **Teste 1: Verificar Credenciais**

```bash
python google_sheets_sync.py
```

Quando o menu aparecer, digite: **1** (Testar conexão)

**✅ Resultado esperado:**
```
🔐 Configurando credenciais...
✅ Credenciais configuradas com sucesso!

📥 Buscando dados do Google Sheets...
✅ 120 jogadores carregados do Google Sheets
📊 Colunas encontradas: ['ID', 'Nome', 'Posição', ...]

✅ Conexão bem sucedida!
```

**❌ Se der erro:**

**Erro: "Arquivo credentials.json não encontrado"**
- Verifique se o arquivo está na pasta correta
- Verifique se o nome está correto (credentials.json, não credentials.json.txt)

**Erro: "Planilha não encontrada"**
- Verifique se você compartilhou a planilha com o email do Service Account
- Verifique se o email está correto

---

### **Teste 2: Sincronizar Dados**

```bash
python google_sheets_sync.py
```

Digite: **2** (Sincronizar agora)

**✅ Resultado esperado:**
```
🔄 INICIANDO SINCRONIZAÇÃO
============================================================

📥 Buscando dados do Google Sheets...
✅ 120 jogadores carregados

📸 Baixando fotos do Transfermarkt...
  ✓ Yuri Vieira
  ✓ Hugo Gomes
  ✓ Bobsin
  ...
📊 Resultado: 95 fotos baixadas, 25 erros

💾 Atualizando banco de dados...
✅ Importados 120 jogadores e vínculos!

🚨 Gerando alertas...
✅ Criados 34 alertas de contrato!

📈 Estatísticas do banco:
   • Total de jogadores: 120
   • Vínculos ativos: 87
   • Contratos vencendo: 34
   • Alertas ativos: 34

============================================================
✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!
============================================================
```

---

## 🎯 **Usando o Sistema**

### **Opção A: Sincronização Manual (Recomendado para começar)**

```bash
# Sincronizar dados uma vez
python google_sheets_sync.py
# Digite: 2

# Abrir dashboard
streamlit run dashboard.py
```

### **Opção B: Sincronização Automática**

```bash
# Sincronizar automaticamente a cada 60 minutos
python google_sheets_sync.py
# Digite: 3
# Digite o intervalo: 60
```

Isso manterá o sistema rodando e atualizando os dados automaticamente. Para parar, pressione `Ctrl+C`.

### **Opção C: Dashboard com Botão de Sync**

O dashboard tem um botão lateral "🔄 Atualizar dados do Sheets" para sincronizar sob demanda.

---

## 📊 **Recursos do Dashboard**

### **Aba 1: Visão Geral**
- Distribuição por posição
- Pirâmide etária
- Top 10 nacionalidades
- Status dos contratos

### **Aba 2: Lista de Jogadores**
- Busca por nome
- Filtros avançados (posição, liga, idade)
- Ordenação customizada
- Exportação para CSV

### **Aba 3: Central de Alertas**
- Contratos vencendo em breve
- Filtro por prioridade (alta/média/baixa)
- Descrição detalhada de cada alerta

### **Aba 4: Análises Avançadas**
- Jogadores por liga
- Idade média por posição
- Heatmap: Nacionalidade × Posição

---

## 🔧 **Solução de Problemas**

### **Problema: "ModuleNotFoundError: No module named 'gspread'"**

**Solução:**
```bash
pip install -r requirements.txt
```

---

### **Problema: Fotos não aparecem no dashboard**

**Verificar:**
1. A pasta `fotos/` foi criada?
2. Existem arquivos .jpg dentro dela?
3. A coluna "TM" na planilha tem os IDs do Transfermarkt?

**Testar manualmente:**
```bash
python -c "import os; print(os.listdir('fotos'))"
```

---

### **Problema: "Permission denied" no Google Sheets**

**Solução:**
1. Verifique se você compartilhou a planilha com o Service Account
2. Abra o arquivo `credentials.json`
3. Copie o campo `"client_email"`
4. Vá na planilha → Compartilhar → Cole o email → Enviar

---

### **Problema: Dados desatualizados no dashboard**

**Solução:**
```bash
# Forçar nova sincronização
python google_sheets_sync.py
# Digite: 2

# Recarregar dashboard (pressione R no navegador)
```

---

## 📁 **Estrutura dos Dados**

### **Banco de Dados (SQLite)**

O sistema cria 6 tabelas:

1. **jogadores** - Dados básicos (nome, idade, nacionalidade, foto)
2. **vinculos** - Clube atual, contrato, posição
3. **avaliacoes** - Scouting reports e notas
4. **caracteristicas** - Perfil técnico (passe, drible, etc)
5. **estatisticas** - Performance (gols, assistências, minutos)
6. **alertas** - Notificações automáticas

### **Mapeamento Google Sheets → Banco**

| Coluna na Planilha | Campo no Banco |
|--------------------|----------------|
| ID | id_jogador |
| Nome | nome |
| Nacionalidade | nacionalidade |
| Ano | ano_nascimento |
| Idade | idade_atual |
| Altura | altura |
| Pé dominante | pe_dominante |
| Clube | clube |
| Liga do Clube | liga_clube |
| Posição | posicao |
| Fim de Contrato | data_fim_contrato |
| TM | transfermarkt_id |

---

## 🚀 **Próximos Passos**

Após ter o sistema funcionando:

1. **Adicionar características técnicas** (passe, drible, etc)
2. **Criar páginas de perfil detalhadas** com fotos grandes
3. **Implementar radar charts** de habilidades
4. **Adicionar comparação entre jogadores**
5. **Gerar relatórios PDF** de scouting

---

## 🔒 **Segurança**

### **IMPORTANTE: NÃO COMMITAR `credentials.json`**

Se você usa Git, adicione ao `.gitignore`:

```
# .gitignore
credentials.json
scouting.db
fotos/
*.pyc
__pycache__/
```

---

## 📞 **Suporte**

Se tiver problemas:

1. Verifique se seguiu TODOS os passos do Passo 2
2. Teste a conexão (Opção 1 do menu)
3. Verifique o arquivo credentials.json existe
4. Verifique se compartilhou a planilha corretamente

---

## ⚡ **Comandos Rápidos**

```bash
# Instalar dependências
pip install -r requirements.txt

# Testar conexão
python google_sheets_sync.py  # Opção 1

# Sincronizar agora
python google_sheets_sync.py  # Opção 2

# Abrir dashboard
streamlit run dashboard.py

# Sincronização automática (60 min)
python google_sheets_sync.py  # Opção 3
```

---

**✅ Sistema desenvolvido por Caio Felipe - Scout @ Sport Club do Recife**
