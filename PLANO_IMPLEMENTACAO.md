# 📋 PLANO DE IMPLEMENTAÇÃO - MIGRAÇÃO STREAMLIT → REACT + FASTAPI

## 🎯 Objetivos

1. Migrar 100% das funcionalidades do Streamlit para React + FastAPI
2. Manter o scraping intacto e funcional
3. Preservar todos os dados existentes (707 jogadores, 548 fotos)
4. Melhorar performance e UX
5. Implementar arquitetura escalável

---

## 📊 Estado Atual da Migração

### ✅ Backend (70% completo)

**Implementado:**
- FastAPI app estruturado
- Autenticação JWT
- CRUD Jogadores
- CRUD Avaliações
- CRUD Wishlist
- Conexão PostgreSQL
- Models SQLAlchemy (11 tabelas)
- Schemas Pydantic básicos

**Faltando:**
- Endpoints: Tags, Alertas, Propostas, Notas Rápidas
- Endpoint: Ranking (queries complexas)
- Endpoint: Comparador
- Endpoint: Shadow Team
- Endpoint: Analytics (análise de mercado)
- Endpoint: Scraping (integração)
- Endpoint: Google Sheets Sync
- Endpoint: Busca Avançada
- Middleware de cache (Redis)
- Testes unitários/integração

### ⚠️ Frontend (20% completo)

**Implementado:**
- Estrutura base Vite + React
- Routing com React Router
- Página de Login
- Layout básico
- Axios API client
- Zustand auth store

**Faltando:**
- 90% dos componentes
- Todas as páginas principais
- Gráficos (Recharts/Plotly)
- Visualização de campo (Pitch)
- Filtros avançados
- Tabelas editáveis
- Sistema de cache (React Query completo)
- Testes E2E

---

## 🗓️ FASES DE IMPLEMENTAÇÃO

---

## FASE 1: FUNDAÇÃO BACKEND (Semana 1-2)

### 1.1 Completar Endpoints Críticos

**Prioridade: ALTA**

#### Tarefa 1.1.1: Endpoints de Tags
- [ ] `GET /api/v1/tags`
- [ ] `POST /api/v1/tags`
- [ ] `PUT /api/v1/tags/{id}`
- [ ] `DELETE /api/v1/tags/{id}`
- [ ] `POST /api/v1/jogadores/{id_jogador}/tags/{id_tag}`
- [ ] `DELETE /api/v1/jogadores/{id_jogador}/tags/{id_tag}`

**Arquivos:**
- `backend/app/api/v1/endpoints/tags.py`
- `backend/app/crud/tag.py`

---

#### Tarefa 1.1.2: Endpoints de Ranking
- [ ] `GET /api/v1/ranking`
  - Suporte a `?tipo=top_20|por_posicao|completo`
  - Suporte a `?ordem=media_geral|nota_potencial|...`
- [ ] `GET /api/v1/ranking/posicao/{posicao}`

**Arquivos:**
- `backend/app/api/v1/endpoints/ranking.py`
- `backend/app/crud/ranking.py`
- `backend/app/schemas/ranking.py`

**Query SQL exemplo:**
```python
# crud/ranking.py
def get_ranking(
    db: Session,
    tipo: str = "completo",
    posicao: Optional[str] = None,
    ordem: str = "media_geral",
    limit: int = 20
):
    query = (
        db.query(Jogador)
        .join(Avaliacao, Jogador.id_jogador == Avaliacao.id_jogador)
        .filter(...)
    )

    # Calcular média das últimas 3 avaliações
    # ORDER BY
    # LIMIT

    return query.all()
```

---

#### Tarefa 1.1.3: Endpoints de Comparador
- [ ] `GET /api/v1/comparador?ids=1,2,3`

**Arquivos:**
- `backend/app/api/v1/endpoints/comparador.py`
- `backend/app/schemas/comparador.py`

