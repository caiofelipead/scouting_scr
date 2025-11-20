"""
Sistema de Banco de Dados para Monitoramento de Jogadores
Estrutura normalizada para análise de mercado e scouting
"""

import sqlite3
from datetime import datetime
import pandas as pd
import re

class ScoutingDatabase:
    def __init__(self, db_path='scouting.db'):
        self.db_path = db_path
        self.conn = None
        self.create_tables()

    def connect(self):
        """Estabelece conexão com o banco de dados"""
        self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def _extrair_id_tm(self, link):
        """Extrai apenas o ID numérico do link do Transfermarkt"""
        if pd.isna(link) or not isinstance(link, str):
            return None
        # Procura por números após 'spieler/' ou no final da string
        match = re.search(r"spieler/(\d+)", link)
        if match:
            return match.group(1)
        return None

    def create_tables(self):
        """Cria estrutura de tabelas normalizada"""
        conn = self.connect()
        cursor = conn.cursor()

        # Tabela 1: JOGADORES (dados fixos)
        # Adicionada coluna transfermarkt_id explicitamente
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogadores (
            id_jogador INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            nacionalidade TEXT,
            ano_nascimento INTEGER,
            idade_atual INTEGER,
            altura INTEGER,
            pe_dominante TEXT,
            foto_path TEXT,
            transfermarkt_id TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Tabela 2: VÍNCULOS (dados que mudam)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vinculos (
            id_vinculo INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER,
            clube TEXT,
            liga_clube TEXT,
            posicao TEXT,
            data_fim_contrato DATE,
            status_contrato TEXT,
            FOREIGN KEY (id_jogador) REFERENCES jogadores (id_jogador)
        )
        ''')

        # Tabela 3: AVALIAÇÕES (scouting reports)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id_avaliacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER,
            data_avaliacao DATE,
            avaliador TEXT,
            nota_tecnica REAL,
            nota_tatica REAL,
            nota_fisica REAL,
            nota_mental REAL,
            nota_geral REAL,
            observacoes TEXT,
            FOREIGN KEY (id_jogador) REFERENCES jogadores (id_jogador)
        )
        ''')

        # Tabela 4: CARACTERÍSTICAS (perfil detalhado)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS caracteristicas (
            id_caracteristica INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER,
            passe_curto INTEGER,
            passe_longo INTEGER,
            finalizacao INTEGER,
            drible INTEGER,
            velocidade INTEGER,
            forca INTEGER,
            marcacao INTEGER,
            posicionamento INTEGER,
            jogo_aereo INTEGER,
            pe_fraco INTEGER,
            FOREIGN KEY (id_jogador) REFERENCES jogadores (id_jogador)
        )
        ''')

        # Tabela 5: ESTATÍSTICAS (dados de performance)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS estatisticas (
            id_estatistica INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER,
            temporada TEXT,
            jogos INTEGER,
            gols INTEGER,
            assistencias INTEGER,
            minutos_jogados INTEGER,
            cartoes_amarelos INTEGER,
            cartoes_vermelhos INTEGER,
            FOREIGN KEY (id_jogador) REFERENCES jogadores (id_jogador)
        )
        ''')

        # Tabela 6: ALERTAS (contratos, lesões, etc)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS alertas (
            id_alerta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER,
            tipo_alerta TEXT,
            descricao TEXT,
            prioridade TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'ativo',
            FOREIGN KEY (id_jogador) REFERENCES jogadores (id_jogador)
        )
        ''')

        conn.commit()
        conn.close()
        print("✅ Estrutura do banco de dados verificada/criada!")

    def importar_dados_planilha(self, df):
        """Importa dados da planilha antiga para estrutura normalizada"""
        conn = self.connect()

        print("🔄 Processando importação...")

        # 1. Identificar coluna de Link do Transfermarkt na planilha
        coluna_link = None
        possiveis_nomes_link = ['Link', 'URL', 'Transfermarkt', 'TM', 'Link TM']

        for col in df.columns:
            if col in possiveis_nomes_link or 'transfermarkt' in col.lower():
                coluna_link = col
                break

        # 2. Preparar DataFrame de Jogadores
        colunas_base = ['ID', 'Nome', 'Nacionalidade', 'Ano', 'Idade', 'Altura', 'Pé']

        # Verifica quais colunas existem no DF recebido
        colunas_existentes = [c for c in colunas_base if c in df.columns]
        jogadores_df = df[colunas_existentes].copy()

        # Renomear para o padrão do banco
        mapa_colunas = {
            'ID': 'id_jogador', 'Nome': 'nome', 'Nacionalidade': 'nacionalidade',
            'Ano': 'ano_nascimento', 'Idade': 'idade_atual',
            'Altura': 'altura', 'Pé': 'pe_dominante'
        }
        jogadores_df.rename(columns=mapa_colunas, inplace=True)

        # 3. Extrair IDs do Transfermarkt (Se achou a coluna de link)
        if coluna_link:
            print(f"   🔗 Extraindo IDs da coluna '{coluna_link}'...")
            # Aplica a função de extração em cada linha
            jogadores_df['transfermarkt_id'] = df[coluna_link].apply(self._extrair_id_tm)
        else:
            print("   ⚠️ Coluna de Link/URL não encontrada na planilha. IDs ficarão vazios.")
            jogadores_df['transfermarkt_id'] = None

        # Salvar Jogadores
        jogadores_df.to_sql('jogadores', conn, if_exists='replace', index=False)

        # 4. Importar Vínculos
        cols_vinculos = ['ID', 'Clube', 'Liga do Clube', 'Posição', 'Fim de contrato']
        cols_existentes_vinc = [c for c in cols_vinculos if c in df.columns]

        vinculos_df = df[cols_existentes_vinc].copy()

        mapa_vinculos = {
            'ID': 'id_jogador', 'Clube': 'clube', 'Liga do Clube': 'liga_clube',
            'Posição': 'posicao', 'Fim de contrato': 'data_fim_contrato'
        }
        vinculos_df.rename(columns=mapa_vinculos, inplace=True)

        # Adicionar status do contrato (baseado na data)
        if 'data_fim_contrato' in vinculos_df.columns:
            vinculos_df['status_contrato'] = vinculos_df['data_fim_contrato'].apply(
                self._calcular_status_contrato
            )

        vinculos_df.to_sql('vinculos', conn, if_exists='replace', index=False)

        conn.close()
        print(f"✅ Importação concluída: {len(jogadores_df)} jogadores atualizados!")

    def _calcular_status_contrato(self, data_fim):
        """Calcula status do contrato baseado na data de vencimento"""
        if pd.isna(data_fim):
            return 'livre'

        try:
            data_fim = pd.to_datetime(data_fim, dayfirst=True)
            hoje = datetime.now()
            dias_restantes = (data_fim - hoje).days

            if dias_restantes < 0:
                return 'vencido'
            elif dias_restantes <= 180:  # 6 meses
                return 'ultimos_6_meses'
            elif dias_restantes <= 365:  # 1 ano
                return 'ultimo_ano'
            else:
                return 'ativo'
        except:
            return 'desconhecido'

    def criar_alertas_automaticos(self):
        """Cria alertas automáticos para contratos próximos do vencimento"""
        conn = self.connect()
        cursor = conn.cursor()

        # Limpar alertas antigos
        cursor.execute("DELETE FROM alertas WHERE tipo_alerta = 'contrato_vencendo'")

        # Buscar jogadores com contrato próximo do vencimento
        query = """
        SELECT j.id_jogador, j.nome, v.data_fim_contrato, v.clube
        FROM jogadores j
        JOIN vinculos v ON j.id_jogador = v.id_jogador
        WHERE v.status_contrato IN ('ultimos_6_meses', 'ultimo_ano')
        """

        try:
            jogadores_alerta = pd.read_sql_query(query, conn)

            for _, row in jogadores_alerta.iterrows():
                # Conversão segura de data
                try:
                    data_obj = pd.to_datetime(row['data_fim_contrato'], dayfirst=True)
                    dias_restantes = (data_obj - datetime.now()).days
                except:
                    dias_restantes = 0

                if dias_restantes <= 180:
                    prioridade = 'alta'
                else:
                    prioridade = 'media'

                descricao = f"{row['nome']} - Contrato no {row['clube']} vence em {dias_restantes} dias"

                cursor.execute("""
                    INSERT INTO alertas (id_jogador, tipo_alerta, descricao, prioridade)
                    VALUES (?, ?, ?, ?)
                """, (row['id_jogador'], 'contrato_vencendo', descricao, prioridade))

            conn.commit()
            print(f"✅ Criados {len(jogadores_alerta)} alertas de contrato!")

        except Exception as e:
            print(f"⚠️ Erro ao criar alertas: {e}")

        conn.close()

    def get_jogadores_com_vinculos(self):
        """Retorna dados completos de jogadores com seus vínculos atuais"""
        conn = self.connect()
        # Query atualizada para incluir transfermarkt_id
        query = """
        SELECT 
            j.id_jogador,
            j.nome,
            j.nacionalidade,
            j.idade_atual,
            j.altura,
            j.pe_dominante,
            j.transfermarkt_id,
            v.clube,
            v.liga_clube,
            v.posicao,
            v.data_fim_contrato,
            v.status_contrato
        FROM jogadores j
        LEFT JOIN vinculos v ON j.id_jogador = v.id_jogador
        ORDER BY j.nome
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_alertas_ativos(self):
        """Retorna todos os alertas ativos"""
        conn = self.connect()
        query = """
        SELECT 
            a.tipo_alerta,
            a.descricao,
            a.prioridade,
            a.data_criacao,
            j.nome as jogador
        FROM alertas a
        JOIN jogadores j ON a.id_jogador = j.id_jogador
        WHERE a.status = 'ativo'
        ORDER BY 
            CASE a.prioridade 
                WHEN 'alta' THEN 1
                WHEN 'media' THEN 2
                WHEN 'baixa' THEN 3
            END,
            a.data_criacao DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_estatisticas_gerais(self):
        """Retorna estatísticas gerais do banco de dados"""
        conn = self.connect()

        stats = {}
        try:
            stats['total_jogadores'] = pd.read_sql_query("SELECT COUNT(*) as total FROM jogadores", conn)['total'][0]
            stats['total_vinculos_ativos'] = pd.read_sql_query(
                "SELECT COUNT(*) as total FROM vinculos WHERE status_contrato = 'ativo'", conn
            )['total'][0]
            stats['alertas_ativos'] = pd.read_sql_query(
                "SELECT COUNT(*) as total FROM alertas WHERE status = 'ativo'", conn
            )['total'][0]
            stats['contratos_vencendo'] = pd.read_sql_query(
                "SELECT COUNT(*) as total FROM vinculos WHERE status_contrato IN ('ultimos_6_meses', 'ultimo_ano')", conn
            )['total'][0]
        except:
            stats = {'total_jogadores': 0, 'total_vinculos_ativos': 0, 'alertas_ativos': 0, 'contratos_vencendo': 0}

        conn.close()
        return stats