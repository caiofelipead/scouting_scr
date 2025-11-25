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
    current_path = Path(__file__).resolve()
    root_path = current_path.parent.parent

    if str(root_path) not in sys.path:
        sys.path.append(str(root_path))

    from database import ScoutingDatabase

except ImportError as e:
    st.error(f"❌ Erro Crítico de Importação: {e}")
    st.info(f"📂 Caminho tentado: {root_path}")
    st.stop()

"""
Dashboard Interativo de Scouting
Sistema moderno de visualização e análise de jogadores
"""

# CSS customizado
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
    h1 {
        color: #1f77b4;
        padding-bottom: 1rem;
    }
    h2 {
        color: #2c3e50;
        padding-top: 1rem;
    }
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
    }
    td {
        padding: 10px;
        border-bottom: 1px solid #eee;
    }
    tr:hover {
        background-color: #f5f5f5 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(ttl=None)
def get_database():
    """Inicializa conexão com banco de dados"""
    return ScoutingDatabase()


def get_foto_jogador(id_jogador):
    """Retorna o caminho da foto do jogador ou None"""
    root_path = Path(__file__).resolve().parent.parent
    foto_path = root_path / "fotos" / f"{id_jogador}.jpg"
    if foto_path.exists() and foto_path.is_file():
        return str(foto_path)
    return None


def get_perfil_url(id_jogador):
    """Retorna a URL completa do perfil do jogador"""
    return f"?jogador={id_jogador}"


def calcular_media_jogador(db, id_jogador):
    """Calcula a média geral das últimas avaliações do jogador"""
    avals = db.get_ultima_avaliacao(id_jogador)
    if not avals.empty:
        media = (
            avals["nota_tatico"].iloc[0]
            + avals["nota_tecnico"].iloc[0]
            + avals["nota_fisico"].iloc[0]
            + avals["nota_mental"].iloc[0]
        ) / 4
        return media
    return 0.0


def get_top_jogadores_por_posicao(df_jogadores, db, posicoes_filtro, top_n=15):
    """Retorna os top N jogadores para uma lista de posições"""
    mask = (
        df_jogadores["posicao"]
        .astype(str)
        .str.contains("|".join(posicoes_filtro), case=False, na=False)
    )
    candidatos = df_jogadores[mask].copy()

    if len(candidatos) == 0:
        return []

    medias = []
    for _, jogador in candidatos.iterrows():
        media = calcular_media_jogador(db, jogador["id_jogador"])
        medias.append(media)

    candidatos["media_ranking"] = medias
    candidatos = candidatos.sort_values("media_ranking", ascending=False).head(top_n)

    opcoes = []
    for _, row in candidatos.iterrows():
        media_fmt = f"{row['media_ranking']:.1f}" if row["media_ranking"] > 0 else "N/A"
        label = f"{row['nome']} ({row['clube']}) - Média: {media_fmt}"
        opcoes.append({
            "label": label,
            "id": row["id_jogador"],
            "nome": row["nome"],
            "pos": row["posicao"],
            "media": row["media_ranking"],
        })

    return opcoes


def criar_radar_avaliacao(notas_dict, titulo="Avaliação do Atleta", cor="rgba(46, 204, 113, 0.4)"):
    """Cria gráfico de radar para avaliação do jogador"""
    categorias = list(notas_dict.keys())
    valores = list(notas_dict.values())
    valores += valores[:1]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=valores,
            theta=categorias + [categorias[0]],
            fill="toself",
            fillcolor=cor,
            line=dict(color=cor.replace("0.4", "1.0"), width=3),
            name="Avaliação",
        )
    )

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


def criar_radar_comparacao(jogadores_notas, nomes):
    """Cria gráfico de radar comparando múltiplos jogadores"""
    fig = go.Figure()
    
    cores = [
        "rgba(46, 204, 113, 0.4)",
        "rgba(52, 152, 219, 0.4)", 
        "rgba(231, 76, 60, 0.4)",
    ]
    
    for idx, (notas, nome) in enumerate(zip(jogadores_notas, nomes)):
        categorias = list(notas.keys())
        valores = list(notas.values())
        valores += valores[:1]
        
        fig.add_trace(
            go.Scatterpolar(
                r=valores,
                theta=categorias + [categorias[0]],
                fill="toself",
                fillcolor=cores[idx],
                line=dict(color=cores[idx].replace("0.4", "1.0"), width=3),
                name=nome,
            )
        )
    
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
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        title=dict(
            text="Comparação de Jogadores", 
            x=0.5, 
            xanchor="center", 
            font=dict(size=18, color="#2c3e50")
        ),
        height=500,
        margin=dict(l=80, r=80, t=80, b=80),
    )
    
    return fig