**Response exemplo:**
```json
{
  "jogadores": [...],
  "radar_data": {
    "categorias": ["Potencial", "Tático", ...],
    "series": [
      {"name": "Neymar", "data": [5.0, 4.5, ...]},
      {"name": "Vinicius", "data": [5.0, 4.5, ...]}
    ]
  }
}
```

---

#### Tarefa 1.1.4: Endpoints de Shadow Team
- [ ] `GET /api/v1/shadow-teams`
- [ ] `GET /api/v1/shadow-teams/{id}`
- [ ] `POST /api/v1/shadow-teams`
- [ ] `PUT /api/v1/shadow-teams/{id}`
- [ ] `DELETE /api/v1/shadow-teams/{id}`

**Arquivos:**
- `backend/app/models/shadow_team.py`
- `backend/app/schemas/shadow_team.py`
- `backend/app/api/v1/endpoints/shadow_team.py`

---

#### Tarefa 1.1.5: Endpoints de Alertas
- [ ] `GET /api/v1/alertas`
- [ ] `POST /api/v1/alertas`
- [ ] `PUT /api/v1/alertas/{id}`
- [ ] `DELETE /api/v1/alertas/{id}`

**Arquivos:**
- `backend/app/api/v1/endpoints/alertas.py`

---

#### Tarefa 1.1.6: Endpoints de Notas Rápidas
- [ ] `GET /api/v1/notas-rapidas/jogador/{id_jogador}`
- [ ] `POST /api/v1/notas-rapidas`
- [ ] `DELETE /api/v1/notas-rapidas/{id}`

**Arquivos:**
- `backend/app/api/v1/endpoints/notas_rapidas.py`

---

#### Tarefa 1.1.7: Endpoints de Analytics
- [ ] `GET /api/v1/analytics/distribuicao`
- [ ] `GET /api/v1/analytics/scatter`

**Arquivos:**
- `backend/app/api/v1/endpoints/analytics.py`
- `backend/app/crud/analytics.py`

---

### 1.2 Integrar Scraping com Backend

**Prioridade: ALTA**

#### Tarefa 1.2.1: Endpoint de Scraping
- [ ] `POST /api/v1/scraping/foto/{id_jogador}`
- [ ] `POST /api/v1/scraping/fotos/lote`

**Arquivos:**
- `backend/app/api/v1/endpoints/scraping.py`
- `backend/app/services/scraper.py` (migrar de `/src/scraping/`)

**Implementação:**
```python
# services/scraper.py
import requests
from bs4 import BeautifulSoup

class TransfermarktScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 ...'
        }

    def scrape_foto(self, transfermarkt_id: int) -> Optional[str]:
        url = f"https://www.transfermarkt.com/player/profil/spieler/{transfermarkt_id}"
        response = requests.get(url, headers=self.headers, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Método 1: Modal img
        img = soup.select_one('img.modal-header-image')
        if img and img.get('src'):
            return img['src']

        # Método 2: Data-src
        # Método 3: Fallback
        return None

    def download_foto(self, url: str, id_jogador: int) -> bool:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            filepath = f"frontend/public/fotos/{id_jogador}.jpg"
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
        return False
```

---

### 1.3 Google Sheets Sync

**Prioridade: MÉDIA**

#### Tarefa 1.3.1: Endpoint de Sincronização
- [ ] `POST /api/v1/sync/google-sheets`

**Arquivos:**
- `backend/app/api/v1/endpoints/sync.py`
- `backend/app/services/google_sheets.py` (migrar de `/src/sync/`)

---

### 1.4 Busca Avançada

**Prioridade: MÉDIA**

#### Tarefa 1.4.1: Endpoints
- [ ] `POST /api/v1/busca-avancada`
- [ ] `GET /api/v1/buscas-salvas`
- [ ] `POST /api/v1/buscas-salvas`
- [ ] `GET /api/v1/buscas-salvas/{id}/executar`
- [ ] `DELETE /api/v1/buscas-salvas/{id}`

