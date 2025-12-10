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
def extrair_url_foto_transfermarkt(tm_id, usar_scraping=False):
    """
    Extrai a URL da foto do Transfermarkt

    Args:
        tm_id: ID numérico do Transfermarkt
        usar_scraping: Se True, faz scraping da página (mais lento mas confiável)
                       Se False, usa URL padrão (rápido e confiável)

    Returns:
        URL da foto ou None
    """
    if not tm_id:
        return None

    # MÉTODO 1: URLs Padrão (RÁPIDO E CONFIÁVEL)
    # Simplesmente retorna a URL padrão sem validação
    # O navegador irá carregar a imagem ou mostrar erro
    if not usar_scraping:
        # URL primária do CDN do Transfermarkt
        url_principal = f"https://img.a.transfermarkt.technology/portrait/big/{tm_id}.jpg"
        return url_principal

    # MÉTODO 2: Scraping (CONFIÁVEL mas mais lento)
    # Apenas use se explicitamente solicitado
    if usar_scraping:
        url_pagina = f"https://www.transfermarkt.com.br/player/profil/spieler/{tm_id}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        try:
            response = requests.get(url_pagina, headers=headers, timeout=15, allow_redirects=True)

            if response.status_code != 200:
                st.warning(f"⚠️ Transfermarkt retornou status {response.status_code}")
                return None

            soup = BeautifulSoup(response.content, "html.parser")

            # Procurar pela tag img com a foto
            # Método 1: Buscar no modal da foto
            modal_img = soup.find("img", {"src": re.compile(r"portrait/(big|medium)/.*\.jpg")})
            if modal_img and modal_img.get("src"):
                url_foto = modal_img["src"].split("?")[0]
                return url_foto

            # Método 2: Buscar em data-src
            modal_img = soup.find("img", {"data-src": re.compile(r"portrait/(big|medium)/.*\.jpg")})
            if modal_img and modal_img.get("data-src"):
                url_foto = modal_img["data-src"].split("?")[0]
                return url_foto

            # Método 3: Buscar qualquer img com portrait
            for img in soup.find_all("img"):
                src = img.get("src", "") or img.get("data-src", "")
                if "portrait" in src and ".jpg" in src:
                    url_foto = src.split("?")[0]
                    return url_foto

            st.warning(f"⚠️ Foto não encontrada no HTML do Transfermarkt")

        except Exception as e:
            st.error(f"❌ Erro ao buscar foto do Transfermarkt: {e}")
            return None

    return None


def get_foto_jogador(id_jogador, transfermarkt_id=None, nome_jogador="Jogador", debug=False):
    """
    Retorna a URL da foto do jogador
    
    PRIORIDADE:
    1. Transfermarkt (URL padrão - rápido)
    2. Transfermarkt (Scraping - confiável)
    3. Placeholder (fallback)
    
    Args:
        id_jogador: ID do banco de dados
        transfermarkt_id: ID ou URL do Transfermarkt
        nome_jogador: Nome para o placeholder
        debug: Mostra informações de debug
    
    Returns:
        URL da foto (string)
    """
    
    # 1️⃣ TRANSFERMARKT
    if transfermarkt_id:
        tm_id = extrair_id_da_url(transfermarkt_id)
        
        if tm_id:
            if debug:
                st.sidebar.write(f"🔍 **Buscando foto**")
                st.sidebar.write(f"   ID TM: `{tm_id}`")
            
            # Tentar URL padrão primeiro (rápido)
            url_foto = extrair_url_foto_transfermarkt(tm_id, usar_scraping=False)
            
            if url_foto:
                if debug:
                    st.sidebar.success(f"✅ Foto encontrada (URL padrão)")
                    st.sidebar.code(url_foto)
                return url_foto
            
            # Se falhar, tentar scraping (cache evita repetir)
            url_foto = extrair_url_foto_transfermarkt(tm_id, usar_scraping=True)
            
            if url_foto:
                if debug:
                    st.sidebar.success(f"✅ Foto encontrada (scraping)")
                    st.sidebar.code(url_foto)
                return url_foto
    
    # 2️⃣ PLACEHOLDER (Fallback)
    if debug:
        st.sidebar.warning(f"⚠️ Foto não encontrada")
    
    # Placeholder com nome do jogador
    nome_limpo = nome_jogador.replace(" ", "+")
    placeholder_url = f"https://ui-avatars.com/api/?name={nome_limpo}&size=200&background=0D47A1&color=fff&bold=true&font-size=0.4"
    
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
def get_foto_jogador_rapido(transfermarkt_id):
    """
    Versão ultra-rápida: retorna URL direta do Transfermarkt
    Use quando performance é crítica (lista com muitos jogadores)
    """
    if not transfermarkt_id:
        return "https://ui-avatars.com/api/?name=?&size=200&background=764ba2&color=fff&bold=true"

    tm_id = extrair_id_da_url(transfermarkt_id)

    if tm_id:
        # Retorna URL principal do CDN do Transfermarkt
        # O navegador irá carregar a imagem diretamente
        return f"https://img.a.transfermarkt.technology/portrait/big/{tm_id}.jpg"

    return "https://ui-avatars.com/api/?name=?&size=200&background=764ba2&color=fff&bold=true"
