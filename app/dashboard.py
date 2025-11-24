import random
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from mplsoccer import Pitch

# Configuração da página (DEVE SER A PRIMEIRA CHAMADA)
st.set_page_config(page_title="Scout Pro", page_icon="⚽", layout="wide")

# --- CORREÇÃO DE CAMINHOS (CRÍTICO) ---
try:
    # Obtém o caminho absoluto do arquivo atual
    current_path = Path(__file__).resolve()
    # Sobe dois níveis: app -> scouting_scr (raiz)
    root_path = current_path.parent.parent

    # Adiciona a raiz ao sys.path se ainda não estiver lá
    if str(root_path) not in sys.path:
        sys.path.append(str(root_path))

    # Tenta importar o banco de dados
    # MODIFICAÇÃO: Importa direto pois sys.path inclui a raiz
    from database import ScoutingDatabase

except ImportError as e:
    st.error(f"❌ Erro Crítico de Importação: {e}")
    st.info(f"📂 Caminho tentado: {root_path}")
    st.stop()

"""
Dashboard Interativo de Scouting
Sistema moderno de visualização e análise de jogadores
"""

# CSS customizado para melhor visual
st.markdown(
    """
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 1rem;
    }
    h2 {
        color: #2c3e50;
        padding-top: 1rem;
    }
    
    /* Estilos para tabelas HTML */
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
    }
    th {
        background-color: #f0f2f6;
        padding: 12px;
        text-align: left;
        font-weight: bold;
        border-bottom: 2px solid #ddd;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    td {
        padding: 10px;
        border-bottom: 1px solid #eee;
    }
    tr:hover {
        background-color: #f5f5f5 !important;
    }
    a {
        color: #1f77b4;
        text-decoration: none;
        font-weight: bold;
    }
    a:hover {
        text-decoration: underline !important;
        color: #0d5aa7;
    }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(ttl=None)
def get_database():
    """Inicializa conexão com banco de dados - Cache persistente"""
    return ScoutingDatabase()


def get_foto_jogador(id_jogador):
    """Retorna o caminho da foto do jogador ou None"""
    from pathlib import Path

    # Caminho absoluto a partir da raiz do projeto
    root_path = Path(__file__).resolve().parent.parent
    foto_path = root_path / "fotos" / f"{id_jogador}.jpg"

    if foto_path.exists() and foto_path.is_file():
        return str(foto_path)
    return None


def get_perfil_url(id_jogador):
    """Retorna a URL completa do perfil do jogador"""
    return f"?jogador={id_jogador}"


def get_top_jogadores_por_posicao(df_jogadores, db, posicoes_filtro, top_n=15):
    """
    Retorna os top N jogadores para uma lista de posições, ordenados por média geral.
    """
    # Filtrar pelo nome da posição
    mask = (
        df_jogadores["posicao"]
        .astype(str)
        .str.contains("|".join(posicoes_filtro), case=False, na=False)
    )
    candidatos = df_jogadores[mask].copy()

    if len(candidatos) == 0:
        return []

    # Calcular médias para esses candidatos
    medias = []
    for _, jogador in candidatos.iterrows():
        avals = db.get_ultima_avaliacao(jogador["id_jogador"])
        if not avals.empty:
            # Calcula média simples dos 4 pilares
            media = (
                avals["nota_tatico"].iloc[0]
                + avals["nota_tecnico"].iloc[0]
                + avals["nota_fisico"].iloc[0]
                + avals["nota_mental"].iloc[0]
            ) / 4
        else:
            media = 0.0

        medias.append(media)

    candidatos["media_ranking"] = medias

    # Ordenar e pegar os top N
    candidatos = candidatos.sort_values("media_ranking", ascending=False).head(top_n)

    # Formatar para o selectbox: "Nome (Média: 4.5)"
    opcoes = []
    for _, row in candidatos.iterrows():
        media_fmt = f"{row['media_ranking']:.1f}" if row["media_ranking"] > 0 else "N/A"
        label = f"{row['nome']} ({row['clube']}) - Média: {media_fmt}"
        opcoes.append(
            {
                "label": label,
                "id": row["id_jogador"],
                "nome": row["nome"],
                "pos": row["posicao"],
            }
        )

    return opcoes


def criar_radar_avaliacao(notas_dict, titulo="Avaliação do Atleta"):
    """Cria gráfico de radar para avaliação do jogador"""
    categorias = list(notas_dict.keys())
    valores = list(notas_dict.values())

    # Adicionar o primeiro valor no final para fechar o polígono
    valores += valores[:1]

    # Ângulos para cada eixo
    angles = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angles += angles[:1]

    # Criar o gráfico
    fig = go.Figure()

    # Adicionar a área preenchida
    fig.add_trace(
        go.Scatterpolar(
            r=valores,
            theta=categorias + [categorias[0]],
            fill="toself",
            fillcolor="rgba(46, 204, 113, 0.4)",
            line=dict(color="rgb(46, 204, 113)", width=3),
            name="Avaliação",
        )
    )

    # Adicionar linhas de referência
    fig.add_trace(
        go.Scatterpolar(
            r=[3, 3, 3, 3, 3],
            theta=categorias + [categorias[0]],
            mode="lines",
            line=dict(color="rgba(128, 128, 128, 0.3)", width=1, dash="dash"),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # Configurar layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickmode="linear",
                tick0=0,
                dtick=1,
                gridcolor="rgba(128, 128, 128, 0.2)",
                showline=False,
            ),
            angularaxis=dict(
                gridcolor="rgba(128, 128, 128, 0.2)",
                linecolor="rgba(128, 128, 128, 0.3)",
            ),
        ),
        showlegend=False,
        title=dict(
            text=titulo, x=0.5, xanchor="center", font=dict(size=16, color="#2c3e50")
        ),
        height=400,
        margin=dict(l=80, r=80, t=80, b=40),
    )

    return fig


def criar_grafico_evolucao(df_avaliacoes):
    """Cria gráfico de linha mostrando evolução das notas ao longo do tempo"""
    if len(df_avaliacoes) == 0:
        return None

    df = df_avaliacoes.copy()
    df["data_avaliacao"] = pd.to_datetime(df["data_avaliacao"])
    df = df.sort_values("data_avaliacao")

    fig = go.Figure()

    categorias = ["nota_tatico", "nota_tecnico", "nota_fisico", "nota_mental"]
    nomes = ["Tático", "Técnico", "Físico", "Mental"]
    cores = ["#3498db", "#e74c3c", "#f39c12", "#9b59b6"]

    for cat, nome, cor in zip(categorias, nomes, cores):
        if cat in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["data_avaliacao"],
                    y=df[cat],
                    mode="lines+markers",
                    name=nome,
                    line=dict(color=cor, width=2),
                    marker=dict(size=8),
                )
            )

    fig.update_layout(
        title="Evolução das Avaliações",
        xaxis_title="Data",
        yaxis_title="Nota",
        yaxis=dict(range=[0, 5.5]),
        hovermode="x unified",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def plotar_mapa_elenco(df_jogadores, mostrar_nomes=True, coordenadas_fixas=None):
    """
    Cria um campo de futebol usando mplsoccer e plota os jogadores.
    Suporta coordenadas fixas para o Shadow Team Interativo.
    """
    if len(df_jogadores) == 0:
        st.warning("Sem jogadores para exibir no mapa.")
        return

    # Configuração do campo (Statsbomb style: 120x80)
    pitch = Pitch(pitch_type="statsbomb", pitch_color="#22312b", line_color="#c7d5cc")
    fig, ax = pitch.draw(figsize=(12, 8))

    # Dicionário de coordenadas aproximadas (X, Y) - Fallback
    coord_map_fallback = {
        "goleiro": (10, 40),
        "zagueiro": (30, 40),
        "lateral": (35, 10),
        "volante": (50, 40),
        "meia": (75, 40),
        "atacante": (105, 40),
    }

    # Listas para plotagem
    x_list = []
    y_list = []
    names = []
    colors = []

    for _, row in df_jogadores.iterrows():
        # 1. Usa coordenada fixa (Shadow Team Interativo) se existir
        if coordenadas_fixas and row["id_jogador"] in coordenadas_fixas:
            base_coord = coordenadas_fixas[row["id_jogador"]]
            # Jitter mínimo apenas para efeito visual
            x_jitter = random.uniform(-1, 1)
            y_jitter = random.uniform(-1, 1)

        # 2. Fallback (Visualização Geral / Mapa de Calor)
        else:
            pos_str = str(row["posicao"]).lower().strip()
            base_coord = (60, 40)  # Centro por padrão

            match_found = False
            for key, coord in coord_map_fallback.items():
                if key in pos_str:
                    base_coord = coord
                    match_found = True
                    break

            if not match_found:
                base_coord = (random.uniform(10, 110), -5)

            # Jitter maior para espalhar na visualização geral
            x_jitter = random.uniform(-6, 6)
            y_jitter = random.uniform(-6, 6)

        x_list.append(base_coord[0] + x_jitter)
        y_list.append(base_coord[1] + y_jitter)
        names.append(row["nome"])

        # Cor baseada na idade (Mais jovem = verde, Mais velho = vermelho)
        if pd.notna(row["idade_atual"]):
            if row["idade_atual"] < 23:
                colors.append("#2ecc71")  # Verde (Jovem)
            elif row["idade_atual"] < 30:
                colors.append("#f1c40f")  # Amarelo (Auge)
            else:
                colors.append("#e74c3c")  # Vermelho (Veterano)
        else:
            colors.append("#ecf0f1")

    # Plotar os pontos (scatter)
    pitch.scatter(
        x_list, y_list, ax=ax, c=colors, s=500, edgecolors="black", zorder=2, alpha=0.9
    )

    # Plotar os nomes (anotações)
    if mostrar_nomes:
        for i, name in enumerate(names):
            ax.text(
                x_list[i],
                y_list[i] - 3.5,
                name,
                fontsize=9,
                color="white",
                ha="center",
                va="top",
                fontweight="bold",
                zorder=3,
            )

    # Legenda manual simples
    st.pyplot(fig)

    # Legenda de cores
    st.markdown(
        """
    <div style='display: flex; justify-content: center; gap: 20px; margin-top: 10px;'>
        <div><span style='color: #2ecc71;'>●</span> Sub-23</div>
        <div><span style='color: #f1c40f;'>●</span> 23-29 anos</div>
        <div><span style='color: #e74c3c;'>●</span> 30+ anos</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def exibir_perfil_jogador(db, id_jogador):
    """Exibe perfil detalhado do jogador"""
    conn = db.connect()

    try:
        id_busca = int(id_jogador)
    except Exception:
        id_busca = id_jogador

    query = """
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
    """

    # Compatibilidade SQL (Postgres/SQLite)
    # O parametro :id é mais seguro
    jogador = pd.read_sql_query(query, conn, params={'id': id_busca})
    conn.close()

    if len(jogador) == 0:
        st.error(f"Jogador não encontrado! (ID buscado: {id_busca})")
        if st.button("Voltar para Lista"):
            st.session_state.pagina = "dashboard"
            st.rerun()
        return

    jogador = jogador.iloc[0]

    # Layout de 2 colunas
    col1, col2 = st.columns([1, 2])

    with col1:
        foto_path = get_foto_jogador(id_busca)
        if foto_path:
            st.image(foto_path, width=300)
        else:
            st.markdown(
                """
            <div style='
                width: 300px; 
                height: 300px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 120px;
                color: white;
            '>
                ⚽
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.metric(
            "Idade",
            (
                f"{jogador['idade_atual']} anos"
                if pd.notna(jogador["idade_atual"])
                else "N/A"
            ),
        )
        st.metric(
            "Altura",
            f"{jogador['altura']} cm" if pd.notna(jogador["altura"]) else "N/A",
        )
        st.metric(
            "Pé Dominante",
            jogador["pe_dominante"] if pd.notna(jogador["pe_dominante"]) else "N/A",
        )
        st.metric(
            "Nacionalidade",
            jogador["nacionalidade"] if pd.notna(jogador["nacionalidade"]) else "N/A",
        )

    with col2:
        st.title(jogador["nome"])
        st.subheader(
            f"{jogador['posicao'] if pd.notna(jogador['posicao']) else 'N/A'} • {jogador['clube'] if pd.notna(jogador['clube']) else 'Livre'}"
        )

        st.markdown("---")
        st.markdown("### 📋 Informações do Vínculo")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("**Clube Atual**")
            st.markdown(
                f"🏟️ {jogador['clube'] if pd.notna(jogador['clube']) else 'Livre'}"
            )

        with col_b:
            st.markdown("**Liga**")
            st.markdown(
                f"🏆 {jogador['liga_clube'] if pd.notna(jogador['liga_clube']) else 'N/A'}"
            )

        with col_c:
            st.markdown("**Fim de Contrato**")
            if pd.notna(jogador["data_fim_contrato"]):
                st.markdown(f"📅 {jogador['data_fim_contrato']}")
            else:
                st.markdown("📅 N/A")

        st.markdown("---")
        status = (
            jogador["status_contrato"]
            if pd.notna(jogador["status_contrato"])
            else "desconhecido"
        )

        status_color = {
            "ativo": "🟢",
            "ultimo_ano": "🟡",
            "ultimos_6_meses": "🔴",
            "vencido": "⚫",
            "livre": "⚪",
            "desconhecido": "❓",
        }

        status_text = {
            "ativo": "Contrato Ativo",
            "ultimo_ano": "Último Ano de Contrato",
            "ultimos_6_meses": "Vence em Menos de 6 Meses",
            "vencido": "Contrato Vencido",
            "livre": "Jogador Livre",
            "desconhecido": "Status Desconhecido",
        }

        st.markdown(
            f"### {status_color.get(status, '❓')} {status_text.get(status, 'Status Desconhecido')}"
        )

        if pd.notna(jogador["data_fim_contrato"]) and status not in [
            "vencido",
            "livre",
        ]:
            try:
                data_fim = pd.to_datetime(jogador["data_fim_contrato"], dayfirst=True)
                dias_restantes = (data_fim - datetime.now()).days

                if dias_restantes > 0:
                    st.info(f"⏱️ **{dias_restantes} dias** até o vencimento do contrato")
                    dias_totais = 1095
                    progresso = max(0, min(100, (dias_restantes / dias_totais) * 100))
                    st.progress(progresso / 100)
            except Exception:
                pass

    # ============== SEÇÃO DE AVALIAÇÕES ==============
    st.markdown("---")
    st.markdown("---")

    # Tabs para organizar avaliações
    tab_avaliacao, tab_historico, tab_evolucao = st.tabs(
        ["📝 Nova Avaliação", "📊 Histórico", "📈 Evolução"]
    )

    with tab_avaliacao:
        st.markdown("### 📝 Registrar Nova Avaliação")
        st.markdown("Avalie o jogador nas dimensões principais:")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Formulário de avaliação
            with st.form("form_avaliacao"):
                data_avaliacao = st.date_input(
                    "Data da Avaliação", value=datetime.now(), format="DD/MM/YYYY"
                )

                # NOTA DE POTENCIAL EM DESTAQUE
                st.markdown("---")
                st.markdown("#### ⭐ Avaliação Geral de Potencial")
                nota_potencial = st.slider(
                    "Potencial do Jogador",
                    min_value=1.0,
                    max_value=5.0,
                    value=3.0,
                    step=0.5,
                    help="Avaliação geral do potencial do atleta considerando projeção futura e capacidade de desenvolvimento",
                )

                st.markdown("---")
                st.markdown("#### 📊 Notas por Dimensão (1 a 5)")
                col_a, col_b = st.columns(2)

                with col_a:
                    nota_tatico = st.slider(
                        "⚙️ Tático",
                        min_value=1.0,
                        max_value=5.0,
                        value=3.0,
                        step=0.5,
                        help="Posicionamento, leitura de jogo, decisões táticas",
                    )

                    nota_tecnico = st.slider(
                        "⚽ Técnico",
                        min_value=1.0,
                        max_value=5.0,
                        value=3.0,
                        step=0.5,
                        help="Domínio, passe, finalização, controle de bola",
                    )

                with col_b:
                    nota_fisico = st.slider(
                        "💪 Físico",
                        min_value=1.0,
                        max_value=5.0,
                        value=3.0,
                        step=0.5,
                        help="Velocidade, força, resistência, explosão",
                    )

                    nota_mental = st.slider(
                        "🧠 Mental",
                        min_value=1.0,
                        max_value=5.0,
                        value=3.0,
                        step=0.5,
                        help="Concentração, liderança, inteligência emocional",
                    )

                observacoes = st.text_area(
                    "Observações",
                    placeholder="Adicione comentários sobre a avaliação, pontos fortes, áreas de desenvolvimento...",
                    height=100,
                )

                avaliador = st.text_input(
                    "Avaliador", placeholder="Seu nome (opcional)"
                )

                submitted = st.form_submit_button(
                    "💾 Salvar Avaliação", use_container_width=True, type="primary"
                )

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
                            avaliador=avaliador,
                        )
                        st.success("✅ Avaliação salva com sucesso!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar avaliação: {str(e)}")

        with col2:
            st.markdown("#### 📊 Preview do Radar")
            notas_preview = {
                "Tático": 3.0,
                "Técnico": 3.0,
                "Físico": 3.0,
                "Mental": 3.0,
            }
            fig_preview = criar_radar_avaliacao(notas_preview, "Preview")
            st.plotly_chart(fig_preview, use_container_width=True)

            # Mostrar potencial em destaque
            st.markdown("---")
            st.metric("⭐ Potencial", f"{3.0:.1f}", help="Avaliação geral de potencial")

    with tab_historico:
        st.markdown("### 📊 Histórico de Avaliações")

        # Buscar avaliações do jogador
        avaliacoes = db.get_avaliacoes_jogador(id_busca)

        if len(avaliacoes) > 0:
            # Última avaliação em destaque
            ultima = avaliacoes.iloc[0]

            st.markdown("#### 🎯 Última Avaliação")

            col1, col2 = st.columns([1, 2])

            with col1:
                # Potencial em destaque
                if pd.notna(ultima.get("nota_potencial")):
                    st.markdown("---")
                    st.markdown(f"### ⭐ Potencial: {ultima['nota_potencial']:.1f}/5.0")
                    st.progress(ultima["nota_potencial"] / 5.0)
                    st.markdown("---")

                st.markdown(
                    f"""
                **Data:** {pd.to_datetime(ultima['data_avaliacao']).strftime('%d/%m/%Y') if pd.notna(ultima['data_avaliacao']) else 'N/A'}  
                **Avaliador:** {ultima['avaliador'] if pd.notna(ultima.get('avaliador')) and ultima['avaliador'] else 'Não informado'}
                """
                )

                # Métricas
                col_a, col_b = st.columns(2)
                with col_a:
                    if pd.notna(ultima.get("nota_tatico")):
                        st.metric("Tático", f"{ultima['nota_tatico']:.1f}")
                    if pd.notna(ultima.get("nota_tecnico")):
                        st.metric("Técnico", f"{ultima['nota_tecnico']:.1f}")
                with col_b:
                    if pd.notna(ultima.get("nota_fisico")):
                        st.metric("Físico", f"{ultima['nota_fisico']:.1f}")
                    if pd.notna(ultima.get("nota_mental")):
                        st.metric("Mental", f"{ultima['nota_mental']:.1f}")

                if pd.notna(ultima.get("observacoes")) and ultima["observacoes"]:
                    st.markdown("---")
                    st.markdown("**Observações:**")
                    st.info(ultima["observacoes"])

            with col2:
                # Radar chart da última avaliação
                notas_dict = {}
                if pd.notna(ultima.get("nota_tatico")):
                    notas_dict["Tático"] = ultima["nota_tatico"]
                if pd.notna(ultima.get("nota_tecnico")):
                    notas_dict["Técnico"] = ultima["nota_tecnico"]
                if pd.notna(ultima.get("nota_fisico")):
                    notas_dict["Físico"] = ultima["nota_fisico"]
                if pd.notna(ultima.get("nota_mental")):
                    notas_dict["Mental"] = ultima["nota_mental"]

                if notas_dict:
                    fig_radar = criar_radar_avaliacao(notas_dict, "Perfil Atual")
                    st.plotly_chart(fig_radar, use_container_width=True)

            # Histórico completo
            st.markdown("---")
            st.markdown("#### 📜 Todas as Avaliações")

            # Preparar DataFrame para exibição
            df_display = avaliacoes.copy()

            # Selecionar apenas colunas que existem
            colunas_display = []
            colunas_desejadas = {
                "data_avaliacao": "Data",
                "nota_potencial": "Potencial",
                "nota_tatico": "Tático",
                "nota_tecnico": "Técnico",
                "nota_fisico": "Físico",
                "nota_mental": "Mental",
                "avaliador": "Avaliador",
            }

            for col_original, col_nova in colunas_desejadas.items():
                if col_original in df_display.columns:
                    colunas_display.append(col_original)

            if colunas_display:
                df_display = df_display[colunas_display]
                df_display = df_display.rename(columns=colunas_desejadas)
                st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("📝 Nenhuma avaliação registrada para este jogador ainda.")
            st.markdown(
                "👆 Use a aba **'Nova Avaliação'** para adicionar a primeira avaliação!"
            )

    with tab_evolucao:
        st.markdown("### 📈 Evolução das Avaliações")

        avaliacoes = db.get_avaliacoes_jogador(id_busca)

        if len(avaliacoes) > 1:
            # Gráfico de evolução
            fig_evolucao = criar_grafico_evolucao(avaliacoes)
            if fig_evolucao:
                st.plotly_chart(fig_evolucao, use_container_width=True)

            # Estatísticas de evolução
            st.markdown("---")
            st.markdown("#### 📊 Estatísticas")

            col1, col2, col3, col4 = st.columns(4)

            categorias = {
                "nota_tatico": ("Tático", col1),
                "nota_tecnico": ("Técnico", col2),
                "nota_fisico": ("Físico", col3),
                "nota_mental": ("Mental", col4),
            }

            for col_nome, (label, col) in categorias.items():
                if col_nome in avaliacoes.columns:
                    notas = avaliacoes[col_nome].dropna()
                    if len(notas) > 0:
                        with col:
                            media = notas.mean()
                            delta = (
                                notas.iloc[0] - notas.iloc[-1] if len(notas) > 1 else 0
                            )
                            st.metric(
                                label,
                                f"{media:.1f}",
                                delta=f"{delta:+.1f}" if delta != 0 else None,
                            )
        elif len(avaliacoes) == 1:
            st.info(
                "📊 É necessário ter pelo menos 2 avaliações para visualizar a evolução."
            )
        else:
            st.info("📝 Nenhuma avaliação registrada ainda.")

    # Informações adicionais
    st.markdown("---")
    st.markdown("### 📊 Informações Adicionais")

    col_i, col_ii = st.columns(2)

    with col_i:
        st.markdown("**Ano de Nascimento**")
        st.markdown(
            f"🎂 {jogador['ano_nascimento'] if pd.notna(jogador['ano_nascimento']) else 'N/A'}"
        )

    with col_ii:
        st.markdown("**ID do Jogador**")
        st.markdown(f"🔢 {jogador['id_jogador']}")

    if pd.notna(jogador.get("transfermarkt_id")):
        st.markdown("---")
        # Extrair ID numérico se for URL
        tm_id = str(jogador["transfermarkt_id"])
        import re

        match = re.search(r"/spieler/(\d+)", tm_id)
        if match:
            tm_id = match.group(1)

        st.link_button(
            "📊 Ver no Transfermarkt",
            f"https://www.transfermarkt.com.br/player/profil/spieler/{tm_id}",
            use_container_width=True,
        )


def exibir_lista_com_fotos(df_display, db):
    """Exibe lista de jogadores com fotos em formato de cards"""
    st.markdown("### 👥 Jogadores")

    # Remover duplicatas
    df_display = df_display.drop_duplicates(
        subset=["id_jogador"], keep="first"
    ).reset_index(drop=True)

    for i in range(0, len(df_display), 4):
        cols = st.columns(4)

        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(df_display):
                jogador = df_display.iloc[idx]

                with col:
                    foto_path = get_foto_jogador(jogador["id_jogador"])

                    if foto_path:
                        st.image(foto_path, use_container_width=True)
                    else:
                        st.markdown(
                            """
                        <div style='
                            width: 100%; 
                            padding-top: 100%;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            border-radius: 10px;
                            position: relative;
                        '>
                            <div style='
                                position: absolute;
                                top: 50%;
                                left: 50%;
                                transform: translate(-50%, -50%);
                                font-size: 60px;
                            '>⚽</div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                    st.markdown(f"**{jogador['nome']}**")
                    st.caption(
                        f"{jogador['posicao'] if pd.notna(jogador['posicao']) else 'N/A'}"
                    )
                    st.caption(
                        f"{jogador['clube'] if pd.notna(jogador['clube']) else 'Livre'}"
                    )

                    # Criar link para abrir em nova aba
                    perfil_url = get_perfil_url(jogador["id_jogador"])

                    col_a, col_b = st.columns(2)
                    with col_a:
                        # Botão que abre na mesma aba
                        if st.button(
                            "Ver Perfil",
                            key=f"perfil_{jogador['id_jogador']}_{idx}",
                            use_container_width=True,
                        ):
                            st.session_state.pagina = "perfil"
                            st.session_state.jogador_selecionado = jogador["id_jogador"]
                            st.query_params["jogador"] = jogador["id_jogador"]
                            st.rerun()

                    with col_b:
                        # Link que abre em nova aba
                        st.markdown(
                            f'<a href="{perfil_url}" target="_blank" style="'
                            "display: inline-block; "
                            "padding: 0.25rem 0.75rem; "
                            "background-color: #FF4B4B; "
                            "color: white; "
                            "text-decoration: none; "
                            "border-radius: 0.25rem; "
                            "text-align: center; "
                            "font-size: 0.875rem; "
                            "width: 100%; "
                            "box-sizing: border-box;"
                            '">Nova Aba</a>',
                            unsafe_allow_html=True,
                        )


def main():
    # Header
    st.title("⚽ Scout Pro - Sistema de Monitoramento de Jogadores")
    st.markdown("---")

    # Inicializar banco de dados
    db = get_database()

    # Criar tabela de avaliações se não existir
    db.criar_tabela_avaliacoes()

    # Verificar query parameters na URL
    query_params = st.query_params
    jogador_id_url = query_params.get("jogador", None)

    # Sistema de navegação com session_state
    if "pagina" not in st.session_state:
        st.session_state.pagina = "dashboard"
    if "jogador_selecionado" not in st.session_state:
        st.session_state.jogador_selecionado = None

    # Se há um ID de jogador na URL, ir para o perfil
    if jogador_id_url:
        try:
            st.session_state.pagina = "perfil"
            st.session_state.jogador_selecionado = int(jogador_id_url)
        except Exception:
            pass

    # Se estiver na página de perfil
    if st.session_state.pagina == "perfil":
        if st.button("← Voltar para Dashboard"):
            st.session_state.pagina = "dashboard"
            st.session_state.jogador_selecionado = None
            # Limpar query parameter
            st.query_params.clear()
            st.rerun()

        st.markdown("---")
        exibir_perfil_jogador(db, st.session_state.jogador_selecionado)
        return

    # Dashboard principal continua aqui

    # --- BARRA LATERAL (SIDEBAR) COM SINCRONIZAÇÃO ---
    st.sidebar.header("🔄 Sincronização")

    # Botão para puxar dados do Google Sheets
    if st.sidebar.button("Baixar Dados da Planilha", type="primary"):
        with st.spinner("Conectando ao Google Sheets..."):
            # 1. Puxa os dados brutos da planilha
            df_novos_dados = db.get_dados_google_sheets()

            if df_novos_dados is not None:
                # 2. Salva no banco de dados SQLite
                sucesso = db.importar_dados_planilha(df_novos_dados)

                if sucesso:
                    st.sidebar.success("✅ Atualizado com sucesso!")
                    time.sleep(1)  # Espera 1 segundinho pra ler
                    st.rerun()  # Recarrega a página sozinho
                else:
                    st.sidebar.error("❌ Falha ao salvar no banco.")
            else:
                st.sidebar.error("❌ Erro ao conectar na planilha.")

    st.sidebar.markdown("---")

    # Sidebar - Filtros normais
    st.sidebar.header("🔍 Filtros")

    # Carregar dados
    df_jogadores = db.get_jogadores_com_vinculos()

    # Verificar se há dados
    if len(df_jogadores) == 0:
        st.error("⚠️ **Banco de dados vazio!**")
        st.markdown("O sistema não encontrou jogadores cadastrados.")

        # Botão para importar dados se estiver vazio
        if st.button("🔄 Importar Dados do Google Sheets Agora"):
            with st.spinner("Importando dados..."):
                df_novos_dados = db.get_dados_google_sheets()
                if df_novos_dados is not None:
                    db.importar_dados_planilha(df_novos_dados)
                    st.success("Dados importados! Recarregando...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Erro ao conectar na planilha. Verifique os Secrets.")

        st.stop()

    # Limpar dados de idade (remover valores vazios e inválidos)
    df_jogadores["idade_atual"] = pd.to_numeric(
        df_jogadores["idade_atual"], errors="coerce"
    )

    # Filtros
    posicoes = ["Todas"] + sorted(df_jogadores["posicao"].dropna().unique().tolist())
    posicao_selecionada = st.sidebar.selectbox("Posição", posicoes)

    ligas = ["Todas"] + sorted(df_jogadores["liga_clube"].dropna().unique().tolist())
    liga_selecionada = st.sidebar.selectbox("Liga", ligas)

    # Filtro de Nacionalidade
    nacionalidades = ["Todas"] + sorted(
        df_jogadores["nacionalidade"].dropna().unique().tolist()
    )
    nacionalidade_selecionada = st.sidebar.selectbox("Nacionalidade", nacionalidades)

    # Filtro de Clube
    clubes = ["Todos"] + sorted(df_jogadores["clube"].dropna().unique().tolist())
    clube_selecionado = st.sidebar.selectbox("Clube", clubes)

    # Verificar se tem idades válidas para o slider
    idades_validas = df_jogadores["idade_atual"].dropna()
    if len(idades_validas) > 0:
        idade_min_db = int(idades_validas.min())
        idade_max_db = int(idades_validas.max())
    else:
        idade_min_db = 16
        idade_max_db = 40
        st.sidebar.warning("⚠️ Dados de idade incompletos na planilha")

    idade_min, idade_max = st.sidebar.slider(
        "Faixa Etária",
        idade_min_db,
        idade_max_db,
        (max(18, idade_min_db), min(35, idade_max_db)),
    )

    status_contrato = ["Todos"] + sorted(
        df_jogadores["status_contrato"].dropna().unique().tolist()
    )
    status_selecionado = st.sidebar.multiselect(
        "Status do Contrato", status_contrato, default=["Todos"]
    )

    # Aplicar filtros
    df_filtrado = df_jogadores.copy()

    if posicao_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["posicao"] == posicao_selecionada]

    if liga_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["liga_clube"] == liga_selecionada]

    if nacionalidade_selecionada != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["nacionalidade"] == nacionalidade_selecionada
        ]

    if clube_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["clube"] == clube_selecionado]

    df_filtrado = df_filtrado[
        (df_filtrado["idade_atual"].notna())
        & (df_filtrado["idade_atual"] >= idade_min)
        & (df_filtrado["idade_atual"] <= idade_max)
    ]

    if "Todos" not in status_selecionado and len(status_selecionado) > 0:
        df_filtrado = df_filtrado[
            df_filtrado["status_contrato"].isin(status_selecionado)
        ]

    # KPIs principais
    col1, col2, col3, col4, col5 = st.columns(5)

    stats = db.get_estatisticas_gerais()

    with col1:
        st.metric(
            "Total de Jogadores",
            stats["total_jogadores"],
            delta=None,
            help="Total de jogadores no banco de dados",
        )

    with col2:
        st.metric(
            "Vínculos Ativos",
            stats["total_vinculos_ativos"],
            delta=None,
            help="Jogadores com contratos ativos",
        )

    with col3:
        st.metric(
            "Contratos Vencendo",
            stats["contratos_vencendo"],
            delta=None,
            help="Contratos vencendo nos próximos 12 meses",
        )

    with col4:
        st.metric(
            "Alertas Ativos",
            stats["alertas_ativos"],
            delta=None,
            help="Alertas que requerem atenção",
        )

    with col5:
        st.metric(
            "Resultados Filtrados",
            len(df_filtrado),
            delta=None,
            help="Jogadores após aplicar filtros",
        )

    st.markdown("---")

    # Tabs principais
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "📊 Visão Geral",
            "👥 Lista de Jogadores",
            "🏆 Ranking",
            "🆚 Comparador",
            "⚽ Shadow Team",
            "🚨 Alertas",
            "📈 Análises",
        ]
    )

    with tab1:
        st.header("Visão Geral do Banco de Jogadores")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distribuição por Posição")
            posicao_counts = df_filtrado["posicao"].value_counts()
            fig_posicao = px.pie(
                values=posicao_counts.values,
                names=posicao_counts.index,
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig_posicao.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_posicao, use_container_width=True)

        with col2:
            st.subheader("Distribuição por Idade")
            df_idade_valida = df_filtrado[df_filtrado["idade_atual"].notna()]
            fig_idade = px.histogram(
                df_idade_valida,
                x="idade_atual",
                nbins=20,
                color_discrete_sequence=["#1f77b4"],
            )
            fig_idade.update_layout(
                xaxis_title="Idade",
                yaxis_title="Quantidade de Jogadores",
                showlegend=False,
            )
            st.plotly_chart(fig_idade, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 10 Nacionalidades")
            nac_counts = df_filtrado["nacionalidade"].value_counts().head(10)
            fig_nac = px.bar(
                x=nac_counts.values,
                y=nac_counts.index,
                orientation="h",
                color=nac_counts.values,
                color_continuous_scale="Blues",
            )
            fig_nac.update_layout(
                xaxis_title="Quantidade",
                yaxis_title="",
                showlegend=False,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_nac, use_container_width=True)

        with col2:
            st.subheader("Status dos Contratos")
            status_counts = df_filtrado["status_contrato"].value_counts()

            color_map = {
                "ativo": "#2ecc71",
                "ultimo_ano": "#f39c12",
                "ultimos_6_meses": "#e74c3c",
                "vencido": "#95a5a6",
                "livre": "#34495e",
            }

            fig_status = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                color=status_counts.index,
                color_discrete_map=color_map,
            )
            fig_status.update_layout(
                xaxis_title="Status", yaxis_title="Quantidade", showlegend=False
            )
            st.plotly_chart(fig_status, use_container_width=True)

    with tab2:
        st.header("Lista Completa de Jogadores")

        search_term = st.text_input("🔎 Buscar jogador por nome", "")

        if search_term:
            df_filtrado = df_filtrado[
                df_filtrado["nome"].str.contains(search_term, case=False, na=False)
            ]

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            ordenar_por = st.selectbox(
                "Ordenar por",
                ["nome", "idade_atual", "clube", "posicao", "status_contrato"],
            )
        with col2:
            ordem = st.radio("Ordem", ["Crescente", "Decrescente"])
        with col3:
            visualizacao = st.radio("Visualização", ["Cards", "Tabela"])

        df_display = df_filtrado.sort_values(
            by=ordenar_por, ascending=(ordem == "Crescente")
        ).reset_index(drop=True)

        st.markdown("---")

        if visualizacao == "Cards":
            exibir_lista_com_fotos(df_display, db)
        else:
            # Tabela com nomes clicáveis
            df_display_formatted = df_display.copy()

            # Adicionar coluna de ação com link
            df_display_formatted["acao"] = df_display_formatted["id_jogador"].apply(
                lambda x: f"?jogador={x}"
            )

            # Selecionar e renomear colunas
            colunas = [
                "id_jogador",
                "nome",
                "nacionalidade",
                "idade_atual",
                "altura",
                "pe_dominante",
                "clube",
                "liga_clube",
                "posicao",
                "data_fim_contrato",
                "status_contrato",
            ]

            df_display_formatted = df_display_formatted[colunas + ["acao"]]

            # Criar HTML para nomes clicáveis
            df_display_formatted["nome_link"] = df_display_formatted.apply(
                lambda row: f'<a href="?jogador={row["id_jogador"]}" target="_blank" style="color: #1f77b4; text-decoration: none; font-weight: bold;">{row["nome"]}</a>',
                axis=1,
            )

            # Remover coluna nome original e acao
            df_display_formatted = df_display_formatted.drop(["nome", "acao"], axis=1)

            # Reordenar colunas
            cols_order = [
                "id_jogador",
                "nome_link",
                "nacionalidade",
                "idade_atual",
                "altura",
                "pe_dominante",
                "clube",
                "liga_clube",
                "posicao",
                "data_fim_contrato",
                "status_contrato",
            ]

            df_display_formatted = df_display_formatted[cols_order]

            df_display_formatted.columns = [
                "ID",
                "Nome",
                "Nacionalidade",
                "Idade",
                "Altura",
                "Pé",
                "Clube",
                "Liga",
                "Posição",
                "Fim Contrato",
                "Status",
            ]

            # Exibir tabela com HTML
            st.markdown(
                "💡 **Dica:** Clique no nome do jogador para abrir o perfil em nova aba",
                help="Os nomes são clicáveis!",
            )

            st.markdown(
                df_display_formatted.to_html(escape=False, index=False),
                unsafe_allow_html=True,
            )

            # Adicionar CSS para melhorar a aparência da tabela
            st.markdown(
                """
                <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th {
                    background-color: #f0f2f6;
                    padding: 12px;
                    text-align: left;
                    font-weight: bold;
                    border-bottom: 2px solid #ddd;
                }
                td {
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                }
                tr:hover {
                    background-color: #f5f5f5;
                }
                a:hover {
                    text-decoration: underline !important;
                }
                </style>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        csv = df_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Exportar dados filtrados (CSV)",
            data=csv,
            file_name=f'jogadores_filtrados_{datetime.now().strftime("%Y%m%d")}.csv',
            mime="text/csv",
            use_container_width=True,
        )

    with tab3:
        st.header("🏆 Ranking de Jogadores por Avaliações")

        # Buscar todas as avaliações do banco
        conn = db.connect()

        # Query para pegar a última avaliação de cada jogador
        query_avaliacoes = """
        SELECT 
            j.id_jogador,
            j.nome,
            j.nacionalidade,
            j.idade_atual,
            v.clube,
            v.posicao,
            a.nota_potencial,
            a.nota_tatico,
            a.nota_tecnico,
            a.nota_fisico,
            a.nota_mental,
            a.data_avaliacao
        FROM jogadores j
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        INNER JOIN avaliacoes a ON j.id_jogador = a.id_jogador
        INNER JOIN (
            SELECT id_jogador, MAX(data_avaliacao) as max_data
            FROM avaliacoes
            GROUP BY id_jogador
        ) ultima ON a.id_jogador = ultima.id_jogador AND a.data_avaliacao = ultima.max_data
        """

        # Compatibilidade para SQLite/Postgres
        df_avaliacoes = pd.read_sql_query(query_avaliacoes, conn)
        conn.close()

        if len(df_avaliacoes) == 0:
            st.info("📝 Ainda não há avaliações cadastradas no sistema.")
            st.markdown(
                """
            **Para começar:**
            1. Vá na aba **"Lista de Jogadores"**
            2. Clique em **"Ver Perfil"** de um jogador
            3. Use a aba **"Nova Avaliação"** para registrar notas
            """
            )
        else:
            # Aplicar filtros
            df_rank = df_avaliacoes.copy()

            # Filtros específicos do ranking
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                posicoes_rank = ["Todas"] + sorted(
                    df_rank["posicao"].dropna().unique().tolist()
                )
                posicao_rank = st.selectbox(
                    "🎯 Filtrar por Posição", posicoes_rank, key="rank_pos"
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
                    key="rank_ordem",
                )

            with col3:
                nacionalidades_rank = ["Todas"] + sorted(
                    df_rank["nacionalidade"].dropna().unique().tolist()
                )
                nac_rank = st.selectbox(
                    "🌍 Nacionalidade", nacionalidades_rank, key="rank_nac"
                )

            with col4:
                clubes_rank = ["Todos"] + sorted(
                    df_rank["clube"].dropna().unique().tolist()
                )
                clube_rank = st.selectbox("⚽ Clube", clubes_rank, key="rank_clube")

            # Aplicar filtros
            if posicao_rank != "Todas":
                df_rank = df_rank[df_rank["posicao"] == posicao_rank]

            if nac_rank != "Todas":
                df_rank = df_rank[df_rank["nacionalidade"] == nac_rank]

            if clube_rank != "Todos":
                df_rank = df_rank[df_rank["clube"] == clube_rank]

            # Calcular média geral
            df_rank["media_geral"] = df_rank[
                ["nota_tatico", "nota_tecnico", "nota_fisico", "nota_mental"]
            ].mean(axis=1)

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

            # Opção de visualização
            view_option = st.radio(
                "Visualização",
                ["Top 20", "Por Posição", "Tabela Completa"],
                horizontal=True,
            )

            if view_option == "Top 20":
                st.markdown(f"### 🏆 Top 20 Jogadores - Ordenado por {ordenar_rank}")

                df_top20 = df_rank.head(20).copy()

                # Criar tabela formatada
                for idx, jogador in df_top20.iterrows():
                    rank_pos = jogador["rank"]

                    # Emoji de medalha
                    if rank_pos == 1:
                        emoji = "🥇"
                    elif rank_pos == 2:
                        emoji = "🥈"
                    elif rank_pos == 3:
                        emoji = "🥉"
                    else:
                        emoji = f"#{rank_pos}"

                    with st.container():
                        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(
                            [0.5, 2, 1.5, 1, 1, 1, 1, 1]
                        )

                        with col1:
                            st.markdown(f"### {emoji}")

                        with col2:
                            # Nome clicável
                            perfil_url = get_perfil_url(jogador["id_jogador"])
                            st.markdown(
                                f'<a href="{perfil_url}" target="_blank" style="color: #1f77b4; text-decoration: none; font-weight: bold; font-size: 1.1em;">{jogador["nome"]}</a>',
                                unsafe_allow_html=True,
                            )
                            st.caption(f"{jogador['posicao']} | {jogador['clube']}")

                        with col3:
                            st.metric(
                                "⭐ Potencial", f"{jogador['nota_potencial']:.1f}"
                            )

                        with col4:
                            st.metric("Média", f"{jogador['media_geral']:.1f}")

                        with col5:
                            st.metric("Tático", f"{jogador['nota_tatico']:.1f}")

                        with col6:
                            st.metric("Técnico", f"{jogador['nota_tecnico']:.1f}")

                        with col7:
                            st.metric("Físico", f"{jogador['nota_fisico']:.1f}")

                        with col8:
                            st.metric("Mental", f"{jogador['nota_mental']:.1f}")

                        st.markdown("---")

            elif view_option == "Por Posição":
                st.markdown("### 📊 Ranking por Posição")

                # Agrupar por posição
                posicoes_disponiveis = df_rank["posicao"].dropna().unique()

                for posicao in sorted(posicoes_disponiveis):
                    df_pos = df_rank[df_rank["posicao"] == posicao].head(10)

                    with st.expander(
                        f"⚽ {posicao} ({len(df_pos)} jogadores)", expanded=True
                    ):
                        # Criar links clicáveis
                        df_pos_display = df_pos.copy()

                        # Adicionar coluna com link HTML
                        df_pos_display["nome_link"] = df_pos_display.apply(
                            lambda row: f'<a href="?jogador={row["id_jogador"]}" target="_blank" style="color: #1f77b4; text-decoration: none; font-weight: bold;">{row["nome"]}</a>',
                            axis=1,
                        )

                        # Criar DataFrame para exibição
                        df_display = df_pos_display[
                            [
                                "rank",
                                "nome_link",
                                "clube",
                                "nacionalidade",
                                "idade_atual",
                                "nota_potencial",
                                "media_geral",
                                "nota_tatico",
                                "nota_tecnico",
                                "nota_fisico",
                                "nota_mental",
                            ]
                        ].copy()

                        df_display.columns = [
                            "Rank",
                            "Nome",
                            "Clube",
                            "Nacionalidade",
                            "Idade",
                            "⭐ Potencial",
                            "Média",
                            "Tático",
                            "Técnico",
                            "Físico",
                            "Mental",
                        ]

                        # Formatar números
                        for col in [
                            "⭐ Potencial",
                            "Média",
                            "Tático",
                            "Técnico",
                            "Físico",
                            "Mental",
                        ]:
                            df_display[col] = df_display[col].apply(
                                lambda x: f"{x:.1f}"
                            )

                        # Exibir tabela HTML com nomes clicáveis
                        html_table = df_display.to_html(escape=False, index=False)

                        # Aplicar destaque top 3
                        for i in range(min(3, len(df_display))):
                            html_table = html_table.replace(
                                f"<tr>\n      <td>{i+1}</td>",
                                f'<tr style="background-color: #d4edda;">\n      <td>{i+1}</td>',
                            )

                        st.markdown(html_table, unsafe_allow_html=True)

            else:  # Tabela Completa
                st.markdown(f"### 📋 Tabela Completa - {len(df_rank)} jogadores")

                # Criar links clicáveis
                df_rank_display = df_rank.copy()

                # Adicionar coluna com link HTML
                df_rank_display["nome_link"] = df_rank_display.apply(
                    lambda row: f'<a href="?jogador={row["id_jogador"]}" target="_blank" style="color: #1f77b4; text-decoration: none; font-weight: bold;">{row["nome"]}</a>',
                    axis=1,
                )

                # Criar DataFrame para exibição
                df_display = df_rank_display[
                    [
                        "rank",
                        "nome_link",
                        "posicao",
                        "clube",
                        "nacionalidade",
                        "idade_atual",
                        "nota_potencial",
                        "media_geral",
                        "nota_tatico",
                        "nota_tecnico",
                        "nota_fisico",
                        "nota_mental",
                        "data_avaliacao",
                    ]
                ].copy()

                df_display.columns = [
                    "Rank",
                    "Nome",
                    "Posição",
                    "Clube",
                    "Nacionalidade",
                    "Idade",
                    "⭐ Potencial",
                    "Média",
                    "Tático",
                    "Técnico",
                    "Físico",
                    "Mental",
                    "Última Avaliação",
                ]

                # Formatar números
                for col in [
                    "⭐ Potencial",
                    "Média",
                    "Tático",
                    "Técnico",
                    "Físico",
                    "Mental",
                ]:
                    df_display[col] = df_display[col].apply(lambda x: f"{x:.1f}")

                # Formatar data
                df_display["Última Avaliação"] = pd.to_datetime(
                    df_display["Última Avaliação"]
                ).dt.strftime("%d/%m/%Y")

                # Exibir dica
                st.markdown(
                    "💡 **Dica:** Clique no nome do jogador para abrir o perfil em nova aba"
                )

                # Exibir tabela HTML com nomes clicáveis
                html_table = df_display.to_html(escape=False, index=False)

                # Aplicar cores por ranking
                for i, row in df_display.iterrows():
                    rank = i + 1
                    if rank <= 3:
                        bg_color = "#d4edda"
                    elif rank <= 10:
                        bg_color = "#fff3cd"
                    else:
                        bg_color = ""

                    if bg_color:
                        # Encontrar a linha correspondente e adicionar estilo
                        html_table = html_table.replace(
                            f"<tr>\n      <td>{rank}</td>",
                            f'<tr style="background-color: {bg_color};">\n      <td>{rank}</td>',
                            1,  # Substituir apenas a primeira ocorrência
                        )

                # Container com scroll
                st.markdown(
                    f'<div style="height: 600px; overflow-y: scroll;">{html_table}</div>',
                    unsafe_allow_html=True,
                )

                # Adicionar CSS para melhorar aparência
                st.markdown(
                    """
                    <style>
                    table {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    th {
                        background-color: #f0f2f6;
                        padding: 12px;
                        text-align: left;
                        font-weight: bold;
                        border-bottom: 2px solid #ddd;
                        position: sticky;
                        top: 0;
                        z-index: 10;
                    }
                    td {
                        padding: 10px;
                        border-bottom: 1px solid #eee;
                    }
                    tr:hover {
                        background-color: #f5f5f5 !important;
                    }
                    a:hover {
                        text-decoration: underline !important;
                    }
                    </style>
                """,
                    unsafe_allow_html=True,
                )

                # Botão de export
                st.markdown("---")
                csv = df_display.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Exportar Ranking (CSV)",
                    data=csv,
                    file_name=f'ranking_jogadores_{datetime.now().strftime("%Y%m%d")}.csv',
                    mime="text/csv",
                    use_container_width=True,
                )

            # Estatísticas do ranking
            st.markdown("---")
            st.markdown("### 📊 Estatísticas do Ranking")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Jogadores Avaliados",
                    len(df_rank),
                    help="Total de jogadores com avaliações",
                )

            with col2:
                st.metric(
                    "Potencial Médio",
                    f"{df_rank['nota_potencial'].mean():.2f}",
                    help="Média de potencial de todos os jogadores",
                )

            with col3:
                st.metric(
                    "Nota Geral Média",
                    f"{df_rank['media_geral'].mean():.2f}",
                    help="Média geral de todas as dimensões",
                )

            with col4:
                melhor_jogador = df_rank.iloc[0]
                st.metric(
                    "Melhor Jogador",
                    melhor_jogador["nome"],
                    help=f"Nota: {melhor_jogador[ordem_map[ordenar_rank]]:.1f}",
                )

    with tab4:  # Comparador com Fotos (SEM EMOJIS)
        st.header("🆚 Comparador Head-to-Head")

        # Carregar jogadores para os selectboxes
        jogadores_options = df_filtrado[["id_jogador", "nome"]].to_dict("records")
        opcoes = {j["nome"]: j["id_jogador"] for j in jogadores_options}

        if len(opcoes) < 2:
            st.warning(
                "⚠️ É necessário ter pelo menos 2 jogadores filtrados para comparar."
            )
        else:
            col_sel1, col_sel2 = st.columns(2)

            with col_sel1:
                nome_1 = st.selectbox(
                    "Selecionar Jogador A", list(opcoes.keys()), index=0
                )
                id_1 = opcoes[nome_1]

            with col_sel2:
                # Tenta pegar o segundo jogador da lista como padrão
                nome_2 = st.selectbox(
                    "Selecionar Jogador B",
                    list(opcoes.keys()),
                    index=1 if len(opcoes) > 1 else 0,
                )
                id_2 = opcoes[nome_2]

            if id_1 == id_2:
                st.info("💡 Selecione jogadores diferentes para comparar.")
            else:
                # Buscar dados completos
                avals_1 = db.get_ultima_avaliacao(id_1)
                avals_2 = db.get_ultima_avaliacao(id_2)

                # Buscar infos cadastrais (usando o df_filtrado para ser rápido)
                info_1 = df_filtrado[df_filtrado["id_jogador"] == id_1].iloc[0]
                info_2 = df_filtrado[df_filtrado["id_jogador"] == id_2].iloc[0]

                st.markdown("---")

                # --- COLUNAS DE COMPARAÇÃO ---
                col_a, col_b = st.columns(2)

                # Jogador A
                with col_a:
                    f1 = get_foto_jogador(id_1)
                    if f1:
                        st.image(f1, width=150)
                    else:
                        st.markdown(
                            "<div style='width:150px;height:150px;background:#eee;border-radius:10px;display:flex;align-items:center;justify-content:center;'>👤</div>",
                            unsafe_allow_html=True,
                        )

                    st.subheader(f"{info_1['nome']}")
                    st.caption(f"{info_1['posicao']} | {info_1['clube']}")
                    st.metric(
                        "Potencial",
                        (
                            f"{avals_1['nota_potencial'].iloc[0]:.1f}"
                            if not avals_1.empty
                            else "N/A"
                        ),
                    )

                # Jogador B
                with col_b:
                    f2 = get_foto_jogador(id_2)
                    if f2:
                        st.image(f2, width=150)
                    else:
                        st.markdown(
                            "<div style='width:150px;height:150px;background:#eee;border-radius:10px;display:flex;align-items:center;justify-content:center;'>👤</div>",
                            unsafe_allow_html=True,
                        )

                    st.subheader(f"{info_2['nome']}")
                    st.caption(f"{info_2['posicao']} | {info_2['clube']}")
                    st.metric(
                        "Potencial",
                        (
                            f"{avals_2['nota_potencial'].iloc[0]:.1f}"
                            if not avals_2.empty
                            else "N/A"
                        ),
                        delta=(
                            f"{(avals_2['nota_potencial'].iloc[0] - avals_1['nota_potencial'].iloc[0]):.1f}"
                            if not avals_1.empty and not avals_2.empty
                            else None
                        ),
                    )

                # --- GRÁFICO DE RADAR COMPARATIVO ---
                if not avals_1.empty and not avals_2.empty:
                    st.markdown("### 🕸️ Radar Comparativo")

                    categorias = ["Tático", "Técnico", "Físico", "Mental"]

                    # Dados Jogador 1
                    val_1 = [
                        avals_1["nota_tatico"].iloc[0],
                        avals_1["nota_tecnico"].iloc[0],
                        avals_1["nota_fisico"].iloc[0],
                        avals_1["nota_mental"].iloc[0],
                    ]
                    # Dados Jogador 2
                    val_2 = [
                        avals_2["nota_tatico"].iloc[0],
                        avals_2["nota_tecnico"].iloc[0],
                        avals_2["nota_fisico"].iloc[0],
                        avals_2["nota_mental"].iloc[0],
                    ]

                    # Fechar o loop do radar
                    cat_radar = categorias + [categorias[0]]
                    val_1_radar = val_1 + [val_1[0]]
                    val_2_radar = val_2 + [val_2[0]]

                    fig_comp = go.Figure()

                    fig_comp.add_trace(
                        go.Scatterpolar(
                            r=val_1_radar,
                            theta=cat_radar,
                            fill="toself",
                            name=info_1["nome"],
                            line_color="#1f77b4",
                            opacity=0.6,
                        )
                    )

                    fig_comp.add_trace(
                        go.Scatterpolar(
                            r=val_2_radar,
                            theta=cat_radar,
                            fill="toself",
                            name=info_2["nome"],
                            line_color="#d62728",
                            opacity=0.6,
                        )
                    )

                    fig_comp.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                        showlegend=True,
                        height=500,
                    )

                    st.plotly_chart(fig_comp, use_container_width=True)

                    # --- TABELA DETALHADA ---
                    st.markdown("### 📋 Comparativo Detalhado")

                    comp_data = {
                        "Atributo": [
                            "Idade",
                            "Altura",
                            "Fim de Contrato",
                            "Tático",
                            "Técnico",
                            "Físico",
                            "Mental",
                        ],
                        info_1["nome"]: [
                            f"{info_1['idade_atual']} anos",
                            f"{info_1['altura']} cm",
                            f"{info_1['data_fim_contrato']}",
                            f"{val_1[0]:.1f}",
                            f"{val_1[1]:.1f}",
                            f"{val_1[2]:.1f}",
                            f"{val_1[3]:.1f}",
                        ],
                        info_2["nome"]: [
                            f"{info_2['idade_atual']} anos",
                            f"{info_2['altura']} cm",
                            f"{info_2['data_fim_contrato']}",
                            f"{val_2[0]:.1f}",
                            f"{val_2[1]:.1f}",
                            f"{val_2[2]:.1f}",
                            f"{val_2[3]:.1f}",
                        ],
                    }

                    df_comp = pd.DataFrame(comp_data)
                    st.table(df_comp)

                else:
                    st.warning(
                        "Um dos jogadores selecionados não possui avaliação cadastrada."
                    )

    with tab5:  # Shadow Team (4-2-3-1)
        st.header("⚽ Shadow Team Interativo (4-2-3-1)")
        st.markdown(
            "Monte o elenco ideal com base nos melhores ranqueados de cada posição."
        )

        # COORDENADAS AJUSTADAS PARA 4-2-3-1
        esquema_tatico = {
            "ATA_E": {
                "label": "Ponta Esq.",
                "filtros": ["Ponta Esquerda", "Atacante", "Extremo"],
                "coord": (105, 10),
            },
            "ATA_C": {
                "label": "Centroavante",
                "filtros": ["Centroavante", "Atacante"],
                "coord": (110, 40),
            },
            "ATA_D": {
                "label": "Ponta Dir.",
                "filtros": ["Ponta Direita", "Atacante", "Extremo"],
                "coord": (105, 70),
            },
            "MEI_C": {
                "label": "Meia Armador",
                "filtros": ["Meia", "Meia Atacante"],
                "coord": (85, 40),
            },
            "VOL_E": {
                "label": "Volante Esq.",
                "filtros": ["Volante", "Meia Defensivo", "Meia"],
                "coord": (55, 30),
            },
            "VOL_D": {
                "label": "Volante Dir.",
                "filtros": ["Volante", "Meia Defensivo", "Meia"],
                "coord": (55, 50),
            },
            "DEF_E": {
                "label": "Lateral Esq.",
                "filtros": ["Lateral Esquerdo", "Ala Esquerdo", "Lateral"],
                "coord": (35, 5),
            },
            "ZAG_E": {
                "label": "Zagueiro Esq.",
                "filtros": ["Zagueiro", "Defensor"],
                "coord": (25, 28),
            },
            "ZAG_D": {
                "label": "Zagueiro Dir.",
                "filtros": ["Zagueiro", "Defensor"],
                "coord": (25, 52),
            },
            "DEF_D": {
                "label": "Lateral Dir.",
                "filtros": ["Lateral Direito", "Ala Direito", "Lateral"],
                "coord": (35, 75),
            },
            "GOL": {"label": "Goleiro", "filtros": ["Goleiro"], "coord": (5, 40)},
        }

        # Container do Time Selecionado
        elenco_selecionado = []
        coords_fixas = {}

        # --- INTERFACE DE SELEÇÃO (Visual de Formação) ---

        # Linha de Ataque
        c1, c2, c3 = st.columns(3)
        with c1:
            ops = get_top_jogadores_por_posicao(
                df_filtrado, db, esquema_tatico["ATA_E"]["filtros"]
            )
            sel = (
                st.selectbox(
                    "Ponta Esq.",
                    options=ops,
                    format_func=lambda x: x["label"],
                    key="s_ae",
                )
                if ops
                else None
            )
            if sel:
                elenco_selecionado.append(sel["id"])
                coords_fixas[sel["id"]] = esquema_tatico["ATA_E"]["coord"]
        with c2:
            ops = get_top_jogadores_por_posicao(
                df_filtrado, db, esquema_tatico["ATA_C"]["filtros"]
            )
            sel = (
                st.selectbox(
                    "Centroavante",
                    options=ops,
                    format_func=lambda x: x["label"],
                    key="s_ac",
                )
                if ops
                else None
            )
            if sel:
                elenco_selecionado.append(sel["id"])
                coords_fixas[sel["id"]] = esquema_tatico["ATA_C"]["coord"]
        with c3:
            ops = get_top_jogadores_por_posicao(
                df_filtrado, db, esquema_tatico["ATA_D"]["filtros"]
            )
            sel = (
                st.selectbox(
                    "Ponta Dir.",
                    options=ops,
                    format_func=lambda x: x["label"],
                    key="s_ad",
                )
                if ops
                else None
            )
            if sel:
                elenco_selecionado.append(sel["id"])
                coords_fixas[sel["id"]] = esquema_tatico["ATA_D"]["coord"]

        # Meia Central
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            ops = get_top_jogadores_por_posicao(
                df_filtrado, db, esquema_tatico["MEI_C"]["filtros"]
            )
            sel = (
                st.selectbox(
                    "Meia Armador",
                    options=ops,
                    format_func=lambda x: x["label"],
                    key="s_mc",
                )
                if ops
                else None
            )
            if sel:
                elenco_selecionado.append(sel["id"])
                coords_fixas[sel["id"]] = esquema_tatico["MEI_C"]["coord"]

        # Volantes (Dupla)
        c1, c2 = st.columns(2)
        with c1:
            ops = get_top_jogadores_por_posicao(
                df_filtrado, db, esquema_tatico["VOL_E"]["filtros"]
            )
            sel = (
                st.selectbox(
                    "Volante Esq.",
                    options=ops,
                    format_func=lambda x: x["label"],
                    key="s_ve",
                )
                if ops
                else None
            )
            if sel:
                elenco_selecionado.append(sel["id"])
                coords_fixas[sel["id"]] = esquema_tatico["VOL_E"]["coord"]
        with c2:
            ops = get_top_jogadores_por_posicao(
                df_filtrado, db, esquema_tatico["VOL_D"]["filtros"]
            )
            # Tenta pegar o segundo da lista pra não repetir se for a mesma query
            idx = 1 if len(ops) > 1 else 0
            sel = (
                st.selectbox(
                    "Volante Dir.",
                    options=ops,
                    index=idx,
                    format_func=lambda x: x["label"],
                    key="s_vd",
                )
                if ops
                else None
            )
            if sel:
                elenco_selecionado.append(sel["id"])
                coords_fixas[sel["id"]] = esquema_tatico["VOL_D"]["coord"]

        # Linha de Defesa
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            ops = get_top_jogadores_por_posicao(
                df_filtrado, db, esquema_tatico["DEF_E"]["filtros"]
            )
            sel = (
                st.selectbox(
                    "Lat. Esq.",
                    options=ops,
                    format_func=lambda x: x["label"],
                    key="s_le",
                )
                if ops
                else None
            )
            if sel:
                elenco_selecionado.append(sel["id"])
                coords_fixas[sel["id"]] = esquema_tatico["DEF_E"]["coord"]
        with c2:
            ops = get_top_jogadores_por_posicao(
                df_filtrado, db, esquema_tatico["ZAG_E"]["filtros"]
            )
            sel = (
                st.selectbox(
                    "Zagueiro Esq.",
                    options=ops,
                    format_func=lambda x: x["label"],
                    key="s_ze",
                )
                if ops
                else None
            )
            if sel:
                elenco_selecionado.append(sel["id"])
                coords_fixas[sel["id"]] = esquema_tatico["ZAG_E"]["coord"]
        with c3:
            ops = get_top_jogadores_por_posicao(
                df_filtrado, db, esquema_tatico["ZAG_D"]["filtros"]
            )
            idx_padrao = 1 if len(ops) > 1 else 0
            sel = (
                st.selectbox(
                    "Zagueiro Dir.",
                    options=ops,
                    index=idx_padrao,
                    format_func=lambda x: x["label"],
                    key="s_zd",
                )
                if ops
                else None
            )
            if sel:
                elenco_selecionado.append(sel["id"])
                coords_fixas[sel["id"]] = esquema_tatico["ZAG_D"]["coord"]
        with c4:
            ops = get_top_jogadores_por_posicao(
                df_filtrado, db, esquema_tatico["DEF_D"]["filtros"]
            )
            sel = (
                st.selectbox(
                    "Lat. Dir.",
                    options=ops,
                    format_func=lambda x: x["label"],
                    key="s_ld",
                )
                if ops
                else None
            )
            if sel:
                elenco_selecionado.append(sel["id"])
                coords_fixas[sel["id"]] = esquema_tatico["DEF_D"]["coord"]

        # Goleiro
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            ops = get_top_jogadores_por_posicao(
                df_filtrado, db, esquema_tatico["GOL"]["filtros"]
            )
            sel = (
                st.selectbox(
                    "Goleiro",
                    options=ops,
                    format_func=lambda x: x["label"],
                    key="s_gol",
                )
                if ops
                else None
            )
            if sel:
                elenco_selecionado.append(sel["id"])
                coords_fixas[sel["id"]] = esquema_tatico["GOL"]["coord"]

        st.markdown("---")

        # --- PLOTAR O CAMPO COM OS SELECIONADOS ---
        if elenco_selecionado:
            # Criar DataFrame apenas com os selecionados para passar pro plotador
            df_visualizacao = df_filtrado[
                df_filtrado["id_jogador"].isin(elenco_selecionado)
            ].copy()

            # Passamos True para mostrar nomes e as coordenadas fixas para garantir a posição tática
            plotar_mapa_elenco(
                df_visualizacao, mostrar_nomes=True, coordenadas_fixas=coords_fixas
            )
        else:
            st.info("Nenhum jogador encontrado com os filtros atuais.")

    with tab6:
        st.header("Central de Alertas")

        alertas = db.get_alertas_ativos()

        if len(alertas) == 0:
            st.info("✅ Nenhum alerta ativo no momento!")
        else:
            prioridade_filter = st.multiselect(
                "Filtrar por prioridade",
                ["alta", "media", "baixa"],
                default=["alta", "media", "baixa"],
            )

            alertas_filtrados = alertas[alertas["prioridade"].isin(prioridade_filter)]

            for _, alerta in alertas_filtrados.iterrows():
                if alerta["prioridade"] == "alta":
                    st.error(f"🚨 **{alerta['jogador']}** - {alerta['descricao']}")
                elif alerta["prioridade"] == "media":
                    st.warning(f"⚠️ **{alerta['jogador']}** - {alerta['descricao']}")
                else:
                    st.info(f"ℹ️ **{alerta['jogador']}** - {alerta['descricao']}")

    with tab7:
        st.header("Análises Avançadas")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Jogadores por Liga")
            liga_counts = df_filtrado["liga_clube"].value_counts().head(10)
            fig_liga = px.bar(
                x=liga_counts.index,
                y=liga_counts.values,
                color=liga_counts.values,
                color_continuous_scale="Viridis",
            )
            fig_liga.update_layout(
                xaxis_title="",
                yaxis_title="Quantidade",
                showlegend=False,
                coloraxis_showscale=False,
                xaxis={"tickangle": 45},
            )
            st.plotly_chart(fig_liga, use_container_width=True)

        with col2:
            st.subheader("Idade Média por Posição")
            idade_media = (
                df_filtrado.groupby("posicao")["idade_atual"].mean().sort_values()
            )
            fig_idade_pos = px.bar(
                x=idade_media.values,
                y=idade_media.index,
                orientation="h",
                color=idade_media.values,
                color_continuous_scale="RdYlGn_r",
            )
            fig_idade_pos.update_layout(
                xaxis_title="Idade Média",
                yaxis_title="",
                showlegend=False,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_idade_pos, use_container_width=True)

        st.subheader("Heatmap: Nacionalidade x Posição")

        top_nacs = df_filtrado["nacionalidade"].value_counts().head(10).index
        df_heatmap = df_filtrado[df_filtrado["nacionalidade"].isin(top_nacs)]

        heatmap_data = pd.crosstab(df_heatmap["nacionalidade"], df_heatmap["posicao"])

        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Posição", y="Nacionalidade", color="Quantidade"),
            color_continuous_scale="YlOrRd",
            aspect="auto",
        )
        fig_heatmap.update_layout(height=500)
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #7f8c8d;'>"
        f"🎯 Scout Pro v2.0 | Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()