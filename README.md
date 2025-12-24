# Scout Pro ⚽

> Sistema profissional de scouting de jogadores de futebol com React + FastAPI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org/)

## 🎯 Features

- 👥 **Gestão de Jogadores** - Cadastro completo de 707+ jogadores
- 📊 **Avaliações 5D** - Sistema de avaliação em 5 dimensões (Técnico, Tático, Físico, Mental, Potencial)
- ⭐ **Wishlist** - Lista de desejos com priorização
- 📈 **Analytics** - Scatter plots e visualizações avançadas
- ⚽ **Shadow Team** - Montagem tática de time ideal (4-3-3, 4-4-2, 3-5-2)
- 🔄 **Comparador** - Comparação lado a lado de jogadores
- 📱 **Dashboard Executivo** - KPIs e métricas em tempo real
- 📄 **Export PDF** - Relatórios profissionais para impressão
- 🔐 **Autenticação JWT** - Sistema seguro de login
- 🌐 **API RESTful** - Backend completo com FastAPI

## 🚀 Deploy Rápido

### Opção 1: Render (Recomendado)

1. Acesse: https://dashboard.render.com
2. New + > **Blueprint**
3. Conecte este repositório
4. Deploy automático em ~10 minutos

**📖 [Guia Completo de Deploy](./DEPLOY_ONLINE.md)**

### Opção 2: Docker Local

```bash
# Clone o repositório
git clone https://github.com/caiofelipead/scouting_scr.git
cd scouting_scr

# Configure variáveis
cp .env.example .env
nano .env  # Edite as senhas

# Inicie os containers
docker-compose up -d --build

# Execute migrações
docker-compose exec backend alembic upgrade head

# Crie usuário admin
docker-compose exec backend python create_admin.py

# Acesse: http://localhost
```

## 📁 Estrutura do Projeto

```
scout-pro/
├── backend/                  # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/             # Endpoints REST
│   │   ├── core/            # Config, Database, Auth
│   │   ├── models/          # SQLAlchemy Models
│   │   ├── schemas/         # Pydantic Schemas
│   │   └── crud/            # Database Operations
│   ├── alembic/             # Database Migrations
│   ├── tests/               # Pytest Tests
│   └── Dockerfile
│
├── frontend/                 # React + TypeScript
│   ├── src/
│   │   ├── api/             # API Services
│   │   ├── components/      # React Components
│   │   ├── pages/           # Page Components
│   │   ├── store/           # Zustand State
│   │   └── lib/             # Utilities
│   ├── tests/               # Vitest Tests
│   └── Dockerfile
│
├── .github/workflows/        # CI/CD Pipeline
├── docker-compose.yml        # Local Development
├── render.yaml               # Render Deployment
└── DEPLOY_ONLINE.md          # Deployment Guide
```

## 🛠️ Tecnologias

### Backend
- **FastAPI** 0.109 - Framework web moderno
- **SQLAlchemy** 2.0 - ORM para PostgreSQL
- **Alembic** - Migrations
- **Pydantic** - Validação de dados
- **JWT** - Autenticação
- **Pytest** - Testes unitários

### Frontend
- **React** 18.3 - UI Library
- **TypeScript** - Type safety
- **TanStack Query** - Server state
- **TanStack Table** - Tabelas avançadas
- **Zustand** - Client state
- **Recharts** - Data visualization
- **Framer Motion** - Animações
- **Tailwind CSS** - Styling
- **Vitest** - Testes unitários

### Infraestrutura
- **PostgreSQL** 15 - Database
- **Redis** 7 - Cache
- **Docker** - Containerização
- **Nginx** - Web server
- **GitHub Actions** - CI/CD

## 📊 Migrações de Dados

Para migrar dados do sistema antigo (Streamlit/SQLite):

```bash
cd backend
python migrate_data.py \
  --source sqlite \
  --db-path ../data/scouting.db \
  --photos-dir ../fotos \
  --target-db "postgresql://user:pass@localhost:5432/scout_pro"
```

**📖 [Guia de Migração](./DEPLOY.md#migração-de-dados)**

## 🧪 Testes

```bash
# Backend
cd backend
pytest tests/ -v --cov=app

# Frontend
cd frontend
npm run test
npm run test:coverage
```

## 📈 CI/CD

Pipeline automático com GitHub Actions:
- ✅ Testes backend (Pytest)
- ✅ Testes frontend (Vitest)
- ✅ Linting (ESLint, flake8)
- ✅ Type checking (TypeScript)
- ✅ Docker build
- ✅ Security scan (Trivy)
- ✅ Deploy automático (Render/Railway)

## 🔐 Segurança

- JWT authentication
- Password hashing (bcrypt)
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection headers
- Environment variables
- Non-root containers
- Security scanning

## 📝 Variáveis de Ambiente

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/scout_pro

# JWT
JWT_SECRET=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://:password@localhost:6379/0

# App
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=http://localhost,https://your-domain.com
```

## 📖 Documentação

- **[Deploy Online](./DEPLOY_ONLINE.md)** - Como colocar online
- **[Deploy Completo](./DEPLOY.md)** - Guia detalhado de infraestrutura
- **[API Docs](http://localhost:8000/docs)** - Swagger UI (quando rodando)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) pela excelente documentação
- [React](https://reactjs.org/) pelo framework poderoso
- [Transfermarkt](https://www.transfermarkt.com/) pelos dados de jogadores
- Comunidade open source

## 📞 Suporte

- 📧 Email: suporte@scoutpro.com
- 🐛 Issues: https://github.com/caiofelipead/scouting_scr/issues
- 📖 Docs: [DEPLOY_ONLINE.md](./DEPLOY_ONLINE.md)

---

**Desenvolvido com ⚽ para scouts profissionais**
