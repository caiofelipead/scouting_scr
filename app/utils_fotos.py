"""
Obter URL de Fotos do Transfermarkt - Versão Streamlit
Retorna a URL da foto sem baixar (carregamento direto na web)
"""

import re
import requests
from bs4 import BeautifulSoup
import streamlit as st


def extrair_id_da_url(tm_value):
    """
    Extrai o ID numérico do Transfermarkt de uma URL ou string
    
    Exemplos:
    - https://www.transfermarkt.com.br/adriano/profil/spieler/1046580 -> 1046580
    - 1046580 -> 1046580
    """
    if not tm_value or str(tm_value).strip() == "":
        return None
    
    tm_str = str(tm_value).strip()
    
    # Tentar extrair ID numérico da URL
    match = re.search(r"/spieler/(\d+)", tm_str)
    if match:
        return match.group(1)
    
    # Se não encontrar na URL, verificar se já é um ID numérico
    if tm_str.isdigit():
        return tm_str
    
    return None


@st.cache_data(ttl=86400)  # Cache por 24 horas
def extrair_url_foto_transfermarkt(tm_id, usar_scraping=True):
    """
    Extrai a URL da foto do Transfermarkt com scraping melhorado

    Args:
        tm_id: ID numérico do Transfermarkt
        usar_scraping: Se True (PADRÃO), faz scraping para pegar URL real
                       Se False, retorna URL padrão (pode não funcionar)

    Returns:
        URL da foto ou None
    """
    if not tm_id:
        return None

    # MÉTODO 1: SCRAPING (RECOMENDADO - pega URL real com timestamp)
    if usar_scraping:
        url_pagina = f"https://www.transfermarkt.com.br/player/profil/spieler/{tm_id}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    }

        try:
            response = requests.get(url_pagina, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # PRIORIDADE 1: Buscar img com class="data-header__profile-image"
                profile_img = soup.find("img", {"class": re.compile(r"data-header__profile-image")})
                if profile_img:
                    src = profile_img.get("src") or profile_img.get("data-src")
                    if src and "portrait" in src:
                        # Pegar URL completa com timestamp
                        url_completa = src if src.startswith("http") else f"https:{src}"
                        return url_completa

                # PRIORIDADE 2: Buscar qualquer img com portrait/big no src
                for img in soup.find_all("img"):
                    src = img.get("src", "") or img.get("data-src", "")
                    if "portrait/big" in src and tm_id in src:
                        url_completa = src if src.startswith("http") else f"https:{src}"
                        return url_completa

                # PRIORIDADE 3: Buscar em qualquer img com portrait
                for img in soup.find_all("img"):
                    src = img.get("src", "") or img.get("data-src", "")
                    if "portrait" in src and ".jpg" in src:
                        url_completa = src if src.startswith("http") else f"https:{src}"
                        return url_completa

        except requests.Timeout:
            # Timeout: tentar URL padrão como fallback
            pass
        except Exception:
            # Qualquer outro erro: tentar URL padrão
            pass

    # MÉTODO 2: URL Padrão (FALLBACK)
    # Tenta várias variações de URL padrão
    urls_tentar = [
        f"https://img.a.transfermarkt.technology/portrait/big/{tm_id}.jpg?lm=1",
        f"https://img.a.transfermarkt.technology/portrait/medium/{tm_id}.jpg?lm=1",
        f"https://tmssl.akamaized.net/images/portrait/big/{tm_id}.jpg?lm=1"
    ]

    # Retorna primeira URL (browser tentará carregar)
    return urls_tentar[0]


def get_foto_jogador(id_jogador, transfermarkt_id=None, nome_jogador="Jogador", debug=False):
    """
    Retorna a URL da foto do jogador

    ESTRATÉGIA MELHORADA:
    1. Transfermarkt (Scraping com cache - pega URL real)
    2. Transfermarkt (URL padrão - fallback rápido)
    3. Placeholder UI Avatars (último recurso)

    Args:
        id_jogador: ID do banco de dados
        transfermarkt_id: ID ou URL do Transfermarkt
        nome_jogador: Nome para o placeholder
        debug: Mostra informações de debug

    Returns:
        URL da foto (string) - SEMPRE retorna uma URL válida
    """

    # 1️⃣ TRANSFERMARKT (com scraping)
    if transfermarkt_id:
        tm_id = extrair_id_da_url(transfermarkt_id)

        if tm_id:
            if debug:
                st.sidebar.write(f"🔍 **Buscando foto do Transfermarkt**")
                st.sidebar.write(f"   ID: `{tm_id}`")

            # Tentar scraping primeiro (mais confiável, pega URL com timestamp)
            url_foto = extrair_url_foto_transfermarkt(tm_id, usar_scraping=True)

            if url_foto:
                if debug:
                    st.sidebar.success(f"✅ Foto encontrada!")
                    st.sidebar.code(url_foto)
                return url_foto

    # 2️⃣ PLACEHOLDER (Sempre disponível)
    if debug and transfermarkt_id:
        st.sidebar.warning(f"⚠️ Usando placeholder")

    # Placeholder com inicial do nome
    nome_limpo = nome_jogador.replace(" ", "+")
    placeholder_url = f"https://ui-avatars.com/api/?name={nome_limpo}&size=300&background=6366f1&color=fff&bold=true&font-size=0.4"

    return placeholder_url


# ========== FUNÇÕES AUXILIARES PARA O DASHBOARD ==========

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


@st.cache_data(ttl=86400)  # Cache por 24 horas
def get_foto_jogador_rapido(transfermarkt_id, nome="?"):
    """
    Versão ultra-rápida: retorna URL do Transfermarkt sem scraping
    Use quando performance é crítica (listas com muitos jogadores)

    Args:
        transfermarkt_id: ID ou URL do Transfermarkt
        nome: Nome do jogador para placeholder

    Returns:
        URL da foto
    """
    if not transfermarkt_id:
        nome_limpo = nome.replace(" ", "+")
        return f"https://ui-avatars.com/api/?name={nome_limpo}&size=200&background=6366f1&color=fff&bold=true"

    tm_id = extrair_id_da_url(transfermarkt_id)

    if tm_id:
        # URL padrão (rápido, mas pode não funcionar para todos)
        return f"https://img.a.transfermarkt.technology/portrait/big/{tm_id}.jpg?lm=1"

    # Fallback placeholder
    nome_limpo = nome.replace(" ", "+")
    return f"https://ui-avatars.com/api/?name={nome_limpo}&size=200&background=6366f1&color=fff&bold=true"
