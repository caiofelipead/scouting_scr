"""
Dashboard Interativo de Scouting
Sistema moderno de visualização e análise de jogadores
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import ScoutingDatabase
from datetime import datetime, timedelta
import numpy as np
import os
import time

# Configuração da página
st.set_page_config(
    page_title="Scout Pro - Sistema de Monitoramento",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhor visual
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 1rem;
    }
    h2 {
        color: #2c3e50;
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_database():
    """Inicializa conexão com banco de dados"""
    return ScoutingDatabase()

def get_foto_jogador(id_jogador):
    """Retorna o caminho da foto do jogador ou uma imagem placeholder"""
    foto_path = f'fotos/{id_jogador}.jpg'
    if os.path.exists(foto_path):
        return foto_path
    else:
        return None

def criar_radar_avaliacao(notas_dict, titulo="Avaliação do Atleta"):
    """
    Cria gráfico de radar para avaliação do jogador
    notas_dict: {'Tático': 4.5, 'Técnico': 4.0, 'Físico': 3.5, 'Mental': 4.2}
    """
    categorias = list(notas_dict.keys())
    valores = list(notas_dict.values())

    # Adicionar o primeiro valor no final para fechar o polígono
    valores += valores[:1]

    # Ângulos para cada eixo
    angles = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angles += angles[:1]

    # Criar o gráfico
    fig = go.Figure()

    # Adicionar a área preenchida
    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=categorias + [categorias[0]],
        fill='toself',
        fillcolor='rgba(46, 204, 113, 0.4)',
        line=dict(color='rgb(46, 204, 113)', width=3),
        name='Avaliação'
    ))

    # Adicionar linhas de referência
    fig.add_trace(go.Scatterpolar(
        r=[3, 3, 3, 3, 3],
        theta=categorias + [categorias[0]],
        mode='lines',
        line=dict(color='rgba(128, 128, 128, 0.3)', width=1, dash='dash'),
        showlegend=False,
        hoverinfo='skip'
    ))

    # Configurar layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickmode='linear',
                tick0=0,
                dtick=1,
                gridcolor='rgba(128, 128, 128, 0.2)',
                showline=False
            ),
            angularaxis=dict(
                gridcolor='rgba(128, 128, 128, 0.2)',
                linecolor='rgba(128, 128, 128, 0.3)'
            )
        ),
        showlegend=False,
        title=dict(
            text=titulo,
            x=0.5,
            xanchor='center',
            font=dict(size=16, color='#2c3e50')
        ),
        height=400,
        margin=dict(l=80, r=80, t=80, b=40)
    )

    return fig

def criar_grafico_evolucao(df_avaliacoes):
    """Cria gráfico de linha mostrando evolução das notas ao longo do tempo"""
    if len(df_avaliacoes) == 0:
        return None

    df = df_avaliacoes.copy()
    df['data_avaliacao'] = pd.to_datetime(df['data_avaliacao'])
    df = df.sort_values('data_avaliacao')

    fig = go.Figure()

    categorias = ['nota_tatico', 'nota_tecnico', 'nota_fisico', 'nota_mental']
    nomes = ['Tático', 'Técnico', 'Físico', 'Mental']
    cores = ['#3498db', '#e74c3c', '#f39c12', '#9b59b6']

    for cat, nome, cor in zip(categorias, nomes, cores):
        fig.add_trace(go.Scatter(
            x=df['data_avaliacao'],
            y=df[cat],
            mode='lines+markers',
            name=nome,
            line=dict(color=cor, width=2),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title="Evolução das Avaliações",
        xaxis_title="Data",
        yaxis_title="Nota",
        yaxis=dict(range=[0, 5.5]),
        hovermode='x unified',
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

def exibir_perfil_jogador(db, id_jogador):
    """Exibe perfil detalhado do jogador"""
    conn = db.connect()

    try:
        id_busca = int(id_jogador)
    except:
        id_busca = id_jogador

    query = """
    SELECT 
        j.*,
        v.clube,
        v.liga_clube,
        v.posicao,
        v.data_fim_contrato,
        v.status_contrato
    FROM jogadores j
    LEFT JOIN vinculos v ON j.id_jogador = v.id_jogador
    WHERE j.id_jogador = ?
    """

    jogador = pd.read_sql_query(query, conn, params=(id_busca,))
    conn.close()

    if len(jogador) == 0:
        st.error(f"Jogador não encontrado! (ID buscado: {id_busca})")
        if st.button("Voltar para Lista"):
            st.session_state.pagina = 'dashboard'
            st.rerun()
        return

    jogador = jogador.iloc[0]

    # Layout de 2 colunas
    col1, col2 = st.columns([1, 2])

    with col1:
        foto_path = get_foto_jogador(id_busca)
        if foto_path:
            st.image(foto_path, width=300)
        else:
            st.markdown("""
            <div style='
                width: 300px; 
                height: 300px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 120px;
                color: white;
            '>
                ⚽
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.metric("Idade", f"{jogador['idade_atual']} anos" if pd.notna(jogador['idade_atual']) else "N/A")
        st.metric("Altura", f"{jogador['altura']} cm" if pd.notna(jogador['altura']) else "N/A")
        st.metric("Pé Dominante", jogador['pe_dominante'] if pd.notna(jogador['pe_dominante']) else "N/A")
        st.metric("Nacionalidade", jogador['nacionalidade'] if pd.notna(jogador['nacionalidade']) else "N/A")

    with col2:
        st.title(jogador['nome'])
        st.subheader(f"{jogador['posicao'] if pd.notna(jogador['posicao']) else 'N/A'} • {jogador['clube'] if pd.notna(jogador['clube']) else 'Livre'}")

        st.markdown("---")
        st.markdown("### 📋 Informações do Vínculo")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("**Clube Atual**")
            st.markdown(f"🏟️ {jogador['clube'] if pd.notna(jogador['clube']) else 'Livre'}")

        with col_b:
            st.markdown("**Liga**")
            st.markdown(f"🏆 {jogador['liga_clube'] if pd.notna(jogador['liga_clube']) else 'N/A'}")

        with col_c:
            st.markdown("**Fim de Contrato**")
            if pd.notna(jogador['data_fim_contrato']):
                st.markdown(f"📅 {jogador['data_fim_contrato']}")
            else:
                st.markdown("📅 N/A")

        st.markdown("---")
        status = jogador['status_contrato'] if pd.notna(jogador['status_contrato']) else 'desconhecido'

        status_color = {
            'ativo': '🟢',
            'ultimo_ano': '🟡',
            'ultimos_6_meses': '🔴',
            'vencido': '⚫',
            'livre': '⚪',
            'desconhecido': '❓'
        }

        status_text = {
            'ativo': 'Contrato Ativo',
            'ultimo_ano': 'Último Ano de Contrato',
            'ultimos_6_meses': 'Vence em Menos de 6 Meses',
            'vencido': 'Contrato Vencido',
            'livre': 'Jogador Livre',
            'desconhecido': 'Status Desconhecido'
        }

        st.markdown(f"### {status_color.get(status, '❓')} {status_text.get(status, 'Status Desconhecido')}")

        if pd.notna(jogador['data_fim_contrato']) and status not in ['vencido', 'livre']:
            try:
                data_fim = pd.to_datetime(jogador['data_fim_contrato'], dayfirst=True)
                dias_restantes = (data_fim - datetime.now()).days

                if dias_restantes > 0:
                    st.info(f"⏱️ **{dias_restantes} dias** até o vencimento do contrato")
                    dias_totais = 1095
                    progresso = max(0, min(100, (dias_restantes / dias_totais) * 100))
                    st.progress(progresso / 100)
            except:
                pass

    # ============== SEÇÃO DE AVALIAÇÕES ==============
    st.markdown("---")
    st.markdown("---")

    # Tabs para organizar avaliações
    tab_avaliacao, tab_historico, tab_evolucao = st.tabs([
        "📝 Nova Avaliação",
        "📊 Histórico",
        "📈 Evolução"
    ])

    with tab_avaliacao:
        st.markdown("### 📝 Registrar Nova Avaliação")
        st.markdown("Avalie o jogador nas dimensões principais:")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Formulário de avaliação
            with st.form("form_avaliacao"):
                data_avaliacao = st.date_input(
                    "Data da Avaliação",
                    value=datetime.now(),
                    format="DD/MM/YYYY"
                )
                
                # NOTA DE POTENCIAL EM DESTAQUE
                st.markdown("---")
                st.markdown("#### ⭐ Avaliação Geral de Potencial")
                nota_potencial = st.slider(
                    "Potencial do Jogador",
                    min_value=1.0,
                    max_value=5.0,
                    value=3.0,
                    step=0.5,
                    help="Avaliação geral do potencial do atleta considerando projeção futura e capacidade de desenvolvimento"
                )
                
                st.markdown("---")
                st.markdown("#### 📊 Notas por Dimensão (1 a 5)")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    nota_tatico = st.slider(
                        "⚙️ Tático",
                        min_value=1.0,
                        max_value=5.0,
                        value=3.0,
                        step=0.5,
                        help="Posicionamento, leitura de jogo, decisões táticas"
                    )
                    
                    nota_tecnico = st.slider(
                        "⚽ Técnico",
                        min_value=1.0,
                        max_value=5.0,
                        value=3.0,
                        step=0.5,
                        help="Domínio, passe, finalização, controle de bola"
                    )
                
                with col_b:
                    nota_fisico = st.slider(
                        "💪 Físico",
                        min_value=1.0,
                        max_value=5.0,
                        value=3.0,
                        step=0.5,
                        help="Velocidade, força, resistência, explosão"
                    )
                    
                    nota_mental = st.slider(
                        "🧠 Mental",
                        min_value=1.0,
                        max_value=5.0,
                        value=3.0,
                        step=0.5,
                        help="Concentração, liderança, inteligência emocional"
                    )
                
                observacoes = st.text_area(
                    "Observações",
                    placeholder="Adicione comentários sobre a avaliação, pontos fortes, áreas de desenvolvimento...",
                    height=100
                )
                
                avaliador = st.text_input(
                    "Avaliador",
                    placeholder="Seu nome (opcional)"
                )
                
                submitted = st.form_submit_button(
                    "💾 Salvar Avaliação",
                    use_container_width=True,
                    type="primary"
                )
                
                if submitted:
                    try:
                        db.salvar_avaliacao(
                            id_jogador=id_busca,
                            data_avaliacao=data_avaliacao.strftime('%Y-%m-%d'),
                            nota_potencial=nota_potencial,
                            nota_tatico=nota_tatico,
                            nota_tecnico=nota_tecnico,
                            nota_fisico=nota_fisico,
                            nota_mental=nota_mental,
                            observacoes=observacoes,
                            avaliador=avaliador
                        )
                        st.success("✅ Avaliação salva com sucesso!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar avaliação: {str(e)}")
                        st.error("Execute: python fix_avaliacoes.py")
        
        with col2:
            st.markdown("#### 📊 Preview do Radar")
            notas_preview = {
                'Tático': 3.0,
                'Técnico': 3.0,
                'Físico': 3.0,
                'Mental': 3.0
            }
            fig_preview = criar_radar_avaliacao(notas_preview, "Preview")
            st.plotly_chart(fig_preview, use_container_width=True)
            
            # Mostrar potencial em destaque
            st.markdown("---")
            st.metric(
                "⭐ Potencial",
                f"{3.0:.1f}",
                help="Avaliação geral de potencial"
            )

    # ============== FIM DA SEÇÃO DE AVALIAÇÕES ==============
    with col1:
                # ADICIONE ISTO NO INÍCIO
                st.markdown("---")
                st.markdown(f"### ⭐ Potencial: {ultima['nota_potencial']:.1f}/5.0")
                st.progress(ultima['nota_potencial'] / 5.0)
                st.markdown("---")
                
                st.markdown(f"""
                **Data:** {pd.to_datetime(ultima['data_avaliacao']).strftime('%d/%m/%Y')}  
                **Avaliador:** {ultima['avaliador'] if ultima['avaliador'] else 'Não informado'}
                """)
                
                # Métricas
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Tático", f"{ultima['nota_tatico']:.1f}")
                with col_b:
                    st.metric("Técnico", f"{ultima['nota_tecnico']:.1f}")
                with col_c:
                    st.metric("Físico", f"{ultima['nota_fisico']:.1f}")
                with col_d:
                    st.metric("Mental", f"{ultima['nota_mental']:.1f}")
                    
    st.markdown("---")
    st.markdown("### 📊 Informações Adicionais")

    col_i, col_ii = st.columns(2)

    with col_i:
        st.markdown("**Ano de Nascimento**")
        st.markdown(f"🎂 {jogador['ano_nascimento'] if pd.notna(jogador['ano_nascimento']) else 'N/A'}")

    with col_ii:
        st.markdown("**ID do Jogador**")
        st.markdown(f"🔢 {jogador['id_jogador']}")

    if pd.notna(jogador.get('transfermarkt_id')):
        st.markdown("---")
        st.link_button(
            "📊 Ver no Transfermarkt",
            f"https://www.transfermarkt.com.br/player/profil/spieler/{jogador['transfermarkt_id']}",
            use_container_width=True
        )