**Arquivos:**
- `backend/app/api/v1/endpoints/busca_avancada.py`
- `backend/app/crud/busca.py`

---

### 1.5 Propostas Financeiras

**Prioridade: BAIXA**

#### Tarefa 1.5.1: Endpoints
- [ ] `GET /api/v1/propostas`
- [ ] `POST /api/v1/propostas`
- [ ] `PUT /api/v1/propostas/{id}`
- [ ] `DELETE /api/v1/propostas/{id}`

---

### 1.6 Melhorias de Performance

**Prioridade: MÉDIA**

#### Tarefa 1.6.1: Implementar Cache com Redis
- [ ] Instalar Redis
- [ ] Configurar Redis client
- [ ] Cachear queries de listagem (jogadores, ranking)
- [ ] Invalidação de cache em mutations

**Arquivos:**
- `backend/app/core/cache.py`

**Implementação:**
```python
# core/cache.py
import redis
from typing import Optional
import json

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

def get_cached(key: str) -> Optional[dict]:
    data = redis_client.get(key)
    return json.loads(data) if data else None

def set_cached(key: str, value: dict, ttl: int = 300):
    redis_client.setex(key, ttl, json.dumps(value))

def invalidate_cache(pattern: str):
    for key in redis_client.scan_iter(pattern):
        redis_client.delete(key)
```

---

#### Tarefa 1.6.2: Otimizar Queries com Eager Loading
- [ ] Usar `joinedload()` para evitar N+1 queries
- [ ] Adicionar índices no banco de dados

**Exemplo:**
```python
# Antes (N+1 queries)
jogadores = db.query(Jogador).all()
for j in jogadores:
    print(j.ultima_avaliacao)  # Nova query por jogador!

# Depois (1 query)
from sqlalchemy.orm import joinedload

jogadores = (
    db.query(Jogador)
    .options(joinedload(Jogador.avaliacoes))
    .all()
)
```

---

#### Tarefa 1.6.3: Paginação Cursor-based (opcional)
- [ ] Implementar cursor pagination para listas grandes

---

### 1.7 Testes Backend

**Prioridade: MÉDIA**

#### Tarefa 1.7.1: Testes Unitários
- [ ] Configurar pytest
- [ ] Testes para CRUD layers
- [ ] Testes para endpoints

**Arquivos:**
- `backend/tests/conftest.py`
- `backend/tests/test_jogadores.py`
- `backend/tests/test_avaliacoes.py`

---

## FASE 2: FUNDAÇÃO FRONTEND (Semana 3-4)

### 2.1 Setup Inicial

**Prioridade: ALTA**

#### Tarefa 2.1.1: Configurar React Query
- [ ] Instalar `@tanstack/react-query`
- [ ] Configurar QueryClientProvider
- [ ] Configurar React Query DevTools

**Arquivo:** `frontend/src/main.tsx`

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 min
      cacheTime: 10 * 60 * 1000, // 10 min
      refetchOnWindowFocus: false,
      retry: 1
    }
  }
});

root.render(
  <QueryClientProvider client={queryClient}>
    <App />
    <ReactQueryDevtools />
  </QueryClientProvider>
);
```

---

#### Tarefa 2.1.2: Configurar Toasts (Notificações)
- [ ] Instalar `react-hot-toast`
- [ ] Configurar Toaster global

**Arquivo:** `frontend/src/App.tsx`

```typescript
import { Toaster } from 'react-hot-toast';

