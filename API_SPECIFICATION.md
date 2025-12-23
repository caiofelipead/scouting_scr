# 🚀 DEFINIÇÃO DE API - SCOUT PRO

## Endpoints RESTful

### Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.scoutpro.com/api/v1
```

---

## 1. AUTENTICAÇÃO

### POST /auth/login
Autenticar usuário e receber JWT token.

**Request:**
```json
{
  "username": "scout@exemplo.com",
  "password": "senha123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id_usuario": 1,
    "username": "scout@exemplo.com",
    "nome": "João Scout",
    "nivel": "scout"
  }
}
```

**Response (401):**
```json
{
  "detail": "Incorrect username or password"
}
```

---

### POST /auth/register
Criar novo usuário.

**Request:**
```json
{
  "username": "novoscout@exemplo.com",
  "email": "novoscout@exemplo.com",
  "password": "senha123",
  "nome": "Novo Scout",
  "nivel": "scout"
}
```

**Response (201):**
```json
{
  "id_usuario": 2,
  "username": "novoscout@exemplo.com",
  "email": "novoscout@exemplo.com",
  "nome": "Novo Scout",
  "nivel": "scout",
  "data_criacao": "2024-01-15T10:30:00Z"
}
```

---

### GET /auth/me
Obter informações do usuário autenticado.

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "id_usuario": 1,
  "username": "scout@exemplo.com",
  "nome": "João Scout",
  "nivel": "scout"
}
```

---

## 2. JOGADORES

### GET /jogadores
Listar jogadores com filtros e paginação.

**Query Params:**
```
?posicao=MEI,ATA
&clube=Flamengo,Palmeiras
&liga=Brasileirão Série A
&nacionalidade=Brasil
&idade_min=18
&idade_max=25
&media_min=3.5
&nome=Neymar
&page=1
&limit=50
&sort_by=media_geral
&order=desc
```

**Response (200):**
```json
{
  "total": 707,
  "page": 1,
  "limit": 50,
  "pages": 15,
  "data": [
    {
      "id_jogador": 1,
      "nome": "Neymar Jr.",
      "nacionalidade": "Brasil",
      "ano_nascimento": 1992,
      "idade_atual": 32,
      "altura": 175,
      "pe_dominante": "Direito",
      "posicao": "ATA",
      "clube": "Al-Hilal",
      "liga_clube": "Saudi Pro League",
      "transfermarkt_id": 68290,
      "foto_url": "/fotos/68290.jpg",
      "logo_clube_url": "/logos/clubes/al-hilal.png",
      "media_geral": 4.5,
      "ultima_avaliacao": {
        "data_avaliacao": "2024-01-10",
        "nota_potencial": 5.0,
        "nota_tatico": 4.5,
        "nota_tecnico": 5.0,
        "nota_fisico": 4.0,
        "nota_mental": 4.5
      },
      "na_wishlist": true,
      "prioridade_wishlist": "alta",
      "tags": [
        { "id_tag": 1, "nome": "Drible", "cor": "#3b82f6" },
        { "id_tag": 5, "nome": "Velocidade", "cor": "#10b981" }
      ],
      "status_contrato": "Ativo",
      "data_fim_contrato": "2025-06-30"
    }
  ]
}
```

---

### GET /jogadores/{id}
Obter detalhes completos de um jogador.

