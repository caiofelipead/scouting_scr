"""
database_extended.py
Extensão da classe ScoutingDatabase com métodos adicionais
para gestão financeira e análises avançadas
"""

from database import ScoutingDatabase
import pandas as pd
from datetime import datetime
from sqlalchemy import text


class ScoutingDatabaseExtended(ScoutingDatabase):
    """
    Extensão da classe ScoutingDatabase com funcionalidades adicionais
    para análise financeira, agentes e gestão avançada de jogadores
    """
    
    def __init__(self):
        """Inicializa a classe extendida"""
        super().__init__()
    
    def get_connection(self):
        """Retorna uma conexão do engine SQLAlchemy"""
        return self.engine.connect()
    
    # ==================== ESTATÍSTICAS ====================
    
    def estatisticas_jogadores(self):
        """
        Retorna estatísticas gerais dos jogadores para a aba financeira
        
        Returns:
            dict: Estatísticas dos jogadores
        """
        try:
            query = """
                SELECT 
                    COUNT(DISTINCT j.id_jogador) as total,
                    COUNT(DISTINCT CASE 
                        WHEN j.salario_mensal_min IS NOT NULL 
                        OR j.salario_mensal_max IS NOT NULL 
                        THEN j.id_jogador 
                    END) as com_info_financeira,
                    COUNT(DISTINCT CASE 
                        WHEN j.agente_nome IS NOT NULL 
                        THEN j.id_jogador 
                    END) as com_agente
                FROM jogadores j
            """
            
            result = self.execute_query(query)
            
            if result and len(result) > 0:
                return {
                    'total': result[0].get('total', 0) or 0,
                    'com_info_financeira': result[0].get('com_info_financeira', 0) or 0,
                    'com_agente': result[0].get('com_agente', 0) or 0
                }
            else:
                return {
                    'total': 0,
                    'com_info_financeira': 0,
                    'com_agente': 0
                }
                
        except Exception as e:
            print(f"❌ Erro ao buscar estatísticas de jogadores: {e}")
            # Fallback: contar apenas total de jogadores (colunas que existem)
            try:
                query_fallback = "SELECT COUNT(*) as total FROM jogadores"
                result = self.execute_query(query_fallback)
                total = result[0].get('total', 0) if result else 0
                return {
                    'total': total,
                    'com_info_financeira': 0,
                    'com_agente': 0
                }
            except:
                return {
                    'total': 0,
                    'com_info_financeira': 0,
                    'com_agente': 0
                }
    
    def estatisticas_financeiras(self):
        """
        Retorna estatísticas das propostas financeiras
        
        Returns:
            dict: Estatísticas das propostas
        """
        try:
            query = """
                SELECT 
                    COUNT(*) as total_propostas,
                    COUNT(CASE WHEN status = 'Em análise' THEN 1 END) as em_analise,
                    COUNT(CASE WHEN status = 'Aprovada' THEN 1 END) as aprovadas,
                    COUNT(CASE WHEN status = 'Rejeitada' THEN 1 END) as rejeitadas
                FROM propostas
            """
            
            result = self.execute_query(query)
            
            if result and len(result) > 0:
                return {
                    'total_propostas': result[0].get('total_propostas', 0) or 0,
                    'em_analise': result[0].get('em_analise', 0) or 0,
                    'aprovadas': result[0].get('aprovadas', 0) or 0,
                    'rejeitadas': result[0].get('rejeitadas', 0) or 0
                }
            else:
                return {
                    'total_propostas': 0,
                    'em_analise': 0,
                    'aprovadas': 0,
                    'rejeitadas': 0
                }
                
        except Exception as e:
            print(f"⚠️ Aviso: Tabela 'propostas' não encontrada ou erro: {e}")
            return {
                'total_propostas': 0,
                'em_analise': 0,
                'aprovadas': 0,
                'rejeitadas': 0
            }
    
    # ==================== BUSCA E FILTROS ====================
    
    def buscar_por_faixa_salarial(self, salario_min=None, salario_max=None, moeda='BRL'):
        """
        Busca jogadores por faixa salarial
        
        Args:
            salario_min: Salário mínimo (opcional)
            salario_max: Salário máximo (opcional)
            moeda: Moeda de referência (padrão: BRL)
            
        Returns:
            DataFrame: Jogadores que atendem aos critérios
        """
        try:
            # Query base usando estrutura atual do banco
            query = """
                SELECT 
                    j.id_jogador,
                    j.nome,
                    v.posicao,
                    v.clube,
                    v.liga_clube as liga,
                    j.idade_atual as idade,
                    j.salario_mensal_min,
                    j.salario_mensal_max,
                    j.moeda_salario,
                    j.agente_nome,
                    j.agente_empresa,
                    j.clausula_rescisoria,
                    a.nota_potencial as potencial,
                    a.nota_tatico as tatico
                FROM jogadores j
                LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
                LEFT JOIN avaliacoes a ON j.id_jogador = a.id_jogador
                WHERE 1=1
            """
            
            params = {}
            
            # Filtro de moeda
            if moeda:
                query += " AND (j.moeda_salario = :moeda OR j.moeda_salario IS NULL)"
                params['moeda'] = moeda
            
            # Filtro de salário mínimo
            if salario_min is not None:
                query += " AND j.salario_mensal_max >= :salario_min"
                params['salario_min'] = salario_min
            
            # Filtro de salário máximo
            if salario_max is not None:
                query += " AND (j.salario_mensal_min <= :salario_max OR j.salario_mensal_min IS NULL)"
                params['salario_max'] = salario_max
            
            query += " ORDER BY j.salario_mensal_max DESC NULLS LAST"
            
            # Executa query
            df = pd.read_sql(text(query), self.engine, params=params if params else None)
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao buscar por faixa salarial: {e}")
            # Fallback: retorna jogadores sem filtro financeiro
            try:
                query_fallback = """
                    SELECT 
                        j.id_jogador,
                        j.nome,
                        v.posicao,
                        v.clube,
                        v.liga_clube as liga,
                        j.idade_atual as idade,
                        a.nota_potencial as potencial,
                        a.nota_tatico as tatico
                    FROM jogadores j
                    LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
                    LEFT JOIN avaliacoes a ON j.id_jogador = a.id_jogador
                    ORDER BY j.nome
                """
                return pd.read_sql(text(query_fallback), self.engine)
            except:
                return pd.DataFrame()
    
    # ==================== DADOS FINANCEIROS ====================
    
    def obter_dados_financeiros(self, jogador_id):
        """
        Obtém dados financeiros de um jogador específico
        
        Args:
            jogador_id: ID do jogador
            
        Returns:
            dict: Dados financeiros do jogador
        """
        jogador_id = self._safe_int(jogador_id)
        try:
            query = """
                SELECT 
                    salario_mensal_min as salario_min,
                    salario_mensal_max as salario_max,
                    moeda_salario as moeda,
                    bonificacoes,
                    custo_transferencia,
                    clausula_rescisoria as clausula,
                    percentual_direitos_economicos as percentual_direitos,
                    condicoes_negocio as condicoes,
                    observacoes_financeiras as observacoes,
                    agente_telefone,
                    agente_email,
                    agente_comissao
                FROM jogadores
                WHERE id_jogador = :jogador_id
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {'jogador_id': jogador_id})
                row = result.fetchone()
                
                if row:
                    columns = result.keys()
                    return dict(zip(columns, row))
                return None
                
        except Exception as e:
            print(f"❌ Erro ao obter dados financeiros: {e}")
            return None
    
    def atualizar_financeiro(self, jogador_id, dados_financeiros, usuario_id=1):
        """
        Atualiza informações financeiras de um jogador
        
        Args:
            jogador_id: ID do jogador
            dados_financeiros: Dict com os dados financeiros
            usuario_id: ID do usuário que está fazendo a atualização
            
        Returns:
            bool: True se atualizado com sucesso
        """
        jogador_id = self._safe_int(jogador_id)
        try:
            query = """
                UPDATE jogadores
                SET 
                    salario_mensal_min = :salario_min,
                    salario_mensal_max = :salario_max,
                    moeda_salario = :moeda,
                    bonificacoes = :bonificacoes,
                    custo_transferencia = :custo_transferencia,
                    condicoes_negocio = :condicoes,
                    clausula_rescisoria = :clausula,
                    percentual_direitos_economicos = :percentual_direitos,
                    observacoes_financeiras = :observacoes,
                    data_atualizacao = CURRENT_TIMESTAMP
                WHERE id_jogador = :jogador_id
            """
            
            params = {
                'salario_min': dados_financeiros.get('salario_min'),
                'salario_max': dados_financeiros.get('salario_max'),
                'moeda': dados_financeiros.get('moeda'),
                'bonificacoes': dados_financeiros.get('bonificacoes'),
                'custo_transferencia': dados_financeiros.get('custo_transferencia'),
                'condicoes': dados_financeiros.get('condicoes'),
                'clausula': dados_financeiros.get('clausula'),
                'percentual_direitos': dados_financeiros.get('percentual_direitos', 100),
                'observacoes': dados_financeiros.get('observacoes'),
                'jogador_id': jogador_id
            }
            
            with self.engine.connect() as conn:
                conn.execute(text(query), params)
                conn.commit()
            
            print(f"✅ Dados financeiros do jogador {jogador_id} atualizados com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar informações financeiras: {e}")
            return False
    
    # ==================== AGENTES ====================
    
    def listar_agentes(self):
        """
        Lista todos os agentes cadastrados
        
        Returns:
            DataFrame: Agentes e quantidade de jogadores
        """
        try:
            query = """
                SELECT 
                    agente_nome,
                    agente_empresa,
                    COUNT(*) as qtd_jogadores,
                    AVG(agente_comissao) as comissao_media
                FROM jogadores
                WHERE agente_nome IS NOT NULL
                GROUP BY agente_nome, agente_empresa
                ORDER BY qtd_jogadores DESC
            """
            
            df = pd.read_sql(text(query), self.engine)
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao listar agentes: {e}")
            return pd.DataFrame()
    
    def jogadores_por_agente(self, agente_nome):
        """
        Lista todos os jogadores de um agente específico
        
        Args:
            agente_nome: Nome do agente
            
        Returns:
            DataFrame: Jogadores representados pelo agente
        """
        try:
            query = """
                SELECT 
                    j.id_jogador,
                    j.nome,
                    v.posicao,
                    v.clube,
                    v.liga_clube as liga,
                    j.idade_atual as idade,
                    j.salario_mensal_min,
                    j.salario_mensal_max,
                    j.agente_comissao,
                    a.nota_potencial
                FROM jogadores j
                LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
                LEFT JOIN avaliacoes a ON j.id_jogador = a.id_jogador
                WHERE j.agente_nome = :agente_nome
                ORDER BY j.nome
            """
            
            df = pd.read_sql(text(query), self.engine, params={'agente_nome': agente_nome})
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao buscar jogadores do agente: {e}")
            return pd.DataFrame()
    
    # ==================== ANÁLISES FINANCEIRAS ====================
    
    def analise_salarial_por_posicao(self):
        """
        Análise de distribuição salarial por posição
        
        Returns:
            DataFrame: Estatísticas salariais por posição
        """
        try:
            query = """
                SELECT 
                    v.posicao,
                    COUNT(*) as total_jogadores,
                    AVG((j.salario_mensal_min + j.salario_mensal_max) / 2) as salario_medio,
                    MIN(j.salario_mensal_min) as salario_minimo,
                    MAX(j.salario_mensal_max) as salario_maximo,
                    STDDEV((j.salario_mensal_min + j.salario_mensal_max) / 2) as desvio_padrao
                FROM jogadores j
                JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
                WHERE j.salario_mensal_min IS NOT NULL 
                    AND j.salario_mensal_max IS NOT NULL
                GROUP BY v.posicao
                ORDER BY salario_medio DESC
            """
            
            df = pd.read_sql(text(query), self.engine)
            
            return df
            
        except Exception as e:
            print(f"❌ Erro na análise salarial por posição: {e}")
            return pd.DataFrame()
    
    def jogadores_alto_custo_beneficio(self, limite_potencial=4.0):
        """
        Identifica jogadores com alto custo-benefício
        (bom potencial com salário acessível)
        
        Args:
            limite_potencial: Nota mínima de potencial (padrão: 4.0)
            
        Returns:
            DataFrame: Jogadores com bom custo-benefício
        """
        try:
            query = """
                SELECT 
                    j.id_jogador,
                    j.nome,
                    v.posicao,
                    v.clube,
                    j.idade_atual as idade,
                    j.salario_mensal_max,
                    j.moeda_salario,
                    a.nota_potencial,
                    (a.nota_tatico + a.nota_tecnico + a.nota_fisico + a.nota_mental) / 4 as nota_media,
                    ROUND((a.nota_potencial / NULLIF(j.salario_mensal_max, 0)) * 10000, 2) as indice_custo_beneficio
                FROM jogadores j
                INNER JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
                INNER JOIN avaliacoes a ON j.id_jogador = a.id_jogador
                WHERE a.nota_potencial >= :limite_potencial
                    AND j.salario_mensal_max IS NOT NULL
                    AND j.salario_mensal_max > 0
                ORDER BY indice_custo_beneficio DESC
                LIMIT 20
            """
            
            df = pd.read_sql(text(query), self.engine, params={'limite_potencial': limite_potencial})
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao buscar jogadores com alto custo-benefício: {e}")
            return pd.DataFrame()
    
    # ==================== PROPOSTAS ====================
    
    def criar_proposta(self, jogador_id, dados_proposta, usuario_id=1):
        """
        Cria uma nova proposta de contratação/transferência
        
        Args:
            jogador_id: ID do jogador
            dados_proposta: Dict com dados da proposta
            usuario_id: ID do usuário
            
        Returns:
            int: ID da proposta criada ou None
        """
        jogador_id = self._safe_int(jogador_id)
        try:
            # Primeiro garante que a tabela existe
            self.criar_tabela_propostas()
            
            query = """
                INSERT INTO propostas (
                    id_jogador,
                    valor_proposta,
                    moeda,
                    tipo_transferencia,
                    clube_interessado,
                    status,
                    observacoes
                ) VALUES (
                    :id_jogador,
                    :valor_proposta,
                    :moeda,
                    :tipo_transferencia,
                    :clube_interessado,
                    :status,
                    :observacoes
                )
            """
            
            if self.db_type == 'postgresql':
                query += " RETURNING id_proposta"
            
            params = {
                'id_jogador': jogador_id,
                'valor_proposta': dados_proposta.get('valor'),
                'moeda': dados_proposta.get('moeda', 'BRL'),
                'tipo_transferencia': dados_proposta.get('tipo', 'Definitiva'),
                'clube_interessado': dados_proposta.get('clube_interessado'),
                'status': 'Em análise',
                'observacoes': dados_proposta.get('observacoes')
            }
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params)
                
                if self.db_type == 'postgresql':
                    proposta_id = result.fetchone()[0]
                else:
                    conn.commit()
                    result = conn.execute(text("SELECT last_insert_rowid()"))
                    proposta_id = result.fetchone()[0]
                
                conn.commit()
            
            print(f"✅ Proposta {proposta_id} criada com sucesso")
            return proposta_id
            
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível criar proposta: {e}")
            return None
    
    def listar_propostas(self, jogador_id=None, status=None):
        """
        Lista propostas com filtros opcionais
        
        Args:
            jogador_id: Filtrar por jogador (opcional)
            status: Filtrar por status (opcional)
            
        Returns:
            DataFrame: Propostas encontradas
        """
        try:
            query = """
                SELECT 
                    p.*,
                    j.nome as jogador_nome,
                    v.clube as clube_atual,
                    v.posicao
                FROM propostas p
                JOIN jogadores j ON p.id_jogador = j.id_jogador
                LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
                WHERE 1=1
            """
            
            params = {}
            
            if jogador_id:
                query += " AND p.id_jogador = :jogador_id"
                params['jogador_id'] = self._safe_int(jogador_id)
            
            if status:
                query += " AND p.status = :status"
                params['status'] = status
            
            query += " ORDER BY p.data_proposta DESC"
            
            df = pd.read_sql(text(query), self.engine, params=params if params else None)
            return df
            
        except Exception as e:
            print(f"❌ Erro ao listar propostas: {e}")
            return pd.DataFrame()
    
    def atualizar_status_proposta(self, proposta_id, novo_status):
        """
        Atualiza o status de uma proposta
        
        Args:
            proposta_id: ID da proposta
            novo_status: Novo status ('Em análise', 'Aprovada', 'Rejeitada')
            
        Returns:
            bool: True se atualizado com sucesso
        """
        proposta_id = self._safe_int(proposta_id)
        try:
            query = """
                UPDATE propostas
                SET status = :status
                WHERE id_proposta = :proposta_id
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(query), {'status': novo_status, 'proposta_id': proposta_id})
                conn.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar proposta: {e}")
            return False