def exibir_lista_com_fotos(df_display, db):
    """Exibe lista de jogadores com fotos em formato de cards"""
    st.markdown("### 👥 Jogadores")

    for i in range(0, len(df_display), 4):
        cols = st.columns(4)

        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(df_display):
                jogador = df_display.iloc[idx]

                with col:
                    foto_path = get_foto_jogador(jogador['id_jogador'])

                    if foto_path:
                        st.image(foto_path, use_container_width=True)
                    else:
                        st.markdown("""
                        <div style='
                            width: 100%; 
                            padding-top: 100%;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            border-radius: 10px;
                            position: relative;
                        '>
                            <div style='
                                position: absolute;
                                top: 50%;
                                left: 50%;
                                transform: translate(-50%, -50%);
                                font-size: 60px;
                            '>⚽</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown(f"**{jogador['nome']}**")
                    st.caption(f"{jogador['posicao'] if pd.notna(jogador['posicao']) else 'N/A'}")
                    st.caption(f"{jogador['clube'] if pd.notna(jogador['clube']) else 'Livre'}")

                    if st.button("Ver Perfil", key=f"perfil_{jogador['id_jogador']}", use_container_width=True):
                        st.session_state.pagina = 'perfil'
                        st.session_state.jogador_selecionado = jogador['id_jogador']
                        st.rerun()

def criar_gauge_contrato(dias_restantes):
    """Cria gráfico gauge para status de contrato"""
    if dias_restantes <= 180:
        color = "red"
        status = "URGENTE"
    elif dias_restantes <= 365:
        color = "orange"
        status = "ATENÇÃO"
    else:
        color = "green"
        status = "OK"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=dias_restantes,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Dias até vencimento<br><span style='font-size:0.8em;color:{color}'>{status}</span>"},
        gauge={
            'axis': {'range': [None, 1095]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 180], 'color': "rgba(255,0,0,0.3)"},
                {'range': [180, 365], 'color': "rgba(255,165,0,0.3)"},
                {'range': [365, 1095], 'color': "rgba(0,255,0,0.3)"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': 365
            }
        }
    ))

    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def main():
    # Header
    st.title("⚽ Scout Pro - Sistema de Monitoramento de Jogadores")
    st.markdown("---")

    # Inicializar banco de dados
    db = get_database()

    # Criar tabela de avaliações se não existir
    db.criar_tabela_avaliacoes()

    # Sistema de navegação com session_state
    if 'pagina' not in st.session_state:
        st.session_state.pagina = 'dashboard'
    if 'jogador_selecionado' not in st.session_state:
        st.session_state.jogador_selecionado = None

    # Se estiver na página de perfil
    if st.session_state.pagina == 'perfil':
        if st.button("← Voltar para Dashboard"):
            st.session_state.pagina = 'dashboard'
            st.session_state.jogador_selecionado = None
            st.rerun()

        st.markdown("---")
        exibir_perfil_jogador(db, st.session_state.jogador_selecionado)
        return

    # Dashboard principal continua aqui
    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")

    # Carregar dados
    df_jogadores = db.get_jogadores_com_vinculos()

    # Verificar se há dados
    if len(df_jogadores) == 0:
        st.error("⚠️ **Banco de dados vazio!**")
        st.info("""
        **Você precisa importar os dados primeiro:**
        
        1. Configure o Google Sheets API (se ainda não fez)
        2. Execute no terminal:
```bash
        python import_data.py
```
        3. Recarregue esta página (pressione R)
        """)
        st.stop()

    # Limpar dados de idade (remover valores vazios e inválidos)
    df_jogadores['idade_atual'] = pd.to_numeric(df_jogadores['idade_atual'], errors='coerce')

    # Filtros
    posicoes = ['Todas'] + sorted(df_jogadores['posicao'].dropna().unique().tolist())
    posicao_selecionada = st.sidebar.selectbox("Posição", posicoes)

    ligas = ['Todas'] + sorted(df_jogadores['liga_clube'].dropna().unique().tolist())
    liga_selecionada = st.sidebar.selectbox("Liga", ligas)

    # Verificar se tem idades válidas para o slider
    idades_validas = df_jogadores['idade_atual'].dropna()
    if len(idades_validas) > 0:
        idade_min_db = int(idades_validas.min())
        idade_max_db = int(idades_validas.max())
    else:
        idade_min_db = 16
        idade_max_db = 40
        st.sidebar.warning("⚠️ Dados de idade incompletos na planilha")

    idade_min, idade_max = st.sidebar.slider(
        "Faixa Etária",
        idade_min_db,
        idade_max_db,
        (max(18, idade_min_db), min(35, idade_max_db))
    )

    status_contrato = ['Todos'] + sorted(df_jogadores['status_contrato'].dropna().unique().tolist())
    status_selecionado = st.sidebar.multiselect(
        "Status do Contrato",
        status_contrato,
        default=['Todos']
    )

    # Aplicar filtros
    df_filtrado = df_jogadores.copy()

    if posicao_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['posicao'] == posicao_selecionada]

    if liga_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['liga_clube'] == liga_selecionada]

    df_filtrado = df_filtrado[
        (df_filtrado['idade_atual'].notna()) &
        (df_filtrado['idade_atual'] >= idade_min) &
        (df_filtrado['idade_atual'] <= idade_max)
    ]

    if 'Todos' not in status_selecionado and len(status_selecionado) > 0:
        df_filtrado = df_filtrado[df_filtrado['status_contrato'].isin(status_selecionado)]

    # KPIs principais
    col1, col2, col3, col4, col5 = st.columns(5)

    stats = db.get_estatisticas_gerais()

    with col1:
        st.metric(
            "Total de Jogadores",
            stats['total_jogadores'],
            delta=None,
            help="Total de jogadores no banco de dados"
        )

    with col2:
        st.metric(
            "Vínculos Ativos",
            stats['total_vinculos_ativos'],
            delta=None,
            help="Jogadores com contratos ativos"
        )

    with col3:
        st.metric(
            "Contratos Vencendo",
            stats['contratos_vencendo'],
            delta=None,
            help="Contratos vencendo nos próximos 12 meses"
        )

    with col4:
        st.metric(
            "Alertas Ativos",
            stats['alertas_ativos'],
            delta=None,
            help="Alertas que requerem atenção"
        )

    with col5:
        st.metric(
            "Resultados Filtrados",
            len(df_filtrado),
            delta=None,
            help="Jogadores após aplicar filtros"
        )

    st.markdown("---")

    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Visão Geral",
        "👥 Lista de Jogadores",
        "🚨 Alertas",
        "📈 Análises"
    ])

    with tab1:
        st.header("Visão Geral do Banco de Jogadores")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distribuição por Posição")
            posicao_counts = df_filtrado['posicao'].value_counts()
            fig_posicao = px.pie(
                values=posicao_counts.values,
                names=posicao_counts.index,
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_posicao.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_posicao, use_container_width=True)

        with col2:
            st.subheader("Distribuição por Idade")
            df_idade_valida = df_filtrado[df_filtrado['idade_atual'].notna()]
            fig_idade = px.histogram(
                df_idade_valida,
                x='idade_atual',
                nbins=20,
                color_discrete_sequence=['#1f77b4']
            )
            fig_idade.update_layout(
                xaxis_title="Idade",
                yaxis_title="Quantidade de Jogadores",
                showlegend=False
            )
            st.plotly_chart(fig_idade, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 10 Nacionalidades")
            nac_counts = df_filtrado['nacionalidade'].value_counts().head(10)
            fig_nac = px.bar(
                x=nac_counts.values,
                y=nac_counts.index,
                orientation='h',
                color=nac_counts.values,
                color_continuous_scale='Blues'
            )
            fig_nac.update_layout(
                xaxis_title="Quantidade",
                yaxis_title="",
                showlegend=False,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_nac, use_container_width=True)

        with col2:
            st.subheader("Status dos Contratos")
            status_counts = df_filtrado['status_contrato'].value_counts()

            color_map = {
                'ativo': '#2ecc71',
                'ultimo_ano': '#f39c12',
                'ultimos_6_meses': '#e74c3c',
                'vencido': '#95a5a6',
                'livre': '#34495e'
            }
            colors = [color_map.get(status, '#3498db') for status in status_counts.index]

            fig_status = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                color=status_counts.index,
                color_discrete_map=color_map
            )
            fig_status.update_layout(
                xaxis_title="Status",
                yaxis_title="Quantidade",
                showlegend=False
            )
            st.plotly_chart(fig_status, use_container_width=True)

    with tab2:
        st.header("Lista Completa de Jogadores")

        search_term = st.text_input("🔎 Buscar jogador por nome", "")

        if search_term:
            df_filtrado = df_filtrado[
                df_filtrado['nome'].str.contains(search_term, case=False, na=False)
            ]

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            ordenar_por = st.selectbox(
                "Ordenar por",
                ['nome', 'idade_atual', 'clube', 'posicao', 'status_contrato']
            )
        with col2:
            ordem = st.radio("Ordem", ['Crescente', 'Decrescente'])
        with col3:
            visualizacao = st.radio("Visualização", ['Cards', 'Tabela'])

        df_display = df_filtrado.sort_values(
            by=ordenar_por,
            ascending=(ordem == 'Crescente')
        ).reset_index(drop=True)

        st.markdown("---")

        if visualizacao == 'Cards':
            exibir_lista_com_fotos(df_display, db)
        else:
            df_display_formatted = df_display.copy()
            df_display_formatted.columns = [
                'ID', 'Nome', 'Nacionalidade', 'Idade', 'Altura', 'Pé',
                'Clube', 'Liga', 'Posição', 'Fim Contrato', 'Status'
            ]

            def highlight_status(row):
                if row['Status'] == 'ultimos_6_meses':
                    return ['background-color: #ffcccc'] * len(row)
                elif row['Status'] == 'ultimo_ano':
                    return ['background-color: #fff4cc'] * len(row)
                else:
                    return [''] * len(row)

            st.dataframe(
                df_display_formatted.style.apply(highlight_status, axis=1),
                use_container_width=True,
                height=500
            )

        st.markdown("---")
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar dados filtrados (CSV)",
            data=csv,
            file_name=f'jogadores_filtrados_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
            use_container_width=True
        )

    with tab3:
        st.header("Central de Alertas")

        alertas = db.get_alertas_ativos()

        if len(alertas) == 0:
            st.info("✅ Nenhum alerta ativo no momento!")
        else:
            prioridade_filter = st.multiselect(
                "Filtrar por prioridade",
                ['alta', 'media', 'baixa'],
                default=['alta', 'media', 'baixa']
            )

            alertas_filtrados = alertas[alertas['prioridade'].isin(prioridade_filter)]

            for _, alerta in alertas_filtrados.iterrows():
                if alerta['prioridade'] == 'alta':
                    st.error(f"🚨 **{alerta['jogador']}** - {alerta['descricao']}")
                elif alerta['prioridade'] == 'media':
                    st.warning(f"⚠️ **{alerta['jogador']}** - {alerta['descricao']}")
                else:
                    st.info(f"ℹ️ **{alerta['jogador']}** - {alerta['descricao']}")

    with tab4:
        st.header("Análises Avançadas")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Jogadores por Liga")
            liga_counts = df_filtrado['liga_clube'].value_counts().head(10)
            fig_liga = px.bar(
                x=liga_counts.index,
                y=liga_counts.values,
                color=liga_counts.values,
                color_continuous_scale='Viridis'
            )
            fig_liga.update_layout(
                xaxis_title="",
                yaxis_title="Quantidade",
                showlegend=False,
                coloraxis_showscale=False,
                xaxis={'tickangle': 45}
            )
            st.plotly_chart(fig_liga, use_container_width=True)

        with col2:
            st.subheader("Idade Média por Posição")
            idade_media = df_filtrado.groupby('posicao')['idade_atual'].mean().sort_values()
            fig_idade_pos = px.bar(
                x=idade_media.values,
                y=idade_media.index,
                orientation='h',
                color=idade_media.values,
                color_continuous_scale='RdYlGn_r'
            )
            fig_idade_pos.update_layout(
                xaxis_title="Idade Média",
                yaxis_title="",
                showlegend=False,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_idade_pos, use_container_width=True)

        st.subheader("Heatmap: Nacionalidade x Posição")

        top_nacs = df_filtrado['nacionalidade'].value_counts().head(10).index
        df_heatmap = df_filtrado[df_filtrado['nacionalidade'].isin(top_nacs)]

        heatmap_data = pd.crosstab(df_heatmap['nacionalidade'], df_heatmap['posicao'])

        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Posição", y="Nacionalidade", color="Quantidade"),
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        fig_heatmap.update_layout(height=500)
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #7f8c8d;'>"
        f"🎯 Scout Pro v1.0 | Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