**Response (200):**
```json
{
  "id_jogador": 1,
  "nome": "Neymar Jr.",
  "nacionalidade": "Brasil",
  "ano_nascimento": 1992,
  "idade_atual": 32,
  "altura": 175,
  "pe_dominante": "Direito",
  "transfermarkt_id": 68290,
  "foto_url": "/fotos/68290.jpg",
  "data_criacao": "2023-01-01T00:00:00Z",
  "data_atualizacao": "2024-01-15T10:30:00Z",

  "vinculo_atual": {
    "id_vinculo": 10,
    "clube": "Al-Hilal",
    "liga_clube": "Saudi Pro League",
    "posicao": "ATA",
    "data_inicio_contrato": "2023-08-15",
    "data_fim_contrato": "2025-06-30",
    "status_contrato": "Ativo",
    "salario_anual": 100000000.00,
    "moeda_salario": "EUR",
    "clausula_rescisao": null,
    "agente": "Wagner Ribeiro"
  },

  "avaliacoes": [
    {
      "id": 150,
      "data_avaliacao": "2024-01-10",
      "nota_potencial": 5.0,
      "nota_tatico": 4.5,
      "nota_tecnico": 5.0,
      "nota_fisico": 4.0,
      "nota_mental": 4.5,
      "media_geral": 4.6,
      "observacoes": "Recuperando-se de lesão",
      "avaliador": "João Scout"
    }
  ],

  "wishlist": {
    "id_wishlist": 25,
    "prioridade": "alta",
    "observacao": "Possível contratação para 2025",
    "adicionado_em": "2024-01-01T00:00:00Z"
  },

  "tags": [
    { "id_tag": 1, "nome": "Drible", "cor": "#3b82f6", "categoria": "Técnica" },
    { "id_tag": 5, "nome": "Velocidade", "cor": "#10b981", "categoria": "Física" }
  ],

  "alertas_ativos": [
    {
      "id_alerta": 5,
      "tipo_alerta": "contrato_vencendo",
      "descricao": "Contrato vence em 6 meses",
      "prioridade": "alta",
      "ativo": true
    }
  ],

  "notas_rapidas": [
    {
      "id_nota": 30,
      "tipo": "Observação",
      "conteudo": "Demonstrou interesse em voltar ao Brasil",
      "autor": "João Scout",
      "data_criacao": "2024-01-05T14:20:00Z"
    }
  ]
}
```

---

### POST /jogadores
Criar novo jogador.

**Request:**
```json
{
  "nome": "Endrick",
  "nacionalidade": "Brasil",
  "ano_nascimento": 2006,
  "altura": 173,
  "pe_dominante": "Esquerdo",
  "transfermarkt_id": 658568,
  "vinculo": {
    "clube": "Real Madrid",
    "liga_clube": "La Liga",
    "posicao": "ATA",
    "data_inicio_contrato": "2024-07-01",
    "data_fim_contrato": "2030-06-30"
  }
}
```

**Response (201):**
```json
{
  "id_jogador": 708,
  "nome": "Endrick",
  "nacionalidade": "Brasil",
  "ano_nascimento": 2006,
  "idade_atual": 18,
  "altura": 173,
  "pe_dominante": "Esquerdo",
  "transfermarkt_id": 658568,
  "data_criacao": "2024-01-15T15:00:00Z"
}
```

---

### PUT /jogadores/{id}
Atualizar jogador.

**Request:**
```json
{
  "altura": 174,
  "transfermarkt_id": 658568
}
```

**Response (200):**
```json
{
  "id_jogador": 708,
  "nome": "Endrick",
  "altura": 174,
  "transfermarkt_id": 658568,
  "data_atualizacao": "2024-01-15T15:30:00Z"
}
```

---

### DELETE /jogadores/{id}
Deletar jogador.

**Response (204):** No Content

---

### GET /jogadores/stats/total
Estatísticas gerais.

**Response (200):**
```json
{
  "total_jogadores": 707,
  "total_avaliacoes": 2450,
  "total_wishlist": 35,
  "total_tags": 50,
  "jogadores_com_foto": 548,
  "contratos_vencendo_30_dias": 12,
  "contratos_vencendo_90_dias": 45,
  "media_geral_plataforma": 3.8,
  "distribuicao_por_posicao": {
    "GOL": 45,
    "LAD": 120,
    "ZAG": 95,
    "VOL": 85,
    "MEI": 180,
    "ATA": 182
  },
  "top_5_ligas": [
    { "liga": "Brasileirão Série A", "total": 250 },
    { "liga": "La Liga", "total": 120 },
    { "liga": "Premier League", "total": 110 },
    { "liga": "Serie A", "total": 95 },
    { "liga": "Bundesliga", "total": 80 }
  ]
}
```

---

## 3. AVALIAÇÕES

### GET /avaliacoes/jogador/{id_jogador}
Listar todas as avaliações de um jogador.

**Response (200):**
```json
{
  "jogador_id": 1,
  "total_avaliacoes": 15,
  "data": [
    {
      "id": 150,
      "data_avaliacao": "2024-01-10",
      "nota_potencial": 5.0,
      "nota_tatico": 4.5,
      "nota_tecnico": 5.0,
      "nota_fisico": 4.0,
      "nota_mental": 4.5,
      "media_geral": 4.6,
      "observacoes": "Recuperando-se de lesão",
      "avaliador": "João Scout"
    }
  ]
}
```

