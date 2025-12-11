"""
Dashboard Refatorado com Streamlit Shadcn UI
Design minimalista e moderno estilo Vercel/Linear
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import plotly.graph_objects as go
from utils_fotos import get_foto_jogador
from utils_logos import get_logo_clube, get_logo_liga

# Importar streamlit-shadcn-ui com fallback
try:
    import streamlit_shadcn_ui as ui
    SHADCN_AVAILABLE = True
except ImportError:
    SHADCN_AVAILABLE = False
    st.warning("""
    ⚠️ **streamlit-shadcn-ui não instalado!**

    Para usar a nova UI modernizada, instale a biblioteca:
    ```bash
    pip install --upgrade setuptools wheel
    pip install streamlit-shadcn-ui
    ```

    Usando fallback para componentes nativos do Streamlit...
    """)

    # Mock UI object para fallback
    class MockUI:
        """Mock para quando streamlit-shadcn-ui não está disponível"""

        class MockCard:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def render(self):
                st.metric(self.kwargs.get('title', ''), self.kwargs.get('content', ''))

            def __enter__(self):
                # Retorna um container do Streamlit para simular contexto
                return st.container()

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        def card(self, **kwargs):
            return self.MockCard(**kwargs)

        def badges(self, badge_list, **kwargs):
            for text, variant in badge_list:
                color = {"default": "blue", "secondary": "gray", "destructive": "red"}.get(variant, "blue")
                st.markdown(f':{color}[{text}]')

        def tabs(self, options, default_value, **kwargs):
            return st.selectbox("Navegação", options, index=options.index(default_value) if default_value in options else 0)

        def button(self, text, variant="default", **kwargs):
            button_type = "primary" if variant == "default" else "secondary"
            return st.button(text, **{k: v for k, v in kwargs.items() if k != 'variant'}, type=button_type)

    ui = MockUI()


def exibir_perfil_jogador_refatorado(db, id_jogador, debug=False):
    """
    Perfil do jogador com design moderno usando Shadcn UI
    Remove CSS massivo e usa componentes nativos do Shadcn
    """
    conn = db.engine.connect()

    try:
        id_busca = int(id_jogador)
    except Exception:
        id_busca = id_jogador

    query = text("""
    SELECT
        j.*,
        v.clube,
        v.liga_clube,
        v.posicao,
        v.data_fim_contrato,
        v.status_contrato
    FROM jogadores j
    LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
    WHERE j.id_jogador = :id
    """)

    result = conn.execute(query, {"id": id_busca})
    jogador = pd.DataFrame(result.fetchall(), columns=result.keys())

    if len(jogador) == 0:
        st.error(f"Jogador não encontrado! (ID buscado: {id_busca})")
        if ui.button(text="Voltar para Lista", key="btn_voltar_erro"):
            st.session_state.pagina = "dashboard"
            st.rerun()
        return

    jogador = jogador.iloc[0]

    # ==========================================
    # CALCULAR STATUS DO CONTRATO
    # ==========================================

    status = "desconhecido"
    dias_restantes = None

    if pd.notna(jogador.get("data_fim_contrato")):
        try:
            data_fim = pd.to_datetime(jogador["data_fim_contrato"], dayfirst=True)
            dias_restantes = (data_fim - datetime.now()).days

            if dias_restantes < 0:
                status = "vencido"
            elif dias_restantes <= 180:
                status = "ultimos_6_meses"
            elif dias_restantes <= 365:
                status = "ultimo_ano"
            else:
                status = "ativo"
        except Exception:
            status = "desconhecido"
    elif pd.notna(jogador.get("status_contrato")):
        status = jogador.get("status_contrato", "desconhecido")

    if jogador.get("clube") == "Livre" or jogador.get("status_contrato") == "livre":
        status = "livre"

    # ==========================================
    # PREPARAR DADOS
    # ==========================================

    nome = jogador.get('nome', 'Jogador')
    posicao = jogador.get('posicao', 'N/A') if pd.notna(jogador.get('posicao')) else 'N/A'
    clube = jogador.get('clube', 'Livre') if pd.notna(jogador.get('clube')) else 'Livre'
    liga = jogador.get('liga_clube', 'N/A') if pd.notna(jogador.get('liga_clube')) else 'N/A'
    idade = jogador.get('idade_atual', 'N/A')
    altura = jogador.get('altura', 'N/A')
    pe_dom = jogador.get('pe_dominante', 'N/A') if pd.notna(jogador.get('pe_dominante')) else 'N/A'
    nacionalidade = jogador.get('nacionalidade', 'N/A') if pd.notna(jogador.get('nacionalidade')) else 'N/A'
    fim_contrato = jogador.get('data_fim_contrato', 'N/A') if pd.notna(jogador.get('data_fim_contrato')) else 'N/A'

    # Buscar foto
    tm_id = jogador.get('transfermarkt_id', None)
    foto_url = get_foto_jogador(id_busca, transfermarkt_id=tm_id, debug=debug)

    # Buscar logos
    logo_clube_url = get_logo_clube(clube)
    logo_liga_url = get_logo_liga(liga)

    # ==========================================
    # CSS MÍNIMO (apenas spacing essencial)
    # ==========================================

    st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
        }

        /* Remove gaps vazios */
        div[data-testid="stVerticalBlock"] > div:empty {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # HEADER COM FOTO E INFO BÁSICA
    # ==========================================

    col_foto, col_info = st.columns([1, 3])

    with col_foto:
        if foto_url:
            st.image(foto_url, width=180)
        else:
            inicial = nome[0].upper() if nome else "?"
            st.markdown(f"""
            <div style="width: 180px; height: 180px; border-radius: 90px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        display: flex; align-items: center; justify-content: center;
                        font-size: 72px; color: white; font-weight: bold;">
                {inicial}
            </div>
            """, unsafe_allow_html=True)

    with col_info:
        st.title(nome)
        st.markdown(f"**{posicao}** • {clube}")

        # Status do contrato com badges
        status_badge_config = {
            "ativo": ("Contrato Ativo", "default"),
            "ultimo_ano": ("Último Ano", "secondary"),
            "ultimos_6_meses": ("Vence em Breve", "destructive"),
            "vencido": ("Vencido", "outline"),
            "livre": ("Livre", "secondary"),
            "desconhecido": ("Status Desconhecido", "outline"),
        }

        badge_text, badge_variant = status_badge_config.get(status, ("Desconhecido", "outline"))
        ui.badges(
            badge_list=[(badge_text, badge_variant)],
            class_name="flex gap-2",
            key="status_badge"
        )

        # Barra de progresso do contrato
        if dias_restantes is not None and dias_restantes > 0:
            st.info(f"⏱️ **{dias_restantes} dias** até o fim do contrato")

    st.markdown("---")

    # ==========================================
    # GRID DE MÉTRICAS COM SHADCN UI CARDS
    # ==========================================

    st.markdown("### 📊 Informações do Jogador")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        ui.card(
            title="Idade",
            content=f"{idade}" if idade != 'N/A' else "N/A",
            description="anos",
            key="card_idade"
        ).render()

    with col2:
        ui.card(
            title="Altura",
            content=f"{altura}" if altura != 'N/A' else "N/A",
            description="cm",
            key="card_altura"
        ).render()

    with col3:
        ui.card(
            title="Pé",
            content=pe_dom,
            description="dominante",
            key="card_pe"
        ).render()

    with col4:
        ui.card(
            title="Nacionalidade",
            content=nacionalidade,
            description="",
            key="card_nac"
        ).render()

    with col5:
        ui.card(
            title="Contrato",
            content=str(fim_contrato),
            description="vencimento",
            key="card_contrato"
        ).render()

    # ==========================================
    # CLUBE E LIGA COM LOGOS
    # ==========================================

    st.markdown("---")

    col_clube, col_liga = st.columns(2)

    with col_clube:
        if logo_clube_url:
            st.image(logo_clube_url, width=48)
        st.markdown(f"**{clube}**")

    with col_liga:
        if logo_liga_url:
            st.image(logo_liga_url, width=48)
        st.markdown(f"**{liga}**")

    st.markdown("---")

    # ==========================================
    # TABS COM SHADCN UI
    # ==========================================

    selected_tab = ui.tabs(
        options=['Nova Avaliação', 'Histórico', 'Evolução', 'Análise Avançada'],
        default_value='Nova Avaliação',
        key="perfil_tabs"
    )

    # ==========================================
    # TAB: NOVA AVALIAÇÃO
    # ==========================================

    if selected_tab == 'Nova Avaliação':
        st.markdown("### 📝 Registrar Nova Avaliação")

        col1, col2 = st.columns([2, 1])

        with col1:
            with st.form("form_avaliacao"):
                data_avaliacao = st.date_input(
                    "Data da Avaliação",
                    value=datetime.now(),
                    format="DD/MM/YYYY"
                )

                st.markdown("#### ⭐ Avaliação Geral de Potencial")
                nota_potencial = st.slider(
                    "Potencial do Jogador",
                    min_value=1.0,
                    max_value=5.0,
                    value=3.0,
                    step=0.5
                )

                st.markdown("#### 📊 Notas por Dimensão")
                col_a, col_b = st.columns(2)

                with col_a:
                    nota_tatico = st.slider("⚙️ Tático", 1.0, 5.0, 3.0, 0.5)
                    nota_tecnico = st.slider("⚽ Técnico", 1.0, 5.0, 3.0, 0.5)

                with col_b:
                    nota_fisico = st.slider("💪 Físico", 1.0, 5.0, 3.0, 0.5)
                    nota_mental = st.slider("🧠 Mental", 1.0, 5.0, 3.0, 0.5)

                observacoes = st.text_area(
                    "Observações",
                    placeholder="Adicione comentários...",
                    height=100
                )

                avaliador = st.text_input("Avaliador", placeholder="Seu nome (opcional)")

                submitted = st.form_submit_button("💾 Salvar Avaliação", type="primary")

                if submitted:
                    try:
                        db.salvar_avaliacao(
                            id_jogador=id_busca,
                            data_avaliacao=data_avaliacao.strftime("%Y-%m-%d"),
                            nota_potencial=nota_potencial,
                            nota_tatico=nota_tatico,
                            nota_tecnico=nota_tecnico,
                            nota_fisico=nota_fisico,
                            nota_mental=nota_mental,
                            observacoes=observacoes,
                            avaliador=avaliador
                        )
                        st.success("✅ Avaliação salva com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")

        with col2:
            st.markdown("#### 📊 Preview")
            # Preview das notas pode ser adicionado aqui

    # ==========================================
    # TAB: HISTÓRICO
    # ==========================================

    elif selected_tab == 'Histórico':
        st.markdown("### 📊 Histórico de Avaliações")

        avaliacoes = db.get_avaliacoes_jogador(id_busca)

        if len(avaliacoes) > 0:
            ultima = avaliacoes.iloc[0]

            st.markdown("#### 🎯 Última Avaliação")

            # Grid de métricas das avaliações
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if pd.notna(ultima.get("nota_tatico")):
                    ui.card(
                        title="Tático",
                        content=f"{ultima['nota_tatico']:.1f}",
                        description="/ 5.0",
                        key="hist_tatico"
                    ).render()

            with col2:
                if pd.notna(ultima.get("nota_tecnico")):
                    ui.card(
                        title="Técnico",
                        content=f"{ultima['nota_tecnico']:.1f}",
                        description="/ 5.0",
                        key="hist_tecnico"
                    ).render()

            with col3:
                if pd.notna(ultima.get("nota_fisico")):
                    ui.card(
                        title="Físico",
                        content=f"{ultima['nota_fisico']:.1f}",
                        description="/ 5.0",
                        key="hist_fisico"
                    ).render()

            with col4:
                if pd.notna(ultima.get("nota_mental")):
                    ui.card(
                        title="Mental",
                        content=f"{ultima['nota_mental']:.1f}",
                        description="/ 5.0",
                        key="hist_mental"
                    ).render()

            # Potencial em destaque
            if pd.notna(ultima.get("nota_potencial")):
                st.markdown("---")
                ui.card(
                    title="⭐ Potencial",
                    content=f"{ultima['nota_potencial']:.1f}",
                    description="/ 5.0",
                    key="hist_potencial"
                ).render()

            # Observações
            if pd.notna(ultima.get("observacoes")) and ultima["observacoes"]:
                st.markdown("---")
                st.markdown("**Observações:**")
                st.info(ultima["observacoes"])

            # Histórico completo
            st.markdown("---")
            st.markdown("#### 📜 Todas as Avaliações")
            st.dataframe(avaliacoes, use_container_width=True, hide_index=True)
        else:
            st.info("📝 Nenhuma avaliação registrada para este jogador.")

    # ==========================================
    # TAB: EVOLUÇÃO
    # ==========================================

    elif selected_tab == 'Evolução':
        st.markdown("### 📈 Evolução do Jogador")
        st.info("Gráficos de evolução serão implementados aqui")

    # ==========================================
    # TAB: ANÁLISE AVANÇADA
    # ==========================================

    elif selected_tab == 'Análise Avançada':
        st.markdown("### 🎯 Análise Avançada")
        st.info("Análises comparativas serão implementadas aqui")

    # Botão de voltar
    st.markdown("---")
    if ui.button(text="← Voltar para Dashboard", key="btn_voltar", variant="secondary"):
        st.session_state.pagina = "dashboard"
        st.rerun()


def exibir_lista_com_fotos_refatorado(df_display, db, debug=False, sufixo_key="padrao"):
    """
    Lista de jogadores com cards modernos usando Shadcn UI
    Remove HTML complexo e usa componentes nativos
    """
    st.markdown("### Jogadores")

    # Remover duplicatas
    df_display = df_display.drop_duplicates(subset=['id_jogador'], keep='first').reset_index(drop=True)

    if len(df_display) == 0:
        st.info("Nenhum jogador encontrado com os filtros aplicados.")
        return

    # Buscar IDs da wishlist
    ids_wishlist = db.get_ids_wishlist()

    # Grid 4 colunas
    for i in range(0, len(df_display), 4):
        cols = st.columns(4, gap="medium")

        for j, col in enumerate(cols):
            idx = i + j

            if idx < len(df_display):
                jogador = df_display.iloc[idx]

                with col:
                    # === CARD DO JOGADOR ===
                    with ui.card(key=f"player_card_{jogador['id_jogador']}_{sufixo_key}"):
                        # Foto do jogador
                        tm_id = jogador.get('transfermarkt_id', None)
                        nome_jogador = jogador.get('nome', 'Jogador')
                        foto_url = get_foto_jogador(
                            jogador['id_jogador'],
                            transfermarkt_id=tm_id,
                            nome_jogador=nome_jogador,
                            debug=(debug and idx == 0)
                        )

                        if foto_url:
                            st.image(foto_url, use_container_width=True)
                        else:
                            inicial = nome_jogador[0].upper() if nome_jogador else "?"
                            st.markdown(f"""
                            <div style="width: 100%; padding-top: 133.33%; position: relative;
                                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        border-radius: 8px;">
                                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                                            font-size: 60px; color: white; font-weight: bold;">
                                    {inicial}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        # Info do jogador
                        st.markdown(f"**{jogador['nome']}**")
                        st.caption(f"{jogador['posicao'] if pd.notna(jogador['posicao']) else 'N/A'}")
                        st.caption(f"{jogador['clube'] if pd.notna(jogador['clube']) else 'Livre'}")

                        # Botões de ação
                        col_perfil, col_wish = st.columns(2)

                        with col_perfil:
                            if ui.button(
                                text="Ver Perfil",
                                key=f"perfil_{jogador['id_jogador']}_{idx}_{sufixo_key}",
                                variant="default"
                            ):
                                st.session_state.pagina = "perfil"
                                st.session_state.jogador_selecionado = jogador['id_jogador']
                                st.query_params["jogador"] = jogador['id_jogador']
                                st.rerun()

                        with col_wish:
                            na_wishlist = jogador['id_jogador'] in ids_wishlist

                            if na_wishlist:
                                if ui.button(
                                    text="❌",
                                    key=f"remwish_{jogador['id_jogador']}_{idx}_{sufixo_key}",
                                    variant="destructive"
                                ):
                                    if db.remover_wishlist(jogador['id_jogador']):
                                        st.success("Removido!")
                                        st.rerun()
                            else:
                                if ui.button(
                                    text="⭐",
                                    key=f"addwish_{jogador['id_jogador']}_{idx}_{sufixo_key}",
                                    variant="secondary"
                                ):
                                    if db.adicionar_wishlist(jogador['id_jogador'], prioridade='media'):
                                        st.success("Adicionado!")
                                        st.rerun()


