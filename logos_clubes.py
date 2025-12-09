"""
Módulo de Logos de Clubes e Ligas
==================================
Busca logos de clubes e ligas via APIs públicas

Autor: Scout Pro
Data: 2025-12-09
"""

import requests
from typing import Optional
import streamlit as st


# ========================================
# MAPEAMENTO DE LOGOS - PRINCIPAIS LIGAS
# ========================================

LOGOS_LIGAS = {
    # Brasil
    "Brasileirão Série A": "https://upload.wikimedia.org/wikipedia/pt/7/70/Brasileir%C3%A3o_logo_2024.png",
    "Brasileirão Série B": "https://upload.wikimedia.org/wikipedia/pt/7/70/Brasileir%C3%A3o_logo_2024.png",
    "Brasileirão": "https://upload.wikimedia.org/wikipedia/pt/7/70/Brasileir%C3%A3o_logo_2024.png",
    "Serie A": "https://upload.wikimedia.org/wikipedia/pt/7/70/Brasileir%C3%A3o_logo_2024.png",

    # Europa - Top 5
    "Premier League": "https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg",
    "La Liga": "https://upload.wikimedia.org/wikipedia/commons/1/13/LaLiga_EA_Sports_2023_Vertical_Logo.svg",
    "Serie A (ITA)": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Serie_A_logo_2022.svg/200px-Serie_A_logo_2022.svg.png",
    "Bundesliga": "https://upload.wikimedia.org/wikipedia/en/d/df/Bundesliga_logo_%282017%29.svg",
    "Ligue 1": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Ligue_1_Uber_Eats.svg/200px-Ligue_1_Uber_Eats.svg.png",

    # Portugal
    "Primeira Liga": "https://upload.wikimedia.org/wikipedia/pt/thumb/e/e8/Liga_Portugal_Betclic_logo.svg/200px-Liga_Portugal_Betclic_logo.svg.png",

    # Argentina
    "Liga Profesional": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Logo_de_Liga_Profesional_de_F%C3%BAtbol_%28Argentina%29.svg/200px-Logo_de_Liga_Profesional_de_F%C3%BAtbol_%28Argentina%29.svg.png",

    # MLS
    "MLS": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/MLS_crest_logo_RGB_gradient.svg/200px-MLS_crest_logo_RGB_gradient.svg.png",
}


# ========================================
# LOGOS DE CLUBES PRINCIPAIS
# ========================================

LOGOS_CLUBES = {
    # Brasil - Série A
    "Flamengo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Flamengo-RJ_%28BRA%29.png/150px-Flamengo-RJ_%28BRA%29.png",
    "Palmeiras": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Palmeiras_logo.svg/150px-Palmeiras_logo.svg.png",
    "Corinthians": "https://upload.wikimedia.org/wikipedia/pt/thumb/5/5a/Sport_Club_Corinthians_Paulista_crest.svg/150px-Sport_Club_Corinthians_Paulista_crest.svg.png",
    "São Paulo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Brasao_do_Sao_Paulo_Futebol_Clube.svg/150px-Brasao_do_Sao_Paulo_Futebol_Clube.svg.png",
    "Grêmio": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Gremio.svg/150px-Gremio.svg.png",
    "Internacional": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Escudo_do_Sport_Club_Internacional.svg/150px-Escudo_do_Sport_Club_Internacional.svg.png",
    "Atlético-MG": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Atletico_mineiro_galo.png/150px-Atletico_mineiro_galo.png",
    "Cruzeiro": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Cruzeiro_Esporte_Clube_%28logo%29.svg/150px-Cruzeiro_Esporte_Clube_%28logo%29.svg.png",
    "Botafogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Botafogo_de_Futebol_e_Regatas_logo.svg/150px-Botafogo_de_Futebol_e_Regatas_logo.svg.png",
    "Vasco": "https://upload.wikimedia.org/wikipedia/pt/thumb/a/ac/CRVascodaGama.svg/150px-CRVascodaGama.svg.png",
    "Fluminense": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Fluminense_FC_escudo.svg/150px-Fluminense_FC_escudo.svg.png",
    "Santos": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Santos_Logo.png/150px-Santos_Logo.png",
    "Athletico-PR": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Club_Athletico_Paranaense_bras%C3%A3o.png/150px-Club_Athletico_Paranaense_bras%C3%A3o.png",
    "Bahia": "https://upload.wikimedia.org/wikipedia/pt/thumb/5/54/Esporte_Clube_Bahia_2019.png/150px-Esporte_Clube_Bahia_2019.png",
    "Fortaleza": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/FortalezaEsporteClube.svg/150px-FortalezaEsporteClube.svg.png",
    "Sport Recife": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Sport_Club_do_Recife_%28escudo%29.svg/150px-Sport_Club_do_Recife_%28escudo%29.svg.png",

    # Europa - Inglaterra
    "Manchester City": "https://upload.wikimedia.org/wikipedia/pt/0/02/Manchester_City_Football_Club.png",
    "Liverpool": "https://upload.wikimedia.org/wikipedia/pt/9/9f/Liverpool_Football_Club.png",
    "Arsenal": "https://upload.wikimedia.org/wikipedia/pt/6/63/Arsenal_FC.png",
    "Chelsea": "https://upload.wikimedia.org/wikipedia/pt/c/cc/Chelsea_FC.svg",
    "Manchester United": "https://upload.wikimedia.org/wikipedia/pt/4/43/Manchester_United_Football_Club.png",
    "Tottenham": "https://upload.wikimedia.org/wikipedia/pt/b/b4/Tottenham_Hotspur.svg",

    # Europa - Espanha
    "Real Madrid": "https://upload.wikimedia.org/wikipedia/pt/9/98/Real_Madrid.png",
    "Barcelona": "https://upload.wikimedia.org/wikipedia/pt/4/43/FCBarcelona.svg",
    "Atlético Madrid": "https://upload.wikimedia.org/wikipedia/pt/e/e2/Atletico_Madrid.svg",

    # Europa - Itália
    "Inter Milan": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/FC_Internazionale_Milano_2021.svg/150px-FC_Internazionale_Milano_2021.svg.png",
    "AC Milan": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Logo_of_AC_Milan.svg/150px-Logo_of_AC_Milan.svg.png",
    "Juventus": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Juventus_FC_2017_logo.svg/150px-Juventus_FC_2017_logo.svg.png",

    # Europa - Alemanha
    "Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg/150px-FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg.png",
    "Borussia Dortmund": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Borussia_Dortmund_logo.svg/150px-Borussia_Dortmund_logo.svg.png",

    # Europa - França
    "PSG": "https://upload.wikimedia.org/wikipedia/pt/8/86/Paris_Saint-Germain_Logo.svg",

    # Portugal
    "Benfica": "https://upload.wikimedia.org/wikipedia/pt/4/43/S.L._Benfica_logo.svg",
    "Porto": "https://upload.wikimedia.org/wikipedia/pt/f/f1/FC_Porto.svg",
    "Sporting": "https://upload.wikimedia.org/wikipedia/pt/8/8b/Sporting_Clube_de_Portugal.svg",

    # Argentina
    "Boca Juniors": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/CABJ70.png/150px-CABJ70.png",
    "River Plate": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Escudo_del_C_A_River_Plate.svg/150px-Escudo_del_C_A_River_Plate.svg.png",
}


