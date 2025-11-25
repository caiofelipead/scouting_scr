# 🔧 Correção: Erro AttributeError - get_wishlist()

## 🔴 Problema Identificado

O erro ocorre porque a **tabela `wishlist` não existe** no banco de dados PostgreSQL do Railway.

```
AttributeError: This app has encountered an error.
Traceback:
File "/mount/src/scouting_scr/app/dashboard.py", line 2525, in tab_wishlist
    wishlist = db.get_wishlist()
               ^^^^^^^^^^^^^^^^^
```

### Causa

O arquivo `database.py` tem o método `get_wishlist()` definido, mas o método `criar_tabelas()` **não cria** as tabelas do Scout Pro v3.0:

**Tabelas faltantes:**
- ❌ `wishlist`
- ❌ `tags`
- ❌ `jogador_tags`
- ❌ `notas_rapidas`
- ❌ `buscas_salvas`

**Tabelas existentes:**
- ✅ `jogadores`
- ✅ `vinculos_clubes`
- ✅ `alertas`
- ✅ `avaliacoes`

---

## ✅ Solução

### Opção 1: Executar Script de Migração (Recomendado)

Use o script que criei para adicionar todas as tabelas faltantes:

```bash
# No terminal local ou Codespaces
python scripts/criar_tabelas_v3.py
```

**O que o script faz:**
1. Conecta ao PostgreSQL do Railway
2. Cria todas as 5 tabelas faltantes
3. Cria 2 views (benchmark e alertas inteligentes)
4. Insere 6 tags padrão

**Importante:** O arquivo `.env` deve ter a variável `DATABASE_URL` configurada.

---

### Opção 2: SQL Manual no Railway

Se preferir executar SQL direto no Railway:

1. Acesse o painel do Railway
2. Abra o banco PostgreSQL
3. Vá em "Query" ou "Connect"
4. Execute este SQL:

```sql
-- 1. TABELA TAGS
CREATE TABLE IF NOT EXISTS tags (
    id_tag SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    cor VARCHAR(20) DEFAULT '#3b82f6',
    descricao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABELA JOGADOR_TAGS
CREATE TABLE IF NOT EXISTS jogador_tags (
    id SERIAL PRIMARY KEY,
    id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
    id_tag INTEGER REFERENCES tags(id_tag) ON DELETE CASCADE,
    adicionado_por VARCHAR(255),
    adicionado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_jogador, id_tag)
);

-- 3. TABELA WISHLIST
CREATE TABLE IF NOT EXISTS wishlist (
    id SERIAL PRIMARY KEY,
    id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE UNIQUE,
    prioridade VARCHAR(20) DEFAULT 'media' CHECK (prioridade IN ('alta', 'media', 'baixa')),
    observacao TEXT,
    adicionado_por VARCHAR(255),
    adicionado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. TABELA NOTAS_RAPIDAS
CREATE TABLE IF NOT EXISTS notas_rapidas (
    id_nota SERIAL PRIMARY KEY,
    id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
    texto TEXT NOT NULL,
    autor VARCHAR(255),
    tipo VARCHAR(50) DEFAULT 'observacao',
    data_nota TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. TABELA BUSCAS_SALVAS
CREATE TABLE IF NOT EXISTS buscas_salvas (
    id_busca SERIAL PRIMARY KEY,
    nome_busca VARCHAR(255) NOT NULL,
    filtros JSONB NOT NULL,
    criado_por VARCHAR(255),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usado_em TIMESTAMP
);

-- 6. VIEWS
CREATE OR REPLACE VIEW vw_benchmark_posicoes AS
SELECT 
    v.posicao,
    COUNT(DISTINCT a.id_jogador) as total_jogadores,
    ROUND(AVG(a.nota_tatico), 2) as media_tatico,
    ROUND(AVG(a.nota_tecnico), 2) as media_tecnico,
    ROUND(AVG(a.nota_fisico), 2) as media_fisico,
    ROUND(AVG(a.nota_mental), 2) as media_mental,
    ROUND(AVG(a.nota_potencial), 2) as media_potencial,
    ROUND(AVG((a.nota_tatico + a.nota_tecnico + a.nota_fisico + a.nota_mental) / 4.0), 2) as media_geral
FROM avaliacoes a
INNER JOIN jogadores j ON a.id_jogador = j.id_jogador
INNER JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
WHERE a.data_avaliacao >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY v.posicao
ORDER BY v.posicao;

CREATE OR REPLACE VIEW vw_alertas_inteligentes AS
SELECT 
    'Contrato Vencendo' as tipo_alerta,
    j.id_jogador,
    j.nome,
    v.clube,
    v.posicao,
    v.data_fim_contrato,
    CASE 
        WHEN v.data_fim_contrato <= CURRENT_DATE + INTERVAL '3 months' THEN 'alta'
        WHEN v.data_fim_contrato <= CURRENT_DATE + INTERVAL '6 months' THEN 'media'
        ELSE 'baixa'
    END as prioridade,
    'Contrato termina em ' || TO_CHAR(v.data_fim_contrato, 'DD/MM/YYYY') as descricao
FROM vinculos_clubes v
INNER JOIN jogadores j ON v.id_jogador = j.id_jogador
WHERE v.data_fim_contrato BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '12 months'

UNION ALL

SELECT 
    'Jovem Promessa' as tipo_alerta,
    j.id_jogador,
    j.nome,
    v.clube,
    v.posicao,
    NULL as data_fim_contrato,
    'media' as prioridade,
    'Jogador com menos de 21 anos' as descricao
FROM jogadores j
INNER JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
WHERE j.idade_atual <= 21

ORDER BY prioridade, nome;

-- 7. TAGS PADRÃO
INSERT INTO tags (nome, cor, descricao) VALUES
('Prioridade', '#ef4444', 'Jogador de alta prioridade'),
('Monitorar', '#f59e0b', 'Jogador para monitoramento'),
('Promessa', '#10b981', 'Jovem promessa'),
('Veterano', '#6366f1', 'Jogador experiente'),
('Lesionado', '#ec4899', 'Jogador com histórico de lesões'),
('Indisponível', '#64748b', 'Jogador indisponível temporariamente')
ON CONFLICT (nome) DO NOTHING;
```

---

## 📝 Verificação

Após executar a migração, verifique se as tabelas foram criadas:

```sql
-- No PostgreSQL do Railway
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
```

**Resultado esperado:**
```
alertas
avaliacoes
buscas_salvas
jogador_tags
jogadores
notas_rapidas
tags
vinculos_clubes
wishlist
```

---

## 🚀 Próximos Passos

1. Execute a migração (opção 1 ou 2)
2. Reinicie a aplicação Streamlit no Railway/Streamlit Cloud
3. Teste a aba "Wishlist" no dashboard
4. O erro deve estar resolvido! ✅

---

## 💡 Solução Permanente (Para o Futuro)

Para evitar esse problema no futuro, o método `criar_tabelas()` em `database.py` precisa ser atualizado para incluir a criação de **todas** as tabelas do Scout Pro v3.0.

Eu recomendo criar um PR (Pull Request) para adicionar essas tabelas ao método `criar_tabelas()` do arquivo `database.py`.

---

## ❓ Dúvidas

Se tiver problemas:

1. Verifique se o `.env` tem `DATABASE_URL` correto
2. Confirme que você tem permissão de escrita no banco
3. Veja os logs do Streamlit para mais detalhes
4. Teste a conexão: `python -c "from database import ScoutingDatabase; db = ScoutingDatabase(); print(db.verificar_saude_conexao())"`
