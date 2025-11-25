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

# CSS Profissional - Scout Pro
st.markdown(
    """
    <style>
    /* Layout principal */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Header com gradiente */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.95);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Métricas melhoradas */
    .stMetric {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stMetric:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    }
    
    /* Cards de jogadores */
    .player-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .player-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    /* Tabs customizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #f8f9fa;
        padding: 0.75rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background-color: white;
        border-radius: 10px;
        color: #495057;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 1.5rem;
        border: 2px solid transparent;
        transition: all 0.2s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-color: #667eea;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Botões */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
        border: 2px solid transparent;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Botões primários */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
    }
    
    /* Tabelas HTML */
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-radius: 10px;
        overflow: hidden;
        background: white;
    }
    
    th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 14px 12px;
        text-align: left;
        font-weight: 600;
        position: sticky;
        top: 0;
        z-index: 10;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    td {
        padding: 12px;
        border-bottom: 1px solid #e9ecef;
    }
    
    tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    tr:hover {
        background-color: #e3f2fd !important;
        transition: background-color 0.2s;
    }
    
    /* Links */
    a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    a:hover {
        color: #764ba2;
        text-decoration: underline !important;
    }
    
    /* Medalhas de ranking */
    .rank-medal {
        font-size: 2rem;
        display: inline-block;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    /* Containers de ranking */
    .rank-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
        transition: all 0.2s;
    }
    
    .rank-container:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateX(5px);
    }
    
    /* Top 3 highlight */
    .rank-1 { border-left-color: #FFD700 !important; background: linear-gradient(90deg, #fff9e6 0%, white 100%); }
    .rank-2 { border-left-color: #C0C0C0 !important; background: linear-gradient(90deg, #f5f5f5 0%, white 100%); }
    .rank-3 { border-left-color: #CD7F32 !important; background: linear-gradient(90deg, #fff4e6 0%, white 100%); }
    
    /* Alertas */
    .alert-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .alert-danger {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Scrollbar customizada */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f3f4;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        border: 2px solid #f1f3f4;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Expander customizado */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #6c757d;
        font-size: 0.9rem;
        border-top: 2px solid #e9ecef;
        margin-top: 3rem;
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-in;
    }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(ttl=None)
def get_database():
    """Inicializa conexão com banco de dados - Cache persistente"""
    return ScoutingDatabase()


def get_foto_jogador(id_jogador, transfermarkt_id=None, debug=False):
    """Retorna o caminho da foto do jogador ou None
    
    Procura fotos com:
    1. ID do banco de dados (ex: 123.jpg)
    2. ID do Transfermarkt (ex: 68290.jpg)
    
    Funciona tanto se dashboard.py está em:
    - scouting_scr/dashboard.py → fotos em scouting_scr/fotos/
    - scouting_scr/app/dashboard.py → fotos em scouting_scr/fotos/
    """
    from pathlib import Path
    import re

    current_file = Path(__file__).resolve()
    
    # Tentar múltiplos caminhos
    possivel_fotos_dirs = [
        current_file.parent / "fotos",  # Se dashboard está na raiz
        current_file.parent.parent / "fotos",  # Se dashboard está em app/
    ]
    
    # Encontrar a pasta fotos que existe
    fotos_dir = None
    for dir_path in possivel_fotos_dirs:
        if dir_path.exists() and dir_path.is_dir():
            fotos_dir = dir_path
            break
    
    if fotos_dir is None:
        if debug:
            st.sidebar.error("❌ Pasta 'fotos' não encontrada!")
            st.sidebar.write(f"📂 Arquivo atual: `{current_file}`")
            st.sidebar.write("Caminhos tentados:")
            for d in possivel_fotos_dirs:
                st.sidebar.code(str(d))
        return None
    
    if debug:
        st.sidebar.write(f"🔍 **Debug - Foto do jogador ID: {id_jogador}**")
        st.sidebar.write(f"📂 Dashboard: `{current_file}`")
        st.sidebar.write(f"📁 Pasta fotos: `{fotos_dir}`")
        st.sidebar.write(f"✅ Pasta existe: SIM")
    
    # Lista de IDs para tentar
    ids_para_tentar = [id_jogador]
    
    # Adicionar Transfermarkt ID se fornecido
    if transfermarkt_id:
        tm_id = str(transfermarkt_id)
        match = re.search(r'\d+', tm_id)
        if match:
            ids_para_tentar.append(match.group(0))
    
    # Tentar encontrar foto com cada ID
    for test_id in ids_para_tentar:
        # Tentar .jpg
        foto_path = fotos_dir / f"{test_id}.jpg"
        
        if debug:
            st.sidebar.write(f"📸 Tentando: `{test_id}.jpg`")
            st.sidebar.write(f"   Caminho: `{foto_path}`")
            st.sidebar.write(f"   Existe: {'✅ SIM' if foto_path.exists() else '❌ NÃO'}")
        
        if foto_path.exists() and foto_path.is_file():
            if debug:
                st.sidebar.success(f"✅ FOTO ENCONTRADA: {foto_path.name}")
            return str(foto_path)
        
        # Tentar .png
        foto_path_png = fotos_dir / f"{test_id}.png"
        if foto_path_png.exists() and foto_path_png.is_file():
            if debug:
                st.sidebar.success(f"✅ FOTO ENCONTRADA: {foto_path_png.name}")
            return str(foto_path_png)
    
    if debug:
        # Listar fotos disponíveis
        fotos = list(fotos_dir.glob("*.jpg")) + list(fotos_dir.glob("*.png"))
        st.sidebar.write(f"📁 Total de fotos na pasta: {len(fotos)}")
        if len(fotos) > 0:
            st.sidebar.write("**Primeiras 10 fotos:**")
            for f in fotos[:10]:
                st.sidebar.code(f.name)
        else:
            st.sidebar.warning("⚠️ Pasta de fotos está vazia!")
    
    return None


def get_perfil_url(id_jogador):
    """Retorna a URL completa do perfil do jogador"""
    return f"?jogador={id_jogador}"


def calcular_media_jogador(db, id_jogador):
    """Calcula a média geral das avaliações do jogador (4 pilares)"""
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
        media = calcular_media_jogador(db, jogador["id_jogador"])
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
                "media": row["media_ranking"],
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
                base_coord = (random.uniform(10, 110), 40)

            # Jitter maior para espalhar na visualização geral
            x_jitter = random.uniform(-6, 6)
            y_jitter = random.uniform(-6, 6)

        x_list.append(base_coord[0] + x_jitter)
        y_list.append(base_coord[1] + y_jitter)
        names.append(row["nome"])

        # Cor baseada na idade (Mais jovem = verde, Mais velho = vermelho)
        if pd.notna(row.get("idade_atual")):
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


def exibir_perfil_jogador(db, id_jogador, debug=False):
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
        # Buscar foto com ambos os IDs
        tm_id = jogador.get('transfermarkt_id', None)
        foto_path = get_foto_jogador(id_busca, transfermarkt_id=tm_id, debug=debug)
        
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


def exibir_lista_com_fotos(df_display, db, debug=False):
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
                    # Tentar pegar foto com ambos os IDs
                    tm_id = jogador.get('transfermarkt_id', None)
                    foto_path = get_foto_jogador(
                        jogador["id_jogador"], 
                        transfermarkt_id=tm_id,
                        debug=debug and idx == 0  # Debug apenas no primeiro
                    )

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


def tab_ranking(db, df_jogadores):
    """Tab de Ranking de Jogadores por Posição"""
    st.markdown("### 🏆 Ranking de Jogadores")
    st.markdown("Visualize os melhores jogadores por posição baseado nas avaliações")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("#### Filtros")
        
        posicao_grupo = st.selectbox(
            "Selecione o Grupo de Posição",
            [
                "Goleiros",
                "Zagueiros",
                "Laterais",
                "Volantes",
                "Meias",
                "Atacantes",
                "Todas as Posições"
            ]
        )
        
        mapa_posicoes = {
            "Goleiros": ["goleiro", "gk"],
            "Zagueiros": ["zagueiro", "cb", "defensor"],
            "Laterais": ["lateral", "lb", "rb", "wing"],
            "Volantes": ["volante", "cdm", "dm"],
            "Meias": ["meia", "cam", "cm", "am"],
            "Atacantes": ["atacante", "st", "cf", "fw"],
            "Todas as Posições": []
        }
        
        top_n = st.slider("Quantidade de jogadores", 5, 30, 15)
        
    with col2:
        if posicao_grupo == "Todas as Posições":
            st.info("📊 Calculando ranking geral de todos os jogadores...")
            
            # Calcular média para todos
            ranking_data = []
            for _, jogador in df_jogadores.iterrows():
                media = calcular_media_jogador(db, jogador["id_jogador"])
                if media > 0:  # Apenas jogadores com avaliação
                    ranking_data.append({
                        "id_jogador": jogador["id_jogador"],
                        "nome": jogador["nome"],
                        "posicao": jogador["posicao"],
                        "clube": jogador["clube"],
                        "idade": jogador.get("idade_atual", "N/A"),
                        "media": media
                    })
            
            if ranking_data:
                df_ranking = pd.DataFrame(ranking_data)
                df_ranking = df_ranking.sort_values("media", ascending=False).head(top_n)
                
                # Exibir tabela
                st.markdown(f"#### 🏅 Top {top_n} Jogadores (Geral)")
                
                for idx, row in df_ranking.iterrows():
                    col_a, col_b, col_c = st.columns([1, 3, 1])
                    
                    with col_a:
                        # Medalhas para Top 3
                        if idx == 0:
                            st.markdown("### 🥇")
                        elif idx == 1:
                            st.markdown("### 🥈")
                        elif idx == 2:
                            st.markdown("### 🥉")
                        else:
                            st.markdown(f"**#{idx+1}**")
                    
                    with col_b:
                        st.markdown(f"**{row['nome']}** ({row['posicao']})")
                        st.caption(f"{row['clube']} • {row['idade']} anos")
                    
                    with col_c:
                        st.metric("Média", f"{row['media']:.2f}")
                    
                    st.markdown("---")
            else:
                st.warning("Nenhum jogador com avaliação encontrado.")
        
        else:
            posicoes = mapa_posicoes[posicao_grupo]
            top_jogadores = get_top_jogadores_por_posicao(df_jogadores, db, posicoes, top_n)
            
            if len(top_jogadores) > 0:
                st.markdown(f"#### 🏅 Top {len(top_jogadores)} {posicao_grupo}")
                
                for idx, jogador in enumerate(top_jogadores):
                    col_a, col_b, col_c = st.columns([1, 3, 1])
                    
                    with col_a:
                        # Medalhas para os 3 primeiros
                        if idx == 0:
                            st.markdown("### 🥇")
                        elif idx == 1:
                            st.markdown("### 🥈")
                        elif idx == 2:
                            st.markdown("### 🥉")
                        else:
                            st.markdown(f"**#{idx+1}**")
                    
                    with col_b:
                        st.markdown(f"**{jogador['nome']}**")
                        st.caption(f"{jogador['pos']}")
                    
                    with col_c:
                        media_val = jogador['media']
                        st.metric("Média", f"{media_val:.2f}")
                        
                        if st.button("Ver Perfil", key=f"rank_{jogador['id']}_{idx}", use_container_width=True):
                            st.session_state.pagina = "perfil"
                            st.session_state.jogador_selecionado = jogador['id']
                            st.query_params["jogador"] = jogador['id']
                            st.rerun()
                    
                    st.markdown("---")
            else:
                st.info(f"Nenhum jogador encontrado na posição {posicao_grupo}")


def tab_comparador(db, df_jogadores):
    """Tab de Comparação de Jogadores"""
    st.markdown("### ⚖️ Comparador de Jogadores")
    st.markdown("Compare até 3 jogadores lado a lado")
    
    # Preparar lista de jogadores para seleção
    opcoes_jogadores = []
    for _, jogador in df_jogadores.iterrows():
        label = f"{jogador['nome']} - {jogador['posicao']} ({jogador['clube']})"
        opcoes_jogadores.append({"label": label, "id": jogador["id_jogador"]})
    
    col1, col2, col3 = st.columns(3)
    
    jogadores_selecionados = []
    
    with col1:
        st.markdown("#### Jogador 1")
        jogador1 = st.selectbox(
            "Selecione o primeiro jogador",
            options=range(len(opcoes_jogadores)),
            format_func=lambda x: opcoes_jogadores[x]["label"],
            key="comp_j1"
        )
        if jogador1 is not None:
            jogadores_selecionados.append(opcoes_jogadores[jogador1]["id"])
    
    with col2:
        st.markdown("#### Jogador 2")
        jogador2 = st.selectbox(
            "Selecione o segundo jogador",
            options=range(len(opcoes_jogadores)),
            format_func=lambda x: opcoes_jogadores[x]["label"],
            key="comp_j2"
        )
        if jogador2 is not None:
            jogadores_selecionados.append(opcoes_jogadores[jogador2]["id"])
    
    with col3:
        st.markdown("#### Jogador 3 (Opcional)")
        jogador3 = st.selectbox(
            "Selecione o terceiro jogador",
            options=["Nenhum"] + list(range(len(opcoes_jogadores))),
            format_func=lambda x: "Nenhum" if x == "Nenhum" else opcoes_jogadores[x]["label"],
            key="comp_j3"
        )
        if jogador3 != "Nenhum":
            jogadores_selecionados.append(opcoes_jogadores[jogador3]["id"])
    
    if len(jogadores_selecionados) >= 2:
        st.markdown("---")
        
        # Buscar dados dos jogadores
        jogadores_data = []
        jogadores_notas = []
        jogadores_nomes = []
        
        for id_jogador in jogadores_selecionados:
            avaliacao = db.get_ultima_avaliacao(id_jogador)
            jogador_info = df_jogadores[df_jogadores['id_jogador'] == id_jogador].iloc[0]
            
            jogadores_data.append({
                "id": id_jogador,
                "nome": jogador_info['nome'],
                "posicao": jogador_info['posicao'],
                "clube": jogador_info['clube'],
                "idade": jogador_info.get('idade_atual', 'N/A'),
                "altura": jogador_info.get('altura', 'N/A'),
            })
            
            if not avaliacao.empty:
                notas = {
                    "Tático": avaliacao['nota_tatico'].iloc[0],
                    "Técnico": avaliacao['nota_tecnico'].iloc[0],
                    "Físico": avaliacao['nota_fisico'].iloc[0],
                    "Mental": avaliacao['nota_mental'].iloc[0],
                }
                jogadores_notas.append(notas)
                jogadores_nomes.append(jogador_info['nome'])
            else:
                jogadores_notas.append({
                    "Tático": 0,
                    "Técnico": 0,
                    "Físico": 0,
                    "Mental": 0,
                })
                jogadores_nomes.append(f"{jogador_info['nome']} (Sem avaliação)")
        
        # Gráfico de radar comparativo
        if len(jogadores_notas) > 0:
            fig_comparacao = criar_radar_comparacao(jogadores_notas, jogadores_nomes)
            st.plotly_chart(fig_comparacao, use_container_width=True)
        
        # Tabela comparativa
        st.markdown("---")
        st.markdown("#### 📊 Comparação Detalhada")
        
        cols = st.columns(len(jogadores_data))
        
        for idx, (col, jogador, notas) in enumerate(zip(cols, jogadores_data, jogadores_notas)):
            with col:
                st.markdown(f"### {jogador['nome']}")
                st.markdown(f"**Posição:** {jogador['posicao']}")
                st.markdown(f"**Clube:** {jogador['clube']}")
                st.markdown(f"**Idade:** {jogador['idade']}")
                st.markdown(f"**Altura:** {jogador['altura']} cm")
                
                st.markdown("---")
                st.markdown("**Avaliações:**")
                
                media = sum(notas.values()) / 4 if sum(notas.values()) > 0 else 0
                st.metric("Média Geral", f"{media:.2f}")
                
                st.metric("Tático", f"{notas['Tático']:.1f}")
                st.metric("Técnico", f"{notas['Técnico']:.1f}")
                st.metric("Físico", f"{notas['Físico']:.1f}")
                st.metric("Mental", f"{notas['Mental']:.1f}")
    else:
        st.info("Selecione pelo menos 2 jogadores para comparar")


def tab_shadow_team(db, df_jogadores):
    """Tab para montar um Shadow Team (time ideal)"""
    st.markdown("### ⚽ Shadow Team - Monte seu Time Ideal")
    st.markdown("Selecione os melhores jogadores por posição para montar uma equipe")
    
    # Inicializar shadow team no session_state
    if "shadow_team" not in st.session_state:
        st.session_state.shadow_team = {}
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Selecione os Jogadores")
        
        formacao = st.selectbox(
            "Formação",
            ["4-4-2", "4-3-3", "3-5-2", "4-2-3-1"]
        )
        
        posicoes_formacao = {
            "4-4-2": ["Goleiro", "Zagueiro (1)", "Zagueiro (2)", "Lateral Esquerdo", 
                      "Lateral Direito", "Meia (1)", "Meia (2)", "Meia (3)", 
                      "Meia (4)", "Atacante (1)", "Atacante (2)"],
            "4-3-3": ["Goleiro", "Zagueiro (1)", "Zagueiro (2)", "Lateral Esquerdo",
                      "Lateral Direito", "Volante", "Meia (1)", "Meia (2)",
                      "Atacante (1)", "Atacante (2)", "Atacante (3)"],
            "3-5-2": ["Goleiro", "Zagueiro (1)", "Zagueiro (2)", "Zagueiro (3)",
                      "Ala Esquerdo", "Ala Direito", "Volante", "Meia (1)",
                      "Meia (2)", "Atacante (1)", "Atacante (2)"],
            "4-2-3-1": ["Goleiro", "Zagueiro (1)", "Zagueiro (2)", "Lateral Esquerdo",
                        "Lateral Direito", "Volante (1)", "Volante (2)", "Meia (1)",
                        "Meia (2)", "Meia (3)", "Atacante"]
        }
        
        posicoes = posicoes_formacao[formacao]
        
        # Criar seletores para cada posição
        for posicao in posicoes:
            # Determinar filtro de posição
            if "Goleiro" in posicao:
                filtro_pos = ["goleiro", "gk"]
            elif "Zagueiro" in posicao:
                filtro_pos = ["zagueiro", "cb"]
            elif "Lateral" in posicao or "Ala" in posicao:
                filtro_pos = ["lateral", "lb", "rb", "wing"]
            elif "Volante" in posicao:
                filtro_pos = ["volante", "cdm", "dm"]
            elif "Meia" in posicao:
                filtro_pos = ["meia", "cam", "cm"]
            else:
                filtro_pos = ["atacante", "st", "cf", "fw"]
            
            # Buscar top jogadores
            top_jogadores = get_top_jogadores_por_posicao(df_jogadores, db, filtro_pos, 20)
            
            if len(top_jogadores) > 0:
                opcoes = ["Nenhum"] + [j["label"] for j in top_jogadores]
                selecionado = st.selectbox(
                    posicao,
                    options=opcoes,
                    key=f"shadow_{posicao}"
                )
                
                if selecionado != "Nenhum":
                    # Encontrar o ID do jogador selecionado
                    for j in top_jogadores:
                        if j["label"] == selecionado:
                            st.session_state.shadow_team[posicao] = j["id"]
                            break
                elif posicao in st.session_state.shadow_team:
                    del st.session_state.shadow_team[posicao]
        
        if st.button("🗑️ Limpar Time", use_container_width=True):
            st.session_state.shadow_team = {}
            st.rerun()
    
    with col2:
        st.markdown("#### Visualização do Time")
        
        if len(st.session_state.shadow_team) > 0:
            # Preparar dados para visualização
            jogadores_selecionados = []
            for posicao, id_jogador in st.session_state.shadow_team.items():
                jogador_info = df_jogadores[df_jogadores['id_jogador'] == id_jogador].iloc[0]
                jogadores_selecionados.append(jogador_info)
            
            if len(jogadores_selecionados) > 0:
                df_shadow = pd.DataFrame(jogadores_selecionados)
                
                # Coordenadas fixas baseadas na formação
                coords_map = {}
                
                if formacao == "4-4-2":
                    coords_formacao = {
                        "Goleiro": (10, 40),
                        "Zagueiro (1)": (25, 25),
                        "Zagueiro (2)": (25, 55),
                        "Lateral Esquerdo": (25, 10),
                        "Lateral Direito": (25, 70),
                        "Meia (1)": (60, 15),
                        "Meia (2)": (60, 30),
                        "Meia (3)": (60, 50),
                        "Meia (4)": (60, 65),
                        "Atacante (1)": (100, 30),
                        "Atacante (2)": (100, 50),
                    }
                elif formacao == "4-3-3":
                    coords_formacao = {
                        "Goleiro": (10, 40),
                        "Zagueiro (1)": (25, 25),
                        "Zagueiro (2)": (25, 55),
                        "Lateral Esquerdo": (25, 10),
                        "Lateral Direito": (25, 70),
                        "Volante": (50, 40),
                        "Meia (1)": (60, 25),
                        "Meia (2)": (60, 55),
                        "Atacante (1)": (100, 20),
                        "Atacante (2)": (100, 40),
                        "Atacante (3)": (100, 60),
                    }
                elif formacao == "3-5-2":
                    coords_formacao = {
                        "Goleiro": (10, 40),
                        "Zagueiro (1)": (25, 20),
                        "Zagueiro (2)": (25, 40),
                        "Zagueiro (3)": (25, 60),
                        "Ala Esquerdo": (55, 10),
                        "Ala Direito": (55, 70),
                        "Volante": (50, 40),
                        "Meia (1)": (65, 30),
                        "Meia (2)": (65, 50),
                        "Atacante (1)": (100, 30),
                        "Atacante (2)": (100, 50),
                    }
                else:  # 4-2-3-1
                    coords_formacao = {
                        "Goleiro": (10, 40),
                        "Zagueiro (1)": (25, 25),
                        "Zagueiro (2)": (25, 55),
                        "Lateral Esquerdo": (25, 10),
                        "Lateral Direito": (25, 70),
                        "Volante (1)": (45, 30),
                        "Volante (2)": (45, 50),
                        "Meia (1)": (70, 20),
                        "Meia (2)": (70, 40),
                        "Meia (3)": (70, 60),
                        "Atacante": (100, 40),
                    }
                
                # Mapear IDs para coordenadas
                for posicao, id_jogador in st.session_state.shadow_team.items():
                    if posicao in coords_formacao:
                        coords_map[id_jogador] = coords_formacao[posicao]
                
                # Plotar campo com jogadores
                plotar_mapa_elenco(df_shadow, mostrar_nomes=True, coordenadas_fixas=coords_map)
                
                # Estatísticas do time
                st.markdown("---")
                st.markdown("#### 📊 Estatísticas do Time")
                
                total_jogadores = len(st.session_state.shadow_team)
                idade_media = df_shadow['idade_atual'].mean() if 'idade_atual' in df_shadow.columns else 0
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Jogadores", total_jogadores)
                with col_b:
                    st.metric("Idade Média", f"{idade_media:.1f}" if idade_media > 0 else "N/A")
                with col_c:
                    # Calcular média geral do time
                    medias = []
                    for id_j in st.session_state.shadow_team.values():
                        media = calcular_media_jogador(db, id_j)
                        if media > 0:
                            medias.append(media)
                    
                    media_time = np.mean(medias) if len(medias) > 0 else 0
                    st.metric("Média do Time", f"{media_time:.2f}" if media_time > 0 else "N/A")
        else:
            st.info("Selecione jogadores para montar seu time ideal")


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
        
        # Checkbox de debug na sidebar para perfil
        debug_fotos_perfil = st.sidebar.checkbox("🐛 Debug de Fotos (Perfil)", value=False, help="Ativa modo debug para verificar o caminho das fotos no perfil")
        
        exibir_perfil_jogador(db, st.session_state.jogador_selecionado, debug=debug_fotos_perfil)
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
    
    # DEBUG MODE
    debug_fotos = st.sidebar.checkbox("🐛 Debug de Fotos", value=False, help="Ativa modo debug para verificar o caminho das fotos")

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
    
    # ============== TABS PRINCIPAIS ==============
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Lista de Jogadores",
        "🏆 Ranking",
        "⚖️ Comparador",
        "🗺️ Mapa de Elenco",
        "⚽ Shadow Team"
    ])
    
    with tab1:
        st.subheader(f"📋 Jogadores Encontrados: {len(df_filtrado)}")
        
        if len(df_filtrado) > 0:
            exibir_lista_com_fotos(df_filtrado.head(20), db, debug=debug_fotos)
            
            if len(df_filtrado) > 20:
                st.info(f"Mostrando os primeiros 20 de {len(df_filtrado)} jogadores. Use os filtros na sidebar para refinar a busca.")
        else:
            st.warning("Nenhum jogador encontrado com os filtros aplicados.")
    
    with tab2:
        tab_ranking(db, df_filtrado)
    
    with tab3:
        tab_comparador(db, df_filtrado)
    
    with tab4:
        st.markdown("### 🗺️ Mapa de Elenco")
        st.markdown("Visualização dos jogadores filtrados no campo")
        
        if len(df_filtrado) > 0:
            plotar_mapa_elenco(df_filtrado.head(50), mostrar_nomes=True)
            
            if len(df_filtrado) > 50:
                st.info(f"Mostrando os primeiros 50 de {len(df_filtrado)} jogadores no mapa.")
        else:
            st.warning("Nenhum jogador para exibir no mapa.")
    
    with tab5:
        tab_shadow_team(db, df_jogadores)


if __name__ == "__main__":
    main()