# ==========================================
# FUNÇÕES AUXILIARES MANTIDAS
# ==========================================

def criar_radar_avaliacao(notas_dict, titulo="Perfil"):
    """Cria gráfico radar para visualização das avaliações"""
    categorias = list(notas_dict.keys())
    valores = list(notas_dict.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=categorias,
        fill='toself',
        name=titulo,
        line_color='#667eea',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        showlegend=False,
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig


def tab_ranking_refatorado(db, df_jogadores):
    """
    Tab de ranking usando Shadcn UI Cards
    Substitui st.metric() por ui.card() para design moderno
    """
    st.markdown("### 🏆 Ranking de Jogadores por Avaliações")

    @st.cache_data(ttl=600, show_spinner=False)
    def carregar_avaliacoes(_db):
        """Carrega média das avaliações dos últimos 6 meses por jogador"""
        query = """
        SELECT
            j.id_jogador,
            j.nome,
            v.clube,
            v.posicao,
            v.liga_clube,
            j.nacionalidade,
            j.idade_atual,
            ROUND(AVG(a.nota_potencial)::numeric, 1) as nota_potencial,
            ROUND(AVG(a.nota_tatico)::numeric, 1) as nota_tatico,
            ROUND(AVG(a.nota_tecnico)::numeric, 1) as nota_tecnico,
            ROUND(AVG(a.nota_fisico)::numeric, 1) as nota_fisico,
            ROUND(AVG(a.nota_mental)::numeric, 1) as nota_mental,
            COUNT(a.id) as total_avaliacoes,
            MAX(a.data_avaliacao) as data_avaliacao
        FROM jogadores j
        INNER JOIN avaliacoes a ON j.id_jogador = a.id_jogador
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        WHERE a.data_avaliacao >= CURRENT_DATE - INTERVAL '6 months'
        GROUP BY
            j.id_jogador,
            j.nome,
            v.clube,
            v.posicao,
            v.liga_clube,
            j.nacionalidade,
            j.idade_atual
        ORDER BY AVG(a.nota_potencial) DESC
        """
        try:
            with _db.engine.connect() as conn:
                result = conn.execute(text(query))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df
        except Exception as e:
            st.error(f"❌ Erro ao buscar avaliações: {e}")
            return pd.DataFrame()

    df_avaliacoes = carregar_avaliacoes(db)

    if df_avaliacoes.empty:
        st.warning("Nenhuma avaliação encontrada para montar o ranking.")
        return

    df_avaliacoes["media_geral"] = df_avaliacoes[
        ["nota_tatico", "nota_tecnico", "nota_fisico", "nota_mental"]
    ].mean(axis=1)

    # --- FILTROS SUPERIORES ---
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        posicoes_rank = ["Todas"] + sorted(
            df_avaliacoes["posicao"].dropna().unique().tolist()
        )
        posicao_rank = st.selectbox(
            "🎯 Filtrar por Posição", posicoes_rank, key="rank_pos_ref"
        )

    with col2:
        ordenar_rank = st.selectbox(
            "📊 Ordenar por",
            [
                "Potencial",
                "Média Geral",
                "Tático",
                "Técnico",
                "Físico",
                "Mental",
            ],
            key="rank_ordem_ref",
        )

    with col3:
        nacionalidades_rank = ["Todas"] + sorted(
            df_avaliacoes["nacionalidade"].dropna().unique().tolist()
        )
        nac_rank = st.selectbox(
            "🌍 Nacionalidade", nacionalidades_rank, key="rank_nac_ref"
        )

    with col4:
        clubes_rank = ["Todos"] + sorted(
            df_avaliacoes["clube"].dropna().unique().tolist()
        )
        clube_rank = st.selectbox("⚽ Clube", clubes_rank, key="rank_clube_ref")

    with col5:
        ligas_rank = ["Todas"] + sorted(
            df_avaliacoes["liga_clube"].dropna().unique().tolist()
        )
        liga_rank = st.selectbox("🏆 Liga", ligas_rank, key="rank_liga_ref")

    # Aplicar filtros
    df_rank = df_avaliacoes.copy()

    if posicao_rank != "Todas":
        df_rank = df_rank[df_rank["posicao"] == posicao_rank]

    if nac_rank != "Todas":
        df_rank = df_rank[df_rank["nacionalidade"] == nac_rank]

    if clube_rank != "Todos":
        df_rank = df_rank[df_rank["clube"] == clube_rank]

    if liga_rank != "Todas":
        df_rank = df_rank[df_rank["liga_clube"] == liga_rank]

    # Mapear ordenação
    ordem_map = {
        "Potencial": "nota_potencial",
        "Média Geral": "media_geral",
        "Tático": "nota_tatico",
        "Técnico": "nota_tecnico",
        "Físico": "nota_fisico",
        "Mental": "nota_mental",
    }

    # Ordenar
    df_rank = df_rank.sort_values(
        by=ordem_map[ordenar_rank], ascending=False
    ).reset_index(drop=True)

    # Adicionar posição no ranking
    df_rank["rank"] = range(1, len(df_rank) + 1)

    st.markdown("---")

    # --- TOP 20 COM SHADCN UI ---
    st.markdown(f"### 🏆 Top 20 Jogadores - Ordenado por {ordenar_rank}")

    df_top20 = df_rank.head(20).copy()

    if len(df_top20) == 0:
        st.warning("Nenhum jogador encontrado com os filtros aplicados.")
        return

    # Exibir cada jogador do Top 20
    for idx, jogador in enumerate(df_top20.itertuples()):
        rank_pos = jogador.rank

        # Determinar emoji
        if rank_pos == 1:
            emoji = "🥇"
        elif rank_pos == 2:
            emoji = "🥈"
        elif rank_pos == 3:
            emoji = "🥉"
        else:
            emoji = f"#{rank_pos}"

        # Layout do jogador
        col_rank, col_info, col_pot, col_media, col_tat, col_tec, col_fis, col_men = st.columns(
            [0.5, 2, 1, 1, 1, 1, 1, 1]
        )

        with col_rank:
            st.markdown(f"## {emoji}")

        with col_info:
            st.markdown(f"**{jogador.nome}**")
            st.caption(f"{jogador.posicao} | {jogador.clube}")

        # Substituir st.metric() por ui.card()
        with col_pot:
            ui.card(
                title="Potencial",
                content=f"{jogador.nota_potencial:.1f}",
                description="/5.0",
                key=f"rank_pot_{jogador.id_jogador}"
            ).render()

        with col_media:
            ui.card(
                title="Média",
                content=f"{jogador.media_geral:.1f}",
                description="/5.0",
                key=f"rank_media_{jogador.id_jogador}"
            ).render()

        with col_tat:
            ui.card(
                title="Tático",
                content=f"{jogador.nota_tatico:.1f}",
                description="/5.0",
                key=f"rank_tat_{jogador.id_jogador}"
            ).render()

        with col_tec:
            ui.card(
                title="Técnico",
                content=f"{jogador.nota_tecnico:.1f}",
                description="/5.0",
                key=f"rank_tec_{jogador.id_jogador}"
            ).render()

        with col_fis:
            ui.card(
                title="Físico",
                content=f"{jogador.nota_fisico:.1f}",
                description="/5.0",
                key=f"rank_fis_{jogador.id_jogador}"
            ).render()

        with col_men:
            ui.card(
                title="Mental",
                content=f"{jogador.nota_mental:.1f}",
                description="/5.0",
                key=f"rank_men_{jogador.id_jogador}"
            ).render()

        st.markdown("---")
