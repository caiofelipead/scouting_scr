import random
import sys
import time
import html
import streamlit_shadcn_ui as ui
from datetime import datetime
from pathlib import Path
# Imports movidos para dentro das funções para evitar dependência circular
# from migrate_financeiro import migrar_colunas_financeiras
# from avaliacao_massiva import criar_aba_avaliacao_massiva

# Imports de terceiros PRIMEIRO
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from mplsoccer import Pitch
from sqlalchemy import text

# Carrega CSS customizado
def load_custom_css():
    """Carrega CSS customizado do tema ScoutingStats"""
    from pathlib import Path
    css_path = Path(__file__).parent / "styles" / "custom.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Configuração da página (DEVE SER A PRIMEIRA CHAMADA)
st.set_page_config(page_title="Scout Pro", page_icon="⚽", layout="wide")
load_custom_css()

# --- CORREÇÃO DE CAMINHOS (CRÍTICO) ---
try:
    current_path = Path(__file__).resolve()
    app_path = current_path.parent  # Diretório app/
    root_path = app_path.parent      # Raiz do projeto

    # Adicionar AMBOS os caminhos
    if str(root_path) not in sys.path:
        sys.path.insert(0, str(root_path))
    if str(app_path) not in sys.path:
        sys.path.insert(0, str(app_path))
except Exception as e:
    st.error(f"❌ Erro ao configurar caminhos: {e}")
    st.stop()

# AGORA importa os módulos locais
try:
    from utils_fotos import get_foto_jogador, get_foto_jogador_rapido
    from utils_logos import get_logo_clube, get_logo_liga
    from auth import check_password, mostrar_info_usuario
    from dashboard_financeiro import aba_financeira
    from database import ScoutingDatabase
    from visualizacoes_avancadas import (
        criar_grafico_percentil,
        criar_heatmap_performance,
        criar_scatter_plot_comparativo,
        criar_grid_cards_estatisticas,
        criar_barras_gradiente
    )
except ImportError as e:
    st.error(f"❌ Erro Crítico de Importação: {e}")
    st.info(f"📂 Caminho tentado: {root_path}")
    st.stop()

"""
Dashboard Interativo de Scouting
Sistema moderno de visualização e análise de jogadores
"""

# === SISTEMA DE AUTENTICAÇÃO (ANTES DE QUALQUER CONTEÚDO) ===
if not check_password():
    st.stop()

# Se passou do login, mostra info do usuário
mostrar_info_usuario()

