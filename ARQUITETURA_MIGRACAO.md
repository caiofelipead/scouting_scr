# 🏗️ ARQUITETURA DE MIGRAÇÃO: STREAMLIT → REACT + FASTAPI

## 📋 Sumário Executivo

**Projeto:** Scout Pro - Sistema de Scouting de Jogadores de Futebol
**Estado Atual:** Monolito Streamlit (4.764 linhas)
**Estado Futuro:** Arquitetura desacoplada React + FastAPI
**Dados:** 707 jogadores, 548 fotos, 11 tabelas PostgreSQL

---

## 1️⃣ ARQUITETURA DE PASTAS

### Estrutura Proposta (Clean Architecture)

```
scouting_scr/
│
├── 📁 backend/                           # FastAPI Backend
│   ├── alembic/                          # Database Migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py                   # Dependencies (JWT, DB)
│   │   │   └── v1/
│   │   │       ├── router.py             # Main API Router
│   │   │       └── endpoints/
│   │   │           ├── auth.py           # POST /login, /register
│   │   │           ├── jogadores.py      # CRUD Jogadores
│   │   │           ├── avaliacoes.py     # CRUD Avaliações
│   │   │           ├── wishlist.py       # CRUD Wishlist
│   │   │           ├── tags.py           # CRUD Tags
│   │   │           ├── alertas.py        # CRUD Alertas
│   │   │           ├── propostas.py      # CRUD Propostas
│   │   │           ├── notas_rapidas.py  # CRUD Notas
│   │   │           ├── ranking.py        # GET /ranking (queries complexas)
│   │   │           ├── comparador.py     # GET /comparar?ids=1,2,3
│   │   │           ├── shadow_team.py    # GET /shadow-teams
│   │   │           ├── analytics.py      # Análise de Mercado
│   │   │           ├── scraping.py       # POST /scrape-foto/{id}
│   │   │           └── sync.py           # POST /sync-google-sheets
│   │   │
│   │   ├── core/
│   │   │   ├── config.py                 # Pydantic Settings (DB_URL, JWT_SECRET)
│   │   │   ├── database.py               # SQLAlchemy Engine + SessionLocal
│   │   │   ├── security.py               # JWT + Password Hashing
│   │   │   └── constants.py              # Enums, Constantes
│   │   │
│   │   ├── models/                       # SQLAlchemy ORM Models
│   │   │   ├── jogador.py                # Model Jogador
│   │   │   ├── avaliacao.py              # Model Avaliacao
│   │   │   ├── wishlist.py               # Model Wishlist
│   │   │   ├── tag.py                    # Model Tag + Associação
│   │   │   ├── alerta.py                 # Model Alerta
│   │   │   ├── proposta.py               # Model Proposta
│   │   │   ├── nota_rapida.py            # Model NotaRapida
│   │   │   ├── busca_salva.py            # Model BuscaSalva
│   │   │   ├── shadow_team.py            # Model ShadowTeam
│   │   │   ├── vinculo_clube.py          # Model VinculoClube
│   │   │   └── usuario.py                # Model Usuario
│   │   │
│   │   ├── schemas/                      # Pydantic Schemas (Request/Response)
│   │   │   ├── jogador.py                # JogadorBase, Create, Update, Response, WithDetails
│   │   │   ├── avaliacao.py              # AvaliacaoBase, Create, Response, EvolutionData
│   │   │   ├── wishlist.py               # WishlistBase, Create, Response
│   │   │   ├── tag.py                    # TagBase, Create, Response
│   │   │   ├── ranking.py                # RankingFilter, RankingResponse
│   │   │   ├── comparador.py             # ComparadorResponse
│   │   │   ├── shadow_team.py            # ShadowTeamCreate, Response, Formacao
│   │   │   ├── analytics.py              # DistributionData, ScatterData
│   │   │   └── usuario.py                # UsuarioBase, Create, Response, Token
│   │   │
│   │   ├── crud/                         # Business Logic Layer
│   │   │   ├── base.py                   # CRUDBase genérico
│   │   │   ├── jogador.py                # get_multi_with_filters, search_advanced
│   │   │   ├── avaliacao.py              # get_evolution_data, get_benchmark
│   │   │   ├── wishlist.py               # add_to_wishlist, remove_from_wishlist
│   │   │   ├── tag.py                    # add_tag_to_jogador
│   │   │   ├── ranking.py                # get_ranking, get_top_20
│   │   │   └── analytics.py              # get_distribution, get_scatter_data
│   │   │
│   │   ├── services/                     # Lógica de Negócio Complexa
│   │   │   ├── scraper.py                # TransfermarktScraper
│   │   │   ├── google_sheets.py          # GoogleSheetsSyncer
│   │   │   ├── photo_manager.py          # DownloadFotos, SaveFotos
│   │   │   ├── logo_manager.py           # GetLogoClube, GetLogoLiga
│   │   │   └── chart_generator.py        # GerarRadar, GerarEvolucao (backend)
│   │   │
│   │   ├── utils/
│   │   │   ├── validators.py             # Validações customizadas
│   │   │   └── formatters.py             # Formatação de dados
│   │   │
│   │   └── main.py                       # FastAPI App + CORS + Middleware
│   │
│   ├── tests/                            # Testes Backend
│   │   ├── test_auth.py
│   │   ├── test_jogadores.py
│   │   ├── test_avaliacoes.py
│   │   └── conftest.py
│   │
│   ├── .env.example                      # Exemplo de variáveis de ambiente
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
│
├── 📁 frontend/                          # React Frontend
│   ├── public/
│   │   ├── fotos/                        # Fotos de jogadores (548 .jpg)
│   │   └── logos/                        # Logos clubes/ligas
│   │
│   ├── src/
│   │   ├── assets/
│   │   │   ├── images/
│   │   │   └── styles/
│   │   │       └── globals.css
│   │   │
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Layout.jsx            # Container principal
│   │   │   │   ├── Sidebar.jsx           # Navegação lateral
│   │   │   │   ├── Header.jsx            # Barra superior
│   │   │   │   └── Footer.jsx
│   │   │   │
│   │   │   ├── jogador/
│   │   │   │   ├── JogadorCard.jsx       # Card com foto + dados básicos
│   │   │   │   ├── JogadorTable.jsx      # Tabela com paginação
│   │   │   │   ├── JogadorFilters.jsx    # Painel de filtros
│   │   │   │   └── JogadorDetails.jsx    # Modal de detalhes
│   │   │   │
│   │   │   ├── avaliacao/
│   │   │   │   ├── AvaliacaoForm.jsx     # Formulário de avaliação
│   │   │   │   ├── AvaliacaoHistory.jsx  # Histórico em tabela
│   │   │   │   └── AvaliacaoEditor.jsx   # Tabela editável (massiva)
│   │   │   │
│   │   │   ├── charts/
│   │   │   │   ├── RadarChart.jsx        # Recharts (avaliação)
│   │   │   │   ├── EvolucaoChart.jsx     # Line chart (evolução)
│   │   │   │   ├── PercentilChart.jsx    # Horizontal bar
│   │   │   │   ├── HeatmapChart.jsx      # Heatmap (react-plotly)
│   │   │   │   ├── ScatterChart.jsx      # Scatter plot
│   │   │   │   └── DistributionChart.jsx # Histogram
│   │   │   │
│   │   │   ├── pitch/
│   │   │   │   ├── PitchVisualization.jsx # Campo de futebol (SVG)
│   │   │   │   ├── PlayerPosition.jsx     # Posição do jogador
│   │   │   │   └── FormacaoSelector.jsx   # Seletor de formação
│   │   │   │
│   │   │   ├── wishlist/
│   │   │   │   ├── WishlistButton.jsx    # Toggle wishlist
│   │   │   │   ├── WishlistCard.jsx      # Card com prioridade
│   │   │   │   └── PriorityBadge.jsx     # Badge colorido
│   │   │   │
│   │   │   ├── tags/
│   │   │   │   ├── TagManager.jsx        # Gerenciar tags
│   │   │   │   ├── TagBadge.jsx          # Badge com cor
│   │   │   │   └── TagFilter.jsx         # Filtro por tag
│   │   │   │
│   │   │   ├── common/
│   │   │   │   ├── Button.jsx            # Botão reutilizável
│   │   │   │   ├── Input.jsx             # Input customizado
│   │   │   │   ├── Select.jsx            # Select customizado
│   │   │   │   ├── Card.jsx              # Card genérico
│   │   │   │   ├── Modal.jsx             # Modal reutilizável
│   │   │   │   ├── Pagination.jsx        # Paginação
│   │   │   │   ├── Loading.jsx           # Spinner
│   │   │   │   ├── ErrorBoundary.jsx     # Error handler
│   │   │   │   └── ProtectedRoute.jsx    # Route guard
│   │   │   │
│   │   │   └── ui/                       # Shadcn/UI components
│   │   │       ├── badge.jsx
│   │   │       ├── button.jsx
│   │   │       ├── card.jsx
│   │   │       ├── dialog.jsx
│   │   │       ├── dropdown-menu.jsx
│   │   │       ├── input.jsx
│   │   │       ├── select.jsx
│   │   │       ├── table.jsx
│   │   │       └── tabs.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Login.jsx                 # Página de login
│   │   │   ├── Dashboard.jsx             # Visão geral (métricas)
│   │   │   ├── Jogadores.jsx             # Lista de jogadores
│   │   │   ├── PerfilJogador.jsx         # Perfil individual (tabs)
│   │   │   ├── Wishlist.jsx              # Wishlist com filtros
│   │   │   ├── Ranking.jsx               # Rankings (Top 20, por posição)
│   │   │   ├── Comparador.jsx            # Comparação de até 3 jogadores
│   │   │   ├── ShadowTeam.jsx            # Shadow Team (campo)
│   │   │   ├── BuscaAvancada.jsx         # Busca avançada + salvar
│   │   │   ├── AnaliseMercado.jsx        # Gráficos de mercado
│   │   │   ├── Alertas.jsx               # Alertas (contratos, etc)
│   │   │   ├── Financeiro.jsx            # Gestão financeira
│   │   │   ├── AvaliacaoMassiva.jsx      # Avaliação em lote
│   │   │   └── NotFound.jsx              # 404
│   │   │
│   │   ├── services/
│   │   │   ├── api.js                    # Axios client + interceptors
│   │   │   ├── auth.js                   # login(), logout(), getMe()
│   │   │   ├── jogadores.js              # getJogadores(), getJogador()
│   │   │   ├── avaliacoes.js             # getAvaliacoes(), createAvaliacao()
│   │   │   ├── wishlist.js               # getWishlist(), addToWishlist()
│   │   │   ├── tags.js                   # getTags(), createTag()
│   │   │   ├── ranking.js                # getRanking(), getTop20()
│   │   │   ├── comparador.js             # compareJogadores()
│   │   │   ├── shadowTeam.js             # getShadowTeams(), createShadowTeam()
│   │   │   ├── analytics.js              # getDistribution(), getScatterData()
│   │   │   └── scraping.js               # scrapeFoto()
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.js                # Hook de autenticação
│   │   │   ├── useJogadores.js           # Hook com React Query
│   │   │   ├── useAvaliacoes.js          # Hook com React Query
│   │   │   ├── useWishlist.js            # Hook com React Query
│   │   │   ├── usePagination.js          # Hook de paginação
│   │   │   ├── useFilters.js             # Hook de filtros
│   │   │   └── useDebounce.js            # Hook de debounce
│   │   │
│   │   ├── store/
│   │   │   ├── authStore.js              # Zustand: user, token, isAuth
│   │   │   ├── filterStore.js            # Zustand: filtros globais
│   │   │   └── uiStore.js                # Zustand: sidebar, modals
│   │   │
│   │   ├── utils/
│   │   │   ├── constants.js              # Constantes (posições, formações)
│   │   │   ├── formatters.js             # Formatação de dados
│   │   │   ├── validators.js             # Validações
│   │   │   └── helpers.js                # Funções auxiliares
│   │   │
│   │   ├── App.jsx                       # Configuração de rotas
│   │   └── main.jsx                      # Entry point
│   │
│   ├── .env.example
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── Dockerfile
│   └── index.html
│
├── 📁 shared/                            # Código compartilhado (opcional)
│   ├── types/                            # TypeScript types
│   └── constants/                        # Constantes compartilhadas
│
├── 📁 docs/                              # Documentação
│   ├── API.md                            # Documentação da API
│   ├── COMPONENTS.md                     # Guia de componentes
│   └── DEPLOYMENT.md                     # Deploy
│
├── 📁 scripts/                           # Scripts utilitários
│   ├── migrate_data.py                   # Migração de dados
│   ├── seed_database.py                  # Popular banco
│   └── scrape_photos.py                  # Scraping em lote
│
├── .gitignore
├── docker-compose.yml                    # Dev environment
├── README.md
└── ARQUITETURA_MIGRACAO.md               # Este arquivo
```