function App() {
  return (
    <>
      <Router>...</Router>
      <Toaster position="top-right" />
    </>
  );
}
```

---

#### Tarefa 2.1.3: Completar Zustand Stores
- [ ] `authStore.js` (já existe)
- [ ] `filterStore.js` (criar)
- [ ] `uiStore.js` (criar)

---

#### Tarefa 2.1.4: Configurar React Router
- [ ] Rotas públicas (login)
- [ ] Rotas privadas (dashboard, jogadores, etc)
- [ ] Route guards (ProtectedRoute)

**Arquivo:** `frontend/src/App.tsx`

```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/common/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="jogadores" element={<Jogadores />} />
            <Route path="jogadores/:id" element={<PerfilJogador />} />
            <Route path="wishlist" element={<Wishlist />} />
            <Route path="ranking" element={<Ranking />} />
            <Route path="comparador" element={<Comparador />} />
            <Route path="shadow-team" element={<ShadowTeam />} />
            <Route path="busca-avancada" element={<BuscaAvancada />} />
            <Route path="analytics" element={<AnaliseMercado />} />
            <Route path="alertas" element={<Alertas />} />
            <Route path="financeiro" element={<Financeiro />} />
            <Route path="avaliacao-massiva" element={<AvaliacaoMassiva />} />
          </Route>
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

### 2.2 Componentes Base (Shadcn/UI)

**Prioridade: ALTA**

#### Tarefa 2.2.1: Instalar Shadcn/UI
- [ ] `npx shadcn-ui@latest init`
- [ ] Adicionar componentes:
  - `button`
  - `input`
  - `select`
  - `card`
  - `dialog`
  - `dropdown-menu`
  - `table`
  - `tabs`
  - `badge`
  - `avatar`
  - `progress`
  - `slider`
  - `checkbox`

---

### 2.3 Serviços API (Axios)

**Prioridade: ALTA**

#### Tarefa 2.3.1: Criar Services
- [ ] `services/api.js` (já existe)
- [ ] `services/auth.js`
- [ ] `services/jogadores.js`
- [ ] `services/avaliacoes.js`
- [ ] `services/wishlist.js`
- [ ] `services/tags.js`
- [ ] `services/ranking.js`
- [ ] `services/comparador.js`
- [ ] `services/shadowTeam.js`
- [ ] `services/analytics.js`
- [ ] `services/alertas.js`
- [ ] `services/propostas.js`
- [ ] `services/scraping.js`

---

### 2.4 Hooks Customizados

**Prioridade: MÉDIA**

#### Tarefa 2.4.1: Criar Hooks
- [ ] `useAuth.js`
- [ ] `useJogadores.js`
- [ ] `useAvaliacoes.js`
- [ ] `useWishlist.js`
- [ ] `usePagination.js`
- [ ] `useFilters.js`
- [ ] `useDebounce.js`

---

## FASE 3: COMPONENTES CORE (Semana 5-6)

### 3.1 Layout

**Prioridade: ALTA**

#### Tarefa 3.1.1: Componentes de Layout
- [ ] `Layout.jsx`
- [ ] `Sidebar.jsx` (navegação lateral)
- [ ] `Header.jsx` (barra superior com user menu)
- [ ] `Footer.jsx`

---

### 3.2 Componentes de Jogador

**Prioridade: ALTA**

#### Tarefa 3.2.1: Lista e Cards
- [ ] `JogadorCard.jsx` (card com foto, dados, wishlist)
- [ ] `JogadorTable.jsx` (tabela com TanStack Table)
- [ ] `FilterPanel.jsx` (painel lateral de filtros)
- [ ] `JogadorDetails.jsx` (modal de detalhes rápidos)

---

#### Tarefa 3.2.2: Página de Jogadores
- [ ] `pages/Jogadores.jsx` (componente principal - ver COMPONENTES_REACT.md)

---

#### Tarefa 3.2.3: Perfil Individual
- [ ] `pages/PerfilJogador.jsx`
  - Tabs: Avaliação, Histórico, Evolução, Análise Avançada
  - Sistema de tags
  - Wishlist toggle
  - Notas rápidas
  - Benchmark

---

### 3.3 Componentes de Avaliação

**Prioridade: ALTA**

