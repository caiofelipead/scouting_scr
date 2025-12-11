"""
Utilitário para buscar logos de clubes e ligas
Solução escalável com busca automática e fallbacks inteligentes
"""
import re
from urllib.parse import quote


def normalizar_nome(nome):
    """Normaliza nome removendo acentos e caracteres especiais"""
    if not nome:
        return ""

    # Remove acentos comuns
    mapa_acentos = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n'
    }

    nome_normalizado = nome.lower()
    for acento, sem_acento in mapa_acentos.items():
        nome_normalizado = nome_normalizado.replace(acento, sem_acento)

    return nome_normalizado


def gerar_url_wikimedia_clube(nome_clube):
    """Gera URL genérica para busca de logo de clube na Wikimedia"""
    # Estratégia: tentar padrões comuns de nomenclatura
    nome_limpo = nome_clube.strip()

    # Padrões de URL mais comuns
    tentativas = [
        # Formato: Nome_Clube_Logo.svg
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{nome_limpo.replace(' ', '_')}_Logo.svg/150px-{nome_limpo.replace(' ', '_')}_Logo.svg.png",
        # Formato: Nome_FC_Logo.svg
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{nome_limpo.replace(' ', '_')}_FC_Logo.svg/150px-{nome_limpo.replace(' ', '_')}_FC_Logo.svg.png",
        # Formato: Nome_Clube.svg
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{nome_limpo.replace(' ', '_')}.svg/150px-{nome_limpo.replace(' ', '_')}.svg.png",
    ]

    # Retorna primeira tentativa (frontend vai ter fallback se não carregar)
    return tentativas[0]


