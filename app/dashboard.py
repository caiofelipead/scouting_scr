import random
import sys
import time
from datetime import datetime
from pathlib import Path
from migrate_financeiro import migrar_colunas_financeiras
migrar_colunas_financeiras()

# Imports de terceiros PRIMEIRO
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from mplsoccer import Pitch
from sqlalchemy import text

# Configuração da página (DEVE SER A PRIMEIRA CHAMADA)
st.set_page_config(page_title="Scout Pro", page_icon="⚽", layout="wide")

# --- CORREÇÃO DE CAMINHOS (CRÍTICO) ---
try:
    current_path = Path(__file__).resolve()
    root_path = current_path.parent.parent
    
    if str(root_path) not in sys.path:
        sys.path.insert(0, str(root_path))
except Exception as e:
    st.error(f"❌ Erro ao configurar caminhos: {e}")
    st.stop()

# AGORA importa os módulos locais
try:
    from utils_fotos import get_foto_jogador, get_foto_jogador_rapido
    from auth import check_password, mostrar_info_usuario
    from dashboard_financeiro import aba_financeira
    from database import ScoutingDatabase
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

# CSS Profissional - Scout Pro (TODO O CSS AQUI)
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
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
        transition: all 0.2s ease;
    }
    
    /* Labels das métricas */
    div[data-testid="stMetric"] label {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
    }
    
    /* Valores das métricas */
    div[data-testid="stMetric"] > div {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #667eea !important;
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
        border: 2px solid transparent;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: all 0.2s ease;
    }
    
    /* Imagens dos jogadores */
    img {
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Cards */
    .element-container {
        transition: all 0.2s ease;
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
    
    /* ========== NOVO: TABELAS HTML ESTILIZADAS ========== */
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-radius: 10px;
        overflow: hidden;
        background: white;
        margin: 1rem 0;
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
        border-bottom: 1px solid #e9ecef;
        color: #2c3e50;
    }
    
    tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    tr:hover {
        background-color: #e3f2fd !important;
        transition: background-color 0.2s;
    }
    
    /* Links na tabela */
    table a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        background: #f0f3ff;
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


def extrair_id_da_url(url_ou_id):
    """Extrai ID do Transfermarkt de uma URL ou retorna o próprio ID"""
    import re
    if not url_ou_id:
        return None
    
    url_str = str(url_ou_id).strip()
    
    # Se já é um número puro
    if url_str.isdigit():
        return url_str
    
    # Tentar extrair de URL
    match = re.search(r"/spieler/(\d+)", url_str)
    if match:
        return match.group(1)
    
    return None


def get_foto_jogador_rapido(transfermarkt_id):
    """
    Versão ultra-rápida: apenas URL padrão, sem scraping
    Use quando performance é crítica (lista com muitos jogadores)
    """
    if not transfermarkt_id:
        return "https://via.placeholder.com/150?text=Sem+Foto"
    
    tm_id = extrair_id_da_url(transfermarkt_id)
    
    if tm_id:
        return f"https://img.a.transfermarkt.technology/portrait/big/{tm_id}.jpg"
    
    return "https://via.placeholder.com/150?text=Sem+Foto"


def exibir_lista_com_fotos(df_jogadores, db, debug=False, sufixo_key=""):
    """
    Exibe uma lista de jogadores em cards com suas fotos.
    Paginação por blocos de 9 (3x3).
    """
    if len(df_jogadores) == 0:
        st.info("Nenhum jogador para exibir.")
        return
    
    # Configuração de paginação
    jogadores_por_pagina = 9
    total_paginas = (len(df_jogadores) - 1) // jogadores_por_pagina + 1
    
    if total_paginas > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pagina_atual = st.number_input(
                "Página",
                min_value=1,
                max_value=total_paginas,
                value=1,
                key=f"paginacao_{sufixo_key}"
            )
    else:
        pagina_atual = 1
    
    # Calcular índices
    inicio = (pagina_atual - 1) * jogadores_por_pagina
    fim = min(inicio + jogadores_por_pagina, len(df_jogadores))
    
    df_pagina = df_jogadores.iloc[inicio:fim]
    
    st.caption(f"Exibindo jogadores {inicio + 1} a {fim} de {len(df_jogadores)}")
    st.markdown("---")
    
    # Exibir em grade 3x3
    for i in range(0, len(df_pagina), 3):
        cols = st.columns(3)
        
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(df_pagina):
                jogador = df_pagina.iloc[idx]
                
                with col:
                    with st.container():
                        # Buscar foto
                        tm_id = jogador.get('transfermarkt_id', None)
                        if tm_id:
                            tm_id_extraido = extrair_id_da_url(tm_id)
                            if tm_id_extraido:
                                url_foto = f"https://img.a.transfermarkt.technology/portrait/big/{tm_id_extraido}.jpg"
                            else:
                                url_foto = "https://via.placeholder.com/150?text=Sem+Foto"
                        else:
                            url_foto = "https://via.placeholder.com/150?text=Sem+Foto"
                        
                        st.image(url_foto, width=200)
                        
                        st.markdown(f"### {jogador['nome']}")
                        st.caption(f"{jogador.get('posicao', 'N/A')} • {jogador.get('clube', 'Livre')}")
                        
                        if pd.notna(jogador.get('idade_atual')):
                            st.metric("Idade", f"{jogador['idade_atual']} anos")
                        
                        if pd.notna(jogador.get('nacionalidade')):
                            st.caption(f"🏁 {jogador['nacionalidade']}")
                        
                        # Botão para ver perfil
                        if st.button("Ver Perfil", key=f"perfil_{jogador['id_jogador']}_{sufixo_key}_{idx}"):
                            st.session_state.pagina = "perfil"
                            st.session_state.jogador_selecionado = jogador['id_jogador']
                            st.query_params["jogador"] = jogador['id_jogador']
                            st.rerun()
                        
                        st.markdown("---")


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


# Continue com o resto do código original...
# (O arquivo completo tem 2600+ linhas, então estou truncando aqui por brevidade)
# As funções tab_ranking, tab_comparador, tab_shadow_team, etc. continuam iguais
