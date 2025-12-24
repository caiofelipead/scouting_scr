# 🚀 Como Colocar o Scout Pro Online

## Opção 1: Render (RECOMENDADO - Mais Fácil) ⭐

**Vantagens**: Tudo em um lugar, plano gratuito, deploy automático

### Passo a Passo:

1. **Acesse Render**
   - Vá para: https://dashboard.render.com
   - Faça login com sua conta GitHub

2. **Criar Novo Blueprint**
   - Clique em **"New +"** (canto superior direito)
   - Selecione **"Blueprint"**
   - Conecte seu repositório **caiofelipead/scouting_scr**
   - Branch: `claude/streamlit-to-react-fastapi-dY8d9`

3. **Deploy Automático**
   - Render detectará o arquivo `render.yaml` automaticamente
   - Clique em **"Apply"**
   - Serviços criados:
     - ✅ PostgreSQL Database (scout-pro-db)
     - ✅ Redis Cache (scout-pro-redis)
     - ✅ Backend API (scout-pro-backend)
     - ✅ Frontend Web (scout-pro-frontend)

4. **Aguarde o Deploy** (5-10 minutos)
   - Você verá o progresso em tempo real
   - Quando aparecer "Live" em verde = Concluído!

5. **Anotar URLs**
   ```
   Backend:  https://scout-pro-backend.onrender.com
   Frontend: https://scout-pro-frontend.onrender.com
   ```

6. **Executar Migrações** (Apenas primeira vez)
   - No dashboard do Render, clique em **scout-pro-backend**
   - Vá em **"Shell"** (menu lateral)
   - Execute:
     ```bash
     alembic upgrade head
     python create_admin.py
     ```

7. **Acessar sua Aplicação**
   - Abra: https://scout-pro-frontend.onrender.com
   - Login com credenciais criadas no passo 6

---

## Opção 2: Vercel (Frontend) + Render (Backend)

**Vantagens**: Frontend na Vercel (muito rápido), Backend no Render

### Frontend (Vercel):

1. Acesse: https://vercel.com/new
2. Importe o repositório: `caiofelipead/scouting_scr`
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Adicione variável de ambiente:
   ```
   VITE_API_URL=https://scout-pro-backend.onrender.com
   ```
5. Clique em **Deploy**

### Backend (Render):

1. Acesse: https://dashboard.render.com
2. New + > **Web Service**
3. Conecte `caiofelipead/scouting_scr`
4. Configure:
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Dockerfile Path**: `backend/Dockerfile`
5. Adicione PostgreSQL:
   - New + > **PostgreSQL**
   - Nome: `scout-pro-db`
6. Variáveis de ambiente (auto-configuradas via render.yaml)

---

## Opção 3: Railway

**Vantagens**: Interface moderna, plano gratuito inicial

1. Acesse: https://railway.app
2. Login com GitHub
3. **New Project** > Deploy from GitHub repo
4. Selecione: `caiofelipead/scouting_scr`
5. Railway detecta Dockerfile automaticamente
6. Adicione serviços:
   - New > Database > **PostgreSQL**
   - New > Database > **Redis**
7. Configure variáveis de ambiente
8. Deploy automático

---

## Opção 4: Docker Local (Para Testes)

### Requisitos:
- Docker Desktop instalado
- 4GB RAM disponível

### Comandos:

```bash
# 1. Navegar para o projeto
cd /home/user/scouting_scr

# 2. Criar arquivo .env
cp .env.example .env
nano .env  # Edite as senhas!

# 3. Iniciar todos os serviços
docker-compose up -d --build

# 4. Executar migrações
docker-compose exec backend alembic upgrade head

# 5. Criar usuário admin
docker-compose exec backend python create_admin.py

# 6. Acessar aplicação
# Frontend: http://localhost
# Backend:  http://localhost:8000
# Docs:     http://localhost:8000/docs

# Ver logs
docker-compose logs -f

# Parar tudo
docker-compose down
```

---

## 🎯 Recomendação Final

Para colocar online **AGORA** de forma mais fácil:

1. **Use o Render** (Opção 1)
2. Demora ~10 minutos
3. É gratuito
4. Tudo configurado automaticamente via `render.yaml`

### Links Rápidos:
- 🌐 Render: https://dashboard.render.com
- 🚀 Vercel: https://vercel.com/new
- 🚂 Railway: https://railway.app

---

## 📞 Precisa de Ajuda?

Se tiver qualquer erro durante o deploy:
1. Verifique os logs no dashboard da plataforma
2. Consulte o arquivo `DEPLOY.md` para troubleshooting
3. Teste localmente primeiro com Docker

**Boa sorte com o deploy! 🎉**