# ========================================
# BANDEIRAS DE PAÍSES
# ========================================

BANDEIRAS_PAISES = {
    "Brasil": "🇧🇷",
    "Argentina": "🇦🇷",
    "Uruguai": "🇺🇾",
    "Colômbia": "🇨🇴",
    "Chile": "🇨🇱",
    "Peru": "🇵🇪",
    "Venezuela": "🇻🇪",
    "Equador": "🇪🇨",
    "Paraguai": "🇵🇾",
    "Bolívia": "🇧🇴",

    "Portugal": "🇵🇹",
    "Espanha": "🇪🇸",
    "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "França": "🇫🇷",
    "Itália": "🇮🇹",
    "Alemanha": "🇩🇪",
    "Holanda": "🇳🇱",
    "Bélgica": "🇧🇪",
    "Croácia": "🇭🇷",
    "Sérvia": "🇷🇸",
    "Suíça": "🇨🇭",
    "Áustria": "🇦🇹",
    "Polônia": "🇵🇱",
    "República Tcheca": "🇨🇿",

    "EUA": "🇺🇸",
    "Estados Unidos": "🇺🇸",
    "México": "🇲🇽",
    "Canadá": "🇨🇦",

    "Japão": "🇯🇵",
    "Coreia do Sul": "🇰🇷",
    "Austrália": "🇦🇺",

    "Senegal": "🇸🇳",
    "Nigéria": "🇳🇬",
    "Camarões": "🇨🇲",
    "Costa do Marfim": "🇨🇮",
    "Gana": "🇬🇭",
    "Marrocos": "🇲🇦",
    "Egito": "🇪🇬",
}


def get_logo_clube(nome_clube: str) -> Optional[str]:
    """
    Retorna URL da logo do clube

    Args:
        nome_clube: Nome do clube

    Returns:
        URL da logo ou None
    """
    if not nome_clube:
        return None

    # Busca exata
    if nome_clube in LOGOS_CLUBES:
        return LOGOS_CLUBES[nome_clube]

    # Busca parcial (case insensitive)
    nome_lower = nome_clube.lower()
    for clube, url in LOGOS_CLUBES.items():
        if clube.lower() in nome_lower or nome_lower in clube.lower():
            return url

    return None


def get_logo_liga(nome_liga: str) -> Optional[str]:
    """
    Retorna URL da logo da liga

    Args:
        nome_liga: Nome da liga

    Returns:
        URL da logo ou None
    """
    if not nome_liga:
        return None

    # Busca exata
    if nome_liga in LOGOS_LIGAS:
        return LOGOS_LIGAS[nome_liga]

    # Busca parcial
    nome_lower = nome_liga.lower()
    for liga, url in LOGOS_LIGAS.items():
        if liga.lower() in nome_lower or nome_lower in liga.lower():
            return url

    return None


def get_bandeira_pais(pais: str) -> str:
    """
    Retorna emoji da bandeira do país

    Args:
        pais: Nome do país

    Returns:
        Emoji da bandeira ou 🌐
    """
    if not pais:
        return "🌐"

    # Busca exata
    if pais in BANDEIRAS_PAISES:
        return BANDEIRAS_PAISES[pais]

    # Busca parcial
    pais_lower = pais.lower()
    for nome, flag in BANDEIRAS_PAISES.items():
        if nome.lower() in pais_lower or pais_lower in nome.lower():
            return flag

    return "🌐"


def renderizar_logo(url: str, width: int = 50, fallback_emoji: str = "⚽") -> None:
    """
    Renderiza logo no Streamlit com fallback para emoji

    Args:
        url: URL da imagem
        width: Largura em pixels
        fallback_emoji: Emoji para mostrar se falhar
    """
    if url:
        try:
            st.image(url, width=width)
        except:
            st.markdown(f"<div style='font-size: {width}px;'>{fallback_emoji}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size: {width}px;'>{fallback_emoji}</div>", unsafe_allow_html=True)