---

## 2️⃣ MAPEAMENTO DE WIDGETS STREAMLIT → REACT

| Streamlit Widget | React Component | Biblioteca |
|-----------------|-----------------|------------|
| `st.sidebar.text_input()` | `<Input />` | Shadcn/UI |
| `st.sidebar.multiselect()` | `<MultiSelect />` | Shadcn/UI |
| `st.sidebar.selectbox()` | `<Select />` | Shadcn/UI |
| `st.sidebar.slider()` | `<Slider />` | Shadcn/UI |
| `st.sidebar.date_input()` | `<DatePicker />` | Shadcn/UI |
| `st.sidebar.checkbox()` | `<Checkbox />` | Shadcn/UI |
| `st.tabs()` | `<Tabs />` | Shadcn/UI |
| `st.columns()` | `<div className="grid">` | Tailwind CSS |
| `st.metric()` | `<Card><MetricValue /></Card>` | Custom |
| `st.dataframe()` | `<Table />` ou `<DataTable />` | Shadcn/UI + TanStack Table |
| `st.data_editor()` | `<EditableTable />` | TanStack Table + React Hook Form |
| `st.plotly_chart()` | `<RadarChart />` | Recharts |
| `st.image()` | `<img />` ou `<Avatar />` | HTML + Shadcn/UI |
| `st.button()` | `<Button />` | Shadcn/UI |
| `st.download_button()` | `<Button onClick={exportCSV}>` | Custom |
| `st.progress()` | `<Progress />` | Shadcn/UI |
| `st.spinner()` | `<Loading />` | Lucide React |
| `st.expander()` | `<Collapsible />` | Shadcn/UI |
| `st.session_state` | Zustand Store | Zustand |
| `st.query_params` | React Router `useSearchParams()` | React Router |
| `st.rerun()` | `queryClient.invalidateQueries()` | React Query |

