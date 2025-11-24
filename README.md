# ⚽ Scout Pro - Sistema de Scouting de Jogadores

> Sistema profissional de monitoramento, análise e gestão de jogadores de futebol

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Sobre o Projeto

Scout Pro é uma plataforma completa para scouting de jogadores, desenvolvida para scouts profissionais e departamentos de análise de futebol. O sistema integra dados do Google Sheets, Transfermarkt e permite avaliações detalhadas com visualizações interativas.

### 🎯 Funcionalidades Principais

- **📊 Dashboard Interativo** - Visualização completa de dados com Streamlit
- **🔄 Sincronização Automática** - Integração com Google Sheets
- **📸 Gestão de Fotos** - 548 fotos de jogadores (77.5% de cobertura)
- **📝 Sistema de Avaliações** - Avaliação multidimensional (Tático, Técnico, Físico, Mental)
- **🏆 Ranking Dinâmico** - Classificação por posição e potencial
- **🆚 Comparador** - Análise head-to-head de jogadores
- **⚽ Shadow Team** - Monte elencos táticos (4-2-3-1)
- **🚨 Sistema de Alertas** - Contratos vencendo e oportunidades

## 🚀 Tecnologias

- **Backend**: Python 3.11+, PostgreSQL (Railway)
- **Frontend**: Streamlit, Plotly, Matplotlib
- **Integrações**: Google Sheets API, Transfermarkt
- **Deploy**: Railway (PostgreSQL), Streamlit Cloud
- **Análise**: Pandas, NumPy, mplsoccer

## 📁 Estrutura do Projeto

```
scouting_scr/
├── 📋 Configuração
│   ├── .env                          # Credenciais (não versionar)
│   ├── .env.example                  # Template de configuração
│   ├── requirements.txt              # Dependências Python
│   └── .gitignore                    # Arquivos ignorados
│
├── 🗄️ Banco de Dados
│   ├── database.py                   # Conexão PostgreSQL
│   └── google_sheets_sync_railway.py # Sincronização Google Sheets
│
├── 🖥️ Interface
│   └── app/
│       └── dashboard.py              # Dashboard principal
│
├── 📸 Mídia
│   └── fotos/                        # Fotos dos jogadores
│       ├── 1417.jpg                  # IDs do PostgreSQL
│       ├── 1418.jpg
│       └── ...
│
├── 🛠️ Scripts
│   ├── scripts/
│   │   ├── maintenance/              # Manutenção do sistema
│   │   └── setup/                    # Scripts de configuração
│   │
│   ├── configurar_sheets.py          # Setup Google Sheets
│   └── health_check.py               # Verificação de saúde
│
└── 📚 Documentação
    ├── README.md                     # Este arquivo
    ├── CHANGELOG.md                  # Histórico de versões
    └── docs/                         # Documentação detalhada
```

## 🔧 Instalação

### Pré-requisitos

- Python 3.11+
- Conta Google (para Google Sheets)
- Conta Railway (para PostgreSQL)

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/caiofelipead/scouting_scr.git
   cd scouting_scr
   ```

2. **Configure o ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite o .env com suas credenciais
   ```

5. **Configure o Google Sheets**
   ```bash
   python configurar_sheets.py
   ```

6. **Execute o dashboard**
   ```bash
   streamlit run app/dashboard.py
   ```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```bash
# PostgreSQL (Railway)
DATABASE_URL=postgresql://user:password@host:port/database

# Google Sheets
GOOGLE_SHEETS_ID=your_spreadsheet_id
GOOGLE_CREDENTIALS_JSON=path/to/credentials.json

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### Google Sheets API

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Ative a Google Sheets API
4. Crie credenciais (Service Account)
5. Baixe o arquivo JSON e salve como `credentials.json`

### PostgreSQL (Railway)

1. Crie uma conta no [Railway](https://railway.app/)
2. Crie um novo projeto PostgreSQL
3. Copie a `DATABASE_URL` para o `.env`

## 📊 Uso do Sistema

### Dashboard Principal

```bash
streamlit run app/dashboard.py
```

O dashboard oferece 7 abas principais:

1. **📊 Visão Geral** - KPIs e estatísticas gerais
2. **👥 Lista de Jogadores** - Navegação e busca
3. **🏆 Ranking** - Top jogadores por avaliação
4. **🆚 Comparador** - Comparação head-to-head
5. **⚽ Shadow Team** - Monte elencos táticos
6. **🚨 Alertas** - Contratos e oportunidades
7. **📈 Análises** - Visualizações avançadas

### Sincronização de Dados

```bash
# Manual
python google_sheets_sync_railway.py

# Automática (configurada no Railway)
# Executa diariamente via workflow
```

## 🎨 Funcionalidades Detalhadas

### Sistema de Avaliações

- **Potencial**: Avaliação geral de 1 a 5
- **Dimensões**: Tático, Técnico, Físico, Mental
- **Histórico**: Acompanhamento de evolução
- **Radar Charts**: Visualização multidimensional

### Gestão de Fotos

- **548 jogadores** com fotos (77.5% de cobertura)
- **Mapeamento automático** via Transfermarkt ID
- **IDs sincronizados** com PostgreSQL
- **Fallback visual** para jogadores sem foto

### Filtros Avançados

- Posição, Liga, Clube, Nacionalidade
- Faixa etária, Status de contrato
- Busca por nome ou ID

## 🔄 Atualização de Dados

### Via Google Sheets

1. Edite a planilha compartilhada
2. No dashboard: **Sidebar > 🔄 Sincronização > Baixar Dados**
3. Dados são atualizados automaticamente

### Via API

```python
from database import ScoutingDatabase

db = ScoutingDatabase()
df = db.get_dados_google_sheets()
db.importar_dados_planilha(df)
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com coverage
pytest --cov=. --cov-report=html

# Teste específico
pytest tests/unit/test_database.py
```

## 📈 Estatísticas do Projeto

- **707 jogadores** cadastrados
- **548 fotos** (77.5% de cobertura)
- **Mapeamento preciso** via Transfermarkt ID
- **PostgreSQL** no Railway
- **Sincronização** com Google Sheets

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para histórico completo de versões.

### Versão 2.0.0 (24/11/2025)

- ✅ Migração completa para PostgreSQL (Railway)
- ✅ Sistema de fotos com mapeamento via Transfermarkt ID
- ✅ 548 fotos corretamente mapeadas (77.5% cobertura)
- ✅ Organização completa do projeto
- ✅ Remoção de arquivos temporários e backups SQLite

## 🐛 Problemas Conhecidos

Nenhum problema crítico no momento. Para reportar bugs:
- Abra uma [Issue no GitHub](https://github.com/caiofelipead/scouting_scr/issues)

## 📄 Licença

Este projeto está sob a licença MIT. Ver [LICENSE](LICENSE) para mais detalhes.

## 👤 Autor

**Caio Felipe**
- GitHub: [@caiofelipead](https://github.com/caiofelipead)
- Scout no Sport Club do Recife

## 🙏 Agradecimentos

- Sport Club do Recife
- CT Lacerda
- Transfermarkt
- StatsBomb / mplsoccer
- Comunidade Python

---

⚽ **Desenvolvido com paixão pelo futebol e análise de dados** ⚽
