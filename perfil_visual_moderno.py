"""
Perfil Visual Ultra Simples - Apenas Funcionalidade

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
    Header profissional com melhorias visuais e máxima legibilidade

    Args:
        jogador: Série do pandas com dados do jogador
        foto_path: URL para a foto do jogador
    """

    # Container principal com gradiente sutil
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
    """, unsafe_allow_html=True)

    # Layout: foto | informações
    col1, col2 = st.columns([1, 3])

    with col1:
        # Foto com border para destaque
        if foto_path:
            st.markdown(f"""
                <div style="border: 3px solid rgba(255,255,255,0.3); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                    <img src="{foto_path}" style="width: 100%; height: auto; display: block;" onerror="this.onerror=null; this.src='https://ui-avatars.com/api/?name={jogador.get('nome', '?')[0]}&size=300&background=4f46e5&color=fff&bold=true&font-size=0.4';">
                </div>
            """, unsafe_allow_html=True)
        else:
            # Placeholder estilizado
            inicial = jogador.get('nome', '?')[0]
            st.markdown(f"""
                <div style="
                    background: #4f46e5;
                    border: 3px solid rgba(255,255,255,0.3);
                    border-radius: 12px;
                    padding: 40px;
                    text-align: center;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                ">
                    <span style="font-size: 56px; color: white; font-weight: bold;">{inicial}</span>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        # Nome com sombra de texto para legibilidade
        nome = jogador.get('nome', 'Jogador')
        st.markdown(f"""
            <h1 style="
                color: #ffffff;
                margin: 0 0 8px 0;
                font-size: 36px;
                font-weight: 700;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
                line-height: 1.2;
            ">{nome}</h1>
        """, unsafe_allow_html=True)

        # Posição
        posicao = jogador.get('posicao', 'N/A')
        st.markdown(f"""
            <p style="
                color: #e0e7ff;
                margin: 0 0 16px 0;
                font-size: 14px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            ">⚽ {posicao}</p>
        """, unsafe_allow_html=True)

        # Informações básicas em badges
        info_parts = []

        if pd.notna(jogador.get('nacionalidade')):
            bandeira = get_bandeira_pais(jogador['nacionalidade'])
            info_parts.append(f"{bandeira} {jogador['nacionalidade']}")

        if pd.notna(jogador.get('idade_atual')):
            info_parts.append(f"🎂 {int(jogador['idade_atual'])} anos")

        if pd.notna(jogador.get('altura')):
            info_parts.append(f"📏 {int(jogador['altura'])} cm")

        if pd.notna(jogador.get('pe_dominante')):
            info_parts.append(f"🦶 {jogador['pe_dominante']}")

        if info_parts:
            badges_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">'
            for info in info_parts:
                badges_html += f'''
                    <span style="
                        background: rgba(255, 255, 255, 0.2);
                        color: white;
                        padding: 6px 12px;
                        border-radius: 6px;
                        font-size: 13px;
                        font-weight: 500;
                        white-space: nowrap;
                        backdrop-filter: blur(10px);
                    ">{info}</span>
                '''
            badges_html += '</div>'
            st.markdown(badges_html, unsafe_allow_html=True)

        # Clube e liga em card destacado
        clube_parts = []
        if pd.notna(jogador.get('clube')) and jogador.get('clube'):
            clube_parts.append(f"⚽ {jogador['clube']}")
        if pd.notna(jogador.get('liga_clube')) and jogador.get('liga_clube'):
            clube_parts.append(f"🏆 {jogador['liga_clube']}")

        if clube_parts:
            clube_text = " • ".join(clube_parts)
            st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.15);
                    padding: 12px;
                    border-radius: 8px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                ">
                    <p style="color: white; font-size: 14px; margin: 0; font-weight: 500;">{clube_text}</p>
                </div>
            """, unsafe_allow_html=True)

    # Fechar container
    st.markdown("</div>", unsafe_allow_html=True)


def criar_secao_stats_rapidas(stats: Dict) -> None:
    """
    Estatísticas em colunas com visual aprimorado

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
            <div style="
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                transition: all 0.2s ease;
            ">
                <p style="
                    font-size: 11px;
                    color: #64748b;
                    font-weight: 600;
                    margin: 0 0 8px 0;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">{label}</p>
                <p style="
                    font-size: 32px;
                    font-weight: 700;
                    color: #6366f1;
                    margin: 0;
                    line-height: 1;
                ">{data['value']}</p>
                <p style="
                    font-size: 11px;
                    color: #94a3b8;
                    margin: 4px 0 0 0;
                ">{data.get('subtitle', '')}</p>
            </div>
            """, unsafe_allow_html=True)


def criar_cards_categorias(categorias: Dict) -> None:
    """
    Cards de categorias com hover e visual aprimorado

    Args:
        categorias: {nome: {icone, valor, descricao}}
    """

    cols = st.columns(len(categorias))

    for col, (nome, data) in zip(cols, categorias.items()):
        with col:
            st.markdown(f"""
            <div style="
                background: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 24px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                transition: all 0.2s ease;
            ">
                <p style="
                    font-size: 36px;
                    margin: 0 0 12px 0;
                ">{data['icone']}</p>
                <p style="
                    font-size: 13px;
                    font-weight: 600;
                    color: #475569;
                    margin: 0 0 8px 0;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">{nome}</p>
                <p style="
                    font-size: 28px;
                    font-weight: 700;
                    color: #6366f1;
                    margin: 0;
                    line-height: 1;
                ">{data['valor']}</p>
                <p style="
                    font-size: 11px;
                    color: #94a3b8;
                    margin: 8px 0 0 0;
                ">{data.get('descricao', '')}</p>
            </div>
            """, unsafe_allow_html=True)


def criar_badge_status(status: str, tipo: str = "success") -> str:
    """
    Badge HTML de status - versão ultra simples

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

    return f'<span style="background: {cor}15; color: {cor}; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; text-transform: uppercase;">{status}</span>'
