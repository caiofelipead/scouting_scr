"""
Perfil Visual Moderno - Estilo ScoutingStats.ai
================================================
Header e componentes visuais profissionais para perfil de jogador

Autor: Scout Pro
Data: 2025-12-09
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict
from logos_clubes import get_bandeira_pais
from transfermarkt_logos import get_logo_clube_transfermarkt, get_logo_liga_transfermarkt


def criar_header_profissional(jogador: pd.Series, foto_path: Optional[str] = None) -> None:
    """
    Cria header estilo scoutingstats.ai com foto grande, informações e logos

    Args:
        jogador: Série do pandas com dados do jogador
        foto_path: Caminho para a foto do jogador
    """

    # CSS customizado para o header - Tema Claro
    st.markdown("""
    <style>
    /* Container principal do header - QUASE PRETO */
    .player-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    }

    .player-name {
        font-size: 42px;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 8px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        line-height: 1.2;
    }

    .player-position {
        font-size: 18px;
        font-weight: 600;
        color: rgba(255,255,255,0.95);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 16px;
    }

    .club-info {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 16px;
        background: rgba(255,255,255,0.15);
        padding: 12px 20px;
        border-radius: 12px;
        border-left: 4px solid rgba(255,255,255,0.5);
    }

    .club-name {
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
    }

    .league-badge {
        background: rgba(255,255,255,0.2);
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        color: #ffffff;
    }

    .info-chip {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        padding: 8px 16px;
        border-radius: 20px;
        margin: 4px;
        font-size: 14px;
        color: #ffffff;
    }

    .info-chip-label {
        color: rgba(255,255,255,0.8);
        font-weight: 500;
    }

    .info-chip-value {
        color: #ffffff;
        font-weight: 700;
        margin-left: 6px;
    }

    .player-photo {
        border-radius: 16px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
        border: 4px solid rgba(255,255,255,0.3);
    }

    .stat-card-pro {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
    }

    .stat-card-pro:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
    }

    .stat-label-pro {
        font-size: 12px;
        color: #667eea;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .stat-value-pro {
        font-size: 32px;
        font-weight: 900;
        color: #2c3e50;
        text-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }

    .stat-subtitle-pro {
        font-size: 11px;
        color: #718096;
        margin-top: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Container com background escuro
    st.markdown('<div class="player-header">', unsafe_allow_html=True)

    # Layout principal: 3 colunas (foto | info | stats)
    col_foto, col_info, col_stats = st.columns([1, 2, 1])

    with col_foto:
        # Foto do jogador
        if foto_path:
            st.markdown(f'<img src="{foto_path}" class="player-photo" width="100%">', unsafe_allow_html=True)
        else:
            # Placeholder com inicial do nome
            inicial = jogador['nome'][0] if jogador.get('nome') else "?"
            st.markdown(f"""
            <div style='
                width: 100%;
                aspect-ratio: 3/4;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 120px;
                color: white;
                font-weight: 900;
                box-shadow: 0 12px 40px rgba(0,0,0,0.6);
                border: 4px solid rgba(255,255,255,0.1);
            '>
                {inicial}
            </div>
            """, unsafe_allow_html=True)

    with col_info:
        # Nome do jogador
        st.markdown(f"<div class='player-name'>{jogador.get('nome', 'Jogador')}</div>", unsafe_allow_html=True)

        # Posição
        posicao = jogador.get('posicao', 'N/A')
        st.markdown(f"<div class='player-position'>🎯 {posicao}</div>", unsafe_allow_html=True)

        # Informações do clube com logos do Transfermarkt
        clube = jogador.get('clube', '')
        liga = jogador.get('liga_clube', '')
        transfermarkt_id = jogador.get('transfermarkt_id', None)

        if clube or liga:
            club_html = "<div class='club-info'>"

            # Logo do clube (Transfermarkt)
            if clube:
                logo_clube = get_logo_clube_transfermarkt(clube, transfermarkt_id)
                if logo_clube:
                    club_html += f'''<img src="{logo_clube}"
                        width="40" height="40"
                        style="object-fit: contain; margin-right: 12px; background: white; padding: 4px; border-radius: 50%;"
                        onerror="this.style.display='none'">'''
                else:
                    # Fallback para emoji
                    club_html += f'<span style="font-size: 32px; margin-right: 12px;">⚽</span>'

                club_html += f"<span class='club-name'>{clube}</span>"

            # Logo da liga (Transfermarkt)
            if liga:
                logo_liga = get_logo_liga_transfermarkt(liga)
                if logo_liga:
                    club_html += f'''<img src="{logo_liga}"
                        width="32" height="32"
                        style="object-fit: contain; margin-left: auto; margin-right: 8px; background: white; padding: 2px; border-radius: 4px;"
                        onerror="this.style.display='none'">'''
                else:
                    # Fallback para emoji
                    liga_emoji = "🏆" if "Série A" in liga or "Serie A" in liga else "🏅"
                    club_html += f'<span style="font-size: 24px; margin-left: auto; margin-right: 8px;">{liga_emoji}</span>'

                club_html += f"<span class='league-badge'>{liga}</span>"

            club_html += "</div>"
            st.markdown(club_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Chips de informação
        info_chips = []

        # Nacionalidade com bandeira
        if pd.notna(jogador.get('nacionalidade')):
            bandeira = get_bandeira_pais(jogador['nacionalidade'])
            info_chips.append(f"<span class='info-chip'>{bandeira} <span class='info-chip-label'>Nacionalidade:</span><span class='info-chip-value'>{jogador['nacionalidade']}</span></span>")

        # Idade
        if pd.notna(jogador.get('idade_atual')):
            info_chips.append(f"<span class='info-chip'>🎂 <span class='info-chip-label'>Idade:</span><span class='info-chip-value'>{int(jogador['idade_atual'])} anos</span></span>")

        # Altura
        if pd.notna(jogador.get('altura')):
            info_chips.append(f"<span class='info-chip'>📏 <span class='info-chip-label'>Altura:</span><span class='info-chip-value'>{int(jogador['altura'])} cm</span></span>")

        # Pé dominante
        if pd.notna(jogador.get('pe_dominante')):
            pe_emoji = "🦶" if jogador['pe_dominante'] == 'Destro' else "🦿"
            info_chips.append(f"<span class='info-chip'>{pe_emoji} <span class='info-chip-label'>Pé:</span><span class='info-chip-value'>{jogador['pe_dominante']}</span></span>")

        # Contrato
        if pd.notna(jogador.get('data_fim_contrato')):
            data_contrato = pd.to_datetime(jogador['data_fim_contrato']).strftime('%d/%m/%Y')
            info_chips.append(f"<span class='info-chip'>📄 <span class='info-chip-label'>Contrato até:</span><span class='info-chip-value'>{data_contrato}</span></span>")

        if info_chips:
            st.markdown("<div>" + "".join(info_chips) + "</div>", unsafe_allow_html=True)
        else:
            # Aviso se não houver dados preenchidos
            st.markdown("""
            <div style='
                background: rgba(251, 191, 36, 0.1);
                border-left: 4px solid #f59e0b;
                padding: 12px 16px;
                border-radius: 8px;
                margin-top: 12px;
            '>
                <span style='color: #fbbf24; font-size: 13px;'>
                    ℹ️ Complete o perfil do jogador para ver mais informações (idade, altura, nacionalidade, etc.)
                </span>
            </div>
            """, unsafe_allow_html=True)

    with col_stats:
        st.markdown("<br>", unsafe_allow_html=True)
        # Cards de estatísticas rápidas (serão preenchidos depois)
        pass

    # Fechar container do header
    st.markdown('</div>', unsafe_allow_html=True)


def criar_secao_stats_rapidas(stats: Dict) -> None:
    """
    Cria seção de estatísticas rápidas em cards modernos

    Args:
        stats: Dicionário com estatísticas {label: {value, subtitle}}
    """

    cols = st.columns(len(stats))

    for col, (label, data) in zip(cols, stats.items()):
        with col:
            st.markdown(f"""
            <div class='stat-card-pro'>
                <div class='stat-label-pro'>{label}</div>
                <div class='stat-value-pro'>{data['value']}</div>
                <div class='stat-subtitle-pro'>{data.get('subtitle', '')}</div>
            </div>
            """, unsafe_allow_html=True)


def criar_cards_categorias(categorias: Dict) -> None:
    """
    Cria cards de categorias com ícones (Avaliações, Estatísticas, etc)

    Args:
        categorias: {nome: {icone, valor, descricao}}
    """

    st.markdown("""
    <style>
    .category-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 2px solid rgba(59, 130, 246, 0.2);
        cursor: pointer;
        transition: all 0.3s ease;
        height: 100%;
    }

    .category-card:hover {
        transform: translateY(-8px);
        border-color: rgba(59, 130, 246, 0.6);
        box-shadow: 0 12px 32px rgba(59, 130, 246, 0.3);
    }

    .category-icon {
        font-size: 48px;
        margin-bottom: 12px;
    }

    .category-title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    .category-value {
        font-size: 28px;
        font-weight: 900;
        color: #3b82f6;
        margin-bottom: 4px;
    }

    .category-desc {
        font-size: 12px;
        color: #94a3b8;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(categorias))

    for col, (nome, data) in zip(cols, categorias.items()):
        with col:
            st.markdown(f"""
            <div class='category-card'>
                <div class='category-icon'>{data['icone']}</div>
                <div class='category-title'>{nome}</div>
                <div class='category-value'>{data['valor']}</div>
                <div class='category-desc'>{data.get('descricao', '')}</div>
            </div>
            """, unsafe_allow_html=True)


def criar_badge_status(status: str, tipo: str = "success") -> str:
    """
    Cria badge HTML de status

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
        "info": "#3b82f6"
    }

    cor = cores.get(tipo, cores["info"])

    return f"""
    <span style='
        background: {cor}20;
        color: {cor};
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 1px solid {cor}40;
    '>
        {status}
    </span>
    """
