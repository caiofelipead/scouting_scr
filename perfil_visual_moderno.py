"""
Perfil Visual Minimalista - Funcional e Responsivo
==================================================
Header e componentes simples e confiáveis para perfil de jogador

Autor: Scout Pro
Data: 2025-12-10
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict
from logos_clubes import get_bandeira_pais
from transfermarkt_logos import get_logo_clube_transfermarkt, get_logo_liga_transfermarkt


def criar_header_profissional(jogador: pd.Series, foto_path: Optional[str] = None) -> None:
    """
    Cria header minimalista e funcional com foto, informações básicas

    Args:
        jogador: Série do pandas com dados do jogador
        foto_path: URL para a foto do jogador
    """

    # CSS minimalista - apenas o essencial
    st.markdown("""
    <style>
    /* Sistema de spacing consistente: 8px base */
    .player-header-simple {
        background: #6366f1;
        padding: 24px;
        border-radius: 8px;
        margin-bottom: 24px;
    }

    .player-name-simple {
        font-size: 32px;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 8px 0;
        line-height: 1.2;
    }

    .player-position-simple {
        font-size: 14px;
        font-weight: 600;
        color: #e0e7ff;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 16px 0;
    }

    .info-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 16px;
    }

    .info-badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 13px;
        color: #ffffff;
        white-space: nowrap;
    }

    .club-section {
        background: rgba(255, 255, 255, 0.15);
        padding: 12px;
        border-radius: 8px;
        margin-top: 16px;
        color: #ffffff;
        font-size: 14px;
    }

    /* Responsividade */
    @media (max-width: 768px) {
        .player-name-simple {
            font-size: 24px;
        }
        .player-header-simple {
            padding: 16px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Container principal
    st.markdown('<div class="player-header-simple">', unsafe_allow_html=True)

    # Layout: 2 colunas (foto pequena | info)
    col_foto, col_info = st.columns([1, 3])

    with col_foto:
        # Foto usando st.image nativo (mais confiável)
        if foto_path:
            try:
                st.image(foto_path, use_container_width=True)
            except:
                # Fallback: mostrar inicial
                inicial = jogador.get('nome', '?')[0]
                st.markdown(f"""
                <div style='
                    width: 100%;
                    aspect-ratio: 1;
                    background: #4f46e5;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 48px;
                    color: white;
                    font-weight: 700;
                '>
                    {inicial}
                </div>
                """, unsafe_allow_html=True)
        else:
            # Placeholder simples
            inicial = jogador.get('nome', '?')[0]
            st.markdown(f"""
            <div style='
                width: 100%;
                aspect-ratio: 1;
                background: #4f46e5;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 48px;
                color: white;
                font-weight: 700;
            '>
                {inicial}
            </div>
            """, unsafe_allow_html=True)

    with col_info:
        # Nome e posição
        nome = jogador.get('nome', 'Jogador')
        posicao = jogador.get('posicao', 'N/A')

        st.markdown(f'<h1 class="player-name-simple">{nome}</h1>', unsafe_allow_html=True)
        st.markdown(f'<div class="player-position-simple">⚽ {posicao}</div>', unsafe_allow_html=True)

        # Informações básicas em badges
        badges_html = '<div class="info-row">'

        # Nacionalidade
        if pd.notna(jogador.get('nacionalidade')):
            bandeira = get_bandeira_pais(jogador['nacionalidade'])
            badges_html += f'<span class="info-badge">{bandeira} {jogador["nacionalidade"]}</span>'

        # Idade
        if pd.notna(jogador.get('idade_atual')):
            badges_html += f'<span class="info-badge">🎂 {int(jogador["idade_atual"])} anos</span>'

        # Altura
        if pd.notna(jogador.get('altura')):
            badges_html += f'<span class="info-badge">📏 {int(jogador["altura"])} cm</span>'

        # Pé dominante
        if pd.notna(jogador.get('pe_dominante')):
            badges_html += f'<span class="info-badge">🦶 {jogador["pe_dominante"]}</span>'

        badges_html += '</div>'
        st.markdown(badges_html, unsafe_allow_html=True)

        # Clube e liga
        clube = jogador.get('clube', '')
        liga = jogador.get('liga_clube', '')

        if clube or liga:
            club_text = f"<div class='club-section'>"
            if clube:
                club_text += f"<strong>⚽ {clube}</strong>"
            if liga:
                if clube:
                    club_text += " • "
                club_text += f"🏆 {liga}"
            club_text += "</div>"
            st.markdown(club_text, unsafe_allow_html=True)

    # Fechar container
    st.markdown('</div>', unsafe_allow_html=True)


def criar_secao_stats_rapidas(stats: Dict) -> None:
    """
    Cria seção de estatísticas rápidas em colunas simples

    Args:
        stats: Dicionário com estatísticas {label: {value, subtitle}}
    """

    st.markdown("""
    <style>
    .stat-card-simple {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }

    .stat-label-simple {
        font-size: 11px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .stat-value-simple {
        font-size: 28px;
        font-weight: 700;
        color: #1e293b;
    }

    .stat-subtitle-simple {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(stats))

    for col, (label, data) in zip(cols, stats.items()):
        with col:
            st.markdown(f"""
            <div class='stat-card-simple'>
                <div class='stat-label-simple'>{label}</div>
                <div class='stat-value-simple'>{data['value']}</div>
                <div class='stat-subtitle-simple'>{data.get('subtitle', '')}</div>
            </div>
            """, unsafe_allow_html=True)


def criar_cards_categorias(categorias: Dict) -> None:
    """
    Cria cards de categorias simples

    Args:
        categorias: {nome: {icone, valor, descricao}}
    """

    st.markdown("""
    <style>
    .category-card-simple {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        transition: all 0.2s ease;
    }

    .category-card-simple:hover {
        border-color: #6366f1;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
    }

    .category-icon-simple {
        font-size: 32px;
        margin-bottom: 8px;
    }

    .category-title-simple {
        font-size: 13px;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    .category-value-simple {
        font-size: 24px;
        font-weight: 700;
        color: #6366f1;
    }

    .category-desc-simple {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(categorias))

    for col, (nome, data) in zip(cols, categorias.items()):
        with col:
            st.markdown(f"""
            <div class='category-card-simple'>
                <div class='category-icon-simple'>{data['icone']}</div>
                <div class='category-title-simple'>{nome}</div>
                <div class='category-value-simple'>{data['valor']}</div>
                <div class='category-desc-simple'>{data.get('descricao', '')}</div>
            </div>
            """, unsafe_allow_html=True)


def criar_badge_status(status: str, tipo: str = "success") -> str:
    """
    Cria badge HTML de status simples

    Args:
        status: Texto do status
        tipo: success, warning, error, info

    Returns:
        HTML do badge
    """

    cores = {
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#6366f1"
    }

    cor = cores.get(tipo, cores["info"])

    return f"""
    <span style='
        background: {cor}15;
        color: {cor};
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    '>
        {status}
    </span>
    """
