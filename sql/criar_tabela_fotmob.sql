-- ===========================================
-- Tabela de Estatísticas FotMob
-- ===========================================
-- Armazena estatísticas avançadas dos jogadores
-- obtidas da API do FotMob
--
-- Autor: Scout Pro
-- Data: 2025-12-09
-- ===========================================

CREATE TABLE IF NOT EXISTS estatisticas_fotmob (
    id_estatistica SERIAL PRIMARY KEY,
    id_jogador INTEGER REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
    fotmob_id INTEGER,  -- ID do jogador no FotMob

    -- Metadata
    temporada VARCHAR(20) DEFAULT '2024/2025',
    competicao VARCHAR(100),
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- ESTATÍSTICAS OFENSIVAS
    gols INTEGER DEFAULT 0,
    assistencias INTEGER DEFAULT 0,
    expected_goals NUMERIC(5,2) DEFAULT 0.00,  -- xG
    expected_assists NUMERIC(5,2) DEFAULT 0.00,  -- xA
    finalizacoes INTEGER DEFAULT 0,
    finalizacoes_no_gol INTEGER DEFAULT 0,
    grandes_chances INTEGER DEFAULT 0,
    grandes_chances_criadas INTEGER DEFAULT 0,
    grandes_chances_perdidas INTEGER DEFAULT 0,

    -- PASSES E CRIAÇÃO
    passes_precisos INTEGER DEFAULT 0,
    passes_totais INTEGER DEFAULT 0,
    passes_longos_precisos INTEGER DEFAULT 0,
    passes_chave INTEGER DEFAULT 0,
    cruzamentos_precisos INTEGER DEFAULT 0,
    cruzamentos_totais INTEGER DEFAULT 0,

    -- DRIBLES E MOVIMENTAÇÃO
    dribles_bem_sucedidos INTEGER DEFAULT 0,
    dribles_tentados INTEGER DEFAULT 0,
    toques_area_adversaria INTEGER DEFAULT 0,
    dispossessed INTEGER DEFAULT 0,  -- Perdas de bola

    -- DEFESA
    desarmes INTEGER DEFAULT 0,
    interceptacoes INTEGER DEFAULT 0,
    limpezas INTEGER DEFAULT 0,
    finalizacoes_bloqueadas INTEGER DEFAULT 0,
    duelos_ganhos INTEGER DEFAULT 0,
    duelos_totais INTEGER DEFAULT 0,
    duelos_aereos_ganhos INTEGER DEFAULT 0,
    duelos_terrestres_ganhos INTEGER DEFAULT 0,

    -- GOLEIRO (se aplicável)
    defesas INTEGER DEFAULT 0,
    defesas_percentual NUMERIC(5,2) DEFAULT 0.00,
    gols_prevenidos NUMERIC(5,2) DEFAULT 0.00,
    jogos_sem_sofrer_gols INTEGER DEFAULT 0,
    gols_sofridos INTEGER DEFAULT 0,

    -- DISCIPLINA
    cartoes_amarelos INTEGER DEFAULT 0,
    cartoes_vermelhos INTEGER DEFAULT 0,
    faltas_cometidas INTEGER DEFAULT 0,
    faltas_sofridas INTEGER DEFAULT 0,

    -- PERFORMANCE GERAL
    minutos_jogados INTEGER DEFAULT 0,
    partidas_jogadas INTEGER DEFAULT 0,
    partidas_titular INTEGER DEFAULT 0,
    nota_media NUMERIC(3,1) DEFAULT 0.0,  -- Rating médio FotMob

    -- AVANÇADAS (xG, etc)
    expected_goals_on_target NUMERIC(5,2) DEFAULT 0.00,
    penaltis_ganhos INTEGER DEFAULT 0,
    penaltis_cometidos INTEGER DEFAULT 0,

    -- Constraint de atualização única
    UNIQUE(id_jogador, temporada, competicao)
);

-- ===========================================
-- ÍNDICES DE PERFORMANCE
-- ===========================================

-- Busca rápida por jogador + temporada
CREATE INDEX IF NOT EXISTS idx_fotmob_jogador_temporada
ON estatisticas_fotmob(id_jogador, temporada);

-- Busca por ID FotMob (sincronização)
CREATE INDEX IF NOT EXISTS idx_fotmob_id
ON estatisticas_fotmob(fotmob_id);

-- Ordenação por performance (gols, assists)
CREATE INDEX IF NOT EXISTS idx_fotmob_performance
ON estatisticas_fotmob(gols DESC, assistencias DESC);

-- Busca por temporada ativa
CREATE INDEX IF NOT EXISTS idx_fotmob_temporada
ON estatisticas_fotmob(temporada);

-- ===========================================
-- VIEW: Estatísticas Consolidadas
-- ===========================================
-- Combina avaliações Scout Pro + FotMob

