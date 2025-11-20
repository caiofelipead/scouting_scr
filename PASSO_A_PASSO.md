# 🎯 PASSO A PASSO COMPLETO - SCOUT PRO

**Sistema pronto para uso! Siga este guia na ordem.**

---

## 📦 ETAPA 1: PREPARAR AMBIENTE (5 minutos)

### Passo 1.1: Baixar os arquivos
✅ **Você já tem todos os arquivos necessários:**

- ✓ database.py
- ✓ google_sheets_sync.py  
- ✓ dashboard.py
- ✓ import_data.py
- ✓ requirements.txt
- ✓ checklist.py
- ✓ README.md
- ✓ GUIA_RAPIDO.md
- ✓ .gitignore

### Passo 1.2: Organizar pasta
```
scout-pro/
├── database.py
├── google_sheets_sync.py
├── dashboard.py
├── import_data.py
├── checklist.py
├── requirements.txt
├── README.md
├── GUIA_RAPIDO.md
└── .gitignore
```

### Passo 1.3: Instalar dependências
Abra o terminal na pasta e execute:

```bash
pip install -r requirements.txt
```

**Tempo:** ~2 minutos  
**Resultado esperado:** "Successfully installed streamlit-1.29.0 pandas-2.1.4 ..."

---

## 🔐 ETAPA 2: CONFIGURAR GOOGLE SHEETS API (10 minutos)

### Passo 2.1: Acessar Google Cloud Console

🔗 Abra: https://console.cloud.google.com

**Ação:** 
1. Clique em **"Select a project"** (topo da página)
2. Clique em **"NEW PROJECT"**
3. Nome do projeto: `Scout Pro`
4. Clique em **"CREATE"**

⏱️ **Aguarde ~10 segundos** para o projeto ser criado

---

### Passo 2.2: Ativar Google Sheets API

**Ação:**
1. No menu lateral esquerdo (☰), clique em: **APIs & Services** → **Library**
2. Na barra de busca, digite: `Google Sheets API`
3. Clique no resultado **"Google Sheets API"**
4. Clique no botão azul **"ENABLE"**

⏱️ **Aguarde ~5 segundos**

---

### Passo 2.3: Ativar Google Drive API

**Ação:**
1. Clique em **"APIs & Services"** → **"Library"** novamente
2. Na barra de busca, digite: `Google Drive API`
3. Clique no resultado **"Google Drive API"**
4. Clique no botão azul **"ENABLE"**

⏱️ **Aguarde ~5 segundos**

---

### Passo 2.4: Criar Service Account

**Ação:**
1. Menu lateral: **APIs & Services** → **Credentials**
2. Clique no botão **"+ CREATE CREDENTIALS"** (topo da página)
3. Selecione: **"Service account"**

**Tela de criação:**
- **Service account name:** `scout-sync`
- **Service account ID:** (será preenchido automaticamente)
- Clique em **"CREATE AND CONTINUE"**

**Tela de permissões:**
- **Role:** Selecione `Project` → `Viewer`
- Clique em **"CONTINUE"**
- Clique em **"DONE"**

---

### Passo 2.5: Baixar credenciais JSON

**Ação:**
1. Na lista de **Service Accounts**, você verá `scout-sync@...`
2. **Clique no email** scout-sync@scout-pro-xxxxx.iam.gserviceaccount.com
3. Vá na aba **"KEYS"** (no topo)
4. Clique em **"ADD KEY"** → **"Create new key"**
5. Selecione **"JSON"**
6. Clique em **"CREATE"**

📥 **Um arquivo JSON será baixado automaticamente**

**IMPORTANTE:**
- Renomeie o arquivo para: `credentials.json`
- Mova para a pasta do projeto (mesma pasta dos arquivos .py)

```
scout-pro/
├── credentials.json  ← AQUI!
├── database.py
├── google_sheets_sync.py
├── ...
```

---

### Passo 2.6: Copiar email do Service Account

**Ação:**
1. Abra o arquivo `credentials.json` com um editor de texto
2. Procure pela linha que contém `"client_email"`
3. **Copie o email completo**

Exemplo:
```json
{
  ...
  "client_email": "scout-sync@scout-pro-123456.iam.gserviceaccount.com",
  ...
}
```

📋 **Copie:** scout-sync@scout-pro-123456.iam.gserviceaccount.com

---

### Passo 2.7: Compartilhar planilha

**Ação:**
1. Abra sua planilha do Google Sheets:
   🔗 https://docs.google.com/spreadsheets/d/1jNAxJIRoZxYH1jKwPCBrd4Na1ko04EDAYaUCVGsJdIA/edit

2. Clique no botão **"Compartilhar"** (canto superior direito, verde)

3. No campo "Adicionar pessoas e grupos":
   - **Cole o email** que você copiou do credentials.json
   - Exemplo: scout-sync@scout-pro-123456.iam.gserviceaccount.com

4. **Permissão:** Certifique-se que está como **"Viewer"** (Leitor)

5. **DESMARQUE** a caixa "Notificar pessoas" (não precisa enviar email)

6. Clique em **"Enviar"**

✅ **Pronto! Configuração do Google concluída.**

---

## 🧪 ETAPA 3: TESTAR CONFIGURAÇÃO (2 minutos)

### Passo 3.1: Executar checklist

Abra o terminal na pasta do projeto e execute:

```bash
python checklist.py
```

**✅ Resultado ESPERADO:**