---

### GET /avaliacoes/jogador/{id_jogador}/ultima
Obter última avaliação.

**Response (200):**
```json
{
  "id": 150,
  "data_avaliacao": "2024-01-10",
  "nota_potencial": 5.0,
  "nota_tatico": 4.5,
  "nota_tecnico": 5.0,
  "nota_fisico": 4.0,
  "nota_mental": 4.5,
  "media_geral": 4.6,
  "observacoes": "Recuperando-se de lesão",
  "avaliador": "João Scout"
}
```

---

### GET /avaliacoes/jogador/{id_jogador}/evolucao
Obter dados de evolução para gráfico.

**Response (200):**
```json
{
  "jogador_id": 1,
  "evolucao": [
    {
      "data_avaliacao": "2023-06-01",
      "nota_potencial": 4.5,
      "nota_tatico": 4.0,
      "nota_tecnico": 4.5,
      "nota_fisico": 4.0,
      "nota_mental": 4.0,
      "media_geral": 4.2
    },
    {
      "data_avaliacao": "2023-09-15",
      "nota_potencial": 4.5,
      "nota_tatico": 4.5,
      "nota_tecnico": 4.5,
      "nota_fisico": 4.0,
      "nota_mental": 4.5,
      "media_geral": 4.4
    },
    {
      "data_avaliacao": "2024-01-10",
      "nota_potencial": 5.0,
      "nota_tatico": 4.5,
      "nota_tecnico": 5.0,
      "nota_fisico": 4.0,
      "nota_mental": 4.5,
      "media_geral": 4.6
    }
  ]
}
```

---

### POST /avaliacoes
Criar nova avaliação.

**Request:**
```json
{
  "id_jogador": 1,
  "data_avaliacao": "2024-01-15",
  "nota_potencial": 5.0,
  "nota_tatico": 4.5,
  "nota_tecnico": 5.0,
  "nota_fisico": 4.0,
  "nota_mental": 4.5,
  "observacoes": "Excelente performance no último jogo",
  "avaliador": "João Scout"
}
```

**Response (201):**
```json
{
  "id": 151,
  "id_jogador": 1,
  "data_avaliacao": "2024-01-15",
  "nota_potencial": 5.0,
  "nota_tatico": 4.5,
  "nota_tecnico": 5.0,
  "nota_fisico": 4.0,
  "nota_mental": 4.5,
  "media_geral": 4.6,
  "observacoes": "Excelente performance no último jogo",
  "avaliador": "João Scout"
}
```

---

### POST /avaliacoes/massiva
Criar múltiplas avaliações de uma vez (avaliação massiva).

**Request:**
```json
{
  "avaliacoes": [
    {
      "id_jogador": 1,
      "data_avaliacao": "2024-01-15",
      "nota_potencial": 5.0,
      "nota_tatico": 4.5,
      "nota_tecnico": 5.0,
      "nota_fisico": 4.0,
      "nota_mental": 4.5
    },
    {
      "id_jogador": 2,
      "data_avaliacao": "2024-01-15",
      "nota_potencial": 4.0,
      "nota_tatico": 4.0,
      "nota_tecnico": 3.5,
      "nota_fisico": 4.5,
      "nota_mental": 3.5
    }
  ],
  "avaliador": "João Scout"
}
```

**Response (201):**
```json
{
  "total_criadas": 2,
  "avaliacoes": [
    { "id": 151, "id_jogador": 1, "media_geral": 4.6 },
    { "id": 152, "id_jogador": 2, "media_geral": 3.9 }
  ]
}
```

---

### PUT /avaliacoes/{id}
Atualizar avaliação existente.

**Request:**
```json
{
  "nota_fisico": 4.5,
  "observacoes": "Melhorou condicionamento físico"
}
```

**Response (200):**
```json
{
  "id": 150,
  "id_jogador": 1,
  "data_avaliacao": "2024-01-10",
  "nota_potencial": 5.0,
  "nota_tatico": 4.5,
  "nota_tecnico": 5.0,
  "nota_fisico": 4.5,
  "nota_mental": 4.5,
  "media_geral": 4.7,
  "observacoes": "Melhorou condicionamento físico",
  "avaliador": "João Scout"
}
```

---

### DELETE /avaliacoes/{id}
Deletar avaliação.

