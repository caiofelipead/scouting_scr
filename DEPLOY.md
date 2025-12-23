# Scout Pro - Guia de Deploy e Infraestrutura

Este documento descreve o processo completo de deploy da aplicação Scout Pro em ambiente de produção.

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Deploy Local (Docker)](#deploy-local-docker)
3. [Migração de Dados](#migração-de-dados)
4. [Deploy em Produção](#deploy-em-produção)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Monitoramento e Logs](#monitoramento-e-logs)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Pré-requisitos

### Software Necessário

- **Docker** 24.0+
- **Docker Compose** 2.20+
- **Node.js** 20+ (para desenvolvimento local)
- **Python** 3.11+ (para desenvolvimento local)
- **PostgreSQL** 15+ (para produção)
- **Git** 2.40+

### Contas de Serviços (Produção)

- GitHub Account (para CI/CD)
- Railway/Render/AWS Account (para hospedagem)
- Google Cloud Account (para Google Sheets API)
- Transfermarkt API Key (opcional)

---

## 🐳 Deploy Local (Docker)

### 1. Clonar Repositório

```bash
git clone https://github.com/seu-usuario/scout-pro.git
cd scout-pro
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar variáveis (use seu editor favorito)
nano .env
```

**Variáveis Críticas:**

```env
# Database
POSTGRES_USER=scoutpro
POSTGRES_PASSWORD=<senha-forte-aqui>
POSTGRES_DB=scout_pro
DATABASE_URL=postgresql://scoutpro:<senha>@db:5432/scout_pro

# JWT
JWT_SECRET=<gerar-com-openssl-rand-hex-32>
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_PASSWORD=<senha-forte-redis>

# Application
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=http://localhost,https://seu-dominio.com
```

### 3. Gerar Secrets Seguros

```bash
# Gerar JWT Secret (32 bytes)
openssl rand -hex 32

# Gerar passwords fortes
openssl rand -base64 24
```

### 4. Iniciar Aplicação

```bash
# Build e start todos os serviços
docker-compose up -d --build

# Verificar logs
docker-compose logs -f

# Verificar status
docker-compose ps
```

### 5. Executar Migrações

```bash
# Executar migrações do Alembic
docker-compose exec backend alembic upgrade head

# Criar usuário admin
docker-compose exec backend python create_admin.py
```

### 6. Acessar Aplicação

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

### 7. Parar Serviços

```bash
# Parar sem remover volumes
docker-compose stop

# Parar e remover containers (mantém volumes)
docker-compose down

# Remover tudo (incluindo volumes - CUIDADO!)
docker-compose down -v
```

---

## 📊 Migração de Dados

### Migrar de Streamlit/SQLite para PostgreSQL

O script `migrate_data.py` realiza a migração completa dos dados.

#### 1. Preparar Dados de Origem

```bash
# Estrutura esperada:
data/
  ├── scouting.db          # Banco SQLite original
  ├── exports/             # CSVs opcionais
  └── raw/                 # Dados brutos

fotos/
  ├── jogador_1.jpg
  ├── jogador_2.jpg
  └── ...
```

#### 2. Validar Dados Antes de Migrar

```bash
cd backend

# Apenas validar (não migra)
python migrate_data.py \
  --source sqlite \
  --db-path ../data/scouting.db \
  --photos-dir ../fotos \
  --validate-only
```

#### 3. Executar Migração

```bash
# Migração completa
python migrate_data.py \
  --source sqlite \
  --db-path ../data/scouting.db \
  --photos-dir ../fotos \
  --target-db "postgresql://scoutpro:password@localhost:5432/scout_pro"

# Verificar logs
tail -f migration_*.log
```

#### 4. Validar Integridade

```bash
# Conectar ao PostgreSQL
docker-compose exec db psql -U scoutpro -d scout_pro

# Contar registros
SELECT 'jogadores' AS tabela, COUNT(*) FROM jogadores
UNION ALL
SELECT 'avaliacoes', COUNT(*) FROM avaliacoes
UNION ALL
SELECT 'wishlist', COUNT(*) FROM wishlist;

# Verificar fotos
SELECT COUNT(*) AS com_foto FROM jogadores WHERE foto_url IS NOT NULL;
SELECT COUNT(*) AS sem_foto FROM jogadores WHERE foto_url IS NULL;
```

---

## 🚀 Deploy em Produção

### Opção 1: Railway

#### 1. Instalar Railway CLI

```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex
```

#### 2. Login e Inicializar

```bash
railway login
railway init
```

#### 3. Criar Serviços

```bash
# PostgreSQL
railway add postgresql

# Redis
railway add redis

# Backend
railway up --service backend

# Frontend
railway up --service frontend
```

#### 4. Configurar Variáveis

```bash
# Via CLI
railway variables set DATABASE_URL="$DATABASE_URL"
railway variables set JWT_SECRET="seu-secret-aqui"

# Ou via Dashboard: https://railway.app/dashboard
```

#### 5. Executar Migrações

```bash
railway run --service backend alembic upgrade head
```

#### 6. Obter URL

```bash
railway domain
# Output: https://scout-pro.up.railway.app
```

---

### Opção 2: Render

#### 1. Conectar Repositório

- Acesse https://dashboard.render.com
- New > Web Service
- Conecte seu repositório GitHub

#### 2. Configurar Backend

```yaml
# render.yaml (na raiz do projeto)
services:
  - type: web
    name: scout-pro-backend
    env: python
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: scout-pro-db
          property: connectionString
      - key: JWT_SECRET
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.11.0

  - type: web
    name: scout-pro-frontend
    env: static
    buildCommand: "cd frontend && npm install && npm run build"
    staticPublishPath: frontend/dist

databases:
  - name: scout-pro-db
    databaseName: scout_pro
    user: scoutpro
```

#### 3. Deploy

```bash
# Commit render.yaml
git add render.yaml
git commit -m "Add Render configuration"
git push origin main

# Deploy automático via webhook
```

---

### Opção 3: AWS (EC2 + RDS)

#### 1. Provisionar Recursos

```bash
# Criar RDS PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier scout-pro-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username scoutpro \
  --master-user-password <senha-forte> \
  --allocated-storage 20

# Criar EC2 Instance
aws ec2 run-instances \
  --image-id ami-xxxxxxxxx \
  --instance-type t3.small \
  --key-name scout-pro-key \
  --security-groups scout-pro-sg
```

#### 2. Instalar Docker na EC2

```bash
# Conectar via SSH
ssh -i scout-pro-key.pem ec2-user@<ip-publico>

# Instalar Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. Deploy via Docker

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/scout-pro.git
cd scout-pro

# Configurar .env
nano .env

# Build e start
docker-compose up -d --build
```

---

## 🔄 CI/CD Pipeline

### Configurar GitHub Actions

O workflow está em `.github/workflows/deploy.yml` e executa automaticamente:

1. **Backend Tests** - Pytest com coverage
2. **Frontend Tests** - Vitest com coverage
3. **Build Docker Images** - Multi-stage build
4. **Security Scan** - Trivy vulnerability scanner
5. **Deploy Production** - Railway (main branch)
6. **Deploy Staging** - Render (develop branch)

### Configurar Secrets no GitHub

```bash
# Via GitHub CLI
gh secret set RAILWAY_TOKEN --body "seu-token-railway"
gh secret set RENDER_DEPLOY_HOOK --body "https://api.render.com/deploy/..."
gh secret set DATABASE_URL --body "postgresql://..."
gh secret set JWT_SECRET --body "seu-jwt-secret"

# Ou via UI: Settings > Secrets and variables > Actions
```

### Trigger Manual

```bash
# Via GitHub CLI
gh workflow run deploy.yml

# Via UI: Actions > Scout Pro CI/CD Pipeline > Run workflow
```

---

## 📈 Monitoramento e Logs

### Logs Locais (Docker)

```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Últimas 100 linhas
docker-compose logs --tail=100 backend
```

### Logs em Produção (Railway)

```bash
# Via CLI
railway logs --service backend

# Via Dashboard: https://railway.app/dashboard > Logs
```

### Health Checks

```bash
# Backend
curl https://seu-dominio.com/health

# Database
docker-compose exec db pg_isready -U scoutpro

# Redis
docker-compose exec redis redis-cli ping
```

### Métricas

```bash
# Uso de recursos (local)
docker stats

# Espaço em disco
docker system df
```

---

## 🔍 Troubleshooting

### Problema 1: Banco não inicia

**Erro**: `FATAL: password authentication failed`

**Solução**:
```bash
# Limpar volumes e reiniciar
docker-compose down -v
docker-compose up -d db
docker-compose logs db
```

### Problema 2: Frontend não conecta ao Backend

**Erro**: `ERR_CONNECTION_REFUSED`

**Solução**:
```bash
# Verificar CORS_ORIGINS no .env
CORS_ORIGINS=http://localhost,http://localhost:3000

# Reiniciar backend
docker-compose restart backend
```

### Problema 3: Migrações falham

**Erro**: `alembic.util.exc.CommandError`

**Solução**:
```bash
# Verificar conexão
docker-compose exec backend python -c "from app.core.database import engine; print(engine.url)"

# Forçar revisão
docker-compose exec backend alembic stamp head
docker-compose exec backend alembic upgrade head
```

### Problema 4: Build do frontend falha

**Erro**: `JavaScript heap out of memory`

**Solução**:
```bash
# Aumentar memória Node.js
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

### Problema 5: Redis não conecta

**Erro**: `NOAUTH Authentication required`

**Solução**:
```bash
# Verificar senha no .env
REDIS_PASSWORD=sua-senha-aqui
REDIS_URL=redis://:sua-senha-aqui@redis:6379/0

# Testar conexão
docker-compose exec redis redis-cli -a sua-senha-aqui ping
```

---

## 📚 Recursos Adicionais

- [Docker Documentation](https://docs.docker.com/)
- [Railway Documentation](https://docs.railway.app/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
- [PostgreSQL Performance](https://www.postgresql.org/docs/current/performance-tips.html)

---

## 🆘 Suporte

Para problemas ou dúvidas:

1. Verificar [Troubleshooting](#troubleshooting)
2. Consultar logs: `docker-compose logs -f`
3. Abrir issue: https://github.com/seu-usuario/scout-pro/issues
4. Contato: suporte@scoutpro.com

---

**Última atualização**: 2025-12-23
**Versão**: 1.0.0