```
🔍 CHECKLIST DE CONFIGURAÇÃO - SCOUT PRO
============================================================

✅ 1. Versão do Python
   Python 3.10.12

✅ 2. Dependências instaladas
   Todas instaladas (7/7)

✅ 3. Arquivo de credenciais
   credentials.json encontrado

✅ 4. Estrutura do projeto
   Todos os arquivos presentes (5/5)

✅ 5. Pastas necessárias
   Pasta 'fotos/' criada

✅ 6. Conexão com banco de dados
   Banco de dados OK

✅ 7. Conexão com Google Sheets
   Conectado - 120 jogadores encontrados

============================================================
🎉 TUDO PRONTO! Sistema configurado corretamente.
============================================================
```

**❌ Se aparecer ERROS:**

**Erro no item 3:** "credentials.json NÃO encontrado"
→ Volte ao Passo 2.5 e verifique se o arquivo está na pasta correta

**Erro no item 7:** "Falha ao buscar dados"
→ Volte ao Passo 2.7 e verifique se compartilhou a planilha

**Erro no item 2:** "Faltam: gspread"
→ Execute: `pip install -r requirements.txt`

---

## 📥 ETAPA 4: IMPORTAR DADOS (5 minutos)

### Passo 4.1: Executar importação

```bash
python import_data.py
```

**O que vai acontecer:**

1. ✓ Conecta no Google Sheets
2. ✓ Busca dados de 120+ jogadores
3. ✓ Baixa fotos do Transfermarkt (~3 minutos)
4. ✓ Cria banco de dados SQLite
5. ✓ Gera alertas automáticos

**✅ Resultado ESPERADO:**

```
🔄 INICIANDO SINCRONIZAÇÃO
============================================================

📥 Buscando dados do Google Sheets...
✅ 120 jogadores carregados do Google Sheets

📸 Baixando fotos do Transfermarkt...
  ✓ Yuri Vieira
  ✓ Hugo Gomes
  ✓ Bobsin
  ... (continua)
  
📊 Resultado: 95 fotos baixadas, 25 erros

💾 Atualizando banco de dados...
✅ Importados 120 jogadores e vínculos!

🚨 Gerando alertas...
✅ Criados 34 alertas de contrato!

============================================================
✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!
============================================================

🎯 PRÓXIMOS PASSOS:
1. Execute: streamlit run dashboard.py
2. Acesse o dashboard interativo no navegador
```

**Novos arquivos criados:**
```
scout-pro/
├── scouting.db        ← Banco de dados SQLite
├── fotos/             ← Pasta com fotos dos jogadores
│   ├── 1.jpg
│   ├── 2.jpg
│   └── ...
```

---

## 🚀 ETAPA 5: ABRIR DASHBOARD (1 minuto)

### Passo 5.1: Executar dashboard

```bash
streamlit run dashboard.py
```

**O que vai acontecer:**

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.10:8501
```

**Seu navegador abrirá automaticamente** com o dashboard!

🎉 **Pronto! Sistema funcionando!**

---

## 🎯 USANDO O SISTEMA

### Recursos disponíveis:

**📊 Aba 1: Visão Geral**
- Gráficos de distribuição por posição
- Pirâmide etária
- Top 10 nacionalidades
- Status dos contratos (cores: verde=OK, laranja=atenção, vermelho=urgente)

**👥 Aba 2: Lista de Jogadores**
- Busca por nome
- Filtros: posição, liga, faixa etária, status contrato
- Ordenação customizada
- Exportar para CSV

**🚨 Aba 3: Central de Alertas**
- Contratos vencendo em breve
- Prioridades: alta (vermelho), média (laranja), baixa (azul)

**📈 Aba 4: Análises Avançadas**
- Distribuição por liga
- Idade média por posição
- Heatmap: Nacionalidade × Posição

### Sidebar (barra lateral):

**Filtros:**
- Posição (dropdown)
- Liga (dropdown)
- Faixa etária (slider)
- Status do contrato (multiselect)

---

## 🔄 ATUALIZAR DADOS

### Opção 1: Manualmente (quando quiser)

```bash
python google_sheets_sync.py
# Digite: 2
```

### Opção 2: Automático (a cada 60 minutos)

```bash
python google_sheets_sync.py
# Digite: 3
# Digite: 60
```

Deixa rodando em segundo plano. Para parar: `Ctrl+C`

---

## 🆘 PROBLEMAS COMUNS

### Dashboard não abre
```bash
# Verifique se Streamlit está instalado
pip install streamlit

# Tente novamente
streamlit run dashboard.py
```

### Dados não aparecem
```bash
# Re-importe os dados
python import_data.py
```

### Fotos não aparecem
- Verifique se a pasta `fotos/` existe
- Verifique se tem arquivos .jpg dentro
- Coluna "TM" na planilha precisa ter os IDs do Transfermarkt

### Google Sheets retorna erro
1. Verifique se `credentials.json` existe na pasta
2. Abra a planilha e verifique se está compartilhada
3. Execute novamente o checklist: `python checklist.py`

---

## 📞 PRECISA DE AJUDA?

1. **Consulte:** `README.md` (guia detalhado)
2. **Consulte:** `GUIA_RAPIDO.md` (versão simplificada)
3. **Execute:** `python checklist.py` (diagnóstico automático)

---

## ✅ CHECKLIST FINAL

Marque conforme avançar:

- [ ] Etapa 1: Arquivos baixados e dependências instaladas
- [ ] Etapa 2: Google Sheets API configurada
- [ ] Etapa 3: Checklist passou todos os testes
- [ ] Etapa 4: Dados importados com sucesso
- [ ] Etapa 5: Dashboard aberto e funcionando

**Se todos marcados: PARABÉNS! 🎉**

---

**Sistema desenvolvido para Caio Felipe**
**Scout @ Sport Club do Recife**
