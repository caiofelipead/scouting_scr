.PHONY: help install setup sync photos clean dashboard update all backup test lint format docs docker-build docker-up docker-down docker-logs

# Variáveis
PYTHON := python3
PIP := pip3
STREAMLIT := streamlit

# Cores para output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

help:
	@echo "$(BLUE)Scout Pro - Comandos Disponíveis$(NC)"
	@echo ""
	@echo "$(GREEN)Setup e Instalação:$(NC)"
	@echo "  make install       - Instala todas as dependências"
	@echo "  make setup         - Setup completo inicial"
	@echo "  make validate      - Valida configurações"
	@echo ""
	@echo "$(GREEN)Operações Diárias:$(NC)"
	@echo "  make sync          - Sincroniza dados do Google Sheets"
	@echo "  make photos        - Baixa fotos faltantes do Transfermarkt"
	@echo "  make update        - Atualização completa (sync + photos)"
	@echo "  make dashboard     - Inicia o dashboard Streamlit"
	@echo ""
	@echo "$(GREEN)Manutenção:$(NC)"
	@echo "  make clean         - Remove duplicatas e limpa banco"
	@echo "  make backup        - Cria backup do banco de dados"
	@echo "  make restore       - Restaura último backup"
	@echo ""
	@echo "$(GREEN)Desenvolvimento:$(NC)"
	@echo "  make test          - Roda todos os testes"
	@echo "  make lint          - Verifica qualidade do código"
	@echo "  make format        - Formata código automaticamente"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  make docker-build  - Build da imagem Docker"
	@echo "  make docker-up     - Inicia containers"
	@echo "  make docker-down   - Para containers"
	@echo "  make docker-logs   - Ver logs dos containers"

install:
	@echo "$(BLUE)📦 Instalando dependências...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dependências instaladas$(NC)"

setup:
	@echo "$(BLUE)⚙️  Executando setup inicial...$(NC)"
	$(PYTHON) scripts/setup/initial_setup.py
	@echo "$(GREEN)✅ Setup concluído$(NC)"

validate:
	@echo "$(BLUE)🔍 Validando configurações...$(NC)"
	$(PYTHON) -c "from src.config import Config; Config.validate()"

sync:
	@echo "$(BLUE)🔄 Sincronizando com Google Sheets...$(NC)"
	$(PYTHON) scripts/import_data.py --auto
	@echo "$(GREEN)✅ Sincronização concluída$(NC)"

photos:
	@echo "$(BLUE)📸 Baixando fotos faltantes...$(NC)"
	$(PYTHON) scripts/maintenance/download_photos.py --missing-only
	@echo "$(GREEN)✅ Fotos atualizadas$(NC)"

clean:
	@echo "$(BLUE)🧹 Limpando duplicatas...$(NC)"
	$(PYTHON) scripts/maintenance/limpar_duplicatas.py --auto
	@echo "$(GREEN)✅ Banco limpo$(NC)"

dashboard:
	@echo "$(BLUE)🚀 Iniciando dashboard...$(NC)"
	$(STREAMLIT) run app/dashboard.py

update: sync photos
	@echo "$(GREEN)✅ Atualização completa concluída!$(NC)"

backup:
	@echo "$(BLUE)💾 Criando backup...$(NC)"
	@mkdir -p backups
	@cp scouting.db backups/scouting_$$(date +%Y%m%d_%H%M%S).db 2>/dev/null || echo "$(YELLOW)⚠️  Banco não encontrado$(NC)"
	@echo "$(GREEN)✅ Backup criado$(NC)"

restore:
	@echo "$(BLUE)📥 Restaurando último backup...$(NC)"
	@LATEST=$$(ls -t backups/scouting_*.db 2>/dev/null | head -1); \
	if [ -n "$$LATEST" ]; then \
		cp "$$LATEST" scouting.db && echo "$(GREEN)✅ Restaurado: $$LATEST$(NC)"; \
	else \
		echo "$(RED)❌ Nenhum backup encontrado$(NC)"; \
	fi

test:
	@echo "$(BLUE)🧪 Rodando testes...$(NC)"
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term
	@echo "$(GREEN)✅ Testes concluídos$(NC)"

lint:
	@echo "$(BLUE)🔍 Verificando código...$(NC)"
	@$(PYTHON) -m flake8 src/ app/ scripts/ --max-line-length=100 --ignore=E203,W503 || true
	@echo "$(GREEN)✅ Lint concluído$(NC)"

format:
	@echo "$(BLUE)✨ Formatando código...$(NC)"
	@$(PYTHON) -m black src/ app/ scripts/ --line-length=100 || true
	@$(PYTHON) -m isort src/ app/ scripts/ || true
	@echo "$(GREEN)✅ Código formatado$(NC)"

docker-build:
	@echo "$(BLUE)🐳 Construindo imagem Docker...$(NC)"
	docker build -t scout-pro:latest .
	@echo "$(GREEN)✅ Imagem construída$(NC)"

docker-up:
	@echo "$(BLUE)🐳 Iniciando containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Containers rodando$(NC)"

docker-down:
	@echo "$(BLUE)🐳 Parando containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Containers parados$(NC)"

docker-logs:
	@echo "$(BLUE)🐳 Logs dos containers...$(NC)"
	docker-compose logs -f

all: install update
	@echo "$(GREEN)✅ Setup completo concluído!$(NC)"

dev: format lint test
	@echo "$(GREEN)✅ Verificações concluídas!$(NC)"

clean-temp:
	@echo "$(BLUE)🗑️  Limpando arquivos temporários...$(NC)"
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Limpeza concluída$(NC)"
