# Changelog

Todas as mudanças notáveis do projeto serão documentadas aqui.

## [2.0.0] - 2025-11-22

### 🎯 Reorganização Major

#### Added
- ✨ Estrutura modular completa (`src/`, `app/`, `scripts/`, `tests/`)
- 🤖 GitHub Actions workflows (sync diário, backup semanal, testes)
- 🐳 Docker e docker-compose configurados
- 📝 Sistema de logging estruturado
- ⚙️ Configuração centralizada via `.env`
- 🎯 Makefile com 15+ comandos úteis
- 📚 Documentação básica em `docs/`
- 🧪 Framework de testes com pytest

#### Changed
- 🔄 **BREAKING**: Estrutura de diretórios reorganizada
- 🔄 **BREAKING**: Imports atualizados para `from src.X import Y`
- 🔄 **BREAKING**: Configuração via `.env` obrigatória
- 📦 Atualização do Streamlit para 1.30+
- 🎨 Dashboard com melhor organização de código

#### Fixed
- 🐛 Compatibilidade do dashboard com Streamlit 1.30+
- 🐛 Sistema de query_params corrigido
- 🐛 Conflitos de merge resolvidos

#### Deprecated
- ⚠️ Configurações hardcoded (use `.env`)
- ⚠️ Arquivos Python soltos na raiz

### Estatísticas
- 69 arquivos reorganizados
- +2,032 / -1,698 linhas
- 8 módulos criados
- 93.8% Python, 6.2% Shell

## [1.0.0] - 2024-XX-XX

### Initial Release
- Dashboard básico com Streamlit
- Integração com Google Sheets
- Download de fotos do Transfermarkt
- Sistema de alertas de contratos