#### Tarefa 3.3.1: Formulários
- [ ] `AvaliacaoForm.jsx` (formulário com sliders 1-5)
- [ ] `AvaliacaoHistory.jsx` (tabela de histórico)
- [ ] `AvaliacaoEditor.jsx` (tabela editável - TanStack Table)

---

### 3.4 Gráficos

**Prioridade: ALTA**

#### Tarefa 3.4.1: Componentes de Charts
- [ ] `RadarChart.jsx` (Recharts - ver COMPONENTES_REACT.md)
- [ ] `EvolucaoChart.jsx` (Line chart - ver COMPONENTES_REACT.md)
- [ ] `PercentilChart.jsx` (Horizontal bar)
- [ ] `HeatmapChart.jsx` (react-plotly.js)
- [ ] `ScatterChart.jsx` (Recharts)
- [ ] `DistributionChart.jsx` (Histogram)

---

## FASE 4: PÁGINAS PRINCIPAIS (Semana 7-9)

### 4.1 Dashboard (Visão Geral)

**Prioridade: ALTA**

#### Tarefa 4.1.1: Implementar Dashboard
- [ ] Métricas (total jogadores, avaliações, wishlist)
- [ ] Top 10 jogadores (cards)
- [ ] Gráficos de distribuição
- [ ] Alertas recentes

**Arquivo:** `pages/Dashboard.jsx`

---

### 4.2 Wishlist

**Prioridade: ALTA**

#### Tarefa 4.2.1: Implementar Wishlist
- [ ] Filtros por prioridade
- [ ] Cards com informações
- [ ] Editar observações
- [ ] Remover da wishlist

**Arquivo:** `pages/Wishlist.jsx`

---

### 4.3 Ranking

**Prioridade: ALTA**

#### Tarefa 4.3.1: Implementar Ranking
- [ ] 3 modos de visualização:
  - Top 20 (com medalhas 🥇🥈🥉)
  - Por Posição
  - Tabela Completa
- [ ] Filtros: posição, nacionalidade, clube, liga
- [ ] Ordenação: Potencial, Média Geral, Tático, Técnico, Físico, Mental

**Arquivo:** `pages/Ranking.jsx`

---

### 4.4 Comparador

**Prioridade: MÉDIA**

#### Tarefa 4.4.1: Implementar Comparador
- [ ] Seletor de até 3 jogadores
- [ ] Gráfico radar comparativo
- [ ] Tabela lado a lado
- [ ] Dados básicos + avaliações

**Arquivo:** `pages/Comparador.jsx`

---

### 4.5 Shadow Team

**Prioridade: MÉDIA**

#### Tarefa 4.5.1: Implementar Shadow Team
- [ ] Seletor de formação (4-4-2, 4-3-3, 3-5-2, 4-2-3-1)
- [ ] Visualização em campo (SVG - ver COMPONENTES_REACT.md)
- [ ] Drag & Drop de jogadores (opcional)
- [ ] Preenchimento automático
- [ ] Estatísticas do time
- [ ] Salvar/carregar times

**Arquivo:** `pages/ShadowTeam.jsx`

**Componentes:**
- `PitchVisualization.jsx` (já descrito)
- `PlayerPosition.jsx`
- `FormacaoSelector.jsx`

---

### 4.6 Busca Avançada

**Prioridade: MÉDIA**

#### Tarefa 4.6.1: Implementar Busca Avançada
- [ ] Formulário com múltiplos filtros
- [ ] Salvar buscas favoritas
- [ ] Executar buscas salvas
- [ ] Resultados em grid/tabela

**Arquivo:** `pages/BuscaAvancada.jsx`

---

### 4.7 Análise de Mercado

**Prioridade: MÉDIA**

#### Tarefa 4.7.1: Implementar Analytics
- [ ] Gráficos de distribuição (idade, altura, média)
- [ ] Scatter plots comparativos
- [ ] Análise por liga/clube
- [ ] Filtros dinâmicos

**Arquivo:** `pages/AnaliseMercado.jsx`

---

### 4.8 Alertas

