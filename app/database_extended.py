"""
database_extended.py
Extensão da classe ScoutingDatabase com métodos adicionais
para gestão financeira e análises avançadas
"""

from database import ScoutingDatabase
import pandas as pd
from datetime import datetime


class ScoutingDatabaseExtended(ScoutingDatabase):
    """
    Extensão da classe ScoutingDatabase com funcionalidades adicionais
    para análise financeira, agentes e gestão avançada de jogadores
    """
    
    def __init__(self):
        """Inicializa a classe extendida"""
        super().__init__()
    
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
                    COUNT(DISTINCT j.id) as total,
                    COUNT(DISTINCT CASE 
                        WHEN j.salario_mensal_min IS NOT NULL 
                        OR j.salario_mensal_max IS NOT NULL 
                        THEN j.id 
                    END) as com_info_financeira,
                    COUNT(DISTINCT CASE 
                        WHEN j.agente_nome IS NOT NULL 
                        THEN j.id 
                    END) as com_agente
                FROM jogadores j
            """
            
            result = self.execute_query(query)
            
            if result and len(result) > 0:
                return {
                    'total': result[0]['total'] or 0,
                    'com_info_financeira': result[0]['com_info_financeira'] or 0,
                    'com_agente': result[0]['com_agente'] or 0
                }
            else:
                return {
                    'total': 0,
                    'com_info_financeira': 0,
                    'com_agente': 0
                }
                
        except Exception as e:
            print(f"❌ Erro ao buscar estatísticas de jogadores: {e}")
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
                    COUNT(CASE WHEN status = 'Em Análise' THEN 1 END) as em_analise,
                    COUNT(CASE WHEN status = 'Aprovada' THEN 1 END) as aprovadas,
                    COUNT(CASE WHEN status = 'Rejeitada' THEN 1 END) as rejeitadas
                FROM propostas
            """
            
            result = self.execute_query(query)
            
            if result and len(result) > 0:
                return {
                    'total_propostas': result[0]['total_propostas'] or 0,
                    'em_analise': result[0]['em_analise'] or 0,
                    'aprovadas': result[0]['aprovadas'] or 0,
                    'rejeitadas': result[0]['rejeitadas'] or 0
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
            # Retornar zeros se a tabela propostas não existir
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
            # Query base
            query = """
                SELECT 
                    j.id,
                    j.nome,
                    j.posicao,
                    j.clube,
                    j.liga,
                    j.idade,
                    j.salario_mensal_min,
                    j.salario_mensal_max,
                    j.moeda_salario,
                    j.agente_nome,
                    j.agente_empresa,
                    j.clausula_rescisoria,
                    a.nota_potencial as potencial,
                    a.nota_tatico as tatico
                FROM jogadores j
                LEFT JOIN avaliacoes a ON j.id = a.id_jogador
                WHERE 1=1
            """
            
            params = []
            
            # Filtro de moeda
            if moeda:
                query += " AND (j.moeda_salario = %s OR j.moeda_salario IS NULL)"
                params.append(moeda)
            
            # Filtro de salário mínimo
            if salario_min is not None:
                query += " AND j.salario_mensal_max >= %s"
                params.append(salario_min)
            
            # Filtro de salário máximo
            if salario_max is not None:
                query += " AND (j.salario_mensal_min <= %s OR j.salario_mensal_min IS NULL)"
                params.append(salario_max)
            
            query += " ORDER BY j.salario_mensal_max DESC NULLS LAST"
            
            # Executa query
            conn = self.get_connection()
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao buscar por faixa salarial: {e}")
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
                WHERE id = %s
            """
            
            result = self.execute_query(query, (jogador_id,))
            
            if result and len(result) > 0:
                return result[0]
            else:
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
        try:
            query = """
                UPDATE jogadores
                SET 
                    salario_mensal_min = %s,
                    salario_mensal_max = %s,
                    moeda_salario = %s,
                    bonificacoes = %s,
                    custo_transferencia = %s,
                    condicoes_negocio = %s,
                    clausula_rescisoria = %s,
                    percentual_direitos_economicos = %s,
                    observacoes_financeiras = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            params = (
                dados_financeiros.get('salario_min'),
                dados_financeiros.get('salario_max'),
                dados_financeiros.get('moeda'),
                dados_financeiros.get('bonificacoes'),
                dados_financeiros.get('custo_transferencia'),
                dados_financeiros.get('condicoes'),
                dados_financeiros.get('clausula'),
                dados_financeiros.get('percentual_direitos', 100),
                dados_financeiros.get('observacoes'),
                jogador_id
            )
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            cursor.close()
            conn.close()
            
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
            
            conn = self.get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            
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
                    j.id,
                    j.nome,
                    j.posicao,
                    j.clube,
                    j.liga,
                    j.idade,
                    j.salario_mensal_min,
                    j.salario_mensal_max,
                    j.agente_comissao,
                    a.nota_potencial
                FROM jogadores j
                LEFT JOIN avaliacoes a ON j.id = a.id_jogador
                WHERE j.agente_nome = %s
                ORDER BY j.nome
            """
            
            conn = self.get_connection()
            df = pd.read_sql(query, conn, params=(agente_nome,))
            conn.close()
            
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
                    posicao,
                    COUNT(*) as total_jogadores,
                    AVG((salario_mensal_min + salario_mensal_max) / 2) as salario_medio,
                    MIN(salario_mensal_min) as salario_minimo,
                    MAX(salario_mensal_max) as salario_maximo,
                    STDDEV((salario_mensal_min + salario_mensal_max) / 2) as desvio_padrao
                FROM jogadores
                WHERE salario_mensal_min IS NOT NULL 
                    AND salario_mensal_max IS NOT NULL
                GROUP BY posicao
                ORDER BY salario_medio DESC
            """
            
            conn = self.get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            
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
                    j.id,
                    j.nome,
                    j.posicao,
                    j.clube,
                    j.idade,
                    j.salario_mensal_max,
                    j.moeda_salario,
                    a.nota_potencial,
                    a.nota_final,
                    ROUND((a.nota_potencial / NULLIF(j.salario_mensal_max, 0)) * 10000, 2) as indice_custo_beneficio
                FROM jogadores j
                INNER JOIN avaliacoes a ON j.id = a.id_jogador
                WHERE a.nota_potencial >= %s
                    AND j.salario_mensal_max IS NOT NULL
                    AND j.salario_mensal_max > 0
                ORDER BY indice_custo_beneficio DESC
                LIMIT 20
            """
            
            conn = self.get_connection()
            df = pd.read_sql(query, conn, params=(limite_potencial,))
            conn.close()
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao buscar jogadores com alto custo-benefício: {e}")
            return pd.DataFrame()
    
    # ==================== PROPOSTAS (FUTURO) ====================
    
    def criar_proposta(self, jogador_id, dados_proposta, usuario_id):
        """
        Cria uma nova proposta de contratação/transferência
        
        Args:
            jogador_id: ID do jogador
            dados_proposta: Dict com dados da proposta
            usuario_id: ID do usuário
            
        Returns:
            int: ID da proposta criada ou None
        """
        try:
            query = """
                INSERT INTO propostas (
                    id_jogador,
                    tipo_proposta,
                    valor_proposta,
                    moeda,
                    condicoes,
                    prazo_resposta,
                    status,
                    criado_por,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING id
            """
            
            params = (
                jogador_id,
                dados_proposta.get('tipo', 'Contratação'),
                dados_proposta.get('valor'),
                dados_proposta.get('moeda', 'BRL'),
                dados_proposta.get('condicoes'),
                dados_proposta.get('prazo_resposta'),
                'Em Análise',
                usuario_id
            )
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            proposta_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Proposta {proposta_id} criada com sucesso")
            return proposta_id
            
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível criar proposta (tabela pode não existir): {e}")
            return None


# ==================== FUNÇÕES AUXILIARES ====================

def formatar_moeda_br(valor):
    """Formata valor como moeda brasileira"""
    if valor is None or pd.isna(valor):
        return "N/A"
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')


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
    custo_salarios = salario_mensal * meses_contrato
    custo_comissao = (custo_salarios * comissao_agente / 100) if comissao_agente > 0 else 0
    custo_total = custo_salarios + custo_comissao + bonus
    
    return custo_total
