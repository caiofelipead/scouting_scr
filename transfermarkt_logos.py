"""
Módulo para buscar logos do Transfermarkt
==========================================
Extrai logos de clubes e ligas do HTML do Transfermarkt

Autor: Scout Pro
Data: 2025-12-09
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Tuple
import streamlit as st


@st.cache_data(ttl=86400)  # Cache de 24 horas
def buscar_logos_transfermarkt(jogador_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Busca logos do clube e liga direto do Transfermarkt

    Args:
        jogador_id: ID do jogador no Transfermarkt

    Returns:
        Tupla (logo_clube_url, logo_liga_url)
    """
    if not jogador_id:
        return None, None

    try:
        # URL do Transfermarkt
        url = f"https://www.transfermarkt.com.br/player/profil/spieler/{jogador_id}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None, None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar logo do clube
        logo_clube = None
        clube_img = soup.select_one('img.dataBild')
        if clube_img and clube_img.get('src'):
            logo_clube = clube_img['src']
            # Converter para URL absoluta se necessário
            if logo_clube.startswith('//'):
                logo_clube = 'https:' + logo_clube

        # Buscar logo da liga
        logo_liga = None
        # Liga geralmente está em um img dentro de um link específico
        liga_elements = soup.select('a[href*="/wettbewerb/"] img')
        if liga_elements:
            logo_liga = liga_elements[0].get('src')
            if logo_liga and logo_liga.startswith('//'):
                logo_liga = 'https:' + logo_liga

        return logo_clube, logo_liga

    except Exception as e:
        print(f"Erro ao buscar logos do Transfermarkt: {e}")
        return None, None


# Mapeamento manual de logos (fallback)
LOGOS_TRANSFERMARKT = {
    "Santos": {
        "clube": "https://tmssl.akamaized.net/images/wappen/head/221.png",
        "liga": "https://tmssl.akamaized.net/images/logo/header/bra1.png"
    },
    "Flamengo": {
        "clube": "https://tmssl.akamaized.net/images/wappen/head/614.png",
        "liga": "https://tmssl.akamaized.net/images/logo/header/bra1.png"
    },
    "Palmeiras": {
        "clube": "https://tmssl.akamaized.net/images/wappen/head/3622.png",
        "liga": "https://tmssl.akamaized.net/images/logo/header/bra1.png"
    },
    "São Paulo": {
        "clube": "https://tmssl.akamaized.net/images/wappen/head/585.png",
        "liga": "https://tmssl.akamaized.net/images/logo/header/bra1.png"
    },
    "Corinthians": {
        "clube": "https://tmssl.akamaized.net/images/wappen/head/199.png",
        "liga": "https://tmssl.akamaized.net/images/logo/header/bra1.png"
    },
    "Grêmio": {
        "clube": "https://tmssl.akamaized.net/images/wappen/head/210.png",
        "liga": "https://tmssl.akamaized.net/images/logo/header/bra1.png"
    },
    "Internacional": {
        "clube": "https://tmssl.akamaized.net/images/wappen/head/2035.png",
        "liga": "https://tmssl.akamaized.net/images/logo/header/bra1.png"
    },
    "Atlético-MG": {
        "clube": "https://tmssl.akamaized.net/images/wappen/head/330.png",
        "liga": "https://tmssl.akamaized.net/images/logo/header/bra1.png"
    },
    "Vasco": {
        "clube": "https://tmssl.akamaized.net/images/wappen/head/2432.png",
        "liga": "https://tmssl.akamaized.net/images/logo/header/bra1.png"
    },
    "Botafogo": {
        "clube": "https://tmssl.akamaized.net/images/wappen/head/537.png",
        "liga": "https://tmssl.akamaized.net/images/logo/header/bra1.png"
    }
}


def get_logo_clube_transfermarkt(clube: str, transfermarkt_id: Optional[str] = None) -> Optional[str]:
    """
    Retorna URL do logo do clube do Transfermarkt

    Args:
        clube: Nome do clube
        transfermarkt_id: ID do jogador no Transfermarkt (opcional)

    Returns:
        URL do logo ou None
    """
    # Tenta buscar do Transfermarkt primeiro
    if transfermarkt_id:
        logo_clube, _ = buscar_logos_transfermarkt(transfermarkt_id)
        if logo_clube:
            return logo_clube

    # Fallback para mapeamento manual
    if clube in LOGOS_TRANSFERMARKT:
        return LOGOS_TRANSFERMARKT[clube]["clube"]

    return None


def get_logo_liga_transfermarkt(liga: str = "Brasileirão Série A") -> Optional[str]:
    """
    Retorna URL do logo da liga do Transfermarkt

    Args:
        liga: Nome da liga

    Returns:
        URL do logo ou None
    """
    # URL padrão da Série A
    if "Série A" in liga or "Serie A" in liga or "Brasileirão" in liga:
        return "https://tmssl.akamaized.net/images/logo/header/bra1.png"

    return None