# ==================== FUNÇÕES AUXILIARES ====================

def formatar_moeda_br(valor):
    """Formata valor como moeda brasileira"""
    if valor is None or pd.isna(valor):
        return "N/A"
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')


def formatar_moeda(valor, moeda='BRL'):
    """Formata valor com símbolo da moeda"""
    if valor is None or pd.isna(valor):
        return "N/A"
    
    simbolos = {
        'BRL': 'R$',
        'EUR': '€',
        'USD': '$',
        'GBP': '£'
    }
    
    simbolo = simbolos.get(moeda, moeda)
    
    if moeda == 'BRL':
        return f"{simbolo} {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    else:
        return f"{simbolo} {valor:,.2f}"


def calcular_custo_total_contratacao(salario_mensal, meses_contrato=12, comissao_agente=0, bonus=0):
    """
    Calcula o custo total estimado de uma contratação
    
    Args:
        salario_mensal: Salário mensal do jogador
        meses_contrato: Duração do contrato em meses
        comissao_agente: Percentual de comissão do agente
        bonus: Valor de bônus adicionais
        
    Returns:
        float: Custo total estimado
    """
    if salario_mensal is None:
        return 0
        
    custo_salarios = salario_mensal * meses_contrato
    custo_comissao = (custo_salarios * comissao_agente / 100) if comissao_agente > 0 else 0
    custo_total = custo_salarios + custo_comissao + bonus
    
    return custo_total
