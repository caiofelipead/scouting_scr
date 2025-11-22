# Scout Pro - Sistema de Scouting SCR

> Sistema completo de scouting com dashboard interativo, sincronização automática com Google Sheets e análise de dados.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-Private-lightgrey.svg)

## ✨ Features

- 📊 Dashboard interativo com Streamlit
- 🔄 Sincronização automática com Google Sheets
- 🖼️ Download automático de fotos (Transfermarkt)
- ⚠️ Sistema de alertas de contratos
- 📈 Análises estatísticas e visualizações
- 🔍 Filtros avançados e busca inteligente

## 🚀 Quick Start
```bash
# Clone o repositório
git clone https://github.com/caiofelipead/scouting_scr.git
cd scouting_scr

# Instale as dependências
pip install -r requirements.txt

# Configure as credenciais (veja docs/INSTALLATION.md)
cp .env.example .env

# Importe os dados
python scripts/import_data.py

# Inicie o dashboard
streamlit run app/dashboard.py
```

📖 **[Guia Completo de Instalação](docs/INSTALLATION.md)**  
🔧 **[Solução de Problemas](docs/TROUBLESHOOTING.md)**