CREATE OR REPLACE VIEW vw_perfil_completo_jogador AS
SELECT
    j.id_jogador,
    j.nome,
    j.nacionalidade,
    j.idade_atual,
    v.posicao,
    v.clube,
    v.liga_clube,

    -- Avaliações Scout Pro (últimas)
    a.nota_tatico,
    a.nota_tecnico,
    a.nota_fisico,
    a.nota_mental,
    a.nota_potencial,
    ROUND((a.nota_tatico + a.nota_tecnico + a.nota_fisico + a.nota_mental) / 4.0, 2) as media_scout,

    -- Estatísticas FotMob (temporada atual)
    f.gols,
    f.assistencias,
    f.expected_goals as xG,
    f.expected_assists as xA,
    f.partidas_jogadas,
    f.minutos_jogados,
    f.nota_media as rating_fotmob,

    -- Métricas calculadas
    CASE
        WHEN f.partidas_jogadas > 0 THEN ROUND(CAST(f.gols AS NUMERIC) / f.partidas_jogadas, 2)
        ELSE 0
    END as gols_por_jogo,

    CASE
        WHEN f.partidas_jogadas > 0 THEN ROUND((CAST(f.gols + f.assistencias AS NUMERIC)) / f.partidas_jogadas, 2)
        ELSE 0
    END as contribuicao_gols_por_jogo,

    -- Metadata
    a.data_avaliacao as ultima_avaliacao_scout,
    f.data_atualizacao as ultima_atualizacao_fotmob,
    f.temporada

FROM jogadores j
LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
LEFT JOIN LATERAL (
    SELECT * FROM avaliacoes
    WHERE id_jogador = j.id_jogador
    ORDER BY data_avaliacao DESC
    LIMIT 1
) a ON true
LEFT JOIN LATERAL (
    SELECT * FROM estatisticas_fotmob
    WHERE id_jogador = j.id_jogador
    ORDER BY data_atualizacao DESC
    LIMIT 1
) f ON true

ORDER BY j.nome;

-- ===========================================
-- VIEW: Rankings com FotMob
-- ===========================================

CREATE OR REPLACE VIEW vw_ranking_combinado AS
SELECT
    j.id_jogador,
    j.nome,
    v.posicao,
    v.clube,

    -- Média Scout Pro
    ROUND((a.nota_tatico + a.nota_tecnico + a.nota_fisico + a.nota_mental) / 4.0, 2) as media_scout,

    -- Performance FotMob
    f.gols,
    f.assistencias,
    f.expected_goals,
    f.nota_media as rating_fotmob,

    -- Score Combinado (70% Scout + 30% FotMob Rating)
    ROUND(
        (((a.nota_tatico + a.nota_tecnico + a.nota_fisico + a.nota_mental) / 4.0) * 0.7) +
        ((f.nota_media / 10.0 * 5.0) * 0.3),
        2
    ) as score_combinado,

    -- Ranks
    ROW_NUMBER() OVER (ORDER BY (a.nota_tatico + a.nota_tecnico + a.nota_fisico + a.nota_mental) DESC) as rank_scout,
    ROW_NUMBER() OVER (ORDER BY f.nota_media DESC NULLS LAST) as rank_fotmob

FROM jogadores j
INNER JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
LEFT JOIN LATERAL (
    SELECT * FROM avaliacoes
    WHERE id_jogador = j.id_jogador
    ORDER BY data_avaliacao DESC
    LIMIT 1
) a ON true
LEFT JOIN LATERAL (
    SELECT * FROM estatisticas_fotmob
    WHERE id_jogador = j.id_jogador
    AND temporada = '2024/2025'
    ORDER BY data_atualizacao DESC
    LIMIT 1
) f ON true

WHERE a.id_avaliacao IS NOT NULL  -- Apenas jogadores com avaliação

ORDER BY score_combinado DESC NULLS LAST;

-- ===========================================
-- COMENTÁRIOS
-- ===========================================

COMMENT ON TABLE estatisticas_fotmob IS 'Estatísticas avançadas de jogadores obtidas da API FotMob';
COMMENT ON COLUMN estatisticas_fotmob.expected_goals IS 'Expected Goals (xG) - Gols esperados baseados em qualidade de chances';
COMMENT ON COLUMN estatisticas_fotmob.expected_assists IS 'Expected Assists (xA) - Assistências esperadas';
COMMENT ON COLUMN estatisticas_fotmob.nota_media IS 'Rating médio do FotMob (0-10)';

COMMENT ON VIEW vw_perfil_completo_jogador IS 'Perfil consolidado: Avaliações Scout Pro + Estatísticas FotMob';
COMMENT ON VIEW vw_ranking_combinado IS 'Ranking combinando avaliações Scout (70%) e Rating FotMob (30%)';