# CSS Profissional - Scout Pro (Tema Claro Natural)
st.markdown(
    """
    <style>
    /* === TEMA CLARO NATURAL === */

    /* CSS de Limpeza Global - Remove espaços vazios do Streamlit */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
    }

    div[data-testid="stVerticalBlock"] > div:empty {
        display: none;
    }

    .element-container {
        margin-bottom: 0.5rem !important;
    }

    .main {
        padding: 0rem 1rem;
    }

    /* Header com gradiente roxo/azul */
    .header-container {
        background: linear-gradient(135deg, #0a0a0a 0%, #000000 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
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
    div[data-testid="stMetric"] {
        background: rgba(102, 126, 234, 0.05);
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.15);
        transition: all 0.2s ease;
    }

    /* Tabs customizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        padding: 0.75rem;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 55px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 1.5rem;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }

    /* Botões com gradiente */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    /* Imagens dos jogadores */
    img {
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Tabelas limpas */
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-radius: 10px;
        overflow: hidden;
        margin: 1rem 0;
        border: 1px solid #1a1a1a;
    }

    th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 14px 12px;
        text-align: left;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    td {
        padding: 12px;
        border-bottom: 1px solid #e2e8f0;
    }

    tr:nth-child(even) {
        background-color: #f8f9fa;
    }

    tr:hover {
        background-color: rgba(102, 126, 234, 0.05);
        transition: background-color 0.2s;
    }

    /* Links na tabela */
    table a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.2s;
        display: inline-block;
    }

    table a:hover {
        background: #667eea;
        color: white;
        text-decoration: none;
        transform: scale(1.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_resource(ttl=None)
def get_database():
    """Inicializa conexão com banco de dados - Cache persistente"""
    return ScoutingDatabase()


def exibir_foto_jogador(id_jogador, transfermarkt_id=None, nome="Jogador", width=150):
    """
    Exibe foto do jogador no Streamlit (uso simplificado)
    
    Exemplo de uso:
        exibir_foto_jogador(
            id_jogador=123,
            transfermarkt_id="68290",
            nome="Neymar",
            width=150
        )
    """
    url_foto = get_foto_jogador(id_jogador, transfermarkt_id, nome)
    st.image(url_foto, width=width)


def get_foto_jogador_rapido(transfermarkt_id):
    """
    Versão ultra-rápida: apenas URL padrão, sem scraping
    Use quando performance é crítica (lista com muitos jogadores)
    """
    import re
    
    if not transfermarkt_id:
        return "https://via.placeholder.com/150/667eea/ffffff?text=Sem+Foto"
    
    # Extrair ID numérico diretamente
    tm_str = str(transfermarkt_id)
    match = re.search(r'(\d+)', tm_str)
    
    if match:
        tm_id = match.group(1)
        return f"https://img.a.transfermarkt.technology/portrait/medium/{tm_id}.jpg"
    
    return "https://via.placeholder.com/150/667eea/ffffff?text=Sem+Foto"


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

    # Listas para plotagem
    x_list = []
    y_list = []
    names = []
    colors = []
    
    # Contador para espalhar jogadores da mesma posição
    posicao_counter = {}

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
            
            # Mapeamento melhorado de posições
            # Goleiros
            if "goleiro" in pos_str or "gk" in pos_str:
                base_coord = (10, 40)
            
            # Zagueiros
            elif "zagueiro" in pos_str or "zag" in pos_str or "defensor" in pos_str or "cb" in pos_str:
                count = posicao_counter.get("zagueiro", 0)
                if count % 2 == 0:
                    base_coord = (30, 25)
                else:
                    base_coord = (30, 55)
                posicao_counter["zagueiro"] = count + 1
            
            # Laterais
            elif "lateral esquerdo" in pos_str or "le" in pos_str or "lb" in pos_str:
                base_coord = (35, 10)
            elif "lateral direito" in pos_str or "ld" in pos_str or "rb" in pos_str:
                base_coord = (35, 70)
            elif "lateral" in pos_str:
                count = posicao_counter.get("lateral", 0)
                if count % 2 == 0:
                    base_coord = (35, 10)
                else:
                    base_coord = (35, 70)
                posicao_counter["lateral"] = count + 1
            
            # Volantes
            elif "volante" in pos_str or "cdm" in pos_str or "dm" in pos_str:
                count = posicao_counter.get("volante", 0)
                if count % 2 == 0:
                    base_coord = (50, 30)
                else:
                    base_coord = (50, 50)
                posicao_counter["volante"] = count + 1
            
            # Meias
            elif "meia" in pos_str or "cam" in pos_str or "cm" in pos_str or "am" in pos_str:
                count = posicao_counter.get("meia", 0)
                # Distribuir em 3 posições
                if count % 3 == 0:
                    base_coord = (70, 20)
                elif count % 3 == 1:
                    base_coord = (70, 40)
                else:
                    base_coord = (70, 60)
                posicao_counter["meia"] = count + 1
            
            # Pontas e Extremos
            elif "ponta esquerda" in pos_str or "pe" in pos_str or "lw" in pos_str or "extremo esquerdo" in pos_str:
                base_coord = (100, 15)
            elif "ponta direita" in pos_str or "pd" in pos_str or "rw" in pos_str or "extremo direito" in pos_str:
                base_coord = (100, 65)
            elif "ponta" in pos_str or "extremo" in pos_str or "ala" in pos_str or "wing" in pos_str:
                count = posicao_counter.get("ponta", 0)
                if count % 2 == 0:
                    base_coord = (100, 15)  # Esquerda
                else:
                    base_coord = (100, 65)  # Direita
                posicao_counter["ponta"] = count + 1
            
            # Atacantes / Centroavantes
            elif "atacante" in pos_str or "centroavante" in pos_str or "st" in pos_str or "cf" in pos_str or "fw" in pos_str:
                count = posicao_counter.get("atacante", 0)
                # Distribuir em 3 posições (ponta esq, centro, ponta dir)
                if count % 3 == 0:
                    base_coord = (105, 20)  # Esquerda
                elif count % 3 == 1:
                    base_coord = (105, 40)  # Centro
                else:
                    base_coord = (105, 60)  # Direita
                posicao_counter["atacante"] = count + 1
            
            # Posição desconhecida
            else:
                base_coord = (60, 40)  # Centro do campo

            # Jitter maior para espalhar na visualização geral
            x_jitter = random.uniform(-4, 4)
            y_jitter = random.uniform(-4, 4)

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
    """
    Exibe perfil detalhado do jogador com design minimalista usando streamlit-shadcn-ui
    """
    conn = db.engine.connect()
    try:
        id_busca = int(id_jogador)
    except Exception:
        id_busca = id_jogador
    
    query = text("""
        SELECT j.*, v.clube, v.liga_clube, v.posicao, v.data_fim_contrato, v.status_contrato
        FROM jogadores j
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        WHERE j.id_jogador = :id
    """)
    
    result = conn.execute(query, {"id": id_busca})
    jogador = pd.DataFrame(result.fetchall(), columns=result.keys())
    
    if len(jogador) == 0:
        st.error(f"Jogador não encontrado! ID buscado: {id_busca}")
        if st.button("Voltar para Lista"):
            st.session_state.pagina = "dashboard"
            st.rerun()
        return
    
    jogador = jogador.iloc[0]
    
    # Determinar status do contrato
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
    
    # Buscar dados do jogador
    tm_id = jogador.get("transfermarkt_id", None)
    foto_url = get_foto_jogador(id_busca, transfermarkt_id=tm_id, debug=debug)
    logo_clube = get_logo_clube(jogador.get("clube"))
    logo_liga = get_logo_liga(jogador.get("liga_clube"))
    
    nome = jogador.get("nome", "Jogador")
    posicao = jogador.get("posicao", "N/A") if pd.notna(jogador.get("posicao")) else "N/A"
    clube = jogador.get("clube", "Livre") if pd.notna(jogador.get("clube")) else "Livre"
    liga = jogador.get("liga_clube", "N/A") if pd.notna(jogador.get("liga_clube")) else "N/A"
    idade = f"{jogador['idade_atual']} anos" if pd.notna(jogador.get("idade_atual")) else "N/A"
    altura = f"{jogador['altura']} cm" if pd.notna(jogador.get("altura")) else "N/A"
    pe_dom = jogador.get("pe_dominante", "N/A") if pd.notna(jogador.get("pe_dominante")) else "N/A"
    nacionalidade = jogador.get("nacionalidade", "N/A") if pd.notna(jogador.get("nacionalidade")) else "N/A"
    fim_contrato = jogador.get("data_fim_contrato", "N/A") if pd.notna(jogador.get("data_fim_contrato")) else "N/A"
    
    # ===== HEADER COM FOTO E INFO BÁSICA =====
    col_foto, col_info = st.columns([1, 3])
    
    with col_foto:
        if foto_url:
            st.image(foto_url, width=180)
        else:
            inicial = nome[0].upper() if nome and len(nome) > 0 else "?"
            st.markdown(
                f"""
                <div style="width:180px;height:180px;border-radius:90px;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display:flex;align-items:center;justify-content:center;font-size:72px;color:white;font-weight:700;">
                    {inicial}
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with col_info:
        st.markdown(f"# {nome}")
        st.markdown(f"**{posicao}** • {clube} • {liga}")
        
        # Badge de status do contrato
        if status == "livre":
            ui.badges(badge_list=[("Livre", "default")], key=f"badge_status_{id_busca}")
        elif status == "vencido":
            ui.badges(badge_list=[("Vencido", "destructive")], key=f"badge_status_{id_busca}")
        elif status == "ultimos_6_meses":
            ui.badges(badge_list=[(f"Vence em {dias_restantes} dias", "destructive")], key=f"badge_status_{id_busca}")
        elif status == "ultimo_ano":
            ui.badges(badge_list=[(f"Vence em {dias_restantes} dias", "secondary")], key=f"badge_status_{id_busca}")
        else:
            ui.badges(badge_list=[("Ativo", "default")], key=f"badge_status_{id_busca}")
        
        st.markdown(f"**Idade:** {idade} • **Altura:** {altura} • **Pé:** {pe_dom}")
        st.markdown(f"**Nacionalidade:** {nacionalidade}")
        if fim_contrato != "N/A":
            st.markdown(f"**Contrato até:** {fim_contrato}")
    
    st.markdown("---")
    
    # ===== MÉTRICAS DE AVALIAÇÃO (usando ui.metric_card) =====
    avaliacao = db.get_ultima_avaliacao(id_busca)
    
    if not avaliacao.empty:
        st.markdown("## Avaliação Técnica")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ui.metric_card(
                title="Tático",
                content=f"{avaliacao['nota_tatico'].iloc[0]:.1f}",
                description="Visão de jogo e posicionamento",
                key=f"metric_tatico_{id_busca}"
            )
        
        with col2:
            ui.metric_card(
                title="Técnico",
                content=f"{avaliacao['nota_tecnico'].iloc[0]:.1f}",
                description="Domínio e fundamentos",
                key=f"metric_tecnico_{id_busca}"
            )
        
        with col3:
            ui.metric_card(
                title="Físico",
                content=f"{avaliacao['nota_fisico'].iloc[0]:.1f}",
                description="Condicionamento físico",
                key=f"metric_fisico_{id_busca}"
            )
        
        with col4:
            ui.metric_card(
                title="Mental",
                content=f"{avaliacao['nota_mental'].iloc[0]:.1f}",
                description="Concentração e liderança",
                key=f"metric_mental_{id_busca}"
            )
        
        # Potencial
        st.markdown("---")
        col_pot, col_media = st.columns(2)
        
        with col_pot:
            ui.metric_card(
                title="Potencial",
                content=f"{avaliacao['nota_potencial'].iloc[0]:.1f}",
                description="Projeção de desenvolvimento",
                key=f"metric_potencial_{id_busca}"
            )
        
        with col_media:
            media_geral = (
                avaliacao['nota_tatico'].iloc[0] + 
                avaliacao['nota_tecnico'].iloc[0] + 
                avaliacao['nota_fisico'].iloc[0] + 
                avaliacao['nota_mental'].iloc[0]
            ) / 4
            ui.metric_card(
                title="Média Geral",
                content=f"{media_geral:.2f}",
                description="Avaliação consolidada",
                key=f"metric_media_{id_busca}"
            )
    
    st.markdown("---")
    
    # ===== TABS PARA INFORMAÇÕES DETALHADAS =====
    tab_labels = ["📝 Observações", "📊 Estatísticas", "🏷️ Tags", "⭐ Histórico"]
    selected_tab = ui.tabs(options=tab_labels, default_value=tab_labels[0], key=f"tabs_perfil_{id_busca}")
    
    if selected_tab == tab_labels[0]:  # Observações
        st.markdown("### Observações do Scout")
        if not avaliacao.empty and pd.notna(avaliacao.get("observacoes", pd.Series([None])).iloc[0]):
            st.info(avaliacao["observacoes"].iloc[0])
        else:
            st.caption("Nenhuma observação registrada.")
    
    elif selected_tab == tab_labels[1]:  # Estatísticas
        st.markdown("### Estatísticas da Temporada")
        st.caption("Em desenvolvimento - integração com StatsBomb")
    
    elif selected_tab == tab_labels[2]:  # Tags
        st.markdown("### Tags do Jogador")
        tags = db.get_tags_jogador(id_busca)
        if len(tags) > 0:
            badge_list = [(tag["nome"], "outline") for _, tag in tags.iterrows()]
            ui.badges(badge_list=badge_list, key=f"badges_tags_{id_busca}")
        else:
            st.caption("Nenhuma tag aplicada.")
    
    elif selected_tab == tab_labels[3]:  # Histórico
        st.markdown("### Histórico de Avaliações")
        historico = db.get_historico_avaliacoes(id_busca)
        if not historico.empty:
            st.dataframe(historico, use_container_width=True)
        else:
            st.caption("Nenhum histórico disponível.")
    
    # ===== BOTÃO DE VOLTAR =====
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if ui.button(text="← Voltar para Lista", key=f"btn_voltar_{id_busca}", variant="outline"):
            st.session_state.pagina = "dashboard"
            st.session_state.jogador_selecionado = None
            st.query_params.clear()
            st.rerun()


def exibir_lista_com_fotos(df, db, debug=False, sufixo_key=""):
    """
    Exibe lista de jogadores em cards modernos usando streamlit-shadcn-ui
    """
    if len(df) == 0:
        st.warning("Nenhum jogador para exibir.")
        return
    
    # Layout em grid de 3 colunas
    for i in range(0, len(df), 3):
        cols = st.columns(3, gap="medium")
        
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(df):
                break
            
            jogador = df.iloc[idx]
            with col:
                # Container com borda para cada card
                with st.container(border=True):
                    # Foto do jogador
                    foto_url = get_foto_jogador(
                        jogador["id_jogador"],
                        transfermarkt_id=jogador.get("transfermarkt_id"),
                        debug=debug
                    )
                    
                    if foto_url:
                        st.image(foto_url, use_container_width=True)
                    else:
                        inicial = jogador["nome"][0].upper() if jogador["nome"] and len(jogador["nome"]) > 0 else "?"
                        st.markdown(
                            f"""
                            <div style="width:100%;padding-top:100%;position:relative;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            border-radius:8px;">
                                <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                                font-size:48px;color:white;font-weight:700;">
                                    {inicial}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    # Nome e posição
                    st.markdown(f"### {jogador['nome']}")
                    st.caption(f"{jogador.get('posicao', 'N/A')} • {jogador.get('clube', 'Livre')}")
                    
                    # Badges de info rápida
                    badges = []
                    if pd.notna(jogador.get("idade_atual")):
                        badges.append((f"{int(jogador['idade_atual'])} anos", "secondary"))
                    if "media_geral" in jogador and pd.notna(jogador["media_geral"]):
                        badges.append((f"⭐ {jogador['media_geral']:.1f}", "default"))
                    
                    if badges:
                        ui.badges(badge_list=badges, key=f"badges_{sufixo_key}_{jogador['id_jogador']}")
                    
                    st.markdown("---")
                    
                    # Botões de ação
                    col_btn1, col_btn2 = st.columns(2, gap="small")
                    
                    with col_btn1:
                        if ui.button(
                            text="Ver Perfil",
                            key=f"btn_perfil_{sufixo_key}_{jogador['id_jogador']}",
                            variant="default"
                        ):
                            st.session_state.pagina = "perfil"
                            st.session_state.jogador_selecionado = jogador["id_jogador"]
                            st.query_params["jogador"] = jogador["id_jogador"]
                            st.rerun()
                    
                    with col_btn2:
                        # Verificar se está na wishlist
                        wishlist_ids = db.get_ids_wishlist()
                        is_in_wishlist = jogador["id_jogador"] in wishlist_ids
                        
                        if is_in_wishlist:
                            btn_text = "★ Wishlist"
                            btn_variant = "outline"
                        else:
                            btn_text = "☆ Adicionar"
                            btn_variant = "secondary"
                        
                        if ui.button(
                            text=btn_text,
                            key=f"btn_wishlist_{sufixo_key}_{jogador['id_jogador']}",
                            variant=btn_variant
                        ):
                            if is_in_wishlist:
                                db.remover_da_wishlist(jogador["id_jogador"])
                                st.toast("Removido da Wishlist", icon="🗑️")
                            else:
                                db.adicionar_na_wishlist(jogador["id_jogador"])
                                st.toast("Adicionado à Wishlist", icon="⭐")
                            st.rerun()



def tab_ranking(db, df_jogadores):
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
            df_avaliacoes["nacionalidade"].dropna().unique().tolist()
        )
        nac_rank = st.selectbox(
            "🌍 Nacionalidade", nacionalidades_rank, key="rank_nac"
        )
    
    with col4:
        clubes_rank = ["Todos"] + sorted(
            df_avaliacoes["clube"].dropna().unique().tolist()
        )
        clube_rank = st.selectbox("⚽ Clube", clubes_rank, key="rank_clube")
    
    with col5:
        ligas_rank = ["Todas"] + sorted(
            df_avaliacoes["liga_clube"].dropna().unique().tolist()
        )
        liga_rank = st.selectbox("🏆 Liga", ligas_rank, key="rank_liga")
    
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
    
    # --- MODOS DE VISUALIZAÇÃO ---
    view_option = st.radio(
        "Visualização",
        ["🏅 Top 20", "📊 Por Posição", "📋 Tabela Completa"],
        horizontal=True,
    )
    
    st.markdown("---")
    
    # ========== TOP 20 ==========
    if view_option == "🏅 Top 20":
        st.markdown(f"### 🏆 Top 20 Jogadores - Ordenado por {ordenar_rank}")
        
        df_top20 = df_rank.head(20).copy()
        
        if len(df_top20) == 0:
            st.warning("Nenhum jogador encontrado com os filtros aplicados.")
            return
        
        # Exibir cada jogador do Top 20
        for idx, jogador in enumerate(df_top20.itertuples()):
            rank_pos = jogador.rank
            
            # Determinar classe CSS e emoji
            if rank_pos == 1:
                emoji = "🥇"
                css_class = "rank-1"
            elif rank_pos == 2:
                emoji = "🥈"
                css_class = "rank-2"
            elif rank_pos == 3:
                emoji = "🥉"
                css_class = "rank-3"
            else:
                emoji = f"#{rank_pos}"
                css_class = "rank-container"
            
            # Container com classe CSS apropriada
            st.markdown(
                f'<div class="rank-container {css_class}">',
                unsafe_allow_html=True,
            )
            
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(
                [0.5, 2, 1.5, 1, 1, 1, 1, 1]
            )
            
            with col1:
                st.markdown(f'<div class="rank-medal">{emoji}</div>', unsafe_allow_html=True)
            
            with col2:
                # Nome clicável
                perfil_url = f"?jogador={jogador.id_jogador}"
                st.markdown(
                    f'<a href="{perfil_url}" target="_blank" style="font-size: 1.1em;">{jogador.nome}</a>',
                    unsafe_allow_html=True,
                )
                st.caption(f"{jogador.posicao} | {jogador.clube}")
            
            with col3:
                st.metric("⭐ Potencial", f"{jogador.nota_potencial:.1f}")
            
            with col4:
                st.metric("Média", f"{jogador.media_geral:.1f}")
            
            with col5:
                st.metric("Tático", f"{jogador.nota_tatico:.1f}")
            
            with col6:
                st.metric("Técnico", f"{jogador.nota_tecnico:.1f}")
            
            with col7:
                st.metric("Físico", f"{jogador.nota_fisico:.1f}")
            
            with col8:
                st.metric("Mental", f"{jogador.nota_mental:.1f}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")  # Espaçamento
    
    # ========== POR POSIÇÃO ==========
    elif view_option == "📊 Por Posição":
        st.markdown("### 📊 Ranking por Posição")
        
        # Agrupar por posição
        posicoes_disponiveis = df_rank["posicao"].dropna().unique()
        
        if len(posicoes_disponiveis) == 0:
            st.warning("Nenhuma posição encontrada com os filtros aplicados.")
            return
        
        for posicao in sorted(posicoes_disponiveis):
            df_pos = df_rank[df_rank["posicao"] == posicao].head(10)
            
            with st.expander(
                f"⚽ {posicao} ({len(df_pos)} jogadores)", expanded=True
            ):
                # Criar tabela HTML clicável
                html_rows = []
                
                for idx, row in df_pos.iterrows():
                    rank_num = idx + 1
                    
                    # Destaque para top 3
                    if rank_num <= 3:
                        bg_color = "#fff9e6" if rank_num == 1 else ("#f5f5f5" if rank_num == 2 else "#fff4e6")
                    else:
                        bg_color = "white"
                    
                    nome_link = f'<a href="?jogador={row["id_jogador"]}" target="_blank">{row["nome"]}</a>'
                    
                    html_rows.append(
                        f"""
                        <tr style="background-color: {bg_color};">
                            <td><strong>{rank_num}</strong></td>
                            <td>{nome_link}</td>
                            <td>{row['clube']}</td>
                            <td>{row['nacionalidade']}</td>
                            <td>{int(row['idade_atual']) if pd.notna(row['idade_atual']) else 'N/A'}</td>
                            <td><strong>{row['nota_potencial']:.1f}</strong></td>
                            <td>{row['media_geral']:.1f}</td>
                            <td>{row['nota_tatico']:.1f}</td>
                            <td>{row['nota_tecnico']:.1f}</td>
                            <td>{row['nota_fisico']:.1f}</td>
                            <td>{row['nota_mental']:.1f}</td>
                        </tr>
                        """
                    )
                
                table_html = f"""
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Nome</th>
                            <th>Clube</th>
                            <th>Nacionalidade</th>
                            <th>Idade</th>
                            <th>⭐ Potencial</th>
                            <th>Média</th>
                            <th>Tático</th>
                            <th>Técnico</th>
                            <th>Físico</th>
                            <th>Mental</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(html_rows)}
                    </tbody>
                </table>
                """
                
                st.html(table_html)
    
    # ========== TABELA COMPLETA ==========
    else:  # Tabela Completa
        st.markdown(f"### 📋 Tabela Completa - {len(df_rank)} jogadores")
        
        # Criar tabela HTML completa e scrollável
        html_rows = []
        
        for idx, row in df_rank.iterrows():
            rank_num = row['rank']
            
            # Cores por ranking
            if rank_num <= 3:
                bg_color = "#fff9e6" if rank_num == 1 else ("#f5f5f5" if rank_num == 2 else "#fff4e6")
            elif rank_num <= 10:
                bg_color = "#fff3cd"
            else:
                bg_color = "white"
            
            nome_link = f'<a href="?jogador={row["id_jogador"]}" target="_blank">{row["nome"]}</a>'
            data_fmt = pd.to_datetime(row['data_avaliacao']).strftime("%d/%m/%Y")
            
            html_rows.append(
                f"""
                <tr style="background-color: {bg_color};">
                    <td><strong>{rank_num}</strong></td>
                    <td>{nome_link}</td>
                    <td>{row['posicao']}</td>
                    <td>{row['clube']}</td>
                    <td>{row['nacionalidade']}</td>
                    <td>{int(row['idade_atual']) if pd.notna(row['idade_atual']) else 'N/A'}</td>
                    <td><strong>{row['nota_potencial']:.1f}</strong></td>
                    <td>{row['media_geral']:.1f}</td>
                    <td>{row['nota_tatico']:.1f}</td>
                    <td>{row['nota_tecnico']:.1f}</td>
                    <td>{row['nota_fisico']:.1f}</td>
                    <td>{row['nota_mental']:.1f}</td>
                    <td>{data_fmt}</td>
                </tr>
                """
            )
        
        table_html = f"""
        <div style="height: 600px; overflow-y: scroll; border-radius: 10px;">
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Nome</th>
                        <th>Posição</th>
                        <th>Clube</th>
                        <th>Nacionalidade</th>
                        <th>Idade</th>
                        <th>⭐ Potencial</th>
                        <th>Média</th>
                        <th>Tático</th>
                        <th>Técnico</th>
                        <th>Físico</th>
                        <th>Mental</th>
                        <th>Última Avaliação</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(html_rows)}
                </tbody>
            </table>
        </div>
        """
        
        st.markdown(
            "💡 **Dica:** Clique no nome do jogador para abrir o perfil em nova aba"
        )
        st.html(table_html)
        
        # Botão de export
        st.markdown("---")
        csv = df_rank.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Exportar Ranking (CSV)",
            data=csv,
            file_name=f'ranking_jogadores_{datetime.now().strftime("%Y%m%d")}.csv',
            mime="text/csv",
            width='stretch',
        )
    
    # --- ESTATÍSTICAS DO RANKING ---
    st.markdown("---")
    st.markdown("### 📊 Estatísticas do Ranking")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Jogadores Avaliados",
            len(df_rank),
            help="Total de jogadores com avaliações nos filtros aplicados",
        )
    
    with col2:
        st.metric(
            "Potencial Médio",
            f"{df_rank['nota_potencial'].mean():.2f}",
            help="Média de potencial de todos os jogadores filtrados",
        )
    
    with col3:
        st.metric(
            "Nota Geral Média",
            f"{df_rank['media_geral'].mean():.2f}",
            help="Média geral de todas as dimensões",
        )
    
    with col4:
        if len(df_rank) > 0:
            melhor_jogador = df_rank.iloc[0]
            st.metric(
                "Melhor Jogador",
                melhor_jogador["nome"],
                help=f"Nota: {melhor_jogador[ordem_map[ordenar_rank]]:.1f}",
            )



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
            st.plotly_chart(fig_comparacao, width='stretch')
        
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
    """
    Monta Shadow Team com layout visual simulando posições em campo
    """
    st.markdown("## ⚽ Shadow Team")
    st.caption("Monte seu time ideal selecionando jogadores por posição")
    
    # Preparar dados
    jogadores_por_posicao = {}
    for posicao in ["Goleiro", "Zagueiro", "Lateral", "Volante", "Meia", "Atacante"]:
        jogadores = df_jogadores[df_jogadores["posicao"].str.contains(posicao, case=False, na=False)]
        jogadores_por_posicao[posicao] = ["Nenhum"] + jogadores["nome"].tolist()
    
    # Inicializar session_state
    if "shadow_team" not in st.session_state:
        st.session_state.shadow_team = {
            "goleiro": "Nenhum",
            "zagueiro_esq": "Nenhum",
            "zagueiro_dir": "Nenhum",
            "lateral_esq": "Nenhum",
            "lateral_dir": "Nenhum",
            "volante_1": "Nenhum",
            "volante_2": "Nenhum",
            "meia_1": "Nenhum",
            "meia_2": "Nenhum",
            "atacante_1": "Nenhum",
            "atacante_2": "Nenhum",
        }
    
    st.markdown("---")
    
    # ===== LAYOUT DE CAMPO (4-2-2-2) =====
    st.markdown("### 🏟️ Formação 4-2-2-2")
    
    # ATACANTES
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_atk1, col_atk2 = st.columns(2, gap="small")
        with col_atk1:
            st.markdown("**Atacante Esquerdo**")
            st.session_state.shadow_team["atacante_1"] = ui.select(
                options=jogadores_por_posicao.get("Atacante", ["Nenhum"]),
                default_value=st.session_state.shadow_team["atacante_1"],
                key="select_atk1"
            )
        with col_atk2:
            st.markdown("**Atacante Direito**")
            st.session_state.shadow_team["atacante_2"] = ui.select(
                options=jogadores_por_posicao.get("Atacante", ["Nenhum"]),
                default_value=st.session_state.shadow_team["atacante_2"],
                key="select_atk2"
            )
    
    st.markdown("")
    
    # MEIAS
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_mid1, col_mid2 = st.columns(2, gap="small")
        with col_mid1:
            st.markdown("**Meia Esquerdo**")
            st.session_state.shadow_team["meia_1"] = ui.select(
                options=jogadores_por_posicao.get("Meia", ["Nenhum"]),
                default_value=st.session_state.shadow_team["meia_1"],
                key="select_mid1"
            )
        with col_mid2:
            st.markdown("**Meia Direito**")
            st.session_state.shadow_team["meia_2"] = ui.select(
                options=jogadores_por_posicao.get("Meia", ["Nenhum"]),
                default_value=st.session_state.shadow_team["meia_2"],
                key="select_mid2"
            )
    
    st.markdown("")
    
    # VOLANTES
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_vol1, col_vol2 = st.columns(2, gap="small")
        with col_vol1:
            st.markdown("**Volante Esquerdo**")
            st.session_state.shadow_team["volante_1"] = ui.select(
                options=jogadores_por_posicao.get("Volante", ["Nenhum"]),
                default_value=st.session_state.shadow_team["volante_1"],
                key="select_vol1"
            )
        with col_vol2:
            st.markdown("**Volante Direito**")
            st.session_state.shadow_team["volante_2"] = ui.select(
                options=jogadores_por_posicao.get("Volante", ["Nenhum"]),
                default_value=st.session_state.shadow_team["volante_2"],
                key="select_vol2"
            )
    
    st.markdown("")
    
    # DEFESA
    col_def = st.columns([0.5, 1, 1, 1, 1, 0.5])
    with col_def[1]:
        st.markdown("**Lateral Esq.**")
        st.session_state.shadow_team["lateral_esq"] = ui.select(
            options=jogadores_por_posicao.get("Lateral", ["Nenhum"]),
            default_value=st.session_state.shadow_team["lateral_esq"],
            key="select_lat_esq"
        )
    with col_def[2]:
        st.markdown("**Zagueiro Esq.**")
        st.session_state.shadow_team["zagueiro_esq"] = ui.select(
            options=jogadores_por_posicao.get("Zagueiro", ["Nenhum"]),
            default_value=st.session_state.shadow_team["zagueiro_esq"],
            key="select_zag_esq"
        )
    with col_def[3]:
        st.markdown("**Zagueiro Dir.**")
        st.session_state.shadow_team["zagueiro_dir"] = ui.select(
            options=jogadores_por_posicao.get("Zagueiro", ["Nenhum"]),
            default_value=st.session_state.shadow_team["zagueiro_dir"],
            key="select_zag_dir"
        )
    with col_def[4]:
        st.markdown("**Lateral Dir.**")
        st.session_state.shadow_team["lateral_dir"] = ui.select(
            options=jogadores_por_posicao.get("Lateral", ["Nenhum"]),
            default_value=st.session_state.shadow_team["lateral_dir"],
            key="select_lat_dir"
        )
    
    st.markdown("")
    
    # GOLEIRO
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        st.markdown("**Goleiro**")
        st.session_state.shadow_team["goleiro"] = ui.select(
            options=jogadores_por_posicao.get("Goleiro", ["Nenhum"]),
            default_value=st.session_state.shadow_team["goleiro"],
            key="select_gol"
        )
    
    st.markdown("---")
    
    # ===== RESUMO DO TIME =====
    jogadores_selecionados = [j for j in st.session_state.shadow_team.values() if j != "Nenhum"]
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        ui.metric_card(
            title="Jogadores Selecionados",
            content=str(len(jogadores_selecionados)),
            description="de 11 posições",
            key="metric_shadow_count"
        )
    
    with col_info2:
        if len(jogadores_selecionados) > 0:
            # Calcular idade média
            idades = []
            for nome in jogadores_selecionados:
                jogador = df_jogadores[df_jogadores["nome"] == nome]
                if not jogador.empty and pd.notna(jogador.iloc[0].get("idade_atual")):
                    idades.append(jogador.iloc[0]["idade_atual"])
            
            if idades:
                idade_media = sum(idades) / len(idades)
                ui.metric_card(
                    title="Idade Média",
                    content=f"{idade_media:.1f}",
                    description="anos",
                    key="metric_shadow_age"
                )
    
    with col_info3:
        if len(jogadores_selecionados) > 0:
            # Calcular média geral do time
            medias = []
            for nome in jogadores_selecionados:
                jogador = df_jogadores[df_jogadores["nome"] == nome]
                if not jogador.empty and "media_geral" in jogador.columns:
                    if pd.notna(jogador.iloc[0].get("media_geral")):
                        medias.append(jogador.iloc[0]["media_geral"])
            
            if medias:
                media_time = sum(medias) / len(medias)
                ui.metric_card(
                    title="Média do Time",
                    content=f"{media_time:.2f}",
                    description="avaliação geral",
                    key="metric_shadow_rating"
                )
    
    # Botões de ação
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if ui.button(text="💾 Salvar Time", key="btn_salvar_shadow", variant="default"):
            if len(jogadores_selecionados) == 11:
                st.success("Time salvo com sucesso!")
            else:
                st.warning(f"Complete a escalação! Faltam {11 - len(jogadores_selecionados)} jogadores.")
    
    with col2:
        if ui.button(text="📊 Análise Completa", key="btn_analisar_shadow", variant="outline"):
            if len(jogadores_selecionados) >= 6:
                st.info("Análise em desenvolvimento - integração com StatsBomb")
            else:
                st.warning("Adicione pelo menos 6 jogadores para análise.")
    
    with col3:
        if ui.button(text="🗑️ Limpar Seleção", key="btn_limpar_shadow", variant="secondary"):
            for key in st.session_state.shadow_team:
                st.session_state.shadow_team[key] = "Nenhum"
            st.rerun()



def criar_seletor_posicao(posicao, df_jogadores, db):
    """Cria um seletor para uma posição específica"""
    # Determinar filtro de posição
    if "Goleiro" in posicao:
        filtro_pos = ["goleiro", "gk"]
    elif "Zagueiro" in posicao:
        filtro_pos = ["zagueiro", "cb"]
    elif "Lateral" in posicao or "Ala" in posicao:
        filtro_pos = ["lateral", "lb", "rb", "wing", "ala"]
    elif "Volante" in posicao:
        filtro_pos = ["volante", "cdm", "dm"]
    elif "Meia" in posicao:
        filtro_pos = ["meia", "cam", "cm", "am"]
    else:  # Atacante
        filtro_pos = ["atacante", "st", "cf", "fw", "ponta", "extremo"]
    
    # Buscar top jogadores
    top_jogadores = get_top_jogadores_por_posicao(df_jogadores, db, filtro_pos, 20)
    
    if len(top_jogadores) > 0:
        opcoes = ["Nenhum"] + [j["label"] for j in top_jogadores]
        
        # Valor default se já estiver selecionado
        valor_default = "Nenhum"
        if posicao in st.session_state.shadow_team:
            id_atual = st.session_state.shadow_team[posicao]
            for j in top_jogadores:
                if j["id"] == id_atual:
                    valor_default = j["label"]
                    break
        
        default_index = opcoes.index(valor_default) if valor_default in opcoes else 0
        
        selecionado = st.selectbox(
            f"**{posicao}**",
            options=opcoes,
            index=default_index,
            key=f"shadow_{posicao}_{hash(posicao)}"
        )
        
        if selecionado != "Nenhum":
            # Encontrar o ID do jogador selecionado
            for j in top_jogadores:
                if j["label"] == selecionado:
                    st.session_state.shadow_team[posicao] = j["id"]
                    break
        elif posicao in st.session_state.shadow_team:
            del st.session_state.shadow_team[posicao]
    else:
        st.warning(f"Nenhum jogador encontrado para {posicao}")


def preencher_automaticamente(posicoes, df_jogadores, db):
    """Preenche automaticamente com os melhores jogadores"""
    st.session_state.shadow_team = {}
    
    for posicao in posicoes:
        # Determinar filtro de posição
        if "Goleiro" in posicao:
            filtro_pos = ["goleiro", "gk"]
        elif "Zagueiro" in posicao:
            filtro_pos = ["zagueiro", "cb"]
        elif "Lateral" in posicao or "Ala" in posicao:
            filtro_pos = ["lateral", "lb", "rb", "wing", "ala"]
        elif "Volante" in posicao:
            filtro_pos = ["volante", "cdm", "dm"]
        elif "Meia" in posicao:
            filtro_pos = ["meia", "cam", "cm", "am"]
        else:  # Atacante
            filtro_pos = ["atacante", "st", "cf", "fw", "ponta", "extremo"]
        
        # Buscar melhor jogador
        top_jogadores = get_top_jogadores_por_posicao(df_jogadores, db, filtro_pos, 1)
        
        if len(top_jogadores) > 0:
            st.session_state.shadow_team[posicao] = top_jogadores[0]["id"]




# ========================================
# COMPONENTES VISUAIS - NOVAS FUNCIONALIDADES
# ========================================



from datetime import datetime

# ============================================
# 1. WIDGET DE TAGS
# ============================================

def render_tags_widget(db, id_jogador):
    """Renderiza widget de tags para um jogador"""
    st.markdown("#### 🏷️ Tags")
    
    # Buscar tags do jogador
    tags_jogador = db.get_jogador_tags(id_jogador)
    
    # Mostrar tags atuais
    if len(tags_jogador) > 0:
        cols = st.columns(len(tags_jogador))
        for idx, (_, tag) in enumerate(tags_jogador.iterrows()):
            with cols[idx]:
                st.markdown(
                    f'<span style="background-color: {tag["cor"]}; color: white; '
                    f'padding: 5px 10px; border-radius: 15px; font-size: 0.9em; '
                    f'display: inline-block; margin: 2px;">{tag["nome"]}</span>',
                    unsafe_allow_html=True
                )
    else:
        st.caption("Nenhuma tag adicionada")
    
    # Adicionar nova tag
    with st.expander("➕ Adicionar/Remover Tags"):
        todas_tags = db.get_all_tags()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Adicionar Tag:**")
            tags_disponiveis = todas_tags[~todas_tags['id_tag'].isin(tags_jogador['id_tag'])]
            
            if len(tags_disponiveis) > 0:
                tag_selecionada = st.selectbox(
                    "Selecione uma tag",
                    options=tags_disponiveis['id_tag'].tolist(),
                    format_func=lambda x: todas_tags[todas_tags['id_tag'] == x]['nome'].iloc[0],
                    key=f"add_tag_{id_jogador}"
                )
                
                if st.button("Adicionar", key=f"btn_add_tag_{id_jogador}_{tag_selecionada}"):
                    if db.adicionar_tag_jogador(id_jogador, tag_selecionada):
                        st.success("Tag adicionada!")
                        st.rerun()
            else:
                st.info("Todas as tags já foram adicionadas")
        
        with col2:
            st.markdown("**Remover Tag:**")
            if len(tags_jogador) > 0:
                tag_remover = st.selectbox(
                    "Selecione uma tag para remover",
                    options=tags_jogador['id_tag'].tolist(),
                    format_func=lambda x: tags_jogador[tags_jogador['id_tag'] == x]['nome'].iloc[0],
                    key=f"rem_tag_{id_jogador}"
                )
                
                if st.button("Remover", key=f"btn_rem_tag_{id_jogador}_{tag_remover}", type="secondary"):
                    if db.remover_tag_jogador(id_jogador, tag_remover):
                        st.success("Tag removida!")
                        st.rerun()
            else:
                st.info("Nenhuma tag para remover")


# ============================================
# 2. WIDGET DE WISHLIST
# ============================================

def render_wishlist_button(db, id_jogador):
    """Renderiza botão de adicionar/remover da wishlist"""
    esta_na_wishlist = db.esta_na_wishlist(id_jogador)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if esta_na_wishlist:
            if st.button("⭐ Remover da Wishlist", key=f"wishlist_{id_jogador}", 
                        width='stretch', type="secondary"):
                if db.remover_wishlist(id_jogador):
                    st.success("Removido da wishlist!")
                    st.rerun()
        else:
            if st.button("⭐ Adicionar à Wishlist", key=f"wishlist_{id_jogador}", 
                        width='stretch'):
                # Mostrar modal para escolher prioridade
                st.session_state[f'show_wishlist_modal_{id_jogador}'] = True
    
    # Modal para configurar prioridade
    if st.session_state.get(f'show_wishlist_modal_{id_jogador}', False):
        with st.form(key=f"form_wishlist_{id_jogador}"):
            st.markdown("### Adicionar à Wishlist")
            prioridade = st.selectbox(
                "Prioridade",
                options=['alta', 'media', 'baixa'],
                format_func=lambda x: {'alta': '🔴 Alta', 'media': '🟡 Média', 'baixa': '🟢 Baixa'}[x]
            )
            observacao = st.text_area("Observação (opcional)")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.form_submit_button("Adicionar", width='stretch'):
                    if db.adicionar_wishlist(id_jogador, prioridade, observacao):
                        st.success("Adicionado à wishlist!")
                        st.session_state[f'show_wishlist_modal_{id_jogador}'] = False
                        st.rerun()
            with col_b:
                if st.form_submit_button("Cancelar", width='stretch'):
                    st.session_state[f'show_wishlist_modal_{id_jogador}'] = False
                    st.rerun()


# ============================================
# 3. GRÁFICO DE PIZZA (DISTRIBUIÇÃO DE NOTAS)
# ============================================

def criar_grafico_pizza_avaliacoes(notas_dict):
    """Cria gráfico de pizza mostrando distribuição percentual das notas"""
    categorias = list(notas_dict.keys())
    valores = list(notas_dict.values())
    
    # Calcular porcentagens
    total = sum(valores)
    porcentagens = [v/total*100 for v in valores]
    
    cores = {
        'Tático': '#3498db',
        'Técnico': '#e74c3c',
        'Físico': '#f39c12',
        'Mental': '#9b59b6'
    }
    
    colors_list = [cores.get(cat, '#95a5a6') for cat in categorias]
    
    fig = go.Figure(data=[go.Pie(
        labels=categorias,
        values=valores,
        hole=0.4,
        marker=dict(colors=colors_list),
        textinfo='label+percent',
        textposition='inside',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>%{label}</b><br>Nota: %{value:.1f}<br>Percentual: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text="Distribuição das Notas",
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=400,
        margin=dict(l=20, r=20, t=60, b=60)
    )
    
    return fig


# ============================================
# 4. COMPARAÇÃO COM BENCHMARK
# ============================================

def render_benchmark_comparison(db, id_jogador, posicao):
    """Renderiza comparação do jogador com benchmark da posição"""
    # Buscar benchmark
    benchmark = db.get_benchmark_posicao(posicao)
    
    if benchmark.empty:
        st.warning(f"Sem dados de benchmark para {posicao}")
        return
    
    # Buscar avaliação do jogador
    avaliacao = db.get_ultima_avaliacao(id_jogador)
    
    if avaliacao.empty:
        st.info("Jogador sem avaliação para comparar")
        return
    
    st.markdown("#### 📊 Comparação com Benchmark")
    st.caption(f"Média de {int(benchmark['total_jogadores'].iloc[0])} {posicao}s avaliados")
    
    # Criar gráfico de barras comparativo
    categorias = ['Potencial', 'Tático', 'Técnico', 'Físico', 'Mental', 'Geral']
    
    valores_jogador = [
        avaliacao['nota_potencial'].iloc[0],
        avaliacao['nota_tatico'].iloc[0],
        avaliacao['nota_tecnico'].iloc[0],
        avaliacao['nota_fisico'].iloc[0],
        avaliacao['nota_mental'].iloc[0],
        (avaliacao['nota_tatico'].iloc[0] + avaliacao['nota_tecnico'].iloc[0] + 
         avaliacao['nota_fisico'].iloc[0] + avaliacao['nota_mental'].iloc[0]) / 4
    ]
    
    valores_benchmark = [
        float(benchmark['media_potencial'].iloc[0]),
        float(benchmark['media_tatico'].iloc[0]),
        float(benchmark['media_tecnico'].iloc[0]),
        float(benchmark['media_fisico'].iloc[0]),
        float(benchmark['media_mental'].iloc[0]),
        float(benchmark['media_geral'].iloc[0])
    ]
    
    # Calcular diferenças
    diferencas = [j - b for j, b in zip(valores_jogador, valores_benchmark)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Jogador',
        x=categorias,
        y=valores_jogador,
        marker_color='#667eea',
        text=[f'{v:.1f}' for v in valores_jogador],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name=f'Média {posicao}',
        x=categorias,
        y=valores_benchmark,
        marker_color='#95a5a6',
        text=[f'{v:.1f}' for v in valores_benchmark],
        textposition='outside'
    ))
    
    fig.update_layout(
        barmode='group',
        height=400,
        yaxis=dict(range=[0, 5.5], title='Nota'),
        xaxis=dict(title=''),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Mostrar diferenças
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    cols = [col1, col2, col3, col4, col5, col6]
    
    for i, (cat, diff) in enumerate(zip(categorias, diferencas)):
        with cols[i]:
            delta_color = "normal" if diff >= 0 else "inverse"
            st.metric(
                cat,
                f"{valores_jogador[i]:.1f}",
                delta=f"{diff:+.1f}",
                delta_color=delta_color
            )


# ============================================
# 5. WIDGET DE NOTAS RÁPIDAS
# ============================================

def render_notas_rapidas(db, id_jogador):
    """Renderiza seção de notas rápidas"""
    st.markdown("#### 📝 Notas Rápidas")
    
    notas = db.get_notas_rapidas(id_jogador)
    
    # Formulário para adicionar nota
    with st.expander("✍️ Adicionar Nota Rápida"):
        with st.form(key=f"form_nota_{id_jogador}"):
            texto = st.text_area(
                "Observação",
                placeholder="Ex: Visto ao vivo no jogo contra o Palmeiras - Boa atuação defensiva",
                height=100
            )
            
            col1, col2 = st.columns([2, 1])
            with col1:
                tipo = st.selectbox(
                    "Tipo",
                    options=['observacao', 'jogo_assistido', 'conversa', 'alerta'],
                    format_func=lambda x: {
                        'observacao': '👁️ Observação',
                        'jogo_assistido': '⚽ Jogo Assistido',
                        'conversa': '💬 Conversa/Contato',
                        'alerta': '⚠️ Alerta'
                    }[x]
                )
            
            with col2:
                autor = st.text_input("Seu nome", value="Scout")
            
            if st.form_submit_button("💾 Salvar Nota", width='stretch'):
                if texto.strip():
                    if db.adicionar_nota_rapida(id_jogador, texto, autor, tipo):
                        st.success("Nota adicionada!")
                        st.rerun()
                else:
                    st.warning("Digite uma observação")
    
    # Mostrar notas existentes
    if len(notas) > 0:
        st.markdown(f"**{len(notas)} nota(s) registrada(s)**")
        
        for _, nota in notas.iterrows():
            tipo_icon = {
                'observacao': '👁️',
                'jogo_assistido': '⚽',
                'conversa': '💬',
                'alerta': '⚠️'
            }.get(nota['tipo'], '📝')
            
            data_fmt = pd.to_datetime(nota['data_nota']).strftime("%d/%m/%Y %H:%M")
            
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"{tipo_icon} **{nota.get('autor', 'N/A')}** • {data_fmt}")
                    st.markdown(f"_{nota['texto']}_")
                with col2:
                    if st.button("🗑️", key=f"del_nota_{nota['id_nota']}"):
                        if db.deletar_nota_rapida(nota['id_nota']):
                            st.rerun()
                st.markdown("---")
    else:
        st.info("Nenhuma nota registrada ainda")


# ============================================
# 6. TAB DE WISHLIST
# ============================================

def tab_wishlist(db):
    """Tab dedicada à Wishlist"""
    st.markdown("### ⭐ Minha Wishlist")
    st.markdown("Jogadores prioritários para monitoramento e contratação")
    
    # Filtro por prioridade
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        filtro_prioridade = st.multiselect(
            "Filtrar por Prioridade",
            options=['alta', 'media', 'baixa'],
            default=['alta', 'media', 'baixa'],
            format_func=lambda x: {'alta': '🔴 Alta', 'media': '🟡 Média', 'baixa': '🟢 Baixa'}[x]
        )
    
    # Buscar wishlist
    wishlist = db.get_wishlist()
    
    if len(wishlist) == 0:
        st.info("📝 Sua wishlist está vazia. Adicione jogadores para monitorar!")
        return
    
    # Filtrar
    if filtro_prioridade:
        wishlist = wishlist[wishlist['prioridade'].isin(filtro_prioridade)]
    
    with col2:
        st.metric("Total na Wishlist", len(wishlist))
    
    with col3:
        ordenar = st.selectbox(
            "Ordenar por",
            options=['prioridade', 'nome', 'data'],
            format_func=lambda x: {'prioridade': 'Prioridade', 'nome': 'Nome', 'data': 'Data Adição'}[x]
        )
    
    # Ordenar
    if ordenar == 'prioridade':
        wishlist['_sort'] = wishlist['prioridade'].map({'alta': 1, 'media': 2, 'baixa': 3})
        wishlist = wishlist.sort_values('_sort')
    elif ordenar == 'nome':
        wishlist = wishlist.sort_values('nome')
    else:
        wishlist = wishlist.sort_values('wishlist_adicionado_em', ascending=False)
    
    st.markdown("---")
    
    # Mostrar jogadores
    for idx, jogador in enumerate(wishlist.iterrows()):
        # Correção: iterrows() retorna (index, Series)
        # Então 'jogador' aqui é na verdade uma tupla (index, row)
        # Vamos corrigir para usar 'row'
        row = jogador[1]  # Pegando a Series
        
        prioridade_color = {'alta': '#dc3545', 'media': '#ffc107', 'baixa': '#28a745'}[row['prioridade']]
        prioridade_label = {'alta': '🔴 ALTA', 'media': '🟡 MÉDIA', 'baixa': '🟢 BAIXA'}[row['prioridade']]
        
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"### {row['nome']}")
                st.caption(f"{row.get('posicao', 'N/A')} • {row.get('clube', 'Livre')}")
            
            with col2:
                st.markdown(f"**Prioridade:** <span style='color: {prioridade_color}; font-weight: bold;'>{prioridade_label}</span>", 
                           unsafe_allow_html=True)
                if pd.notna(row.get('observacao')):
                    with st.expander("💬 Ver observação"):
                        st.info(row['observacao'])
            
            with col3:
                data_add = pd.to_datetime(row['wishlist_adicionado_em']).strftime("%d/%m/%Y")
                st.metric("Adicionado em", data_add)
            
            with col4:
                if st.button("Ver Perfil", key=f"wishlist_perfil_{row['id_jogador']}_{idx}"):
                    st.session_state.pagina = "perfil"
                    st.session_state.jogador_selecionado = row['id_jogador']
                    st.query_params["jogador"] = row['id_jogador']
                    st.rerun()
                
                if st.button("Remover", key=f"wishlist_rem_{row['id_jogador']}_{idx}", type="secondary"):
                    if db.remover_wishlist(row['id_jogador']):
                        st.success("Removido!")
                        st.rerun()
            
            st.markdown("---")


# ============================================
# 7. TAB DE ALERTAS INTELIGENTES
# ============================================

def tab_alertas_inteligentes(db):
    """Tab de alertas inteligentes melhorados"""
    st.markdown("### 🔔 Alertas Inteligentes")
    st.markdown("Sistema automático de monitoramento baseado em regras")
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        filtro_tipo = st.multiselect(
            "Tipo de Alerta",
            options=['Contrato vencendo em breve', 'Sem avaliação recente', 
                    'Desempenho em queda', 'Idade crítica + Contrato curto'],
            default=['Contrato vencendo em breve', 'Desempenho em queda']
        )
    
    with col2:
        filtro_prioridade = st.multiselect(
            "Prioridade",
            options=['alta', 'media', 'baixa'],
            default=['alta', 'media'],
            format_func=lambda x: {'alta': '🔴 Alta', 'media': '🟡 Média', 'baixa': '🟢 Baixa'}[x]
        )
    
    # Buscar alertas
    alertas = db.get_alertas_inteligentes()
    
    # Filtrar
    if filtro_tipo:
        alertas = alertas[alertas['tipo_alerta'].isin(filtro_tipo)]
    
    if filtro_prioridade:
        alertas = alertas[alertas['prioridade'].isin(filtro_prioridade)]
        
    
    st.metric("Total de Alertas", len(alertas))
    
    st.markdown("---")

   
    if alertas.empty or 'tipo_alerta' not in alertas.columns:
        st.info("✅ Tudo tranquilo! Nenhum alerta ativo no momento.")
        return
    
    # Agrupar por tipo
    for tipo in alertas['tipo_alerta'].unique():
        alertas_tipo = alertas[alertas['tipo_alerta'] == tipo]
        
        with st.expander(f"⚠️ {tipo} ({len(alertas_tipo)})", expanded=True):
            for _, alerta in alertas_tipo.iterrows():
                prioridade_icon = {'alta': '🔴', 'media': '🟡', 'baixa': '🟢'}[alerta['prioridade']]
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"{prioridade_icon} **{alerta['nome']}**")
                    st.caption(f"{alerta.get('posicao', 'N/A')} • {alerta.get('clube', 'N/A')}")
                
                with col2:
                    st.info(alerta['descricao'])
                
                with col3:
                    if st.button("Ver Perfil", key=f"alerta_{alerta['id_jogador']}_{tipo}"):
                        st.session_state.pagina = "perfil"
                        st.session_state.jogador_selecionado = alerta['id_jogador']
                        st.query_params["jogador"] = alerta['id_jogador']
                        st.rerun()
                
                st.markdown("---")


# ========================================
# TABS AVANÇADAS - BUSCA E ANÁLISE DE MERCADO
# ========================================



from datetime import datetime

# ============================================
# TAB DE BUSCA AVANÇADA
# ============================================

def tab_busca_avancada(db, df_jogadores):
    """Tab de Busca Avançada com Múltiplos Filtros"""
    st.markdown("### 🔍 Busca Avançada")
    st.markdown("Encontre jogadores com critérios específicos e salve suas buscas")
    
    # Inicializar filtros
    if 'filtros_busca' not in st.session_state:
        st.session_state.filtros_busca = {}
    
    # === SEÇÃO DE BUSCAS SALVAS ===
    with st.expander("💾 Minhas Buscas Salvas"):
        buscas_salvas = db.get_buscas_salvas()
        
        if len(buscas_salvas) > 0:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                busca_selecionada = st.selectbox(
                    "Carregar Busca Salva",
                    options=buscas_salvas['id_busca'].tolist(),
                    format_func=lambda x: buscas_salvas[buscas_salvas['id_busca'] == x]['nome_busca'].iloc[0]
                )
            
            with col2:
                if st.button("Carregar", width='stretch'):
                    resultado = db.executar_busca_salva(busca_selecionada)
                    st.session_state['resultado_busca'] = resultado
                    st.success("Busca carregada!")
        else:
            st.info("Nenhuma busca salva ainda")
    
    st.markdown("---")
    
    # === FORMULÁRIO DE FILTROS ===
    st.markdown("#### 🎯 Critérios de Busca")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Posição & Clube**")
        
        posicoes_disponiveis = sorted(df_jogadores['posicao'].dropna().unique().tolist())
        posicoes_selecionadas = st.multiselect(
            "Posições",
            options=posicoes_disponiveis,
            key="busca_posicoes"
        )
        
        clubes_disponiveis = sorted(df_jogadores['clube'].dropna().unique().tolist())
        clubes_selecionados = st.multiselect(
            "Clubes",
            options=clubes_disponiveis,
            key="busca_clubes"
        )
        
        nacionalidades_disponiveis = sorted(df_jogadores['nacionalidade'].dropna().unique().tolist())
        nacionalidades_selecionadas = st.multiselect(
            "Nacionalidades",
            options=nacionalidades_disponiveis,
            key="busca_nacs"
        )
    
    with col2:
        st.markdown("**Idade & Desempenho**")
        
        col_idade1, col_idade2 = st.columns(2)
        with col_idade1:
            idade_min = st.number_input("Idade Mínima", min_value=15, max_value=45, value=18)
        with col_idade2:
            idade_max = st.number_input("Idade Máxima", min_value=15, max_value=45, value=35)
        
        media_min = st.slider(
            "Média Mínima (Avaliação)",
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=0.5,
            help="Apenas jogadores com média igual ou superior"
        )
        
        contrato_vencendo = st.checkbox(
            "🚨 Apenas contratos vencendo (próximos 12 meses)",
            key="busca_contrato"
        )
    
    # Tags
    st.markdown("**Tags**")
    todas_tags = db.get_all_tags()
    tags_selecionadas = st.multiselect(
        "Filtrar por Tags",
        options=todas_tags['id_tag'].tolist(),
        format_func=lambda x: todas_tags[todas_tags['id_tag'] == x]['nome'].iloc[0],
        key="busca_tags"
    )
    
    # === BOTÕES DE AÇÃO ===
    col1, col2, col3 = st.columns([2, 2, 1])
    
    buscar_clicked = False
    salvar_clicked = False
    limpar_clicked = False
    
    with col1:
        buscar_clicked = st.button("🔎 Buscar", width='stretch', type="primary")
    
    with col2:
        salvar_clicked = st.button("💾 Salvar Busca", width='stretch')
    
    with col3:
        limpar_clicked = st.button("🗑️ Limpar", width='stretch')
    
    # === EXECUTAR BUSCA ===
    if buscar_clicked:
        filtros = {
            'posicoes': posicoes_selecionadas if posicoes_selecionadas else None,
            'clubes': clubes_selecionados if clubes_selecionados else None,
            'nacionalidades': nacionalidades_selecionadas if nacionalidades_selecionadas else None,
            'idade_min': idade_min,
            'idade_max': idade_max,
            'media_min': media_min,
            'contrato_vencendo': contrato_vencendo,
            'tags': tags_selecionadas if tags_selecionadas else None
        }
        
        with st.spinner("Buscando jogadores..."):
            resultado = db.busca_avancada(filtros)
            st.session_state['resultado_busca'] = resultado
            st.session_state['filtros_busca'] = filtros
    
    # === SALVAR BUSCA ===
    if salvar_clicked:
        if st.session_state.get('filtros_busca'):
            with st.form("form_salvar_busca"):
                nome_busca = st.text_input("Nome da Busca", 
                                             placeholder="Ex: Zagueiros brasileiros sub-25")
                autor = st.text_input("Seu nome", value="Scout")
                
                if st.form_submit_button("Salvar"):
                    if nome_busca:
                        if db.salvar_busca(nome_busca, st.session_state['filtros_busca'], autor):
                            st.success("Busca salva com sucesso!")
                    else:
                        st.warning("Digite um nome para a busca")
        else:
            st.warning("Execute uma busca primeiro")
    
    # === LIMPAR ===
    if limpar_clicked:
        st.session_state['resultado_busca'] = None
        st.session_state['filtros_busca'] = {}
        st.rerun()
    
    # === MOSTRAR RESULTADOS ===
    if 'resultado_busca' in st.session_state and st.session_state['resultado_busca'] is not None:
        resultado = st.session_state['resultado_busca']
        
        st.markdown("---")
        st.markdown("### 📊 Resultados da Busca")
        
        if len(resultado) == 0:
            st.warning("Nenhum jogador encontrado com os critérios especificados")
            return
        
        st.success(f"✅ {len(resultado)} jogador(es) encontrado(s)")
        
        # Opções de visualização
        view_mode = st.radio(
            "Modo de Visualização",
            options=['Cards', 'Tabela', 'Comparação'],
            horizontal=True
        )
        
        if view_mode == 'Cards':
            # Mostrar em cards
            for i in range(0, len(resultado), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(resultado):
                        jogador = resultado.iloc[idx]
                        with col:
                            with st.container():
                                st.markdown(f"### {jogador['nome']}")
                                st.caption(f"{jogador.get('posicao', 'N/A')} • {jogador.get('clube', 'Livre')}")
                                
                                if 'media_geral' in jogador:
                                    st.metric("Média", f"{jogador['media_geral']:.2f}")
                                
                                st.metric("Idade", f"{jogador.get('idade_atual', 'N/A')} anos")
                                
                                if st.button("Ver Perfil", key=f"busca_perfil_{jogador['id_jogador']}_{idx}_{i}"):
                                    st.session_state.pagina = "perfil"
                                    st.session_state.jogador_selecionado = jogador['id_jogador']
                                    st.query_params["jogador"] = jogador['id_jogador']
                                    st.rerun()
                                
                                st.markdown("---")
        
        elif view_mode == 'Tabela':
            # Mostrar em tabela
            df_display = resultado[['nome', 'posicao', 'clube', 'nacionalidade', 'idade_atual']].copy()
            
            if 'media_geral' in resultado.columns:
                df_display['media_geral'] = resultado['media_geral']
            
            st.dataframe(df_display, width='stretch', hide_index=True)
            
            # Botão de export
            csv = resultado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar Resultados (CSV)",
                data=csv,
                file_name=f"busca_avancada_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        else:  # Comparação
            st.markdown("**Selecione até 5 jogadores para comparar:**")
            
            jogadores_comparar = st.multiselect(
                "Jogadores",
                options=resultado['id_jogador'].tolist(),
                format_func=lambda x: resultado[resultado['id_jogador'] == x]['nome'].iloc[0],
                max_selections=5
            )
            
            if len(jogadores_comparar) >= 2:
                comparar_jogadores_busca(db, jogadores_comparar, resultado)
            else:
                st.info("Selecione pelo menos 2 jogadores para comparar")


# ============================================
# TAB DE ANÁLISE DE MERCADO
# ============================================

def tab_analise_mercado(db, df_jogadores):
    """Dashboard de Análise de Mercado"""
    st.markdown("### 📊 Análise de Mercado")
    st.markdown("Visão estratégica do mercado de jogadores")
    
    # === FILTROS RÁPIDOS ===
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        posicao_mercado = st.selectbox(
            "Posição",
            options=['Todas'] + sorted(df_jogadores['posicao'].dropna().unique().tolist())
        )
    
    with col2:
        liga_mercado = st.selectbox(
            "Liga",
            options=['Todas'] + sorted(df_jogadores['liga_clube'].dropna().unique().tolist())
        )
    
    with col3:
        idade_max_mercado = st.slider("Idade Máxima", 18, 40, 30)
    
    with col4:
        mostrar_apenas_prioridade = st.checkbox("Apenas Prioridade Alta")
    
    # Filtrar dados
    df_mercado = df_jogadores.copy()
    
    if posicao_mercado != 'Todas':
        df_mercado = df_mercado[df_mercado['posicao'] == posicao_mercado]
    
    if liga_mercado != 'Todas':
        df_mercado = df_mercado[df_mercado['liga_clube'] == liga_mercado]
    
    df_mercado = df_mercado[df_mercado['idade_atual'] <= idade_max_mercado]
    
    if mostrar_apenas_prioridade:
        wishlist = db.get_wishlist(prioridade='alta')
        df_mercado = df_mercado[df_mercado['id_jogador'].isin(wishlist['id_jogador'])]
    
    st.markdown("---")
    
    # === KPIS DO MERCADO ===
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total de Jogadores", len(df_mercado))
    
    with col2:
        contratos_vencendo = df_mercado[
            (pd.notna(df_mercado['data_fim_contrato'])) &
            (pd.to_datetime(df_mercado['data_fim_contrato']) <= pd.Timestamp.now() + pd.DateOffset(months=12))
        ]
        st.metric("Contratos Vencendo", len(contratos_vencendo))
    
    with col3:
        idade_media = df_mercado['idade_atual'].mean()
        st.metric("Idade Média", f"{idade_media:.1f} anos")
    
    with col4:
        jogadores_livres = df_mercado[df_mercado['status_contrato'] == 'livre']
        st.metric("Jogadores Livres", len(jogadores_livres))
    
    # === VISUALIZAÇÕES ===
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Distribuição", 
        "⏰ Contratos", 
        "💰 Oportunidades",
        "🎯 Benchmark"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Distribuição por Clube")
            top_clubes = df_mercado['clube'].value_counts().head(15)
            fig = px.bar(
                x=top_clubes.values,
                y=top_clubes.index,
                orientation='h',
                title=f"Top 15 Clubes ({posicao_mercado})"
            )
            fig.update_layout(xaxis_title="Quantidade", yaxis_title="")
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.markdown("#### Distribuição por Nacionalidade")
            top_nacs = df_mercado['nacionalidade'].value_counts().head(10)
            fig = px.pie(
                values=top_nacs.values,
                names=top_nacs.index,
                title="Top 10 Nacionalidades",
                hole=0.4
            )
            st.plotly_chart(fig, width='stretch')
        
        # Distribuição de Idade
        st.markdown("#### Pirâmide Etária")
        fig = px.histogram(
            df_mercado[df_mercado['idade_atual'].notna()],
            x='idade_atual',
            nbins=25,
            title=f"Distribuição de Idade - {posicao_mercado}"
        )
        fig.update_layout(xaxis_title="Idade", yaxis_title="Quantidade")
        st.plotly_chart(fig, width='stretch')
    
    with tab2:
        st.markdown("#### 📅 Análise de Contratos")
        
        # Timeline de vencimentos
        df_contratos = df_mercado[pd.notna(df_mercado['data_fim_contrato'])].copy()
        df_contratos['data_fim_contrato'] = pd.to_datetime(df_contratos['data_fim_contrato'])
        df_contratos['ano_vencimento'] = df_contratos['data_fim_contrato'].dt.year
        
        contratos_por_ano = df_contratos['ano_vencimento'].value_counts().sort_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=contratos_por_ano.index,
            y=contratos_por_ano.values,
            marker_color='#667eea',
            text=contratos_por_ano.values,
            textposition='outside'
        ))
        fig.update_layout(
            title="Vencimentos de Contratos por Ano",
            xaxis_title="Ano",
            yaxis_title="Quantidade de Jogadores",
            height=400
        )
        st.plotly_chart(fig, width='stretch')
        
        # Lista de jogadores com contrato vencendo
        st.markdown("#### ⚠️ Contratos Vencendo em 2025")
        df_2025 = df_contratos[df_contratos['ano_vencimento'] == 2025].copy()
        
        if len(df_2025) > 0:
            df_2025_display = df_2025[['nome', 'posicao', 'clube', 'idade_atual', 'data_fim_contrato']].copy()
            df_2025_display['data_fim_contrato'] = df_2025_display['data_fim_contrato'].dt.strftime('%d/%m/%Y')
            st.dataframe(df_2025_display, width='stretch', hide_index=True)
        else:
            st.info("Nenhum contrato vencendo em 2025")
    
    with tab3:
        st.markdown("#### 💰 Oportunidades de Mercado")
        st.caption("Jogadores em situações favoráveis para negociação")
        
        # Critérios de oportunidade
        oportunidades = []
        
        # 1. Jovens promissores com avaliação alta
        for _, jogador in df_mercado.iterrows():
            if pd.notna(jogador.get('idade_atual')) and jogador['idade_atual'] < 23:
                media = calcular_media_jogador(db, jogador['id_jogador'])
                if media >= 4.0:
                    oportunidades.append({
                        'jogador': jogador['nome'],
                        'tipo': '🌟 Jovem Promissor',
                        'detalhes': f"{jogador['idade_atual']} anos, Média: {media:.1f}",
                        'id_jogador': jogador['id_jogador']
                    })
        
        # 2. Contratos vencendo em 6 meses
        for _, jogador in df_mercado.iterrows():
            if pd.notna(jogador.get('data_fim_contrato')):
                dias_restantes = (pd.to_datetime(jogador['data_fim_contrato']) - pd.Timestamp.now()).days
                if 0 < dias_restantes <= 180:
                    oportunidades.append({
                        'jogador': jogador['nome'],
                        'tipo': '⏰ Contrato Curto',
                        'detalhes': f"Vence em {dias_restantes} dias",
                        'id_jogador': jogador['id_jogador']
                    })
        
        # 3. Jogadores livres no mercado
        for _, jogador in df_mercado.iterrows():
            if jogador.get('status_contrato') == 'livre':
                oportunidades.append({
                    'jogador': jogador['nome'],
                    'tipo': '🆓 Livre',
                    'detalhes': f"{jogador.get('posicao', 'N/A')}, {jogador.get('idade_atual', 'N/A')} anos",
                    'id_jogador': jogador['id_jogador']
                })
        
        if len(oportunidades) > 0:
            df_oport = pd.DataFrame(oportunidades)
            
            # Mostrar por tipo
            for tipo in df_oport['tipo'].unique():
                with st.expander(f"{tipo} ({len(df_oport[df_oport['tipo'] == tipo])})", expanded=True):
                    df_tipo = df_oport[df_oport['tipo'] == tipo]
                    
                    for idx, (_, oport) in enumerate(df_tipo.iterrows()):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            st.markdown(f"**{oport['jogador']}**")
                        
                        with col2:
                            st.caption(oport['detalhes'])
                        
                        with col3:
                            if st.button("Ver", key=f"oport_{oport['id_jogador']}_{idx}"):
                                st.session_state.pagina = "perfil"
                                st.session_state.jogador_selecionado = oport['id_jogador']
                                st.query_params["jogador"] = oport['id_jogador']
                                st.rerun()
                        
                        st.markdown("---")
        else:
            st.info("Nenhuma oportunidade identificada com os filtros atuais")
    
    with tab4:
        st.markdown("#### 🎯 Benchmark por Posição")
        
        benchmarks = db.get_all_benchmarks()
        
        if len(benchmarks) > 0:
            # Tabela de benchmarks
            st.dataframe(benchmarks, width='stretch', hide_index=True)
            
            # Gráfico comparativo
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=benchmarks['posicao'],
                y=benchmarks['media_geral'],
                mode='markers+lines',
                name='Média Geral',
                marker=dict(size=12, color='#667eea'),
                line=dict(width=2)
            ))
            
            fig.update_layout(
                title="Média Geral por Posição",
                xaxis_title="Posição",
                yaxis_title="Média",
                yaxis=dict(range=[0, 5]),
                height=400
            )
            
            st.plotly_chart(fig, width='stretch')
        else:
            st.warning("Sem dados de benchmark. Adicione avaliações aos jogadores.")


def comparar_jogadores_busca(db, ids_jogadores, df_jogadores):
    """Compara múltiplos jogadores da busca"""
    st.markdown("### ⚖️ Comparação de Jogadores")
    
    # Buscar dados dos jogadores
    dados_comparacao = []
    
    for id_jog in ids_jogadores:
        jogador = df_jogadores[df_jogadores['id_jogador'] == id_jog].iloc[0]
        avaliacao = db.get_ultima_avaliacao(id_jog)
        
        if not avaliacao.empty:
            dados_comparacao.append({
                'Nome': jogador['nome'],
                'Posição': jogador.get('posicao', 'N/A'),
                'Clube': jogador.get('clube', 'Livre'),
                'Idade': jogador.get('idade_atual', 'N/A'),
                'Potencial': avaliacao['nota_potencial'].iloc[0],
                'Tático': avaliacao['nota_tatico'].iloc[0],
                'Técnico': avaliacao['nota_tecnico'].iloc[0],
                'Físico': avaliacao['nota_fisico'].iloc[0],
                'Mental': avaliacao['nota_mental'].iloc[0],
                'Média': (avaliacao['nota_tatico'].iloc[0] + avaliacao['nota_tecnico'].iloc[0] +
                          avaliacao['nota_fisico'].iloc[0] + avaliacao['nota_mental'].iloc[0]) / 4
            })
    
    if len(dados_comparacao) > 0:
        df_comp = pd.DataFrame(dados_comparacao)
        
        # Tabela
        st.dataframe(df_comp, width='stretch', hide_index=True)
        
        # Gráfico de radar
        categorias = ['Tático', 'Técnico', 'Físico', 'Mental']
        
        fig = go.Figure()
        
        cores = ['#667eea', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
        
        for i, row in df_comp.iterrows():
            valores = [row['Tático'], row['Técnico'], row['Físico'], row['Mental']]
            valores += [valores[0]]  # Fechar o polígono
            
            fig.add_trace(go.Scatterpolar(
                r=valores,
                theta=categorias + [categorias[0]],
                fill='toself',
                name=row['Nome'],
                line=dict(color=cores[i % len(cores)])
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True,
            height=500
        )
        
        st.plotly_chart(fig, width='stretch')
    else:
        st.warning("Jogadores selecionados não possuem avaliações")


def calcular_media_jogador(db, id_jogador):
    """Calcula média de um jogador (helper)"""
    avaliacao = db.get_ultima_avaliacao(id_jogador)
    if not avaliacao.empty:
        return (avaliacao['nota_tatico'].iloc[0] + avaliacao['nota_tecnico'].iloc[0] +
                avaliacao['nota_fisico'].iloc[0] + avaliacao['nota_mental'].iloc[0]) / 4
    return 0.0


# ========================================
# FUNÇÃO PRINCIPAL
# ========================================

@st.cache_data(ttl=600, show_spinner=False)  # ← ADICIONE ESTA LINHA
def carregar_jogadores(_db):
    """Carrega jogadores do banco com cache"""
    return _db.get_jogadores_com_vinculos()

@st.cache_data(ttl=300, show_spinner=False)
def get_opcoes_filtros_cached(_db):
    """Cache das opções de filtros para a sidebar"""
    df = _db.get_jogadores_com_vinculos()
    return {
        'posicoes': sorted(df['posicao'].dropna().unique().tolist()) if 'posicao' in df.columns else [],
        'clubes': sorted(df['clube'].dropna().unique().tolist()) if 'clube' in df.columns else [],
        'nacionalidades': sorted(df['nacionalidade'].dropna().unique().tolist()) if 'nacionalidade' in df.columns else [],
        'ligas': sorted(df['liga_clube'].dropna().unique().tolist()) if 'liga_clube' in df.columns else []
    }


@st.cache_data(ttl=300, show_spinner=False)
def get_ids_wishlist_cached(_db):
    """Cache de IDs da wishlist para lookup O(1)"""
    return _db.get_ids_wishlist()


def invalidar_caches():
    """Limpa todos os caches após sincronização"""
    carregar_jogadores.clear()
    get_opcoes_filtros_cached.clear()
    get_ids_wishlist_cached.clear()


def main():
    # JavaScript para remover elementos vazios após carregamento
    st.markdown("""
    <script>
    window.addEventListener('load', function() {
        // Remove elementos completamente vazios
        document.querySelectorAll('div[data-testid="stElementContainer"]').forEach(el => {
            if (el.children.length === 0 || (el.textContent.trim() === '' && !el.querySelector('img, video, iframe'))) {
                el.remove();
            }
        });

        // Remove stVerticalBlock vazios
        document.querySelectorAll('div[data-testid="stVerticalBlock"]').forEach(el => {
            if (el.children.length === 0) {
                el.remove();
            }
        });
    });
    </script>
    """, unsafe_allow_html=True)

    # Header Visual Profissional (CSS movido para custom.css)
    st.markdown(
        """
        <div class="header-container fade-in">
            <div class="header-title">⚽ Scout Pro</div>
            <div class="header-subtitle">Sistema Profissional de Monitoramento e Análise de Jogadores</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Inicializar banco de dados PRIMEIRO
    db = get_database()

    # Criar tabela de avaliações se não existir
    db.criar_tabelas()

    # Atualizar status dos contratos automaticamente (1x por sessão)
    if 'status_contratos_atualizado' not in st.session_state:
        try:
            db.atualizar_status_contratos()
            st.session_state.status_contratos_atualizado = True
        except Exception as e:
            print(f"⚠️ Erro ao atualizar status de contratos: {e}")

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
        # Botão de voltar com estilo minimalista
        if st.button("← Voltar para Dashboard", key="voltar_perfil", type="secondary", use_container_width=False):
            st.session_state.pagina = "dashboard"
            st.session_state.jogador_selecionado = None
            st.query_params.clear()
            st.rerun()

        debug_fotos_perfil = st.sidebar.checkbox("🐛 Debug de Fotos (Perfil)", value=False, help="Ativa modo debug")

        exibir_perfil_jogador(db, st.session_state.jogador_selecionado, debug=debug_fotos_perfil)
        return

    # Dashboard principal continua aqui

    # --- BARRA LATERAL: SINCRONIZAÇÃO ---
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
                    invalidar_caches()  # ⚡ Função específica ao invés de clear() geral
                    time.sleep(1)
                    st.rerun()
                else:
                    st.sidebar.error("❌ Falha na sincronização.")
            except Exception as e:
                st.sidebar.error(f"❌ Erro: {str(e)}")
    
    st.sidebar.markdown("---") 
    
    # --- BARRA LATERAL: FILTROS ---
    st.sidebar.header("🔍 Filtros")
    
    # DEBUG MODE
    debug_fotos = st.sidebar.checkbox("🐛 Debug de Fotos", value=False, help="Ativa modo debug")
    
    # Carregar dados COM CACHE
    df_jogadores = carregar_jogadores(db)
    
    # Verificar se há dados
    if len(df_jogadores) == 0:
        st.error("⚠️ **Banco de dados vazio!**")
        st.markdown("O sistema não encontrou jogadores cadastrados.")
        
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
    
    # ⚡ Usar opções em cache (evita recalcular a cada rerun)
    opcoes = get_opcoes_filtros_cached(db)
    posicoes = opcoes['posicoes']
    nacionalidades = opcoes['nacionalidades']
    clubes = opcoes['clubes']
    ligas = opcoes['ligas']
    
    # Filtros da sidebar
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
    
    filtro_liga = st.sidebar.multiselect(
        "🏆 Liga",
        options=ligas,
        default=[]
    )
    
    # Aplicar filtros
    df_filtrado = df_jogadores.copy()
    
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
    
    if filtro_liga:
        df_filtrado = df_filtrado[df_filtrado['liga_clube'].isin(filtro_liga)]
    
    # ============== NAVEGAÇÃO OTIMIZADA (LAZY LOADING) ==============
    st.markdown("---")
    
    tab_selecionada = st.selectbox(
        "📍 Navegação",
        [
            "📊 Visão Geral",
            "👥 Lista de Jogadores", 
            "⭐ Wishlist",
            "🏆 Ranking",
            "⚖️ Comparador",
            "⚽ Shadow Team",
            "🔍 Busca Avançada",
            "📈 Análise de Mercado",
            "🔔 Alertas",
            "💰 Financeiro",
            "📋 Avaliação Massiva"
        ],
        key="nav_principal",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Renderizar APENAS a tab selecionada
    if tab_selecionada == "📊 Visão Geral":
        with st.spinner("Carregando visão geral..."):
            st.subheader(f"📋 Visão Geral do Sistema")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total de Jogadores", len(df_filtrado))
            
            with col2:
                try:
                    with db.engine.connect() as conn:
                        result = conn.execute(text("SELECT COUNT(*) as total FROM avaliacoes"))
                        total_avaliacoes = result.fetchone()[0]
                except:
                    total_avaliacoes = 0
                st.metric("Total de Avaliações", total_avaliacoes)
            
            with col3:
                try:
                    wishlist = db.get_wishlist()
                    wishlist_count = len(wishlist)
                except:
                    wishlist_count = 0
                st.metric("Jogadores na Wishlist", wishlist_count)
            
            with col4:
                try:
                    with db.engine.connect() as conn:
                        result = conn.execute(text("SELECT COUNT(DISTINCT id_jogador) as total FROM jogador_tags"))
                        tags_count = result.fetchone()[0]
                except:
                    tags_count = 0
                st.metric("Jogadores com Tags", tags_count)
            
            st.markdown("---")
            
            if len(df_filtrado) > 0:
                st.markdown("#### 🎯 Primeiros Jogadores")
                exibir_lista_com_fotos(df_filtrado.head(10), db, debug=debug_fotos, sufixo_key="overview")
                
                if len(df_filtrado) > 10:
                    st.info(f"Mostrando os primeiros 10 de {len(df_filtrado)} jogadores. Use as outras tabs para explorar mais.")
            else:
                st.warning("Nenhum jogador encontrado com os filtros aplicados.")

    elif tab_selecionada == "👥 Lista de Jogadores":
        with st.spinner("Carregando lista de jogadores..."):
            st.subheader(f"📋 Lista Completa: {len(df_filtrado)} jogadores")
            
            if len(df_filtrado) > 0:
                view_mode = st.radio(
                    "Modo de Visualização",
                    ["📸 Cards com Fotos", "📊 Tabela"],
                    horizontal=True,
                    key="view_mode_tab2"
                )
                
                st.markdown("---")
                
                if view_mode == "📸 Cards com Fotos":
                    exibir_lista_com_fotos(df_filtrado, db, debug=debug_fotos, sufixo_key="lista_completa")
                
                else:  # Tabela
                    df_display = df_filtrado.copy()
                    
                    base_url = "https://scoutingscr-kqoj2ctskq2nv4a4wvrc.streamlit.app"
                    
                    df_display['🔗 Perfil'] = df_display['id_jogador'].apply(
                        lambda x: f'<a href="{base_url}?jogador={x}" target="_blank">Ver Perfil</a>'
                    )
                    
                    colunas_exibir = ['nome', 'posicao', 'clube', 'liga_clube', 'nacionalidade', 
                                    'idade_atual', 'altura', 'pe_dominante', 'data_fim_contrato', '🔗 Perfil']
                    
                    colunas_disponiveis = [col for col in colunas_exibir if col in df_display.columns or col == '🔗 Perfil']
                    df_tabela = df_display[colunas_disponiveis].copy()
                    
                    rename_map = {
                        'nome': 'Nome',
                        'posicao': 'Posição',
                        'clube': 'Clube',
                        'liga_clube': 'Liga',
                        'nacionalidade': 'Nacionalidade',
                        'idade_atual': 'Idade',
                        'altura': 'Altura (cm)',
                        'pe_dominante': 'Pé',
                        'data_fim_contrato': 'Fim Contrato'
                    }
                    df_tabela = df_tabela.rename(columns=rename_map)
                    
                    jogadores_por_pagina = 50
                    total_paginas = (len(df_tabela) - 1) // jogadores_por_pagina + 1
                    
                    if total_paginas > 1:
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            pagina_atual = st.number_input(
                                "Página",
                                min_value=1,
                                max_value=total_paginas,
                                value=1,
                                key="paginacao_tabela"
                            )
                    else:
                        pagina_atual = 1
                    
                    inicio = (pagina_atual - 1) * jogadores_por_pagina
                    fim = min(inicio + jogadores_por_pagina, len(df_tabela))
                    df_pagina = df_tabela.iloc[inicio:fim]
                    
                    st.caption(f"Exibindo jogadores {inicio + 1} a {fim} de {len(df_tabela)}")
                    
                    st.markdown(
                        df_pagina.to_html(escape=False, index=False),
                        unsafe_allow_html=True
                    )
                    
                    st.markdown("---")
                    csv = df_filtrado.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Exportar Lista (CSV)",
                        data=csv,
                        file_name=f"jogadores_scout_pro_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="export_csv_tab2"
                    )
            else:
                st.warning("Nenhum jogador encontrado com os filtros aplicados.")

    elif tab_selecionada == "⭐ Wishlist":
        with st.spinner("Carregando wishlist..."):
            tab_wishlist(db)

    elif tab_selecionada == "🏆 Ranking":
        with st.spinner("Carregando ranking..."):
            tab_ranking(db, df_filtrado)

    elif tab_selecionada == "⚖️ Comparador":
        with st.spinner("Carregando comparador..."):
            tab_comparador(db, df_filtrado)

    elif tab_selecionada == "⚽ Shadow Team":
        with st.spinner("Carregando shadow team..."):
            tab_shadow_team(db, df_jogadores)

    elif tab_selecionada == "🔍 Busca Avançada":
        with st.spinner("Carregando busca avançada..."):
            tab_busca_avancada(db, df_filtrado)

    elif tab_selecionada == "📈 Análise de Mercado":
        with st.spinner("Carregando análise de mercado..."):
            tab_analise_mercado(db, df_filtrado)

    elif tab_selecionada == "🔔 Alertas":
        with st.spinner("Carregando alertas..."):
            tab_alertas_inteligentes(db)

    elif tab_selecionada == "💰 Financeiro":
        with st.spinner("Carregando financeiro..."):
            aba_financeira()

    elif tab_selecionada == "📋 Avaliação Massiva":  # ← ADICIONAR ESTE BLOCO
        with st.spinner("Carregando avaliação massiva..."):
            from avaliacao_massiva import criar_aba_avaliacao_massiva
            criar_aba_avaliacao_massiva(db)

if __name__ == "__main__":
    main()
    
