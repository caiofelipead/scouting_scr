# 🚂 Setup Railway - Scout Pro

Guia passo a passo para configurar o backend no Railway.

---

## 📋 Pré-requisitos

- Conta no Railway (https://railway.app)
- PostgreSQL já configurado (✅ você já tem!)
- Repositório GitHub com o código

---

## 🗄️ 1. Configurar Variáveis de Ambiente do Backend

### Opção A: Via Dashboard Railway

1. Acesse seu projeto no Railway
2. Clique no serviço **Postgres** que você já tem
3. Vá na aba **Variables**
4. **Copie o valor de `DATABASE_URL`** (clique para revelar)

5. Agora crie um **novo serviço** para o backend:
   - Clique em **+ New**
   - Selecione **GitHub Repo**
   - Escolha `caiofelipead/scouting_scr`
   - Railway vai detectar automaticamente que é Python

6. Configure as variáveis no **serviço do backend**:

```env
# Essencial - Cole a DATABASE_URL do Postgres
DATABASE_URL=postgresql://postgres:senha@host:porta/railway

# JWT - Gere uma chave forte!
SECRET_KEY=cole_aqui_resultado_de_openssl_rand_hex_32

# CORS - Adicione seu domínio frontend
CORS_ORIGINS=["https://seu-frontend.vercel.app","http://localhost:3000"]

# Opcional
DEBUG=False
APP_NAME=Scout Pro API
APP_VERSION=1.0.0
```

### Opção B: Conectar automaticamente (Recomendado)

1. No **novo serviço do backend**, vá em **Variables**
2. Clique em **+ New Variable**
3. Clique em **Add Reference**
4. Selecione o serviço **Postgres**
5. Escolha a variável **DATABASE_URL**
6. Isso cria uma referência automática! 🎉

---

## 🔐 2. Gerar SECRET_KEY Segura

No seu terminal local:

```bash
# Linux/Mac
openssl rand -hex 32

# Ou Python
python -c "import secrets; print(secrets.token_hex(32))"
```

**Copie o resultado** e adicione como variável `SECRET_KEY` no Railway.

---

## 📁 3. Configurar Build do Backend

Railway precisa saber como executar o FastAPI.

### Criar `railway.json` (já deve existir na raiz)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd backend && pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Ou criar `Procfile` na raiz:

```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🗃️ 4. Criar Tabelas no Banco (Opcional)

As tabelas já existem do Streamlit! Mas se precisar criá-las:

### Opção A: Via código (descomentar em `backend/app/main.py`)

```python
# No lifespan event
Base.metadata.create_all(bind=engine)
```

### Opção B: Via Alembic (Recomendado para produção)

```bash
cd backend

# Instalar Alembic
pip install alembic

# Inicializar
alembic init migrations

# Configurar alembic.ini com DATABASE_URL

# Criar migration
alembic revision --autogenerate -m "Initial tables"

# Aplicar
alembic upgrade head
```

---

## 👤 5. Criar Primeiro Usuário Admin

**IMPORTANTE**: Você precisa criar um usuário para fazer login!

### Via Railway Shell:

1. No serviço backend, clique nos 3 pontos **⋮**
2. Selecione **Shell**
3. Execute:

```bash
python -c "
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.usuario import Usuario

db = SessionLocal()

admin = Usuario(
    username='admin',
    email='admin@scoutpro.com',
    nome='Administrador',
    senha_hash=hash_password('admin123'),
    nivel='admin',
    ativo=True
)

db.add(admin)
db.commit()
print('✅ Usuário admin criado!')
"
```

### Ou crie um script `backend/create_admin.py`:

```python
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.usuario import Usuario

db = SessionLocal()

admin = Usuario(
    username="admin",
    email="admin@scoutpro.com",
    nome="Administrador",
    senha_hash=hash_password("admin123"),
    nivel="admin",
    ativo=True
)

db.add(admin)
db.commit()
print("✅ Usuário admin criado!")
print("Username: admin")
print("Senha: admin123")
```

Execute no Railway Shell:
```bash
cd backend && python create_admin.py
```

---

## 🌐 6. Obter URL do Backend

Após o deploy:

1. Railway vai gerar uma URL tipo: `https://backend-production-xxxx.up.railway.app`
2. Teste acessando: `https://sua-url.railway.app/api/docs`
3. Você deve ver o Swagger UI! 🎉

---

## ⚛️ 7. Configurar Frontend (Vercel)

1. Faça deploy do frontend no Vercel
2. Configure variável de ambiente:

```env
VITE_API_URL=https://sua-url-backend.railway.app/api/v1
```

3. Redeploy

---

## ✅ Checklist Final

- [ ] PostgreSQL já existe no Railway (✅ você já tem)
- [ ] Novo serviço backend criado e conectado ao repo
- [ ] `DATABASE_URL` configurada (referência ao Postgres)
- [ ] `SECRET_KEY` gerada e configurada
- [ ] `CORS_ORIGINS` configurada com URL do frontend
- [ ] `railway.json` ou `Procfile` criado
- [ ] Deploy do backend funcionando
- [ ] `/api/docs` acessível
- [ ] Usuário admin criado
- [ ] Frontend no Vercel conectado à API
- [ ] Login funcionando! 🎉

---

## 🔍 Debug

### Backend não inicia?

**Verifique os logs:**
1. No serviço backend, clique em **Deployments**
2. Clique no deployment mais recente
3. Veja os **Logs**

**Erros comuns:**

1. **`DATABASE_URL` incorreta**
   - Verifique se copiou do Postgres corretamente
   - Formato: `postgresql://user:pass@host:port/db`

2. **Porta não configurada**
   - Railway define `$PORT` automaticamente
   - Use: `--port $PORT` no uvicorn

3. **Módulo não encontrado**
   - Verifique `requirements.txt`
   - Certifique-se de estar em `backend/`

### API retorna 401 (Unauthorized)?

- Certifique-se de criar o usuário admin
- Verifique se a `SECRET_KEY` está configurada

### CORS error no frontend?

- Adicione a URL do frontend Vercel em `CORS_ORIGINS`
- Formato: `["https://seu-app.vercel.app"]`

---

## 📞 Teste a API

```bash
# Health check
curl https://sua-url.railway.app/api/health

# Login
curl -X POST https://sua-url.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Listar jogadores (com token)
curl https://sua-url.railway.app/api/v1/jogadores \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 🎉 Pronto!

Sua API está no ar! 🚀

**URLs importantes:**
- API: https://seu-backend.railway.app
- Docs: https://seu-backend.railway.app/api/docs
- Frontend: https://seu-frontend.vercel.app

**Credenciais padrão:**
- Username: `admin`
- Senha: `admin123`

⚠️ **Lembre de trocar a senha após primeiro login!**