**Prioridade: BAIXA**

#### Tarefa 4.8.1: Implementar Alertas
- [ ] Lista de alertas ativos
- [ ] Filtros por prioridade
- [ ] Marcar como inativo
- [ ] Criar novos alertas

**Arquivo:** `pages/Alertas.jsx`

---

### 4.9 Financeiro

**Prioridade: BAIXA**

#### Tarefa 4.9.1: Implementar Financeiro
- [ ] Busca por faixa salarial
- [ ] Gestão de agentes
- [ ] Propostas
- [ ] Cláusulas de rescisão

**Arquivo:** `pages/Financeiro.jsx`

---

### 4.10 Avaliação Massiva

**Prioridade: MÉDIA**

#### Tarefa 4.10.1: Implementar Avaliação Massiva
- [ ] Tabela editável (TanStack Table + React Hook Form)
- [ ] Filtros por posição
- [ ] Salvar em lote
- [ ] Validação de dados

**Arquivo:** `pages/AvaliacaoMassiva.jsx`

**Componente chave:**
- `EditableTable.jsx` (TanStack Table com `meta.updateData`)

---

## FASE 5: FEATURES AVANÇADAS (Semana 10-11)

### 5.1 Sistema de Tags

**Prioridade: MÉDIA**

#### Tarefa 5.1.1: Componentes de Tags
- [ ] `TagManager.jsx` (gerenciar tags)
- [ ] `TagBadge.jsx` (badge com cor)
- [ ] `TagFilter.jsx` (filtro por tag)
- [ ] Modal de criação de tag (nome, cor, categoria)

---

### 5.2 Notas Rápidas

**Prioridade: BAIXA**

#### Tarefa 5.2.1: Componente de Notas
- [ ] `NotaRapida.jsx`
- [ ] Adicionar/editar/deletar notas
- [ ] Tipos de nota (Observação, Contato, etc)

---

### 5.3 Upload de Fotos Manual

**Prioridade: BAIXA**

#### Tarefa 5.3.1: Upload de Foto
- [ ] Componente de upload
- [ ] Endpoint `POST /api/v1/jogadores/{id}/foto`
- [ ] Validação (tamanho, formato)
- [ ] Preview da foto

---

### 5.4 Export/Import

**Prioridade: BAIXA**

#### Tarefa 5.4.1: Funcionalidades de Export
- [ ] Export CSV (jogadores)
- [ ] Export PDF (relatórios)
- [ ] Import CSV (jogadores)

---

## FASE 6: POLIMENTO E TESTES (Semana 12-13)

### 6.1 Responsividade

**Prioridade: ALTA**

#### Tarefa 6.1.1: Mobile-first
- [ ] Testar em mobile (< 768px)
- [ ] Ajustar layout de cards
- [ ] Menu hamburger para sidebar
- [ ] Tabelas responsivas (scroll horizontal)

---

### 6.2 Acessibilidade

**Prioridade: MÉDIA**

#### Tarefa 6.2.1: A11y
- [ ] Navegação por teclado
- [ ] ARIA labels
- [ ] Contraste de cores (WCAG AA)
- [ ] Screen reader support

---

### 6.3 Performance

**Prioridade: ALTA**

#### Tarefa 6.3.1: Otimizações
- [ ] Code splitting (React.lazy)
- [ ] Image lazy loading
- [ ] Virtualização de listas longas (react-window)
- [ ] Memoização de componentes (React.memo)
- [ ] Debounce de filtros
- [ ] Lighthouse audit (score > 90)

---

### 6.4 Testes Frontend

**Prioridade: MÉDIA**

#### Tarefa 6.4.1: Testes E2E
- [ ] Configurar Playwright/Cypress
- [ ] Testes de login
- [ ] Testes de CRUD jogadores
- [ ] Testes de filtros
- [ ] Testes de avaliação

---

### 6.5 Documentação

**Prioridade: MÉDIA**

