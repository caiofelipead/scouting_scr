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
    
    def execute_query(self, query, params=None):
        """Executa query e retorna lista de dicts"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                columns = result.keys()
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"❌ Erro na query: {e}")
            return []
    
    def _safe_int(self, value):
        """Converte valor para int de forma segura"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    
    def get_connection(self):
        """Retorna uma conexão do engine SQLAlchemy"""
        return self.engine.connect()
    
    # ==================== ESTATÍSTICAS ====================
    
    def estatisticas_jogadores(self):
        """Retorna estatísticas gerais dos jogadores"""
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
                return {'total': 0, 'com_info_financeira': 0, 'com_agente': 0}
                
        except Exception as e:
            print(f"❌ Erro ao buscar estatísticas: {e}")
            return {'total': 0, 'com_info_financeira': 0, 'com_agente': 0}
    
    def estatisticas_financeiras(self):
        """Retorna estatísticas das propostas financeiras"""
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
                return {'total_propostas': 0, 'em_analise': 0, 'aprovadas': 0, 'rejeitadas': 0}
                
        except Exception as e:
            print(f"⚠️ Tabela propostas não encontrada: {e}")
            return {'total_propostas': 0, 'em_analise': 0, 'aprovadas': 0, 'rejeitadas': 0}
    
    # ==================== BUSCA E FILTROS ====================
    
    def buscar_por_faixa_salarial(self, salario_min=None, salario_max=None, moeda='BRL'):
        """Busca jogadores por faixa salarial"""
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
            
            if moeda:
                query += " AND (j.moeda_salario = :moeda OR j.moeda_salario IS NULL)"
                params['moeda'] = moeda
            
            if salario_min is not None:
                query += " AND j.salario_mensal_max >= :salario_min"
                params['salario_min'] = salario_min
            
            if salario_max is not None:
                query += " AND (j.salario_mensal_min <= :salario_max OR j.salario_mensal_min IS NULL)"
                params['salario_max'] = salario_max
            
            query += " ORDER BY j.salario_mensal_max DESC NULLS LAST"
            
            df = pd.read_sql(text(query), self.engine, params=params if params else None)
            return df
            
        except Exception as e:
            print(f"❌ Erro ao buscar por faixa salarial: {e}")
            return pd.DataFrame()
    
    # ==================== DADOS FINANCEIROS ====================
    
    def obter_dados_financeiros(self, jogador_id):
        """Obtém dados financeiros de um jogador específico"""
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
        """Atualiza informações financeiras de um jogador"""
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
            
            print(f"✅ Dados financeiros do jogador {jogador_id} atualizados")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar financeiro: {e}")
            return False
    
    # ==================== AGENTES ====================
    
    def listar_agentes(self):
        """Lista todos os agentes cadastrados"""
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
            return pd.read_sql(text(query), self.engine)
        except Exception as e:
            print(f"❌ Erro ao listar agentes: {e}")
            return pd.DataFrame()
    
    def jogadores_por_agente(self, agente_nome):
        """Lista jogadores de um agente específico"""
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
            return pd.read_sql(text(query), self.engine, params={'agente_nome': agente_nome})
        except Exception as e:
            print(f"❌ Erro: {e}")
            return pd.DataFrame()


# ==================== FUNÇÕES AUXILIARES ====================

def formatar_moeda(valor, moeda='BRL'):
    """Formata valor com símbolo da moeda"""
    if valor is None or pd.isna(valor):
        return "N/A"
    
    simbolos = {'BRL': 'R$', 'EUR': '€', 'USD': '$', 'GBP': '£'}
    simbolo = simbolos.get(moeda, moeda)
    
    if moeda == 'BRL':
        return f"{simbolo} {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    return f"{simbolo} {valor:,.2f}"
