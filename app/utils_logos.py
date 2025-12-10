"""
Utilit\u00e1rio para buscar logos de clubes e ligas
"""

def get_logo_clube(nome_clube):
    """
    Retorna URL do logo do clube

    Args:
        nome_clube: Nome do clube

    Returns:
        URL do logo ou None
    """
    if not nome_clube or nome_clube == "Livre":
        return None

    # Mapeamento de clubes conhecidos para logos
    logos_clubes = {
        # Clubes Brasileiros - S\u00e9rie A
        "Flamengo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Flamengo-RJ_%28BRA%29.png/150px-Flamengo-RJ_%28BRA%29.png",
        "Palmeiras": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Palmeiras_logo.svg/150px-Palmeiras_logo.svg.png",
        "S\u00e3o Paulo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Brasao_do_Sao_Paulo_Futebol_Clube.svg/150px-Brasao_do_Sao_Paulo_Futebol_Clube.svg.png",
        "Corinthians": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Corinthians_FC_crest.svg/150px-Corinthians_FC_crest.svg.png",
        "Atl\u00e9tico-MG": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Atletico_mineiro_galo.png/150px-Atletico_mineiro_galo.png",
        "Gr\u00eamio": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Gremio_FBPA.svg/150px-Gremio_FBPA.svg.png",
        "Fluminense": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Fluminense_FC_escudo.svg/150px-Fluminense_FC_escudo.svg.png",
        "Botafogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Botafogo_de_Futebol_e_Regatas_logo.svg/150px-Botafogo_de_Futebol_e_Regatas_logo.svg.png",
        "Athletico-PR": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Athletico_Paranaense.svg/150px-Athletico_Paranaense.svg.png",
        "Internacional": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Escudo_do_Sport_Club_Internacional.svg/150px-Escudo_do_Sport_Club_Internacional.svg.png",
        "Cruzeiro": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Cruzeiro_Esporte_Clube_%28logo%29.svg/150px-Cruzeiro_Esporte_Clube_%28logo%29.svg.png",
        "Santos": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Santos_logo.svg/150px-Santos_logo.svg.png",
        "Vasco": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/CRVascodaGama.svg/150px-CRVascodaGama.svg.png",
        "Bahia": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/ECBahia.svg/150px-ECBahia.svg.png",
        "Fortaleza": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/FortalezaEsporteClube.svg/150px-FortalezaEsporteClube.svg.png",

        # Clubes Argentinos
        "Boca Juniors": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/CABJ_Escudo_Boca_Juniors.svg/150px-CABJ_Escudo_Boca_Juniors.svg.png",
        "River Plate": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Escudo_del_C_A_River_Plate.svg/150px-Escudo_del_C_A_River_Plate.svg.png",
        "Racing": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Escudo_de_Racing_Club_%282014%29.svg/150px-Escudo_de_Racing_Club_%282014%29.svg.png",
        "Independiente": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Escudo_del_Club_Atl%C3%A9tico_Independiente.svg/150px-Escudo_del_Club_Atl%C3%A9tico_Independiente.svg.png",
        "San Lorenzo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Escudo_del_Club_Atl%C3%A9tico_San_Lorenzo_de_Almagro.svg/150px-Escudo_del_Club_Atl%C3%A9tico_San_Lorenzo_de_Almagro.svg.png",
        "Def y Justicia": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Escudo_del_Club_Social_y_Deportivo_Defensa_y_Justicia.svg/150px-Escudo_del_Club_Social_y_Deportivo_Defensa_y_Justicia.svg.png",

        # Clubes Europeus
        "Real Madrid": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Logo_Real_Madrid.svg/150px-Logo_Real_Madrid.svg.png",
        "Barcelona": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/FC_Barcelona_%28crest%29.svg/150px-FC_Barcelona_%28crest%29.svg.png",
        "Manchester City": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Manchester_City_FC_badge.svg/150px-Manchester_City_FC_badge.svg.png",
        "Liverpool": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Liverpool_FC.svg/150px-Liverpool_FC.svg.png",
        "Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg/150px-FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg.png",
        "Paris Saint-Germain": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Paris_Saint-Germain_Logo_2013.svg/150px-Paris_Saint-Germain_Logo_2013.svg.png",
        "Juventus": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Juventus_FC_-_pictogram_black_%28Italy%2C_2017%29.svg/150px-Juventus_FC_-_pictogram_black_%28Italy%2C_2017%29.svg.png",
        "Chelsea": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Chelsea_FC.svg/150px-Chelsea_FC.svg.png",
        "Arsenal": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Arsenal_FC.svg/150px-Arsenal_FC.svg.png",
        "Manchester United": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Manchester_United_FC_crest.svg/150px-Manchester_United_FC_crest.svg.png",

        # Clubes Asiáticos (Tailândia, Japão, etc)
        "PT Prachuap": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/PT_Prachuap_FC_Logo.png/150px-PT_Prachuap_FC_Logo.png",
        "PT Prachuap FC": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/PT_Prachuap_FC_Logo.png/150px-PT_Prachuap_FC_Logo.png",
        "Buriram United": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Buriram_United_2014_Logo.png/150px-Buriram_United_2014_Logo.png",
        "Bangkok United": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4c/Bangkok_United_F.C._Logo.png/150px-Bangkok_United_F.C._Logo.png",
        "Muangthong United": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Muangthong_United_FC_2017_Logo.png/150px-Muangthong_United_FC_2017_Logo.png",
    }

    # Tentar encontrar o clube no mapeamento
    for clube, url in logos_clubes.items():
        if clube.lower() in nome_clube.lower() or nome_clube.lower() in clube.lower():
            return url

    # Se n\u00e3o encontrar, retorna None
    return None