---

## 3️⃣ BIBLIOTECAS RECOMENDADAS

### Backend (FastAPI)
```txt
# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9

# Validation
pydantic==2.5.3
pydantic-settings==2.1.0

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Web Scraping
beautifulsoup4==4.12.3
requests==2.31.0
selenium==4.16.0 (opcional, se precisar JS)

# Google Sheets
gspread==5.12.4
google-auth==2.26.2

# Utils
python-dotenv==1.0.0
pandas==2.1.4
numpy==1.26.3
```

### Frontend (React)
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.21.1",

    "axios": "^1.6.5",
    "@tanstack/react-query": "^5.17.9",
    "zustand": "^4.4.7",

    "recharts": "^2.10.4",
    "react-plotly.js": "^2.6.0",
    "plotly.js": "^2.28.0",
    "d3": "^7.8.5",

    "lucide-react": "^0.309.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",

    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-progress": "^1.0.3",

    "react-hook-form": "^7.49.3",
    "zod": "^3.22.4",
    "@hookform/resolvers": "^3.3.4",

    "date-fns": "^3.0.6",
    "react-day-picker": "^8.10.0",

    "@tanstack/react-table": "^8.11.3",
    "react-select": "^5.8.0",
    "react-hot-toast": "^2.4.1"
  },
  "devDependencies": {
    "vite": "^5.0.10",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.33",
    "autoprefixer": "^10.4.16",
    "@vitejs/plugin-react": "^4.2.1"
  }
}
```

---

## 4️⃣ GESTÃO DE ESTADO

### Arquitetura Proposta

```
┌──────────────────────────────────────────────┐
│         CAMADA DE ESTADO (FRONTEND)          │
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  1. ZUSTAND STORES (Cliente)           │ │
│  │     - authStore.js                     │ │
│  │       • user, token, isAuth            │ │
│  │       • login(), logout()              │ │
│  │                                        │ │
│  │     - filterStore.js                   │ │
│  │       • posicoes[], clubes[]           │ │
│  │       • idadeMin, idadeMax             │ │
│  │       • applyFilters()                 │ │
│  │                                        │ │
│  │     - uiStore.js                       │ │
│  │       • sidebarOpen, modalOpen         │ │
│  │       • toggleSidebar()                │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  2. REACT QUERY (Server State)         │ │
│  │     - Cache automático                 │ │
│  │     - Refetch automático               │ │
│  │     - Optimistic updates               │ │
│  │                                        │ │
│  │     useQuery(['jogadores'], ...)       │ │
│  │     useQuery(['avaliacoes', id], ...)  │ │
│  │     useMutation(createAvaliacao)       │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  3. REACT HOOK FORM (Form State)       │ │
│  │     - Validação com Zod                │ │
│  │     - Performance otimizada            │ │
│  │     - Integração com Shadcn/UI         │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  4. URL STATE (React Router)           │ │
│  │     - useSearchParams()                │ │
│  │     - Filtros na URL                   │ │
│  │     - Deep linking                     │ │
│  └────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

