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

    # Inicializar banco de dados PRIMEIRO
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
        with st.spinner("Sincronizando..."):
            try:
                from google_sheets_sync_streamlit import GoogleSheetsSync
                sync = GoogleSheetsSync()
                sucesso = sync.sincronizar_para_banco(limpar_antes=False)
                
                if sucesso:
                    st.sidebar.success("✅ Sincronização concluída!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.sidebar.error("❌ Falha na sincronização.")
            except Exception as e:
                st.sidebar.error(f"❌ Erro: {str(e)}")

    st.sidebar.markdown("---")

    # Sidebar - Filtros normais
    st.sidebar.header("🔍 Filtros")

        # Extrair valores únicos para os filtros
    

    # Carregar dados
    df_jogadores = db.get_jogadores_com_vinculos()

        # Extrair valores únicos para os filtros (DEPOIS de carregar df_jogadores)
    posicoes = sorted(df_jogadores['posicao'].dropna().unique().tolist()) if 'posicao' in df_jogadores.columns else []
    nacionalidades = sorted(df_jogadores['nacionalidade'].dropna().unique().tolist()) if 'nacionalidade' in df_jogadores.columns else []
    clubes = sorted(df_jogadores['clube'].dropna().unique().tolist()) if 'clube' in df_jogadores.columns else []

        # Filtros (AGORA com as listas já criadas)
    filtro_nome = st.sidebar.text_input("🔎 Buscar por nome", "")
    
    filtro_posicao = st.sidebar.multiselect(
        "⚽ Posição",
        options=posicoes,
        default=[]
    )
    
    filtro_idade_min = st.sidebar.number_input("🎂 Idade mínima", min_value=15, max_value=45, value=15)
    filtro_idade_max = st.sidebar.number_input("🎂 Idade máxima", min_value=15, max_value=45, value=45)
    
    filtro_nacionalidade = st.sidebar.multiselect(
        "🏁 Nacionalidade",
        options=nacionalidades,
        default=[]
    )
    
    filtro_clube = st.sidebar.multiselect(
        "🏟️ Clube",
        options=clubes,
        default=[]
    )

    # Verificar se há dados
    if len(df_jogadores) == 0:
        st.error("⚠️ **Banco de dados vazio!**")
        st.markdown("O sistema não encontrou jogadores cadastrados.")

        # Botão para importar dados se estiver vazio
        if st.button("🔄 Importar Dados do Google Sheets Agora"):
            with st.spinner("Importando dados..."):
                try:
                    from google_sheets_sync_streamlit import GoogleSheetsSync
                    sync = GoogleSheetsSync()
                    sucesso = sync.sincronizar_para_banco(limpar_antes=False)
                    
                    if sucesso:
                        st.success("Dados importados! Recarregando...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Falha na sincronização.")
                except Exception as e:
                    st.error(f"Erro: {str(e)}")

        st.stop()

    # Restante do código do dashboard continua...
    # (Os tabs e toda a visualização segue depois)
    st.info("✅ Sistema funcionando! Dados carregados com sucesso.")

    # Aplicar filtros
    df_filtrado = df_jogadores.copy()

        # Aplicar filtros progressivamente
    if filtro_nome:
        df_filtrado = df_filtrado[df_filtrado['nome'].str.contains(filtro_nome, case=False, na=False)]
    
    if filtro_posicao:
        df_filtrado = df_filtrado[df_filtrado['posicao'].isin(filtro_posicao)]
    
    if 'idade_atual' in df_filtrado.columns:
        df_filtrado = df_filtrado[
            (df_filtrado['idade_atual'] >= filtro_idade_min) & 
            (df_filtrado['idade_atual'] <= filtro_idade_max)
        ]
    
    if filtro_nacionalidade:
        df_filtrado = df_filtrado[df_filtrado['nacionalidade'].isin(filtro_nacionalidade)]
    
    if filtro_clube:
        df_filtrado = df_filtrado[df_filtrado['clube'].isin(filtro_clube)]
    
    # Mostrar apenas primeiros 20 jogadores como exemplo
    st.markdown("---")
    st.subheader(f"📋 Jogadores Encontrados: {len(df_filtrado)}")
    
    # Exibir tabela de jogadores
    if len(df_filtrado) > 0:
        # Selecionar colunas principais para exibir
        colunas_exibir = ['nome', 'posicao', 'idade_atual', 'nacionalidade', 'clube']
        colunas_disponiveis = [col for col in colunas_exibir if col in df_filtrado.columns]
        
        # Mostrar tabela
        st.dataframe(
            df_filtrado[colunas_disponiveis].head(20),
            use_container_width=True,
            height=600
        )
        
        if len(df_filtrado) > 20:
            st.info(f"Mostrando os primeiros 20 de {len(df_filtrado)} jogadores. Use os filtros na sidebar para refinar a busca.")
    else:
        st.warning("Nenhum jogador encontrado com os filtros aplicados.")


if __name__ == "__main__":
    main()