#### Tarefa 6.5.1: Docs
- [ ] README.md atualizado
- [ ] Guia de setup (dev)
- [ ] Guia de deployment
- [ ] Documentação de componentes (Storybook - opcional)

---

## FASE 7: DEPLOY (Semana 14)

### 7.1 Preparação

**Prioridade: ALTA**

#### Tarefa 7.1.1: Configuração de Produção
- [ ] Variáveis de ambiente (.env.production)
- [ ] Build do frontend (`npm run build`)
- [ ] Otimização de assets (compressão)
- [ ] HTTPS/SSL

---

### 7.2 Backend Deploy

**Prioridade: ALTA**

#### Tarefa 7.2.1: Deploy FastAPI
- [ ] Escolher plataforma (Railway, Render, AWS, etc)
- [ ] Configurar Dockerfile
- [ ] Migrations automáticas (Alembic)
- [ ] Health checks
- [ ] Logging (Sentry - opcional)

**Dockerfile exemplo:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 7.3 Frontend Deploy

**Prioridade: ALTA**

#### Tarefa 7.3.1: Deploy React
- [ ] Escolher plataforma (Vercel, Netlify, CloudFront + S3)
- [ ] Configurar variáveis de ambiente
- [ ] Build estático
- [ ] CDN para assets
- [ ] Configurar redirects (SPA routing)

**Vercel exemplo:**
```json
// vercel.json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ],
  "env": {
    "VITE_API_URL": "https://api.scoutpro.com"
  }
}
```

---

### 7.4 Database

**Prioridade: ALTA**

#### Tarefa 7.4.1: PostgreSQL Produção
- [ ] Migrar de Railway Dev para Prod (ou outro provider)
- [ ] Backups automáticos
- [ ] Connection pooling (PgBouncer)
- [ ] Monitoring (CloudWatch, Datadog)

---

### 7.5 Migração de Dados

**Prioridade: CRÍTICA**

#### Tarefa 7.5.1: Migrar Fotos
- [ ] Upload de 548 fotos para `/frontend/public/fotos/` ou CDN
- [ ] Atualizar `foto_url` no banco de dados

**Script:**
```bash
# Copiar fotos locais para produção
rsync -avz fotos/ user@server:/var/www/scoutpro/public/fotos/

# Ou upload para S3/CloudFront
aws s3 sync fotos/ s3://scoutpro-assets/fotos/
```

---

### 7.6 Monitoramento

**Prioridade: MÉDIA**

#### Tarefa 7.6.1: Setup de Monitoring
- [ ] Backend: Sentry (errors), Prometheus (metrics)
- [ ] Frontend: Google Analytics, Sentry
- [ ] Uptime monitoring (UptimeRobot, Pingdom)
- [ ] Logs centralizados (CloudWatch, Logtail)

---

## FASE 8: PÓS-DEPLOY (Semana 15+)

### 8.1 Treinamento

**Prioridade: ALTA**

#### Tarefa 8.1.1: Onboarding
- [ ] Criar guia de usuário
- [ ] Vídeo tutorial
- [ ] Treinamento da equipe

---

### 8.2 Feedback e Iteração

**Prioridade: ALTA**

#### Tarefa 8.2.1: Coletar Feedback
- [ ] Formulário de feedback
- [ ] Sessões de teste com usuários
- [ ] Ajustes baseados em uso real

---

### 8.3 Features Futuras (Backlog)

**Prioridade: BAIXA**

- [ ] Notificações push (web push)
- [ ] Modo offline (PWA)
- [ ] App mobile (React Native)
- [ ] Integração com Wyscout/InStat
- [ ] Machine Learning (predição de potencial)
- [ ] Relatórios automatizados (PDF)
- [ ] Chat interno (scouts)
- [ ] Versão multi-idioma

---

## 📊 MÉTRICAS DE SUCESSO

