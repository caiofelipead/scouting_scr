"""
Perfil Visual Ultra Simples - Apenas Funcionalidade
===================================================
Header minimalista estilo Transfermarkt - sem CSS complexo

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
    Header ultra simples - prioridade: funcionalidade e legibilidade

    Args:
        jogador: Série do pandas com dados do jogador
        foto_path: URL para a foto do jogador
    """

    # Container com fundo roxo simples
    st.markdown("""
        <div style="background-color: #6366f1; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    """, unsafe_allow_html=True)

    # Layout simples: foto | informações
    col1, col2 = st.columns([1, 3])

    with col1:
        # Foto - método mais simples possível
        if foto_path:
            st.image(foto_path, use_container_width=True)
        else:
            # Placeholder básico
            inicial = jogador.get('nome', '?')[0]
            st.markdown(f"""
                <div style="background: #4f46e5; border-radius: 8px; padding: 40px; text-align: center;">
                    <span style="font-size: 48px; color: white; font-weight: bold;">{inicial}</span>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        # Nome grande e branco
        nome = jogador.get('nome', 'Jogador')
        st.markdown(f"""
            <h1 style="color: white; margin: 0; font-size: 32px; font-weight: bold;">{nome}</h1>
        """, unsafe_allow_html=True)

        # Posição
        posicao = jogador.get('posicao', 'N/A')
        st.markdown(f"""
            <p style="color: #e0e7ff; margin: 5px 0 15px 0; font-size: 14px; font-weight: 600;">⚽ {posicao}</p>
        """, unsafe_allow_html=True)

        # Informações básicas
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
            info_text = " • ".join(info_parts)
            st.markdown(f"""
                <p style="color: white; font-size: 14px; margin: 10px 0;">{info_text}</p>
            """, unsafe_allow_html=True)

        # Clube e liga
        clube_parts = []
        if pd.notna(jogador.get('clube')) and jogador.get('clube'):
            clube_parts.append(f"⚽ {jogador['clube']}")
        if pd.notna(jogador.get('liga_clube')) and jogador.get('liga_clube'):
            clube_parts.append(f"🏆 {jogador['liga_clube']}")

        if clube_parts:
            clube_text = " • ".join(clube_parts)
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.15); padding: 10px; border-radius: 6px; margin-top: 10px;">
                    <p style="color: white; font-size: 14px; margin: 0;">{clube_text}</p>
                </div>
            """, unsafe_allow_html=True)

    # Fechar container
    st.markdown("</div>", unsafe_allow_html=True)


def criar_secao_stats_rapidas(stats: Dict) -> None:
    """
    Estatísticas em colunas - versão ultra simples

    Args:
        stats: Dicionário com estatísticas {label: {value, subtitle}}
    """

    cols = st.columns(len(stats))

    for col, (label, data) in zip(cols, stats.items()):
        with col:
            st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; text-align: center;">
                <p style="font-size: 11px; color: #64748b; font-weight: 600; margin: 0 0 8px 0; text-transform: uppercase;">{label}</p>
                <p style="font-size: 28px; font-weight: 700; color: #1e293b; margin: 0;">{data['value']}</p>
                <p style="font-size: 11px; color: #94a3b8; margin: 4px 0 0 0;">{data.get('subtitle', '')}</p>
            </div>
            """, unsafe_allow_html=True)


def criar_cards_categorias(categorias: Dict) -> None:
    """
    Cards de categorias - versão ultra simples

    Args:
        categorias: {nome: {icone, valor, descricao}}
    """

    cols = st.columns(len(categorias))

    for col, (nome, data) in zip(cols, categorias.items()):
        with col:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; text-align: center;">
                <p style="font-size: 32px; margin: 0 0 8px 0;">{data['icone']}</p>
                <p style="font-size: 13px; font-weight: 600; color: #475569; margin: 0 0 8px 0; text-transform: uppercase;">{nome}</p>
                <p style="font-size: 24px; font-weight: 700; color: #6366f1; margin: 0;">{data['valor']}</p>
                <p style="font-size: 11px; color: #94a3b8; margin: 4px 0 0 0;">{data.get('descricao', '')}</p>
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
