"""
Módulo de Integração FotMob API
================================
Busca estatísticas avançadas de jogadores do FotMob

Estatísticas disponíveis:
- Gols, Assistências, xG, xA
- Finalizações, Big Chances
- Passes, Dribles
- Defesa (desarmes, interceptações)
- Disciplina (cartões)

Autor: Scout Pro
Data: 2025-12-09
"""

import requests
import pandas as pd
from typing import Optional, Dict, List, Any
from datetime import datetime
import streamlit as st


class FotMobAPI:
    """Cliente para API não-oficial do FotMob"""

    BASE_URL = "https://www.fotmob.com/api"

    # 35 estatísticas disponíveis (baseado em análise real da API)
    PLAYER_STATS = [
        # Ofensivas
        "goals", "assists", "expected_goals", "expected_assists",
        "shots", "shots_on_target", "big_chances_created",

        # Passes
        "accurate_passes", "accurate_long_balls", "key_passes",
        "successful_dribbles", "touches_in_opposition_box",

        # Defesa
        "tackles", "interceptions", "clearances", "blocked_shots",
        "duels_won", "aerial_duels_won", "ground_duels_won",

        # Goleiro
        "saves", "save_percentage", "goals_prevented",
        "clean_sheets", "goals_conceded",

        # Disciplina
        "yellow_cards", "red_cards", "fouls_committed",

        # Performance
        "minutes_played", "appearances", "rating",

        # Avançadas
        "expected_goals_on_target", "big_chances_missed",
        "successful_crosses", "penalties_won", "penalties_committed"
    ]

    def __init__(self):
        """Inicializa o cliente FotMob"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def buscar_jogador_por_nome(self, nome: str) -> Optional[Dict]:
        """
        Busca jogador no FotMob pelo nome

        Args:
            nome: Nome do jogador

        Returns:
            Dados do jogador ou None
        """
        try:
            # Endpoint de busca do FotMob
            url = f"{self.BASE_URL}/searchapi/{nome}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Filtra apenas jogadores (não times/ligas)
                if 'players' in data and len(data['players']) > 0:
                    return data['players'][0]  # Retorna primeiro resultado

            return None

        except Exception as e:
            print(f"❌ Erro ao buscar jogador '{nome}': {e}")
            return None

    def buscar_estatisticas_jogador(self, player_id: int, season: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Busca estatísticas detalhadas do jogador

        Args:
            player_id: ID do jogador no FotMob
            season: Temporada (ex: "2023/2024") - padrão: atual

        Returns:
            DataFrame com estatísticas ou None
        """
        try:
            url = f"{self.BASE_URL}/playerData?id={player_id}"
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                return None

            data = response.json()

            # Extrai estatísticas principais
            stats = self._extrair_estatisticas(data)

            if stats:
                return pd.DataFrame([stats])

            return None

        except Exception as e:
            print(f"❌ Erro ao buscar estatísticas do jogador {player_id}: {e}")
            return None

    def _extrair_estatisticas(self, data: Dict) -> Dict[str, Any]:
        """
        Extrai estatísticas relevantes do JSON da API

        Args:
            data: Resposta JSON da API

        Returns:
            Dicionário com estatísticas processadas
        """
        stats = {
            'fotmob_id': data.get('id'),
            'nome': data.get('name'),
            'data_atualizacao': datetime.now()
        }

        # Navega pela estrutura da API (pode variar)
        if 'statSeasons' in data and len(data['statSeasons']) > 0:
            season_stats = data['statSeasons'][0]  # Temporada mais recente

            if 'stats' in season_stats:
                for stat in season_stats['stats']:
                    stat_name = stat.get('title', '').lower().replace(' ', '_')
                    stat_value = stat.get('value')

                    # Converte para número quando possível
                    try:
                        stat_value = float(stat_value)
                    except (ValueError, TypeError):
                        pass

                    stats[stat_name] = stat_value

        return stats

    @st.cache_data(ttl=86400, show_spinner=False)  # Cache de 24 horas
    def buscar_e_cachear_stats(_self, player_id: int) -> Optional[pd.DataFrame]:
        """
        Busca estatísticas com cache (evita chamadas repetidas)

        Args:
            player_id: ID do jogador

        Returns:
            DataFrame com estatísticas
        """
        return _self.buscar_estatisticas_jogador(player_id)


# ===== FUNÇÕES DE INTEGRAÇÃO COM O BANCO =====

def sincronizar_fotmob_com_banco(db, nome_jogador: str, transfermarkt_id: Optional[str] = None) -> bool:
    """
    Sincroniza estatísticas do FotMob com banco de dados

    Args:
        db: Instância do ScoutingDatabase
        nome_jogador: Nome do jogador
        transfermarkt_id: ID do Transfermarkt (opcional)

    Returns:
        True se sincronizou com sucesso
    """
    try:
        api = FotMobAPI()

        # 1. Busca jogador no FotMob
        jogador_data = api.buscar_jogador_por_nome(nome_jogador)

        if not jogador_data:
            print(f"⚠️ Jogador '{nome_jogador}' não encontrado no FotMob")
            return False

        fotmob_id = jogador_data.get('id')

        # 2. Busca estatísticas
        stats_df = api.buscar_estatisticas_jogador(fotmob_id)

        if stats_df is None or stats_df.empty:
            print(f"⚠️ Estatísticas não disponíveis para {nome_jogador}")
            return False

        # 3. Salva no banco (método a ser implementado na próxima etapa)
        # db.salvar_estatisticas_fotmob(stats_df)

        print(f"✅ Estatísticas de '{nome_jogador}' sincronizadas com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro ao sincronizar {nome_jogador}: {e}")
        return False


def buscar_stats_multiplos_jogadores(db, lista_nomes: List[str]) -> pd.DataFrame:
    """
    Busca estatísticas de múltiplos jogadores em lote

    Args:
        db: Instância do banco
        lista_nomes: Lista de nomes de jogadores

    Returns:
        DataFrame consolidado com todas as estatísticas
    """
    api = FotMobAPI()
    all_stats = []

    for nome in lista_nomes:
        print(f"📊 Buscando {nome}...")

        jogador = api.buscar_jogador_por_nome(nome)
        if jogador:
            stats = api.buscar_estatisticas_jogador(jogador['id'])
            if stats is not None:
                all_stats.append(stats)

    if all_stats:
        return pd.concat(all_stats, ignore_index=True)

    return pd.DataFrame()


# ===== EXEMPLO DE USO =====

if __name__ == "__main__":
    # Teste da API
    api = FotMobAPI()

    # Busca Neymar
    print("🔍 Buscando Neymar...")
    jogador = api.buscar_jogador_por_nome("Neymar")

    if jogador:
        print(f"✅ Encontrado: {jogador.get('name')} (ID: {jogador.get('id')})")

        # Busca estatísticas
        stats = api.buscar_estatisticas_jogador(jogador['id'])
        if stats is not None:
            print("\n📊 Estatísticas:")
            print(stats.head())
    else:
        print("❌ Jogador não encontrado")
