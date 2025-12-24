# 🚂 Deploy no Railway - Scout Pro

## ✅ Por que Railway?
- Interface moderna e intuitiva
- Deploy automático via GitHub
- PostgreSQL e Redis incluídos
- Você já tem a versão paga! 🎉

---

## 🚀 Passo a Passo Completo

### 1️⃣ Acesse o Railway
- Vá para: **https://railway.app/dashboard**
- Faça login com sua conta

### 2️⃣ Criar Novo Projeto
- Clique em **"New Project"**
- Selecione **"Deploy from GitHub repo"**
- Procure por: **caiofelipead/scouting_scr**
- Branch: **claude/streamlit-to-react-fastapi-dY8d9**

### 3️⃣ Railway Detectará Automaticamente
O Railway vai encontrar:
- ✅ `backend/Dockerfile` (Backend FastAPI)
- ✅ `frontend/Dockerfile` (Frontend React)
- ✅ `docker-compose.yml` (mas vamos configurar manual)

### 4️⃣ Adicionar PostgreSQL
No projeto Railway:
- Clique em **"+ New"** (canto superior direito)
- Selecione **"Database"**
- Escolha **"PostgreSQL"**
- Nome: `scout-pro-db`
- Railway cria automaticamente!

### 5️⃣ Adicionar Redis
- Clique em **"+ New"** novamente
- Selecione **"Database"**
- Escolha **"Redis"**
- Nome: `scout-pro-redis`

### 6️⃣ Configurar Backend
Clique no serviço **backend** e vá em **Variables**:

Adicione estas variáveis:

```bash
# Database (copie da aba PostgreSQL > Connect > DATABASE_URL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (copie da aba Redis > Connect > REDIS_URL)
REDIS_URL=${{Redis.REDIS_URL}}

# JWT (gere uma chave segura)
SECRET_KEY=cole-aqui-uma-chave-secreta-de-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://seu-dominio-railway.app,http://localhost:3000
```

**Para gerar SECRET_KEY:**
```bash
# No seu terminal local
openssl rand -hex 32
```

### 7️⃣ Configurar Frontend
Clique no serviço **frontend** e vá em **Variables**:

```bash
# Backend URL (substitua pela URL do seu backend Railway)
VITE_API_URL=https://scout-pro-backend-production.up.railway.app
```

### 8️⃣ Configurar Root Directory
Para cada serviço (backend e frontend):

1. Vá em **Settings**
2. Em **Root Directory**, configure:
   - Backend: `backend`
   - Frontend: `frontend`

### 9️⃣ Deploy!
- Railway fará deploy automaticamente
- Aguarde ~5 minutos
- Quando ficar verde = Deploy completo! ✅

### 🔟 Executar Migrações (Apenas 1ª vez)
No serviço **backend**:
1. Vá em **Settings**
2. Role até **Deployments**
3. Clique nos 3 pontinhos do último deploy
4. Selecione **"View Logs"**
5. Abra um terminal/shell (ou use Railway CLI)

```bash
# Via Railway CLI (se instalado)
railway link
railway run alembic upgrade head
railway run python create_admin.py

# Ou use o console do Railway diretamente
```

---

## 📱 Acessar sua Aplicação

Após o deploy:

1. Clique no serviço **frontend**
2. Vá em **Settings** > **Networking**
3. Clique em **Generate Domain**
4. Você terá algo como: `https://scout-pro-frontend.up.railway.app`

Faça o mesmo para o **backend** para ter:
- `https://scout-pro-backend.up.railway.app`

---

## 🔧 Configuração Rápida via Railway CLI

Se preferir usar linha de comando:

```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Link ao projeto
railway link

# 4. Deploy backend
cd backend
railway up

# 5. Deploy frontend
cd ../frontend
railway up

# 6. Adicionar PostgreSQL
railway add postgresql

# 7. Adicionar Redis
railway add redis

# 8. Executar migrações
railway run alembic upgrade head
railway run python create_admin.py
```

---

## ⚙️ Variáveis de Ambiente Automáticas

O Railway automaticamente injeta:
- `${{Postgres.DATABASE_URL}}` - URL do PostgreSQL
- `${{Redis.REDIS_URL}}` - URL do Redis
- `PORT` - Porta do serviço

Você só precisa adicionar:
- `SECRET_KEY`
- `CORS_ORIGINS`
- `VITE_API_URL`

---

## 🔄 Deploy Automático

Railway faz deploy automático quando você faz push no GitHub!

```bash
git add .
git commit -m "update"
git push
```

E pronto - Railway detecta e faz deploy sozinho! 🚀

---

## 📊 Monitoramento

No Railway você pode ver:
- **Logs em tempo real**
- **Métricas de CPU/RAM**
- **Histórico de deploys**
- **Custos por serviço**

Tudo no dashboard: https://railway.app/dashboard

---

## 💡 Dicas

1. **Domínio Customizado**: Settings > Networking > Custom Domain
2. **Variáveis Compartilhadas**: Use `${{service.VARIABLE}}`
3. **Rollback**: Deployments > Clique no deploy anterior > "Redeploy"
4. **Logs**: Cada serviço tem logs em tempo real
5. **Sleep Mode**: Desabilite em Settings (já que você tem plano pago)

---

## 🆘 Problemas Comuns

### Backend não conecta ao DB
```bash
# Verifique se DATABASE_URL está configurado
railway variables
```

### Frontend não encontra Backend
```bash
# Atualize VITE_API_URL com a URL correta do backend
# E reconfigure CORS_ORIGINS no backend
```

### Migrações falham
```bash
# Execute manualmente
railway run alembic upgrade head
```

---

## ✅ Checklist Final

- [ ] Projeto criado no Railway
- [ ] PostgreSQL adicionado
- [ ] Redis adicionado
- [ ] Backend deployado
- [ ] Frontend deployado
- [ ] Variáveis de ambiente configuradas
- [ ] Domínios gerados
- [ ] Migrações executadas
- [ ] Usuário admin criado
- [ ] CORS atualizado com URL do frontend
- [ ] Aplicação acessível online!

---

**Tempo total: ~15 minutos**

**Tudo pronto para usar o Railway! 🚂💨**