**Response (204):** No Content

---

## 4. WISHLIST

### GET /wishlist
Listar todos os jogadores da wishlist.

**Query Params:**
```
?prioridade=alta,media
```

**Response (200):**
```json
{
  "total": 35,
  "data": [
    {
      "id_wishlist": 25,
      "jogador": {
        "id_jogador": 1,
        "nome": "Neymar Jr.",
        "posicao": "ATA",
        "clube": "Al-Hilal",
        "idade_atual": 32,
        "media_geral": 4.6,
        "foto_url": "/fotos/68290.jpg"
      },
      "prioridade": "alta",
      "observacao": "Possível contratação para 2025",
      "adicionado_em": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### POST /wishlist
Adicionar jogador à wishlist.

**Request:**
```json
{
  "id_jogador": 10,
  "prioridade": "media",
  "observacao": "Monitorar próximos 6 meses"
}
```

**Response (201):**
```json
{
  "id_wishlist": 36,
  "id_jogador": 10,
  "prioridade": "media",
  "observacao": "Monitorar próximos 6 meses",
  "adicionado_em": "2024-01-15T16:00:00Z"
}
```

---

### PUT /wishlist/{id_wishlist}
Atualizar entrada da wishlist.

**Request:**
```json
{
  "prioridade": "alta",
  "observacao": "Negociação em andamento"
}
```

**Response (200):**
```json
{
  "id_wishlist": 36,
  "id_jogador": 10,
  "prioridade": "alta",
  "observacao": "Negociação em andamento",
  "adicionado_em": "2024-01-15T16:00:00Z"
}
```

---

### DELETE /wishlist/{id_jogador}
Remover jogador da wishlist (por ID do jogador).

**Response (204):** No Content

---

### GET /wishlist/check/{id_jogador}
Verificar se jogador está na wishlist.

**Response (200):**
```json
{
  "na_wishlist": true,
  "id_wishlist": 36,
  "prioridade": "alta"
}
```

---

## 5. RANKING

### GET /ranking
Obter ranking de jogadores.

**Query Params:**
```
?tipo=top_20|por_posicao|completo
&posicao=ATA
&ordem=media_geral|nota_potencial|nota_tatico|nota_tecnico|nota_fisico|nota_mental
&limit=20
```

**Response (200):**
```json
{
  "tipo": "top_20",
  "criterio_ordem": "media_geral",
  "total": 707,
  "data": [
    {
      "posicao_ranking": 1,
      "id_jogador": 1,
      "nome": "Neymar Jr.",
      "clube": "Al-Hilal",
      "posicao": "ATA",
      "idade_atual": 32,
      "nacionalidade": "Brasil",
      "media_geral": 4.8,
      "nota_potencial": 5.0,
      "nota_tatico": 4.5,
      "nota_tecnico": 5.0,
      "nota_fisico": 4.5,
      "nota_mental": 5.0,
      "foto_url": "/fotos/68290.jpg",
      "medalha": "🥇"
    },
    {
      "posicao_ranking": 2,
      "id_jogador": 50,
      "nome": "Vinicius Jr.",
      "clube": "Real Madrid",
      "posicao": "ATA",
      "idade_atual": 23,
      "nacionalidade": "Brasil",
      "media_geral": 4.7,
      "nota_potencial": 5.0,
      "nota_tatico": 4.5,
      "nota_tecnico": 4.5,
      "nota_fisico": 5.0,
      "nota_mental": 4.5,
      "foto_url": "/fotos/371998.jpg",
      "medalha": "🥈"
    }
  ]
}
```

---

### GET /ranking/posicao/{posicao}
Ranking por posição específica.

**Response (200):**
```json
{
  "posicao": "ATA",
  "total_jogadores": 182,
  "data": [
    {
      "posicao_ranking": 1,
      "id_jogador": 1,
      "nome": "Neymar Jr.",
      "media_geral": 4.8
    }
  ]
}
```

---

## 6. COMPARADOR

### GET /comparador
Comparar até 3 jogadores.

**Query Params:**
```
?ids=1,50,100
```

**Response (200):**
```json
{
  "total_jogadores": 3,
  "jogadores": [
    {
      "id_jogador": 1,
      "nome": "Neymar Jr.",
      "posicao": "ATA",
      "clube": "Al-Hilal",
      "idade_atual": 32,
      "altura": 175,
      "pe_dominante": "Direito",
      "foto_url": "/fotos/68290.jpg",
      "ultima_avaliacao": {
        "nota_potencial": 5.0,
        "nota_tatico": 4.5,
        "nota_tecnico": 5.0,
        "nota_fisico": 4.5,
        "nota_mental": 5.0,
        "media_geral": 4.8
      }
    },
    {
      "id_jogador": 50,
      "nome": "Vinicius Jr.",
      "posicao": "ATA",
      "clube": "Real Madrid",
      "idade_atual": 23,
      "altura": 176,
      "pe_dominante": "Direito",
      "foto_url": "/fotos/371998.jpg",
      "ultima_avaliacao": {
        "nota_potencial": 5.0,
        "nota_tatico": 4.5,
        "nota_tecnico": 4.5,
        "nota_fisico": 5.0,
        "nota_mental": 4.5,
        "media_geral": 4.7
      }
    }
  ],
  "radar_data": {
    "categorias": ["Potencial", "Tático", "Técnico", "Físico", "Mental"],
    "series": [
      {
        "name": "Neymar Jr.",
        "data": [5.0, 4.5, 5.0, 4.5, 5.0]
      },
      {
        "name": "Vinicius Jr.",
        "data": [5.0, 4.5, 4.5, 5.0, 4.5]
      }
    ]
  }
}
```

---

## 7. SHADOW TEAM

### GET /shadow-teams
Listar todos os shadow teams salvos.

**Response (200):**
```json
{
  "total": 5,
  "data": [
    {
      "id_shadow_team": 1,
      "nome": "Time Ideal - 4-3-3",
      "formacao": "4-3-3",
      "criado_por": "João Scout",
      "data_criacao": "2024-01-10T00:00:00Z",
      "jogadores_count": 11,
      "media_geral_time": 4.2
    }
  ]
}
```

---

### GET /shadow-teams/{id}
Obter detalhes do shadow team.

**Response (200):**
```json
{
  "id_shadow_team": 1,
  "nome": "Time Ideal - 4-3-3",
  "formacao": "4-3-3",
  "criado_por": "João Scout",
  "data_criacao": "2024-01-10T00:00:00Z",
  "jogadores": [
    {
      "posicao_campo": "GOL",
      "coordenada_x": 60,
      "coordenada_y": 5,
      "jogador": {
        "id_jogador": 100,
        "nome": "Alisson Becker",
        "clube": "Liverpool",
        "media_geral": 4.5,
        "foto_url": "/fotos/105470.jpg"
      }
    },
    {
      "posicao_campo": "LAE",
      "coordenada_x": 80,
      "coordenada_y": 15,
      "jogador": {
        "id_jogador": 50,
        "nome": "Marcelo",
        "clube": "Fluminense",
        "media_geral": 4.0,
        "foto_url": "/fotos/34155.jpg"
      }
    }
  ],
  "estatisticas": {
    "media_geral": 4.2,
    "media_potencial": 4.5,
    "media_tatico": 4.0,
    "media_tecnico": 4.3,
    "media_fisico": 4.1,
    "media_mental": 4.2,
    "idade_media": 26.5,
    "altura_media": 180
  }
}
```

---

### POST /shadow-teams
Criar novo shadow team.

**Request:**
```json
{
  "nome": "Time Ideal - 4-4-2",
  "formacao": "4-4-2",
  "jogadores": [
    {
      "posicao_campo": "GOL",
      "coordenada_x": 60,
      "coordenada_y": 5,
      "id_jogador": 100
    },
    {
      "posicao_campo": "LAD",
      "coordenada_x": 80,
      "coordenada_y": 85,
      "id_jogador": 101
    }
  ]
}
```

**Response (201):**
```json
{
  "id_shadow_team": 6,
  "nome": "Time Ideal - 4-4-2",
  "formacao": "4-4-2",
  "criado_por": "João Scout",
  "data_criacao": "2024-01-15T17:00:00Z"
}
```

---

### PUT /shadow-teams/{id}
Atualizar shadow team.

**Request:**
```json
{
  "nome": "Time Ideal Atualizado",
  "jogadores": [...]
}
```

**Response (200):** Shadow team atualizado

---

### DELETE /shadow-teams/{id}
Deletar shadow team.

**Response (204):** No Content

---

## 8. TAGS

### GET /tags
Listar todas as tags.

**Response (200):**
```json
{
  "total": 50,
  "data": [
    {
      "id_tag": 1,
      "nome": "Drible",
      "cor": "#3b82f6",
      "categoria": "Técnica",
      "total_jogadores": 120
    },
    {
      "id_tag": 5,
      "nome": "Velocidade",
      "cor": "#10b981",
      "categoria": "Física",
      "total_jogadores": 95
    }
  ]
}
```

---

### POST /tags
Criar nova tag.

**Request:**
```json
{
  "nome": "Finalização",
  "cor": "#f59e0b",
  "categoria": "Técnica"
}
```

**Response (201):**
```json
{
  "id_tag": 51,
  "nome": "Finalização",
  "cor": "#f59e0b",
  "categoria": "Técnica"
}
```

---

### POST /jogadores/{id_jogador}/tags/{id_tag}
Adicionar tag a um jogador.

**Response (200):**
```json
{
  "message": "Tag adicionada com sucesso",
  "jogador_id": 1,
  "tag_id": 51
}
```

---

### DELETE /jogadores/{id_jogador}/tags/{id_tag}
Remover tag de um jogador.

**Response (204):** No Content

---

## 9. ALERTAS

### GET /alertas
Listar alertas ativos.

**Query Params:**
```
?prioridade=alta,media
&ativo=true
```

**Response (200):**
```json
{
  "total": 25,
  "data": [
    {
      "id_alerta": 5,
      "jogador": {
        "id_jogador": 1,
        "nome": "Neymar Jr.",
        "clube": "Al-Hilal"
      },
      "tipo_alerta": "contrato_vencendo",
      "descricao": "Contrato vence em 6 meses",
      "prioridade": "alta",
      "ativo": true,
      "data_criacao": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### POST /alertas
Criar novo alerta.

**Request:**
```json
{
  "id_jogador": 10,
  "tipo_alerta": "oportunidade_mercado",
  "descricao": "Valor de mercado caiu 20%",
  "prioridade": "media"
}
```

**Response (201):**
```json
{
  "id_alerta": 26,
  "id_jogador": 10,
  "tipo_alerta": "oportunidade_mercado",
  "descricao": "Valor de mercado caiu 20%",
  "prioridade": "media",
  "ativo": true,
  "data_criacao": "2024-01-15T18:00:00Z"
}
```

---

### PUT /alertas/{id}
Atualizar alerta (ex: marcar como inativo).

**Request:**
```json
{
  "ativo": false
}
```

**Response (200):** Alerta atualizado

---

### DELETE /alertas/{id}
Deletar alerta.

**Response (204):** No Content

---

## 10. NOTAS RÁPIDAS

### GET /notas-rapidas/jogador/{id_jogador}
Listar notas rápidas de um jogador.

**Response (200):**
```json
{
  "jogador_id": 1,
  "total": 10,
  "data": [
    {
      "id_nota": 30,
      "tipo": "Observação",
      "conteudo": "Demonstrou interesse em voltar ao Brasil",
      "autor": "João Scout",
      "data_criacao": "2024-01-05T14:20:00Z"
    }
  ]
}
```

---

### POST /notas-rapidas
Criar nota rápida.

**Request:**
```json
{
  "id_jogador": 1,
  "tipo": "Observação",
  "conteudo": "Conversei com agente - possível negociação"
}
```

**Response (201):**
```json
{
  "id_nota": 31,
  "id_jogador": 1,
  "tipo": "Observação",
  "conteudo": "Conversei com agente - possível negociação",
  "autor": "João Scout",
  "data_criacao": "2024-01-15T19:00:00Z"
}
```

---

### DELETE /notas-rapidas/{id}
Deletar nota rápida.

**Response (204):** No Content

---

## 11. ANÁLISE DE MERCADO

### GET /analytics/distribuicao
Obter dados de distribuição para gráficos.

**Query Params:**
```
?tipo=idade|altura|media_geral
&posicao=ATA
&liga=Brasileirão Série A
```

**Response (200):**
```json
{
  "tipo": "media_geral",
  "filtros": {
    "posicao": "ATA",
    "liga": "Brasileirão Série A"
  },
  "distribuicao": [
    { "range": "1.0-2.0", "count": 5 },
    { "range": "2.0-3.0", "count": 25 },
    { "range": "3.0-4.0", "count": 85 },
    { "range": "4.0-5.0", "count": 67 }
  ],
  "estatisticas": {
    "media": 3.8,
    "mediana": 3.9,
    "moda": 4.0,
    "desvio_padrao": 0.6
  }
}
```

---

### GET /analytics/scatter
Obter dados para scatter plot.

**Query Params:**
```
?eixo_x=nota_tecnico
&eixo_y=nota_fisico
&posicao=MEI
```

**Response (200):**
```json
{
  "eixo_x": "nota_tecnico",
  "eixo_y": "nota_fisico",
  "filtros": { "posicao": "MEI" },
  "data": [
    {
      "id_jogador": 1,
      "nome": "Player 1",
      "x": 4.5,
      "y": 4.0,
      "clube": "Flamengo",
      "idade": 25
    },
    {
      "id_jogador": 2,
      "nome": "Player 2",
      "x": 3.5,
      "y": 4.5,
      "clube": "Palmeiras",
      "idade": 23
    }
  ]
}
```

---

## 12. SCRAPING

### POST /scraping/foto/{id_jogador}
Fazer scraping da foto do Transfermarkt.

**Request:**
```json
{
  "transfermarkt_url": "https://www.transfermarkt.com/neymar/profil/spieler/68290"
}
```

**Response (200):**
```json
{
  "id_jogador": 1,
  "nome": "Neymar Jr.",
  "transfermarkt_id": 68290,
  "foto_url": "/fotos/68290.jpg",
  "foto_baixada": true,
  "data_scraping": "2024-01-15T20:00:00Z"
}
```

**Response (404):**
```json
{
  "detail": "Foto não encontrada na página do Transfermarkt"
}
```

---

### POST /scraping/fotos/lote
Fazer scraping em lote (múltiplos jogadores).

**Request:**
```json
{
  "ids_jogadores": [1, 2, 3, 4, 5]
}
```

**Response (200):**
```json
{
  "total_processados": 5,
  "sucesso": 4,
  "falhas": 1,
  "resultados": [
    { "id_jogador": 1, "status": "sucesso" },
    { "id_jogador": 2, "status": "sucesso" },
    { "id_jogador": 3, "status": "falha", "erro": "URL inválida" },
    { "id_jogador": 4, "status": "sucesso" },
    { "id_jogador": 5, "status": "sucesso" }
  ]
}
```

---

## 13. SINCRONIZAÇÃO

### POST /sync/google-sheets
Sincronizar com Google Sheets.

**Request:**
```json
{
  "spreadsheet_id": "1ABC...XYZ",
  "worksheet_name": "Jogadores",
  "sync_mode": "import|export|bidirectional"
}
```

**Response (200):**
```json
{
  "sync_mode": "import",
  "total_linhas": 707,
  "jogadores_importados": 15,
  "jogadores_atualizados": 692,
  "erros": 0,
  "data_sync": "2024-01-15T21:00:00Z"
}
```

---

## 14. BUSCA AVANÇADA

### POST /busca-avancada
Realizar busca com múltiplos filtros.

**Request:**
```json
{
  "nome": "Silva",
  "posicoes": ["MEI", "VOL"],
  "clubes": ["Flamengo", "Palmeiras"],
  "ligas": ["Brasileirão Série A"],
  "nacionalidades": ["Brasil"],
  "idade_min": 18,
  "idade_max": 25,
  "altura_min": 170,
  "altura_max": 185,
  "pe_dominante": "Direito",
  "media_geral_min": 3.5,
  "nota_potencial_min": 4.0,
  "status_contrato": ["Ativo", "Vencendo"],
  "tags": [1, 5, 10],
  "na_wishlist": true,
  "tem_foto": true
}
```

**Response (200):**
```json
{
  "total": 15,
  "filtros_aplicados": 12,
  "data": [
    {
      "id_jogador": 50,
      "nome": "João Silva",
      "posicao": "MEI",
      "clube": "Flamengo",
      "idade_atual": 22,
      "media_geral": 4.0
    }
  ]
}
```

---

### POST /buscas-salvas
Salvar busca avançada.

**Request:**
```json
{
  "nome_busca": "Meio-campistas Brasil Sub-25",
  "filtros": {
    "posicoes": ["MEI", "VOL"],
    "nacionalidades": ["Brasil"],
    "idade_max": 25,
    "media_geral_min": 3.5
  }
}
```

**Response (201):**
```json
{
  "id_busca": 10,
  "nome_busca": "Meio-campistas Brasil Sub-25",
  "filtros": {...},
  "autor": "João Scout",
  "data_criacao": "2024-01-15T22:00:00Z"
}
```

---

### GET /buscas-salvas
Listar buscas salvas.

**Response (200):**
```json
{
  "total": 10,
  "data": [
    {
      "id_busca": 10,
      "nome_busca": "Meio-campistas Brasil Sub-25",
      "total_resultados_atual": 15,
      "data_criacao": "2024-01-15T22:00:00Z"
    }
  ]
}
```

---

### GET /buscas-salvas/{id}/executar
Executar busca salva.

**Response (200):**
```json
{
  "id_busca": 10,
  "nome_busca": "Meio-campistas Brasil Sub-25",
  "total": 15,
  "data": [...]
}
```

---

## 15. PROPOSTAS FINANCEIRAS

### GET /propostas
Listar propostas.

**Query Params:**
```
?status=pendente|aceita|rejeitada
&clube_interessado=Flamengo
```

**Response (200):**
```json
{
  "total": 8,
  "data": [
    {
      "id_proposta": 5,
      "jogador": {
        "id_jogador": 10,
        "nome": "João Silva",
        "clube_atual": "Palmeiras"
      },
      "valor_proposta": 15000000.00,
      "moeda": "EUR",
      "clube_interessado": "Flamengo",
      "status": "pendente",
      "data_proposta": "2024-01-10T00:00:00Z",
      "observacoes": "Proposta inicial"
    }
  ]
}
```

---

### POST /propostas
Criar nova proposta.

**Request:**
```json
{
  "id_jogador": 10,
  "valor_proposta": 15000000.00,
  "moeda": "EUR",
  "clube_interessado": "Flamengo",
  "observacoes": "Proposta inicial"
}
```

**Response (201):**
```json
{
  "id_proposta": 9,
  "id_jogador": 10,
  "valor_proposta": 15000000.00,
  "moeda": "EUR",
  "clube_interessado": "Flamengo",
  "status": "pendente",
  "data_proposta": "2024-01-15T23:00:00Z"
}
```

---

### PUT /propostas/{id}
Atualizar status da proposta.

**Request:**
```json
{
  "status": "aceita",
  "observacoes": "Negociação concluída"
}
```

**Response (200):** Proposta atualizada

---

### DELETE /propostas/{id}
Deletar proposta.

**Response (204):** No Content

---

## 📌 CÓDIGOS DE STATUS HTTP

| Código | Significado | Uso |
|--------|------------|-----|
| 200 | OK | GET, PUT bem-sucedidos |
| 201 | Created | POST bem-sucedido |
| 204 | No Content | DELETE bem-sucedido |
| 400 | Bad Request | Validação falhou |
| 401 | Unauthorized | Token inválido/expirado |
| 403 | Forbidden | Sem permissão |
| 404 | Not Found | Recurso não encontrado |
| 422 | Unprocessable Entity | Erro de validação Pydantic |
| 500 | Internal Server Error | Erro no servidor |

---

## 🔒 HEADERS DE AUTENTICAÇÃO

Todas as rotas (exceto `/auth/login` e `/auth/register`) requerem:

```
Authorization: Bearer {access_token}
```

---

## 📊 PAGINAÇÃO PADRÃO

Todas as rotas de listagem suportam:

```
?page=1&limit=50
```

**Response:**
```json
{
  "total": 707,
  "page": 1,
  "limit": 50,
  "pages": 15,
  "data": [...]
}
```

---

## ⚡ CACHE E PERFORMANCE

- **Backend:** Redis para cache de queries frequentes
- **Frontend:** React Query com `staleTime` configurável
- **Imagens:** CDN ou cache estático

---

## 🔗 RELACIONAMENTOS

Todas as respostas podem incluir dados relacionados via query param:

```
?include=avaliacao,wishlist,tags,vinculo
```

Exemplo:
```
GET /jogadores/1?include=avaliacao,tags
```

**Response inclui:**
```json
{
  "id_jogador": 1,
  "nome": "Neymar Jr.",
  "ultima_avaliacao": {...},
  "tags": [...]
}
```
