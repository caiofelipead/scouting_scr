# 🎯 SCOUT PRO - SISTEMA COMPLETO

**Sistema profissional de scouting com sincronização automática**

---

## 📦 ARQUIVOS INCLUÍDOS

### 🚀 **COMECE AQUI:**

1. **PASSO_A_PASSO.md** ⭐ **LEIA PRIMEIRO!**
   - Guia visual completo
   - Passo a passo numerado
   - Screenshots e exemplos
   - Solução de problemas

2. **GUIA_RAPIDO.md**
   - Versão resumida (15 minutos)
   - Para quem já tem experiência

3. **COMANDOS_RAPIDOS.md**
   - Referência rápida de comandos
   - Workflows comuns
   - Atalhos úteis

---

## 📄 Documentação

- **README.md** - Guia técnico completo e detalhado
- **PASSO_A_PASSO.md** - Tutorial visual para iniciantes
- **GUIA_RAPIDO.md** - Versão acelerada
- **COMANDOS_RAPIDOS.md** - Cheat sheet de comandos

---

## 💻 Código Python

### Core do Sistema:

1. **database.py**
   - Gerencia banco de dados SQLite
   - 6 tabelas normalizadas (jogadores, vínculos, avaliações, etc)
   - Funções de consulta e estatísticas

2. **google_sheets_sync.py** ⭐ **PRINCIPAL**
   - Conecta com Google Sheets API
   - Sincroniza dados automaticamente
   - Baixa fotos do Transfermarkt
   - Menu interativo

3. **dashboard.py**
   - Interface web com Streamlit
   - 4 abas: Visão Geral, Lista, Alertas, Análises
   - Gráficos interativos com Plotly
   - Filtros e exportação

4. **import_data.py**
   - Script de importação inicial
   - Usa google_sheets_sync internamente
   - Execute uma vez no início

5. **checklist.py** ⭐ **ÚTIL**
   - Verifica se tudo está configurado
   - Diagnóstico automático
   - Execute antes de usar o sistema

---

## 📋 Configuração

- **requirements.txt**
  - Lista todas as dependências Python
  - Instale com: `pip install -r requirements.txt`

- **gitignore.txt**
  - Renomeie para `.gitignore` (adicione o ponto no início)
  - Protege credentials.json de commits acidentais

---

## 🎓 ORDEM RECOMENDADA DE LEITURA

### Para iniciantes:

1. ✅ Leia: **PASSO_A_PASSO.md** (completo)
2. ✅ Execute: `pip install -r requirements.txt`
3. ✅ Configure Google Sheets API (seguindo PASSO_A_PASSO.md)
4. ✅ Execute: `python checklist.py`
5. ✅ Execute: `python import_data.py`
6. ✅ Execute: `streamlit run dashboard.py`
7. ✅ Consulte: **COMANDOS_RAPIDOS.md** quando precisar

### Para experientes:

1. ✅ Leia: **GUIA_RAPIDO.md** (15 min)
2. ✅ Configure Google API
3. ✅ Execute: `python checklist.py` e `python import_data.py`
4. ✅ Execute: `streamlit run dashboard.py`

---

## 🗂️ ESTRUTURA FINAL DO PROJETO

Depois de seguir o guia, sua pasta ficará assim:

```
scout-pro/
├── 📄 Documentação
│   ├── README.md
│   ├── PASSO_A_PASSO.md        ← COMECE AQUI!
│   ├── GUIA_RAPIDO.md
│   ├── COMANDOS_RAPIDOS.md
│   └── INDEX.md                 ← Este arquivo
│
├── 💻 Código Python
│   ├── database.py
│   ├── google_sheets_sync.py    ← Principal
│   ├── dashboard.py
│   ├── import_data.py
│   └── checklist.py             ← Verificação
│
├── ⚙️ Configuração
│   ├── requirements.txt
│   ├── .gitignore               (renomeie gitignore.txt)
│   └── credentials.json         ← Você cria no Passo 2
│
└── 📊 Dados (criados automaticamente)
    ├── scouting.db              ← Banco SQLite
    └── fotos/                   ← Fotos dos jogadores
        ├── 1.jpg
        ├── 2.jpg
        └── ...
```

---

## ⚡ INÍCIO RÁPIDO (5 comandos)

```bash
# 1. Instalar
pip install -r requirements.txt

# 2. Configurar Google API (manual - siga PASSO_A_PASSO.md)

# 3. Verificar
python checklist.py

# 4. Importar dados
python import_data.py

# 5. Abrir dashboard
streamlit run dashboard.py
```

---

## 🎯 O QUE O SISTEMA FAZ

### ✅ Sincronização automática
- Conecta com sua planilha do Google Sheets
- Atualiza dados automaticamente (manual ou agendado)
- Baixa fotos do Transfermarkt

### ✅ Dashboard interativo
- Visualizações gráficas (pizza, barras, heatmaps)
- Filtros avançados (posição, liga, idade, status contrato)
- Lista completa de jogadores
- Sistema de alertas automáticos