def get_logo_clube(nome_clube):
    """
    Retorna URL do logo do clube
    Usa mapeamento + busca inteligente

    Args:
        nome_clube: Nome do clube

    Returns:
        URL do logo ou None
    """
    if not nome_clube or nome_clube == "Livre":
        return None

    # Normaliza para busca
    nome_norm = normalizar_nome(nome_clube)

    # Mapeamento otimizado (apenas clubes principais)
    logos_principais = {
        # Brasil - Série A (Top 20)
        "flamengo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Flamengo-RJ_%28BRA%29.png/150px-Flamengo-RJ_%28BRA%29.png",
        "palmeiras": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Palmeiras_logo.svg/150px-Palmeiras_logo.svg.png",
        "sao paulo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Brasao_do_Sao_Paulo_Futebol_Clube.svg/150px-Brasao_do_Sao_Paulo_Futebol_Clube.svg.png",
        "corinthians": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Corinthians_FC_crest.svg/150px-Corinthians_FC_crest.svg.png",
        "atletico-mg": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Atletico_mineiro_galo.png/150px-Atletico_mineiro_galo.png",
        "gremio": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Gremio_FBPA.svg/150px-Gremio_FBPA.svg.png",
        "fluminense": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Fluminense_FC_escudo.svg/150px-Fluminense_FC_escudo.svg.png",
        "botafogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Botafogo_de_Futebol_e_Regatas_logo.svg/150px-Botafogo_de_Futebol_e_Regatas_logo.svg.png",
        "atletico-pr": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Athletico_Paranaense.svg/150px-Athletico_Paranaense.svg.png",
        "athletico": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Athletico_Paranaense.svg/150px-Athletico_Paranaense.svg.png",
        "internacional": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Escudo_do_Sport_Club_Internacional.svg/150px-Escudo_do_Sport_Club_Internacional.svg.png",
        "cruzeiro": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Cruzeiro_Esporte_Clube_%28logo%29.svg/150px-Cruzeiro_Esporte_Clube_%28logo%29.svg.png",
        "santos": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Santos_logo.svg/150px-Santos_logo.svg.png",
        "vasco": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/CRVascodaGama.svg/150px-CRVascodaGama.svg.png",
        "bahia": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/ECBahia.svg/150px-ECBahia.svg.png",
        "fortaleza": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/FortalezaEsporteClube.svg/150px-FortalezaEsporteClube.svg.png",
        "cuiaba": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Cuiaba_Esporte_Clube_logo.svg/150px-Cuiaba_Esporte_Clube_logo.svg.png",
        "goias": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Goi%C3%A1s_Esporte_Clube.svg/150px-Goi%C3%A1s_Esporte_Clube.svg.png",
        "coritiba": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Coritiba_2011.svg/150px-Coritiba_2011.svg.png",
        "sport": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Sport_Club_do_Recife.svg/150px-Sport_Club_do_Recife.svg.png",
        "america-mg": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Am%C3%A9rica_Futebol_Clube_%28MG%29_-_Escudo.svg/150px-Am%C3%A9rica_Futebol_Clube_%28MG%29_-_Escudo.svg.png",
        "vitoria": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Esporte_Clube_Vit%C3%B3ria_logo.svg/150px-Esporte_Clube_Vit%C3%B3ria_logo.svg.png",

        # Portugal - Primeira Liga
        "benfica": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/SL_Benfica_logo.svg/150px-SL_Benfica_logo.svg.png",
        "porto": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/FC_Porto.svg/150px-FC_Porto.svg.png",
        "sporting": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Sporting_Clube_de_Portugal_%28Logo%29.svg/150px-Sporting_Clube_de_Portugal_%28Logo%29.svg.png",
        "braga": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Sporting_Braga_2011.svg/150px-Sporting_Braga_2011.svg.png",
        "santa clara": "https://upload.wikimedia.org/wikipedia/en/thumb/4/47/C.D._Santa_Clara.svg/150px-C.D._Santa_Clara.svg.png",
        "vitoria guimaraes": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Vit%C3%B3ria_S.C._%28crest%29.svg/150px-Vit%C3%B3ria_S.C._%28crest%29.svg.png",

        # Argentina
        "boca juniors": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/CABJ_Escudo_Boca_Juniors.svg/150px-CABJ_Escudo_Boca_Juniors.svg.png",
        "river plate": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Escudo_del_C_A_River_Plate.svg/150px-Escudo_del_C_A_River_Plate.svg.png",
        "racing": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Escudo_de_Racing_Club_%282014%29.svg/150px-Escudo_de_Racing_Club_%282014%29.svg.png",

        # Europa - Top clubes
        "real madrid": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Logo_Real_Madrid.svg/150px-Logo_Real_Madrid.svg.png",
        "barcelona": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/FC_Barcelona_%28crest%29.svg/150px-FC_Barcelona_%28crest%29.svg.png",
        "manchester city": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Manchester_City_FC_badge.svg/150px-Manchester_City_FC_badge.svg.png",
        "liverpool": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Liverpool_FC.svg/150px-Liverpool_FC.svg.png",
        "bayern": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg/150px-FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg.png",
        "psg": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Paris_Saint-Germain_Logo_2013.svg/150px-Paris_Saint-Germain_Logo_2013.svg.png",
        "juventus": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Juventus_FC_-_pictogram_black_%28Italy%2C_2017%29.svg/150px-Juventus_FC_-_pictogram_black_%28Italy%2C_2017%29.svg.png",
        "chelsea": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Chelsea_FC.svg/150px-Chelsea_FC.svg.png",
        "arsenal": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Arsenal_FC.svg/150px-Arsenal_FC.svg.png",
        "manchester united": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Manchester_United_FC_crest.svg/150px-Manchester_United_FC_crest.svg.png",

        # Ásia - Tailândia
        "pt prachuap": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/PT_Prachuap_FC_Logo.png/150px-PT_Prachuap_FC_Logo.png",
        "sukhothai": "https://upload.wikimedia.org/wikipedia/en/thumb/2/28/Sukhothai_FC_Logo.png/150px-Sukhothai_FC_Logo.png",
        "buriram": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Buriram_United_2014_Logo.png/150px-Buriram_United_2014_Logo.png",
        "bangkok united": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4c/Bangkok_United_F.C._Logo.png/150px-Bangkok_United_F.C._Logo.png",
        "muangthong": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Muangthong_United_FC_2017_Logo.png/150px-Muangthong_United_FC_2017_Logo.png",
    }

    # Busca no mapeamento usando nome normalizado
    for clube_key, url in logos_principais.items():
        if clube_key in nome_norm or nome_norm in clube_key:
            return url

    # Se não encontrou, retorna None (frontend usará fallback emoji 🛡️)
    return None


