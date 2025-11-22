# ⚡ Guia Rápido - 15 Minutos

## 1️⃣ Instalar (2 minutos)

```bash
pip install -r requirements.txt
```

## 2️⃣ Configurar Google Sheets API (8 minutos)

### A. Criar projeto no Google Cloud
1. https://console.cloud.google.com
2. "New Project" → Nome: "Scout Pro"

### B. Ativar APIs
1. Menu: APIs & Services → Library
2. Ativar: **Google Sheets API** e **Google Drive API**

### C. Criar Service Account
1. APIs & Services → Credentials
2. "+ CREATE CREDENTIALS" → "Service account"
3. Nome: `scout-sync` → CREATE

### D. Baixar credenciais
1. Clique no Service Account criado
2. Aba KEYS → ADD KEY → Create new key → JSON
3. Arquivo baixado → Renomear para `credentials.json`
4. Mover para pasta do projeto

### E. Compartilhar planilha
1. Abrir `credentials.json` → Copiar campo `"client_email"`
2. Abrir planilha do Google Sheets
3. Compartilhar → Colar email → Permissão: Viewer → Enviar

## 3️⃣ Verificar Configuração (2 minutos)

```bash
python checklist.py
```

Deve aparecer todos ✅ (exceto item 7 que pode ser ⏭️)

## 4️⃣ Importar Dados (3 minutos)

```bash
python import_data.py
```

Aguarde baixar fotos (pode demorar um pouco).

## 5️⃣ Abrir Dashboard

```bash
streamlit run dashboard.py
```

Abre automaticamente no navegador: http://localhost:8501

---

## ✅ Pronto!

**Comandos úteis:**

```bash
# Atualizar dados manualmente
python google_sheets_sync.py  # Opção 2

# Auto-sync a cada 60 minutos
python google_sheets_sync.py  # Opção 3
```

---

## ❌ Problemas Comuns

**"credentials.json não encontrado"**
→ Arquivo não está na pasta correta

**"Planilha não encontrada"**
→ Não compartilhou com o Service Account

**"ModuleNotFoundError"**
→ Execute: `pip install -r requirements.txt`

---

## 📞 Ajuda Completa

Consulte: `README.md` (guia detalhado)