### Exemplo de Store (Zustand)

```javascript
// store/authStore.js
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuth: false,

      login: (user, token) => {
        localStorage.setItem('token', token);
        set({ user, token, isAuth: true });
      },

      logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuth: false });
      },

      refreshUser: async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
          const response = await api.get('/auth/me');
          set({ user: response.data, isAuth: true });
        } catch (error) {
          get().logout();
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token })
    }
  )
);
```

```javascript
// store/filterStore.js
import { create } from 'zustand';

export const useFilterStore = create((set) => ({
  // Estado dos filtros
  posicoes: [],
  clubes: [],
  ligas: [],
  nacionalidades: [],
  idadeMin: 16,
  idadeMax: 40,
  mediaMin: 0,
  buscaNome: '',

  // Ações
  setPosicoes: (posicoes) => set({ posicoes }),
  setClubes: (clubes) => set({ clubes }),
  setIdadeRange: (min, max) => set({ idadeMin: min, idadeMax: max }),
  setBuscaNome: (nome) => set({ buscaNome: nome }),

  resetFilters: () => set({
    posicoes: [],
    clubes: [],
    ligas: [],
    nacionalidades: [],
    idadeMin: 16,
    idadeMax: 40,
    mediaMin: 0,
    buscaNome: ''
  }),

  // Serializar filtros para API
  getApiFilters: () => {
    const state = set((state) => state);
    return {
      posicoes: state.posicoes.join(','),
      clubes: state.clubes.join(','),
      ligas: state.ligas.join(','),
      idade_min: state.idadeMin,
      idade_max: state.idadeMax,
      media_min: state.mediaMin,
      nome: state.buscaNome
    };
  }
}));
```