def get_logo_liga(nome_liga):
    """
    Retorna URL do logo da liga
    Usa padrões genéricos e inteligentes

    Args:
        nome_liga: Nome da liga

    Returns:
        URL do logo ou None
    """
    if not nome_liga:
        return None

    nome_norm = normalizar_nome(nome_liga)

    # Logo genérico brasileiro para todas as séries
    logo_brasileiro = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Brasileiro_2023.png/150px-Brasileiro_2023.png"

    # Logo português genérico
    logo_portugal = "https://upload.wikimedia.org/wikipedia/en/thumb/4/4f/Liga_Portugal_logo.svg/150px-Liga_Portugal_logo.svg.png"

    # Mapeamento com padrões inteligentes
    # Detecta padrões em vez de mapear cada variação

    # BRASIL - Qualquer variação de "Série/Serie A/B/C/D" ou "Brasileirão"
    if any(termo in nome_norm for termo in ["brasileiro", "serie", "serie a", "serie b", "serie c", "serie d"]):
        return logo_brasileiro

    # PORTUGAL - Qualquer variação de "Liga Portugal" ou "Primeira Liga"
    if any(termo in nome_norm for termo in ["portugal", "primeira liga", "liga nos"]):
        return logo_portugal

    # ARGENTINA
    if any(termo in nome_norm for termo in ["argentina", "profesional", "clausura", "apertura"]):
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Logo_LPF.svg/150px-Logo_LPF.svg.png"

    # ESPANHA
    if any(termo in nome_norm for termo in ["la liga", "espanha", "spain"]):
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/LaLiga_EA_Sports_2023_Vertical_Logo.svg/150px-LaLiga_EA_Sports_2023_Vertical_Logo.svg.png"

    # INGLATERRA
    if any(termo in nome_norm for termo in ["premier", "inglaterra", "england"]):
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Premier_League_Logo.svg/150px-Premier_League_Logo.svg.png"

    # ITÁLIA
    if any(termo in nome_norm for termo in ["serie a", "italia", "calcio"]) and "brasil" not in nome_norm:
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Serie_A_logo_2022.svg/150px-Serie_A_logo_2022.svg.png"

    # ALEMANHA
    if any(termo in nome_norm for termo in ["bundesliga", "alemanha", "germany"]):
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Bundesliga_logo_%282017%29.svg/150px-Bundesliga_logo_%282017%29.svg.png"

    # FRANÇA
    if any(termo in nome_norm for termo in ["ligue 1", "franca", "france"]):
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Ligue1.svg/150px-Ligue1.svg.png"

    # TAILÂNDIA
    if any(termo in nome_norm for termo in ["thai", "tailandia"]):
        return "https://upload.wikimedia.org/wikipedia/en/thumb/0/0d/Thai_League_logo.png/150px-Thai_League_logo.png"

    # JAPÃO
    if any(termo in nome_norm for termo in ["j1", "j2", "j-league", "japao", "japan"]):
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/J.League_Logo.svg/150px-J.League_Logo.svg.png"

    # COREIA
    if any(termo in nome_norm for termo in ["k league", "coreia", "korea"]):
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/K_League_1_logo.svg/150px-K_League_1_logo.svg.png"

    # HOLANDA
    if any(termo in nome_norm for termo in ["eredivisie", "holanda", "netherlands"]):
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Eredivisie_Logo.svg/150px-Eredivisie_Logo.svg.png"

    # BÉLGICA
    if any(termo in nome_norm for termo in ["jupiler", "belgica", "belgium"]):
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Belgian_First_Division_A_logo.svg/150px-Belgian_First_Division_A_logo.svg.png"

    # Se não encontrou, retorna None (frontend usará fallback emoji 🏆)
    return None
