# 🚀 Scout Pro API - Backend FastAPI

Backend REST API para o Sistema de Scouting de Jogadores de Futebol.

## 📋 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy 2.0** - ORM para PostgreSQL
- **Pydantic** - Validação de dados
- **JWT** - Autenticação segura
- **PostgreSQL** - Banco de dados (Railway)

## 🛠️ Instalação

### 1. Criar ambiente virtual

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas credenciais
```

### 4. Executar servidor

```bash
# Desenvolvimento (com hot reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ou usando Python
python -m app.main
```

A API estará disponível em: **http://localhost:8000**

## 📚 Documentação

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 🔐 Autenticação

A API usa **JWT (JSON Web Tokens)** para autenticação.

### 1. Login

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "usuario": {
    "id": 1,
    "username": "seu_usuario",
    "email": "email@exemplo.com",
    "nivel": "scout"
  }
}
```

### 2. Usar token nas requisições

```bash
GET /api/v1/jogadores
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## 📡 Endpoints Principais

### **Autenticação**
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Registrar usuário
- `GET /api/v1/auth/me` - Dados do usuário autenticado

### **Jogadores**
- `GET /api/v1/jogadores` - Listar jogadores (com filtros)
- `GET /api/v1/jogadores/{id}` - Buscar jogador por ID
- `POST /api/v1/jogadores` - Criar jogador
- `PUT /api/v1/jogadores/{id}` - Atualizar jogador
- `DELETE /api/v1/jogadores/{id}` - Deletar jogador

### **Avaliações**
- `GET /api/v1/avaliacoes/jogador/{id}` - Listar avaliações de um jogador
- `GET /api/v1/avaliacoes/jogador/{id}/ultima` - Última avaliação
- `POST /api/v1/avaliacoes` - Criar avaliação
- `DELETE /api/v1/avaliacoes/{id}` - Deletar avaliação

### **Wishlist**
- `GET /api/v1/wishlist` - Listar wishlist
- `POST /api/v1/wishlist` - Adicionar à wishlist
- `DELETE /api/v1/wishlist/{jogador_id}` - Remover da wishlist
- `GET /api/v1/wishlist/check/{jogador_id}` - Verificar se está na wishlist

## 🗂️ Estrutura do Projeto

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── jogadores.py
│   │           ├── avaliacoes.py
│   │           └── wishlist.py
│   ├── core/
│   │   ├── config.py          # Configurações
│   │   ├── database.py        # Conexão DB
│   │   └── security.py        # JWT & Auth
│   ├── crud/
│   │   ├── jogador.py         # Operações CRUD
│   │   ├── avaliacao.py
│   │   └── wishlist.py
│   ├── models/                # Modelos SQLAlchemy
│   │   ├── jogador.py
│   │   ├── avaliacao.py
│   │   ├── wishlist.py
│   │   └── ...
│   ├── schemas/               # Schemas Pydantic
│   │   ├── jogador.py
│   │   ├── avaliacao.py
│   │   └── ...
│   └── main.py               # Aplicação FastAPI
├── tests/                    # Testes
├── .env                      # Variáveis de ambiente
├── .env.example             # Template
├── requirements.txt         # Dependências
└── README.md               # Este arquivo
```

## 🔧 Desenvolvimento

### Criar nova migration (Alembic)

```bash
alembic revision --autogenerate -m "Descrição da mudança"
alembic upgrade head
```

### Executar testes

```bash
pytest
```

## 🚢 Deploy

### Railway (Recomendado)

1. Criar novo projeto no Railway
2. Conectar repositório GitHub
3. Adicionar PostgreSQL
4. Configurar variáveis de ambiente
5. Deploy automático

### Comando de start

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 📊 Performance

- **Connection pooling** configurado (15 conexões)
- **Queries otimizadas** com `joinedload` (evita N+1)
- **Índices** no banco de dados
- **Paginação** em todos os endpoints de listagem

## 🔒 Segurança

- ✅ Senhas hasheadas com **bcrypt**
- ✅ Tokens JWT com expiração
- ✅ CORS configurado
- ✅ Validação de dados com Pydantic
- ✅ SSL obrigatório no PostgreSQL

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação interativa em `/api/docs`.