---

## 5️⃣ FLUXO DE DADOS COMPLETO

```
┌───────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                           │
│                                                               │
│  [Componente] → [Hook useJogadores] → [React Query]          │
│       ↓                                    ↓                  │
│  [Zustand Store]                    [API Service]            │
│   (filtros)                         (axios.get)              │
│       ↓                                    ↓                  │
│  [URL Params] ←────────────────────────────┘                 │
│                                                               │
└───────────────────────────────────────────────────────────────┘
                            ↓ HTTP Request
                  GET /api/v1/jogadores?posicao=MEI&idade_min=20
                            ↓
┌───────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                          │
│                                                               │
│  [Middleware CORS] → [JWT Validation] → [Router]             │
│                                            ↓                  │
│                                    [Endpoint Handler]         │
│                                            ↓                  │
│                                    [Pydantic Validation]      │
│                                            ↓                  │
│                                    [CRUD Layer]               │
│                                            ↓                  │
│                                    [SQLAlchemy Query]         │
│                                            ↓                  │
│  [PostgreSQL] ←──────────────────────────────                │
│       ↓                                                       │
│  [Models] → [Schemas] → [Response]                           │
│                                                               │
└───────────────────────────────────────────────────────────────┘
                            ↓ HTTP Response
                        JSON (JogadorResponse[])
                            ↓
┌───────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                           │
│                                                               │
│  [React Query Cache] → [Componente] → [Renderização]         │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 6️⃣ SEGURANÇA E AUTENTICAÇÃO

### Fluxo de Autenticação (JWT)

```
┌────────────────────────────────────────────────────────────┐
│  FRONTEND                                                  │
│                                                            │
│  1. Login.jsx                                              │
│     - Input: username, password                            │
│     - Submit → POST /api/v1/auth/login                     │
│                                                            │
│  2. Recebe Resposta                                        │
│     - { access_token: "eyJ...", token_type: "bearer" }     │
│     - authStore.login(user, token)                         │
│     - localStorage.setItem('token', token)                 │
│     - Redirect para /dashboard                             │
│                                                            │
│  3. Requisições Subsequentes (Axios Interceptor)           │
│     - headers: { Authorization: `Bearer ${token}` }        │
│                                                            │
│  4. Refresh Token (opcional)                               │
│     - 401 Unauthorized → POST /auth/refresh                │
│     - Novo token → Retry request                           │
│                                                            │
│  5. Logout                                                 │
│     - authStore.logout()                                   │
│     - localStorage.removeItem('token')                     │
│     - Redirect para /login                                 │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  BACKEND                                                   │
│                                                            │
│  1. POST /auth/login                                       │
│     - Validar username/password (bcrypt)                   │
│     - Gerar JWT (python-jose)                              │
│     - Payload: { sub: user_id, exp: timestamp }            │
│     - Secret: settings.JWT_SECRET                          │
│                                                            │
│  2. Middleware JWT (deps.py)                               │
│     async def get_current_user(token: str = Depends(...))  │
│     - Decode JWT                                           │
│     - Validar expiração                                    │
│     - Buscar usuário no banco                              │
│     - Retornar CurrentUser                                 │
│                                                            │
│  3. Protected Endpoints                                    │
│     @router.get("/jogadores")                              │
│     async def get_jogadores(                               │
│         current_user: Usuario = Depends(get_current_user)  │
│     )                                                      │
└────────────────────────────────────────────────────────────┘
```

### Implementação JWT (Backend)

```python
# core/security.py
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
```

```python
# api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if user is None:
        raise credentials_exception

    return user
```

### Implementação JWT (Frontend)

```javascript
// services/api.js
import axios from 'axios';
import { useAuthStore } from '@/store/authStore';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor (adicionar token)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (tratar 401)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Se 401 e não foi retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Tentar refresh token (se implementado)
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const { data } = await axios.post('/auth/refresh', { refreshToken });

        localStorage.setItem('token', data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;

        return api(originalRequest);
      } catch (refreshError) {
        // Logout se refresh falhar
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

---

**Continua na Parte 2...**
