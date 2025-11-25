"""
Aba Financeira - Scout Pro
Gestão de informações financeiras e agentes dos jogadores
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database_extended import ScoutingDatabaseExtended
from datetime import datetime


def formatar_moeda(valor, moeda='BRL'):
    """Formata valor como moeda"""
    if valor is None:
        return "N/A"
    
    simbolos = {
        'BRL': 'R$',
        'EUR': '€',
        'USD': '$',
        'GBP': '£'
    }
    
    simbolo = simbolos.get(moeda, moeda)
    return f"{simbolo} {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')


def aba_financeira():
    """
    Aba completa de gestão financeira
    """
    st.title("💰 Gestão Financeira")
    
    db = ScoutingDatabaseExtended()
    
    # Estatísticas separadas
    stats_jogadores = db.estatisticas_jogadores()
    stats_propostas = db.estatisticas_financeiras()
    
    # Cabeçalho com métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Jogadores", 
            stats_jogadores['total'],
            delta=f"{stats_jogadores['com_info_financeira']} com dados financeiros"
        )
    
    with col2:
        percentual_salario = (stats_jogadores['com_info_financeira'] / stats_jogadores['total'] * 100) if stats_jogadores['total'] > 0 else 0
        st.metric(
            "Com Info Salarial", 
            stats_jogadores['com_info_financeira'],
            f"{percentual_salario:.1f}%"
        )
    
    with col3:
        percentual_agente = (stats_jogadores['com_agente'] / stats_jogadores['total'] * 100) if stats_jogadores['total'] > 0 else 0
        st.metric(
            "Com Agente", 
            stats_jogadores['com_agente'],
            f"{percentual_agente:.1f}%"
        )
    
    with col4:
        st.metric(
            "Propostas em Análise",
            stats_propostas['em_analise'],
            delta=f"{stats_propostas['total_propostas']} total"
        )
    
    st.markdown("---")
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Buscar por Faixa Salarial",
        "📊 Análise Financeira",
        "✏️ Editar Informações",
        "👔 Agentes"
    ])
    
    # TAB 1: Busca por Faixa Salarial
    with tab1:
        st.subheader("🔍 Buscar Jogadores por Faixa Salarial")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            moeda = st.selectbox(
                "Moeda",
                ["BRL", "EUR", "USD", "GBP"],
                index=0
            )
        
        with col2:
            salario_min = st.number_input(
                "Salário Mínimo",
                min_value=0,
                value=0,
                step=1000,
                help="Deixe em 0 para não filtrar"
            )
        
        with col3:
            salario_max = st.number_input(
                "Salário Máximo",
                min_value=0,
                value=100000,
                step=5000,
                help="Valor máximo desejado"
            )
        
        # Filtros adicionais
        with st.expander("⚙️ Filtros Adicionais"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                posicoes = st.multiselect(
                    "Posição",
                    ["Goleiro", "Lateral", "Zagueiro", "Volante", 
                     "Meia", "Atacante"],
                    default=[]
                )
            
            with col2:
                idade_min = st.number_input("Idade Mínima", 16, 40, 16)
                idade_max = st.number_input("Idade Máxima", 16, 40, 35)
            
            with col3:
                tem_agente = st.checkbox("Apenas com agente")
                tem_clausula = st.checkbox("Apenas com cláusula")
        
        if st.button("🔍 Buscar", type="primary", use_container_width=True):
            # Busca no banco
            salario_min_busca = salario_min if salario_min > 0 else None
            
            df_resultado = db.buscar_por_faixa_salarial(
                salario_min=salario_min_busca,
                salario_max=salario_max,
                moeda=moeda
            )
            
            if not df_resultado.empty:
                # Aplica filtros adicionais
                if posicoes:
                    df_resultado = df_resultado[df_resultado['posicao'].isin(posicoes)]
                
                if idade_min or idade_max:
                    df_resultado = df_resultado[
                        (df_resultado['idade'] >= idade_min) &
                        (df_resultado['idade'] <= idade_max)
                    ]
                
                if tem_agente:
                    df_resultado = df_resultado[df_resultado['agente_nome'].notna()]
                
                if tem_clausula:
                    df_resultado = df_resultado[df_resultado['clausula_rescisoria'].notna()]
                
                st.success(f"✅ {len(df_resultado)} jogadores encontrados")
                
                # Exibe resultados
                for _, jogador in df_resultado.iterrows():
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                        
                        with col1:
                            st.markdown(f"### {jogador['nome']}")
                            st.caption(f"⚽ {jogador['posicao']} | 🎂 {jogador['idade']} anos")
                            st.caption(f"🏆 {jogador['clube']} ({jogador['liga']})")
                        
                        with col2:
                            st.markdown("**Salário**")
                            if pd.notna(jogador['salario_mensal_min']) and pd.notna(jogador['salario_mensal_max']):
                                st.write(f"{formatar_moeda(jogador['salario_mensal_min'], moeda)}")
                                st.write(f"até {formatar_moeda(jogador['salario_mensal_max'], moeda)}")
                            else:
                                st.caption("Não informado")
                        
                        with col3:
                            st.markdown("**Agente**")
                            if pd.notna(jogador.get('agente_nome')):
                                st.write(jogador['agente_nome'])
                                if pd.notna(jogador.get('agente_empresa')):
                                    st.caption(jogador['agente_empresa'])
                            else:
                                st.caption("Não informado")
                        
                        with col4:
                            st.markdown("**Avaliação**")
                            if pd.notna(jogador.get('potencial')):
                                st.write(f"⭐ {jogador['potencial']}/5")
                                st.caption(f"Tático: {jogador.get('tatico', 0)}/5")
                            else:
                                st.caption("Não avaliado")
                        
                        st.markdown("---")
            else:
                st.warning("⚠️ Nenhum jogador encontrado com esses critérios")
    
    # TAB 2: Análise Financeira
    with tab2:
        st.subheader("📊 Análise Financeira")
        
        # Busca todos os jogadores com info salarial
        df_financeiro = db.buscar_por_faixa_salarial(moeda='BRL')
        
        if not df_financeiro.empty and df_financeiro['salario_mensal_max'].notna().any():
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de distribuição salarial por posição
                df_plot = df_financeiro[df_financeiro['salario_mensal_max'].notna()].copy()
                df_plot['salario_medio'] = (df_plot['salario_mensal_min'] + df_plot['salario_mensal_max']) / 2
                
                fig_pos = px.box(
                    df_plot,
                    x='posicao',
                    y='salario_medio',
                    title='Distribuição Salarial por Posição',
                    labels={'salario_medio': 'Salário Médio (R$)', 'posicao': 'Posição'}
                )
                st.plotly_chart(fig_pos, use_container_width=True)
            
            with col2:
                # Top 10 maiores salários
                df_top = df_plot.nlargest(10, 'salario_medio')
                
                fig_top = px.bar(
                    df_top,
                    x='salario_medio',
                    y='nome',
                    orientation='h',
                    title='Top 10 Maiores Salários',
                    labels={'salario_medio': 'Salário Médio (R$)', 'nome': ''}
                )
                st.plotly_chart(fig_top, use_container_width=True)
            
            # Estatísticas por clube
            st.markdown("### 📈 Estatísticas por Clube")
            
            df_clubes = df_plot.groupby('clube').agg({
                'salario_medio': ['mean', 'min', 'max', 'count']
            }).round(2)
            
            df_clubes.columns = ['Salário Médio', 'Mínimo', 'Máximo', 'Qtd Jogadores']
            df_clubes = df_clubes.sort_values('Salário Médio', ascending=False)
            
            st.dataframe(
                df_clubes.style.format({
                    'Salário Médio': lambda x: formatar_moeda(x),
                    'Mínimo': lambda x: formatar_moeda(x),
                    'Máximo': lambda x: formatar_moeda(x)
                }),
                use_container_width=True
            )
        else:
            st.info("📊 Adicione informações salariais para ver análises")
    
    # TAB 3: Editar Informações Financeiras
    with tab3:
        st.subheader("✏️ Editar Informações Financeiras")
        
        # Seletor de jogador
        conn = db.conn
        df_jogadores = pd.read_sql("SELECT id, nome, posicao, clube FROM jogadores ORDER BY nome", conn)
        conn.close()
        
        if df_jogadores.empty:
            st.warning("⚠️ Nenhum jogador cadastrado")
            return
        
        jogador_selecionado = st.selectbox(
            "Selecione o Jogador",
            options=df_jogadores['id'].tolist(),
            format_func=lambda x: f"{df_jogadores[df_jogadores['id']==x]['nome'].values[0]} - {df_jogadores[df_jogadores['id']==x]['clube'].values[0]}"
        )
        
        if jogador_selecionado:
            # Busca dados atuais
            dados_atuais = db.obter_dados_financeiros(jogador_selecionado)
            
            if dados_atuais is None:
                dados_atuais = {
                    'salario_min': 0,
                    'salario_max': 0,
                    'moeda': 'BRL',
                    'bonificacoes': '',
                    'custo_transferencia': 0,
                    'clausula': 0,
                    'percentual_direitos': 100,
                    'condicoes': '',
                    'observacoes': '',
                    'agente_telefone': '',
                    'agente_email': '',
                    'agente_comissao': 0
                }
            
            with st.form("form_financeiro"):
                st.markdown("#### 💰 Informações Salariais")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    salario_min = st.number_input(
                        "Salário Mínimo",
                        value=float(dados_atuais['salario_min'] or 0),
                        step=1000.0
                    )
                
                with col2:
                    salario_max = st.number_input(
                        "Salário Máximo",
                        value=float(dados_atuais['salario_max'] or 0),
                        step=1000.0
                    )
                
                with col3:
                    moeda_edit = st.selectbox(
                        "Moeda",
                        ["BRL", "EUR", "USD", "GBP"],
                        index=["BRL", "EUR", "USD", "GBP"].index(dados_atuais['moeda'] or 'BRL')
                    )
                
                bonificacoes = st.text_area(
                    "Bonificações e Bônus",
                    value=dados_atuais['bonificacoes'] or '',
                    help="Ex: Bônus por gol, assistência, títulos, etc."
                )
                
                st.markdown("#### 💼 Condições de Negócio")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    custo_transferencia = st.number_input(
                        "Custo de Transferência",
                        value=float(dados_atuais['custo_transferencia'] or 0),
                        step=10000.0
                    )
                
                with col2:
                    clausula = st.number_input(
                        "Cláusula de Recisão",
                        value=float(dados_atuais['clausula'] or 0),
                        step=10000.0
                    )
                
                with col3:
                    percentual_direitos = st.number_input(
                        "% Direitos Econômicos",
                        min_value=0,
                        max_value=100,
                        value=int(dados_atuais['percentual_direitos'] or 100),
                        step=5
                    )
                
                condicoes = st.text_area(
                    "Condições de Negócio",
                    value=dados_atuais['condicoes'] or '',
                    help="Detalhes sobre formas de pagamento, parcelamento, etc."
                )
                
                observacoes = st.text_area(
                    "Observações Gerais",
                    value=dados_atuais['observacoes'] or ''
                )
                
                st.markdown("#### 👔 Informações do Agente")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    agente_telefone = st.text_input(
                        "Telefone do Agente",
                        value=dados_atuais['agente_telefone'] or ''
                    )
                
                with col2:
                    agente_email = st.text_input(
                        "Email do Agente",
                        value=dados_atuais['agente_email'] or ''
                    )
                
                agente_comissao = st.number_input(
                    "Comissão do Agente (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(dados_atuais['agente_comissao'] or 0),
                    step=0.5
                )
                
                submit = st.form_submit_button("💾 Salvar Informações", use_container_width=True, type="primary")
                
                if submit:
                    dados_financeiros = {
                        'salario_min': salario_min if salario_min > 0 else None,
                        'salario_max': salario_max if salario_max > 0 else None,
                        'moeda': moeda_edit,
                        'bonificacoes': bonificacoes if bonificacoes else None,
                        'custo_transferencia': custo_transferencia if custo_transferencia > 0 else None,
                        'condicoes': condicoes if condicoes else None,
                        'clausula': clausula if clausula > 0 else None,
                        'percentual_direitos': percentual_direitos,
                        'observacoes': observacoes if observacoes else None
                    }
                    
                    # Usuario padrão (pode ser ajustado se tiver sistema de login)
                    usuario_id = st.session_state.get('usuario', {}).get('id', 1)
                    
                    if db.atualizar_financeiro(jogador_selecionado, dados_financeiros, usuario_id):
                        st.success("✅ Informações financeiras atualizadas com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao atualizar informações")
    
    # TAB 4: Gestão de Agentes
    with tab4:
        st.subheader("👔 Agentes dos Jogadores")
        
        # Lista de agentes
        conn = db.get_connection()
        df_agentes = pd.read_sql("""
            SELECT agente_nome, agente_empresa, COUNT(*) as qtd_jogadores
            FROM jogadores
            WHERE agente_nome IS NOT NULL
            GROUP BY agente_nome, agente_empresa
            ORDER BY qtd_jogadores DESC
        """, conn)
        conn.close()
        
        if not df_agentes.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📋 Lista de Agentes")
                
                for _, agente in df_agentes.iterrows():
                    with st.container():
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            st.markdown(f"**{agente['agente_nome']}**")
                            if pd.notna(agente['agente_empresa']):
                                st.caption(f"🏢 {agente['agente_empresa']}")
                        
                        with col_b:
                            st.metric("Jogadores", agente['qtd_jogadores'])
                        
                        st.markdown("---")
            
            with col2:
                st.markdown("### 📊 Estatísticas")
                st.metric("Total de Agentes", len(df_agentes))
                st.metric("Jogadores Representados", df_agentes['qtd_jogadores'].sum())
        else:
            st.info("👔 Nenhum agente cadastrado ainda")
            st.markdown("Use o script de scraping para buscar agentes do Transfermarkt")
