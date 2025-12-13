# ⚡ Quick Start - Scout Pro

Guia rápido para colocar o sistema no ar em **5 minutos**!

---

## 🚂 1. Configurar Backend no Railway (2 min)

### Você já tem o Postgres! ✅

Agora vamos criar o serviço backend:

1. **No Railway**, clique em **+ New** → **GitHub Repo**
2. Selecione `caiofelipead/scouting_scr`
3. Railway vai criar o serviço automaticamente

### Configurar Variáveis (IMPORTANTE!)

No serviço **backend** que acabou de criar, vá em **Variables**:

#### 1. DATABASE_URL (Conectar ao Postgres)

**Opção A - Mais fácil (Recomendado):**
```
+ New Variable → Add Reference →
Selecione o serviço "Postgres" →
Escolha a variável "DATABASE_URL"
```

**Opção B - Manual:**
```
Vá no serviço Postgres → Variables → DATABASE_URL
Copie o valor completo (clique para revelar)
Cole no backend como nova variável DATABASE_URL
```

#### 2. SECRET_KEY (Segurança JWT)

No seu terminal local:
```bash
openssl rand -hex 32
```

Copie o resultado e adicione como variável:
```
SECRET_KEY = cole_o_valor_gerado_aqui
```

#### 3. CORS_ORIGINS (Opcional - para depois)

```
CORS_ORIGINS = ["http://localhost:3000","http://localhost:5173"]
```

### ✅ Verificar Deploy

1. Railway vai fazer deploy automaticamente
2. Aguarde 2-3 minutos
3. Clique em **Deployments** → veja os logs
4. Quando aparecer ✅ "Deployed", pegue a URL
5. Acesse: `https://sua-url.railway.app/api/docs`
6. Deve aparecer o **Swagger UI**! 🎉

---

## 👤 2. Criar Usuário Admin (1 min)

### Via Railway Shell:

1. No serviço **backend**, clique nos **3 pontinhos** ⋮
2. Selecione **Shell**
3. Execute:

```bash
cd backend && python create_admin.py
```

4. Se aparecer "✅ Usuário admin criado!", está pronto!

**Credenciais criadas:**
- Username: `admin`
- Senha: `admin123`

---

## ⚛️ 3. Configurar Frontend (2 min)

### Local (desenvolvimento):

```bash
cd frontend
npm install
npm run dev
```

Acesse: http://localhost:3000

### Deploy no Vercel:

1. Acesse https://vercel.com
2. **Import Git Repository** → selecione o repo
3. **Root Directory**: `frontend`
4. **Framework Preset**: Vite
5. **Environment Variables**:
   ```
   VITE_API_URL = https://sua-url-backend.railway.app/api/v1
   ```
6. Click **Deploy**

---

## 🎉 4. Testar

### Teste a API:

```bash
# Health check
curl https://sua-url.railway.app/api/health

# Login
curl -X POST https://sua-url.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Deve retornar um **token JWT**!

### Teste o Frontend:

1. Acesse seu app (localhost ou Vercel)
2. Faça login com `admin` / `admin123`
3. Deve redirecionar para o Dashboard! 🎉

---

## 📋 Checklist

- [ ] Postgres já existe no Railway (✅ você já tem)
- [ ] Novo serviço backend criado
- [ ] `DATABASE_URL` configurada (via reference)
- [ ] `SECRET_KEY` gerada e adicionada
- [ ] Deploy do backend OK (logs sem erro)
- [ ] Swagger UI acessível em `/api/docs`
- [ ] Script `create_admin.py` executado
- [ ] Usuário admin criado com sucesso
- [ ] Frontend rodando (local ou Vercel)
- [ ] Login funcionando! 🚀

---

## 🔧 Troubleshooting

### Backend não inicia?

**Ver logs:**
1. Railway → Serviço backend → **Deployments**
2. Clique no último deploy
3. Veja os **Logs**

**Erros comuns:**

❌ `ModuleNotFoundError: No module named 'app'`
```
Solução: Certifique-se que o comando start é:
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

❌ `sqlalchemy.exc.OperationalError: could not connect`
```
Solução: DATABASE_URL está incorreta ou serviço Postgres offline
Verifique se a variável DATABASE_URL foi configurada
```

❌ `Secret key not found`
```
Solução: Adicione a variável SECRET_KEY no Railway
```

### Swagger retorna 404?

```
✅ Correto: https://sua-url.railway.app/api/docs
❌ Errado:  https://sua-url.railway.app/docs
```

### Frontend não conecta?

1. Verifique se `VITE_API_URL` está correta
2. Adicione a URL do frontend em `CORS_ORIGINS` no backend
3. Redeploy do backend

### Login não funciona?

1. Certifique-se que criou o usuário admin
2. Verifique se a API está retornando token:
   ```bash
   curl -X POST https://sua-url/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'
   ```

---

## 📞 URLs Importantes

**API Backend:**
- URL: https://seu-backend.railway.app
- Docs: https://seu-backend.railway.app/api/docs
- Health: https://seu-backend.railway.app/api/health

**Frontend:**
- Local: http://localhost:3000
- Vercel: https://seu-app.vercel.app

**Postgres:**
- Gerenciado pelo Railway (já configurado!)

---

## 🎓 Próximos Passos

1. ✅ **Trocar senha do admin** (primeiro login)
2. ✅ Importar dados existentes (707 jogadores)
3. ✅ Configurar domínio customizado
4. ✅ Adicionar mais usuários
5. ✅ Explorar a API no Swagger

---

## 💡 Dicas

- **Logs em tempo real**: Railway → Deployments → Logs
- **Ver banco de dados**: Railway → Postgres → Database
- **Redeploy**: Railway → Serviço → Settings → Redeploy
- **Variáveis**: Sempre use referências quando possível

---

**Pronto!** 🚀 Seu sistema está no ar em **produção**!

Login: `admin` / `admin123`