def get_logo_liga(nome_liga):
    """
    Retorna URL do logo da liga

    Args:
        nome_liga: Nome da liga

    Returns:
        URL do logo ou None
    """
    if not nome_liga:
        return None

    # Mapeamento de ligas conhecidas para logos
    logos_ligas = {
        # Brasileir\u00e3o
        "Brasileir\u00e3o S\u00e9rie A": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Brasileiro_2023.png/150px-Brasileiro_2023.png",
        "Brasileir\u00e3o S\u00e9rie B": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Brasileiro_2023.png/150px-Brasileiro_2023.png",
        "Brasileir\u00e3o": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Brasileiro_2023.png/150px-Brasileiro_2023.png",
        "Serie A": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Brasileiro_2023.png/150px-Brasileiro_2023.png",

        # Argentina
        "Liga Profesional": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Logo_LPF.svg/150px-Logo_LPF.svg.png",
        "Torneo Clausura": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Logo_LPF.svg/150px-Logo_LPF.svg.png",
        "Primera Divisi\u00f3n": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Logo_LPF.svg/150px-Logo_LPF.svg.png",

        # Europa
        "La Liga": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/LaLiga_EA_Sports_2023_Vertical_Logo.svg/150px-LaLiga_EA_Sports_2023_Vertical_Logo.svg.png",
        "Premier League": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Premier_League_Logo.svg/150px-Premier_League_Logo.svg.png",
        "Serie A (ITA)": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Serie_A_logo_2022.svg/150px-Serie_A_logo_2022.svg.png",
        "Bundesliga": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Bundesliga_logo_%282017%29.svg/150px-Bundesliga_logo_%282017%29.svg.png",
        "Ligue 1": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Ligue1.svg/150px-Ligue1.svg.png",

        # Ásia
        "Thai League": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0d/Thai_League_logo.png/150px-Thai_League_logo.png",
        "Thai League 1": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0d/Thai_League_logo.png/150px-Thai_League_logo.png",
        "J1 League": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/J.League_Logo.svg/150px-J.League_Logo.svg.png",
        "K League 1": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/K_League_1_logo.svg/150px-K_League_1_logo.svg.png",
    }

    # Tentar encontrar a liga no mapeamento
    for liga, url in logos_ligas.items():
        if liga.lower() in nome_liga.lower() or nome_liga.lower() in liga.lower():
            return url

    # Se n\u00e3o encontrar, retorna None
    return None