def criar_grafico_evolucao(df_avaliacoes):
    """Cria gráfico de linha mostrando evolução das notas"""
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
    """Cria um campo de futebol e plota os jogadores"""
    if len(df_jogadores) == 0:
        st.warning("Sem jogadores para exibir no mapa.")
        return

    pitch = Pitch(pitch_type="statsbomb", pitch_color="#22312b", line_color="#c7d5cc")
    fig, ax = pitch.draw(figsize=(12, 8))

    coord_map_fallback = {
        "goleiro": (10, 40),
        "zagueiro": (30, 40),
        "lateral": (35, 10),
        "volante": (50, 40),
        "meia": (75, 40),
        "atacante": (105, 40),
    }

    x_list = []
    y_list = []
    names = []
    colors = []

    for _, row in df_jogadores.iterrows():
        if coordenadas_fixas and row["id_jogador"] in coordenadas_fixas:
            base_coord = coordenadas_fixas[row["id_jogador"]]
            x_jitter = random.uniform(-1, 1)
            y_jitter = random.uniform(-1, 1)
        else:
            pos_str = str(row["posicao"]).lower().strip()
            base_coord = (60, 40)

            match_found = False
            for key, coord in coord_map_fallback.items():
                if key in pos_str:
                    base_coord = coord
                    match_found = True
                    break

            if not match_found:
                base_coord = (random.uniform(10, 110), 40)

            x_jitter = random.uniform(-6, 6)
            y_jitter = random.uniform(-6, 6)

        x_list.append(base_coord[0] + x_jitter)
        y_list.append(base_coord[1] + y_jitter)
        names.append(row["nome"])

        if pd.notna(row.get("idade_atual")):
            if row["idade_atual"] < 23:
                colors.append("#2ecc71")
            elif row["idade_atual"] < 30:
                colors.append("#f1c40f")
            else:
                colors.append("#e74c3c")
        else:
            colors.append("#ecf0f1")

    pitch.scatter(
        x_list, y_list, ax=ax, c=colors, s=500, edgecolors="black", zorder=2, alpha=0.9
    )

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

    st.pyplot(fig)

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

    jogador = pd.read_sql_query(query, conn, params={'id': id_busca})
    conn.close()

    if len(jogador) == 0:
        st.error(f"Jogador não encontrado! (ID: {id_busca})")
        if st.button("Voltar"):
            st.session_state.pagina = "dashboard"
            st.rerun()
        return

    jogador = jogador.iloc[0]

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
        st.metric("Idade", f"{jogador.get('idade_atual', 'N/A')} anos" if pd.notna(jogador.get("idade_atual")) else "N/A")
        st.metric("Altura", f"{jogador.get('altura', 'N/A')} cm" if pd.notna(jogador.get("altura")) else "N/A")
        st.metric("Pé Dominante", jogador.get("pe_dominante", "N/A") if pd.notna(jogador.get("pe_dominante")) else "N/A")
        st.metric("Nacionalidade", jogador.get("nacionalidade", "N/A") if pd.notna(jogador.get("nacionalidade")) else "N/A")

    with col2:
        st.title(jogador["nome"])
        st.subheader(f"{jogador.get('posicao', 'N/A')} • {jogador.get('clube', 'Livre')}")

        st.markdown("---")
        st.markdown("### 📋 Informações do Vínculo")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("**Clube Atual**")
            st.markdown(f"🏟️ {jogador.get('clube', 'Livre')}")

        with col_b:
            st.markdown("**Liga**")
            st.markdown(f"🏆 {jogador.get('liga_clube', 'N/A')}")

        with col_c:
            st.markdown("**Fim de Contrato**")
            st.markdown(f"📅 {jogador.get('data_fim_contrato', 'N/A')}")

    st.markdown("---")

    # Tabs de avaliação
    tab_aval, tab_hist, tab_evol = st.tabs(["📝 Nova Avaliação", "📊 Histórico", "📈 Evolução"])

    with tab_aval:
        st.markdown("### 📝 Registrar Nova Avaliação")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with st.form("form_avaliacao"):
                data_avaliacao = st.date_input("Data", value=datetime.now())
                
                st.markdown("#### ⭐ Potencial")
                nota_potencial = st.slider("Potencial", 1.0, 5.0, 3.0, 0.5)
                
                st.markdown("#### 📊 Dimensões")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    nota_tatico = st.slider("⚙️ Tático", 1.0, 5.0, 3.0, 0.5)
                    nota_tecnico = st.slider("⚽ Técnico", 1.0, 5.0, 3.0, 0.5)
                
                with col_b:
                    nota_fisico = st.slider("💪 Físico", 1.0, 5.0, 3.0, 0.5)
                    nota_mental = st.slider("🧠 Mental", 1.0, 5.0, 3.0, 0.5)
                
                observacoes = st.text_area("Observações", height=100)
                avaliador = st.text_input("Avaliador (opcional)")
                
                if st.form_submit_button("💾 Salvar", type="primary"):
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
                        st.success("✅ Avaliação salva!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
        
        with col2:
            st.markdown("#### Preview")
            fig = criar_radar_avaliacao({
                "Tático": 3.0,
                "Técnico": 3.0,
                "Físico": 3.0,
                "Mental": 3.0
            })
            st.plotly_chart(fig, use_container_width=True)

    with tab_hist:
        avaliacoes = db.get_avaliacoes_jogador(id_busca)
        
        if len(avaliacoes) > 0:
            ultima = avaliacoes.iloc[0]
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if pd.notna(ultima.get("nota_potencial")):
                    st.metric("⭐ Potencial", f"{ultima['nota_potencial']:.1f}")
                
                st.markdown(f"**Data:** {pd.to_datetime(ultima['data_avaliacao']).strftime('%d/%m/%Y')}")
                st.markdown(f"**Avaliador:** {ultima.get('avaliador', 'N/A')}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Tático", f"{ultima.get('nota_tatico', 0):.1f}")
                    st.metric("Técnico", f"{ultima.get('nota_tecnico', 0):.1f}")
                with col_b:
                    st.metric("Físico", f"{ultima.get('nota_fisico', 0):.1f}")
                    st.metric("Mental", f"{ultima.get('nota_mental', 0):.1f}")
            
            with col2:
                notas = {
                    "Tático": ultima.get("nota_tatico", 0),
                    "Técnico": ultima.get("nota_tecnico", 0),
                    "Físico": ultima.get("nota_fisico", 0),
                    "Mental": ultima.get("nota_mental", 0)
                }
                fig = criar_radar_avaliacao(notas, "Perfil Atual")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma avaliação registrada")

    with tab_evol:
        avaliacoes = db.get_avaliacoes_jogador(id_busca)
        
        if len(avaliacoes) > 1:
            fig = criar_grafico_evolucao(avaliacoes)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Necessário pelo menos 2 avaliações")


def exibir_lista_com_fotos(df_display, db):
    """Exibe lista de jogadores com fotos"""
    df_display = df_display.drop_duplicates(subset=["id_jogador"], keep="first").reset_index(drop=True)

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
                    st.caption(f"{jogador.get('posicao', 'N/A')}")
                    st.caption(f"{jogador.get('clube', 'Livre')}")

                    if st.button("Ver Perfil", key=f"perfil_{jogador['id_jogador']}_{idx}"):
                        st.session_state.pagina = "perfil"
                        st.session_state.jogador_selecionado = jogador["id_jogador"]
                        st.query_params["jogador"] = jogador["id_jogador"]
                        st.rerun()


def tab_ranking(db, df_jogadores):
    """Tab de Ranking"""
    st.markdown("### 🏆 Ranking de Jogadores")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        posicao_grupo = st.selectbox(
            "Grupo de Posição",
            ["Goleiros", "Zagueiros", "Laterais", "Volantes", "Meias", "Atacantes", "Todas"]
        )
        
        mapa_posicoes = {
            "Goleiros": ["goleiro", "gk"],
            "Zagueiros": ["zagueiro", "cb"],
            "Laterais": ["lateral", "lb", "rb"],
            "Volantes": ["volante", "cdm"],
            "Meias": ["meia", "cam", "cm"],
            "Atacantes": ["atacante", "st", "cf"],
            "Todas": []
        }
        
        top_n = st.slider("Quantidade", 5, 30, 15)
    
    with col2:
        if posicao_grupo == "Todas":
            ranking_data = []
            for _, jogador in df_jogadores.iterrows():
                media = calcular_media_jogador(db, jogador["id_jogador"])
                if media > 0:
                    ranking_data.append({
                        "nome": jogador["nome"],
                        "posicao": jogador["posicao"],
                        "clube": jogador["clube"],
                        "media": media
                    })
            
            if ranking_data:
                df_ranking = pd.DataFrame(ranking_data)
                df_ranking = df_ranking.sort_values("media", ascending=False).head(top_n)
                
                for idx, row in df_ranking.iterrows():
                    col_a, col_b, col_c = st.columns([1, 3, 1])
                    
                    with col_a:
                        if idx < 3:
                            st.markdown(f"### {['🥇', '🥈', '🥉'][idx]}")
                        else:
                            st.markdown(f"**#{idx+1}**")
                    
                    with col_b:
                        st.markdown(f"**{row['nome']}** ({row['posicao']})")
                        st.caption(f"{row['clube']}")
                    
                    with col_c:
                        st.metric("Média", f"{row['media']:.2f}")
                    
                    st.markdown("---")
        else:
            posicoes = mapa_posicoes[posicao_grupo]
            top_jogadores = get_top_jogadores_por_posicao(df_jogadores, db, posicoes, top_n)
            
            for idx, jogador in enumerate(top_jogadores):
                col_a, col_b, col_c = st.columns([1, 3, 1])
                
                with col_a:
                    if idx < 3:
                        st.markdown(f"### {['🥇', '🥈', '🥉'][idx]}")
                    else:
                        st.markdown(f"**#{idx+1}**")
                
                with col_b:
                    st.markdown(f"**{jogador['nome']}**")
                    st.caption(f"{jogador['pos']}")
                
                with col_c:
                    st.metric("Média", f"{jogador['media']:.2f}")
                
                st.markdown("---")


def tab_comparador(db, df_jogadores):
    """Tab de Comparação"""
    st.markdown("### ⚖️ Comparador de Jogadores")
    
    opcoes = []
    for _, j in df_jogadores.iterrows():
        opcoes.append({
            "label": f"{j['nome']} - {j['posicao']} ({j['clube']})",
            "id": j["id_jogador"]
        })
    
    col1, col2, col3 = st.columns(3)
    
    jogadores_sel = []
    
    with col1:
        j1 = st.selectbox("Jogador 1", range(len(opcoes)), format_func=lambda x: opcoes[x]["label"])
        jogadores_sel.append(opcoes[j1]["id"])
    
    with col2:
        j2 = st.selectbox("Jogador 2", range(len(opcoes)), format_func=lambda x: opcoes[x]["label"], key="j2")
        jogadores_sel.append(opcoes[j2]["id"])
    
    with col3:
        j3_opt = ["Nenhum"] + list(range(len(opcoes)))
        j3 = st.selectbox("Jogador 3 (Opcional)", j3_opt, 
                         format_func=lambda x: "Nenhum" if x == "Nenhum" else opcoes[x]["label"])
        if j3 != "Nenhum":
            jogadores_sel.append(opcoes[j3]["id"])
    
    if len(jogadores_sel) >= 2:
        jogadores_notas = []
        jogadores_nomes = []
        
        for id_j in jogadores_sel:
            aval = db.get_ultima_avaliacao(id_j)
            info = df_jogadores[df_jogadores['id_jogador'] == id_j].iloc[0]
            
            if not aval.empty:
                notas = {
                    "Tático": aval['nota_tatico'].iloc[0],
                    "Técnico": aval['nota_tecnico'].iloc[0],
                    "Físico": aval['nota_fisico'].iloc[0],
                    "Mental": aval['nota_mental'].iloc[0]
                }
            else:
                notas = {"Tático": 0, "Técnico": 0, "Físico": 0, "Mental": 0}
            
            jogadores_notas.append(notas)
            jogadores_nomes.append(info['nome'])
        
        fig = criar_radar_comparacao(jogadores_notas, jogadores_nomes)
        st.plotly_chart(fig, use_container_width=True)


def tab_shadow_team(db, df_jogadores):
    """Tab Shadow Team"""
    st.markdown("### ⚽ Shadow Team - Monte seu Time Ideal")
    
    if "shadow_team" not in st.session_state:
        st.session_state.shadow_team = {}
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        formacao = st.selectbox("Formação", ["4-4-2", "4-3-3", "3-5-2"])
        
        posicoes_form = {
            "4-4-2": ["Goleiro", "Zagueiro 1", "Zagueiro 2", "Lateral E", "Lateral D",
                      "Meia 1", "Meia 2", "Meia 3", "Meia 4", "Atacante 1", "Atacante 2"],
            "4-3-3": ["Goleiro", "Zagueiro 1", "Zagueiro 2", "Lateral E", "Lateral D",
                      "Volante", "Meia 1", "Meia 2", "Atacante 1", "Atacante 2", "Atacante 3"],
            "3-5-2": ["Goleiro", "Zagueiro 1", "Zagueiro 2", "Zagueiro 3", "Ala E", "Ala D",
                      "Volante", "Meia 1", "Meia 2", "Atacante 1", "Atacante 2"]
        }
        
        for pos in posicoes_form[formacao]:
            if "Goleiro" in pos:
                filtro = ["goleiro"]
            elif "Zagueiro" in pos:
                filtro = ["zagueiro"]
            elif "Lateral" in pos or "Ala" in pos:
                filtro = ["lateral"]
            elif "Volante" in pos:
                filtro = ["volante"]
            elif "Meia" in pos:
                filtro = ["meia"]
            else:
                filtro = ["atacante"]
            
            top = get_top_jogadores_por_posicao(df_jogadores, db, filtro, 10)
            
            if top:
                opcoes = ["Nenhum"] + [j["label"] for j in top]
                sel = st.selectbox(pos, opcoes, key=f"shadow_{pos}")
                
                if sel != "Nenhum":
                    for j in top:
                        if j["label"] == sel:
                            st.session_state.shadow_team[pos] = j["id"]
                            break
        
        if st.button("🗑️ Limpar"):
            st.session_state.shadow_team = {}
            st.rerun()
    
    with col2:
        if len(st.session_state.shadow_team) > 0:
            jogadores_sel = []
            for id_j in st.session_state.shadow_team.values():
                info = df_jogadores[df_jogadores['id_jogador'] == id_j].iloc[0]
                jogadores_sel.append(info)
            
            if jogadores_sel:
                df_shadow = pd.DataFrame(jogadores_sel)
                plotar_mapa_elenco(df_shadow, mostrar_nomes=True)


def main():
    st.title("⚽ Scout Pro - Sistema de Monitoramento")
    st.markdown("---")

    db = get_database()
    db.criar_tabela_avaliacoes()

    query_params = st.query_params
    jogador_id_url = query_params.get("jogador", None)

    if "pagina" not in st.session_state:
        st.session_state.pagina = "dashboard"
    if "jogador_selecionado" not in st.session_state:
        st.session_state.jogador_selecionado = None

    if jogador_id_url:
        try:
            st.session_state.pagina = "perfil"
            st.session_state.jogador_selecionado = int(jogador_id_url)
        except Exception:
            pass

    if st.session_state.pagina == "perfil":
        if st.button("← Voltar"):
            st.session_state.pagina = "dashboard"
            st.session_state.jogador_selecionado = None
            st.query_params.clear()
            st.rerun()

        st.markdown("---")
        exibir_perfil_jogador(db, st.session_state.jogador_selecionado)
        return

    # Sidebar
    st.sidebar.header("🔄 Sincronização")

    if st.sidebar.button("Baixar Dados", type="primary"):
        with st.spinner("Sincronizando..."):
            try:
                from google_sheets_sync_streamlit import GoogleSheetsSync
                sync = GoogleSheetsSync()
                if sync.sincronizar_para_banco(limpar_antes=False):
                    st.sidebar.success("✅ Sincronizado!")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Erro: {str(e)}")

    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filtros")

    df_jogadores = db.get_jogadores_com_vinculos()

    if len(df_jogadores) == 0:
        st.error("⚠️ Banco vazio!")
        st.stop()

    posicoes = sorted(df_jogadores['posicao'].dropna().unique())
    clubes = sorted(df_jogadores['clube'].dropna().unique())

    filtro_nome = st.sidebar.text_input("🔎 Nome", "")
    filtro_posicao = st.sidebar.multiselect("⚽ Posição", posicoes, [])
    filtro_clube = st.sidebar.multiselect("🏟️ Clube", clubes, [])

    # Aplicar filtros
    df_filtrado = df_jogadores.copy()

    if filtro_nome:
        df_filtrado = df_filtrado[df_filtrado['nome'].str.contains(filtro_nome, case=False, na=False)]
    if filtro_posicao:
        df_filtrado = df_filtrado[df_filtrado['posicao'].isin(filtro_posicao)]
    if filtro_clube:
        df_filtrado = df_filtrado[df_filtrado['clube'].isin(filtro_clube)]

    # Tabs principais
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Lista",
        "🏆 Ranking",
        "⚖️ Comparador",
        "🗺️ Mapa",
        "⚽ Shadow Team"
    ])
    
    with tab1:
        st.subheader(f"Jogadores: {len(df_filtrado)}")
        if len(df_filtrado) > 0:
            exibir_lista_com_fotos(df_filtrado.head(20), db)
    
    with tab2:
        tab_ranking(db, df_filtrado)
    
    with tab3:
        tab_comparador(db, df_filtrado)
    
    with tab4:
        if len(df_filtrado) > 0:
            plotar_mapa_elenco(df_filtrado.head(50), mostrar_nomes=True)
    
    with tab5:
        tab_shadow_team(db, df_jogadores)


if __name__ == "__main__":
    main()