### ✅ Banco de dados estruturado
- SQLite normalizado (6 tabelas)
- Consultas SQL quando necessário
- Backup e exportação facilitados

### ✅ Alertas inteligentes
- Contratos vencendo em breve
- Prioridades automáticas (alta/média/baixa)
- Central de notificações

---

## 💡 FUNCIONALIDADES PRINCIPAIS

### Dashboard - Aba 1: Visão Geral
- 📊 Distribuição por posição (gráfico pizza)
- 📈 Pirâmide etária (histograma)
- 🌍 Top 10 nacionalidades (barras horizontais)
- ⚠️ Status dos contratos (barras coloridas)

### Dashboard - Aba 2: Lista de Jogadores
- 🔍 Busca por nome
- 🎚️ Filtros múltiplos
- 🔢 Ordenação customizada
- 📥 Exportação CSV

### Dashboard - Aba 3: Central de Alertas
- 🚨 Contratos próximos do vencimento
- 🔴 Prioridade alta (< 6 meses)
- 🟠 Prioridade média (6-12 meses)
- 🔵 Prioridade baixa (> 12 meses)

### Dashboard - Aba 4: Análises
- 📊 Distribuição por liga
- 👥 Idade média por posição
- 🗺️ Heatmap: Nacionalidade × Posição

---

## 🔧 REQUISITOS DO SISTEMA

- ✅ Python 3.8 ou superior
- ✅ Conta Google (para Google Sheets API)
- ✅ Conexão com internet
- ✅ 500MB de espaço em disco (para fotos)

---

## 📞 PRECISA DE AJUDA?

### Passo a passo não funciona?
1. Verifique se seguiu **TODAS** as etapas do PASSO_A_PASSO.md
2. Execute: `python checklist.py` para diagnóstico
3. Consulte a seção "🆘 PROBLEMAS COMUNS" no PASSO_A_PASSO.md

### Quer entender melhor o código?
- Leia: **README.md** (documentação técnica completa)
- Cada arquivo .py tem comentários explicativos

### Comandos básicos esquecidos?
- Consulte: **COMANDOS_RAPIDOS.md**

---

## 🚀 PRÓXIMAS MELHORIAS POSSÍVEIS

Depois que dominar o sistema básico:

1. **Perfis detalhados de jogadores**
   - Página individual para cada jogador
   - Foto grande + radar chart de habilidades
   - Histórico de avaliações

2. **Comparação de jogadores**
   - Comparar 2-3 jogadores lado a lado
   - Gráficos comparativos

3. **Relatórios em PDF**
   - Gerar relatórios de scouting
   - Exportar análises para apresentações

4. **Integração com outras fontes**
   - Wyscout, InStat, Sofascore
   - Enriquecer dados automaticamente

5. **Machine Learning**
   - Similaridade entre jogadores
   - Previsão de valor de mercado
   - Recomendações automáticas

---

## 🏆 CRÉDITOS

**Sistema desenvolvido para:**
- Caio Felipe
- Scout @ Sport Club do Recife
- Analista de Dados - UFMS

**Tecnologias:**
- Python 3.10+
- Streamlit (dashboard)
- Plotly (gráficos)
- SQLite (banco de dados)
- Google Sheets API
- Pandas (análise de dados)

---

## 📝 NOTAS IMPORTANTES

### ⚠️ Segurança:
- **NUNCA** commite `credentials.json` no Git
- Use o arquivo `.gitignore` fornecido
- Mantenha backup do arquivo `scouting.db`

### 🔄 Atualização de dados:
- Manual: `python google_sheets_sync.py` (Opção 2)
- Automática: `python google_sheets_sync.py` (Opção 3)
- Botão no dashboard: "🔄 Atualizar dados do Sheets"

### 💾 Backup:
```bash
# Backup do banco
cp scouting.db backup_$(date +%Y%m%d).db

# Backup das fotos
tar -czf fotos_backup.tar.gz fotos/
```

---

## ✅ CHECKLIST INICIAL

Antes de começar a usar:

- [ ] Todos os arquivos baixados
- [ ] Python 3.8+ instalado
- [ ] `pip install -r requirements.txt` executado
- [ ] Google Sheets API configurada
- [ ] `credentials.json` na pasta correta
- [ ] Planilha compartilhada com Service Account
- [ ] `python checklist.py` passou todos os testes
- [ ] `python import_data.py` executado com sucesso
- [ ] Dashboard abrindo normalmente

**Se todos marcados:** 🎉 Pronto para usar!

---

## 🎯 COMECE AGORA

1. **Abra:** PASSO_A_PASSO.md
2. **Siga:** As 5 etapas numeradas
3. **Execute:** Os comandos na ordem
4. **Pronto:** Sistema funcionando!

**Tempo estimado:** 20-30 minutos (primeira vez)

---

**Versão:** 1.0  
**Data:** 20/11/2025  
**Licença:** Uso pessoal e profissional

**Boa sorte com seu sistema de scouting! ⚽🎯**