### Performance
- [ ] Backend: Response time < 200ms (95th percentile)
- [ ] Frontend: First Contentful Paint < 1.5s
- [ ] Frontend: Time to Interactive < 3s
- [ ] Lighthouse Score > 90

### Funcionalidade
- [ ] 100% das features do Streamlit migradas
- [ ] 0 regressões de dados
- [ ] Scraping funcionando sem erros

### Qualidade
- [ ] Cobertura de testes backend > 70%
- [ ] Cobertura de testes E2E > 50%
- [ ] 0 bugs críticos em produção (primeiro mês)

---

## 🚨 RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Perda de dados na migração | Baixa | Alto | Backups antes da migração, testes em staging |
| Scraping bloqueado por Transfermarkt | Média | Médio | Rate limiting, User-Agent rotation, fallback manual |
| Performance ruim com 700+ jogadores | Baixa | Médio | Paginação, virtualização, cache |
| Atraso no cronograma | Alta | Médio | Priorizar features críticas, MVP first |
| Resistência de usuários ao novo UI | Média | Baixo | Treinamento, manter layout similar |

---

## 🔄 ESTRATÉGIA DE ROLLOUT

### Opção 1: Big Bang (RECOMENDADO)
- Desenvolver tudo em paralelo
- Testar extensivamente em staging
- Deploy único para produção
- Manter Streamlit como backup por 1 mês

### Opção 2: Incremental
- Migrar feature por feature
- Manter Streamlit rodando em paralelo
- Migração gradual de usuários
- Maior complexidade de manutenção

---

## 📅 CRONOGRAMA RESUMIDO

| Fase | Duração | Entrega |
|------|---------|---------|
| Fase 1: Backend | 2 semanas | Endpoints completos |
| Fase 2: Frontend Base | 2 semanas | Estrutura + componentes base |
| Fase 3: Componentes Core | 2 semanas | Jogadores, Avaliações, Gráficos |
| Fase 4: Páginas Principais | 3 semanas | 12 páginas funcionais |
| Fase 5: Features Avançadas | 2 semanas | Tags, Notas, Upload |
| Fase 6: Polimento | 2 semanas | Testes, Performance, A11y |
| Fase 7: Deploy | 1 semana | Produção |
| **TOTAL** | **14 semanas** | **MVP Completo** |

---

## ✅ CHECKLIST FINAL PRÉ-DEPLOY

### Backend
- [ ] Todos os endpoints testados
- [ ] Migrations aplicadas
- [ ] Redis configurado
- [ ] CORS configurado
- [ ] Rate limiting ativo
- [ ] Logging configurado
- [ ] Health checks funcionando

### Frontend
- [ ] Build de produção sem erros
- [ ] Variáveis de ambiente configuradas
- [ ] Todas as páginas funcionais
- [ ] Mobile responsivo
- [ ] Testes E2E passando
- [ ] Lighthouse > 90

### Data
- [ ] Backup completo do banco
- [ ] Fotos migradas
- [ ] Scripts de migração testados

### Infraestrutura
- [ ] SSL/HTTPS configurado
- [ ] DNS configurado
- [ ] Monitoramento ativo
- [ ] Backups automáticos

### Documentação
- [ ] README atualizado
- [ ] API docs (Swagger)
- [ ] Guia de usuário

---

## 🎉 CONCLUSÃO

Esta migração transformará o Scout Pro de um monolito Streamlit em uma aplicação moderna, escalável e de alta performance. O plano prioriza:

1. **Funcionalidade completa**: 100% das features migradas
2. **Scraping intacto**: Manter capacidade de atualização de fotos
3. **Performance**: Melhorias significativas em UX
4. **Escalabilidade**: Arquitetura preparada para crescimento

**Próximos passos imediatos:**
1. Revisar e aprovar este plano
2. Iniciar Fase 1 (Backend)
3. Setup de repositórios Git (feature branches)
4. Configuração de ambientes (dev, staging, prod)

Boa sorte na migração! 🚀
